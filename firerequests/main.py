import asyncio
import aiohttp
import aiofiles
import os
import time
import requests
import nest_asyncio
import socket
import fire
from urllib.parse import urlparse
from aiohttp import ClientSession
from tqdm.asyncio import tqdm
from typing import Union, Dict, Any, List, Optional

# Enable nested event loops for environments like Jupyter
nest_asyncio.apply()

BASE_WAIT_TIME = 300
MAX_WAIT_TIME = 10000

class FireRequests:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def exponential_backoff(self, base_wait_time: int, attempt: int, max_time: int) -> int:
        return min(base_wait_time + attempt ** 2 + self._jitter(), max_time)

    def _jitter(self) -> int:
        return os.urandom(2)[0] % 500

    async def download_chunk(
        self, session: ClientSession, url: str, start: int, stop: int, headers: Dict[str, str], filename: str
    ):
        range_header = {"Range": f"bytes={start}-{stop}"}
        headers.update(range_header)
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                content = await response.read()
    
                async with aiofiles.open(filename, "r+b") as f:
                    await f.seek(start)
                    await f.write(content)
        except Exception as e:
            print(f"Error in download_chunk: {e}")

    async def download_file(
        self, url: str, filename: str, max_files: int, chunk_size: int, headers: Optional[Dict[str, str]] = None, 
        parallel_failures: int = 3, max_retries: int = 5, callback: Optional[Any] = None, show_progress: bool = True, progress_desc: Optional[str] = None
    ):
        headers = headers or {"User-Agent": "Wget/1.21.2", "Accept": "*/*", "Accept-Encoding": "identity", "Connection": "Keep-Alive"}
        try:
            async with aiohttp.ClientSession() as session:
                # Follow redirects and get the final download URL
                async with session.head(url, headers=headers, allow_redirects=True) as resp:
                    # Resolve the domain name and get IP address
                    url = str(resp.url)
                    print(f"--{time.strftime('%Y-%m-%d %H:%M:%S')}--  {url}")
                    parsed_url = urlparse(url)
                    ip_address = socket.gethostbyname(parsed_url.hostname)
                    print(f"Resolving {parsed_url.hostname} ({parsed_url.hostname})... {ip_address}")
                    print(f"Connecting to {parsed_url.hostname} ({parsed_url.hostname})|{ip_address}|:443... connected.")
                    print(f"HTTP request sent, awaiting response... {resp.status} {resp.reason}")
                    file_size = int(resp.headers['Content-Length'])
                    content_type = resp.headers.get('Content-Type', 'application/octet-stream')
                    print(f"Length: {file_size} ({file_size / (1024 * 1024 * 1024):.1f}G) [{content_type}]")
                    print(f"Saving to: ‘{filename}’\n")
                    chunks = range(0, file_size, chunk_size)
    
                # Create an empty file
                async with aiofiles.open(filename, "wb") as f:
                    await f.seek(file_size - 1)
                    await f.write(b"\0")
    
                semaphore = asyncio.Semaphore(max_files)
                tasks = []
                for start in chunks:
                    stop = min(start + chunk_size - 1, file_size - 1)
                    tasks.append(self.download_chunk_with_retries(
                        session, url, filename, start, stop, headers, semaphore, parallel_failures, max_retries
                    ))

                if show_progress:
                    progress_bar = tqdm(total=file_size, unit="B", unit_scale=True, desc=progress_desc)

                for chunk_result in asyncio.as_completed(tasks):
                    downloaded = await chunk_result
                    if show_progress:
                        progress_bar.update(downloaded)
                    if callback:
                        await callback(downloaded)

                if show_progress:
                    progress_bar.close()

        except Exception as e:
            print(f"Error in download_file: {e}")

    async def download_chunk_with_retries(
        self, session: ClientSession, url: str, filename: str, start: int, stop: int, headers: Dict[str, str], 
        semaphore: asyncio.Semaphore, parallel_failures: int, max_retries: int
    ):
        async with semaphore:
            attempt = 0
            while attempt <= max_retries:
                try:
                    await self.download_chunk(session, url, start, stop, headers, filename)
                    return stop - start + 1
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    await asyncio.sleep(self.exponential_backoff(BASE_WAIT_TIME, attempt, MAX_WAIT_TIME))
                    attempt += 1

    async def upload_file(
        self, file_path: str, parts_urls: List[str], chunk_size: int, max_files: int, 
        parallel_failures: int = 3, max_retries: int = 5, callback: Optional[Any] = None, show_progress: bool = True, progress_desc: Optional[str] = None
    ):
        file_size = os.path.getsize(file_path)
        part_size = file_size // len(parts_urls)
        last_part_size = file_size - part_size * (len(parts_urls) - 1)  # To handle any remaining bytes
    
        semaphore = asyncio.Semaphore(max_files)
        tasks = []
        try:
            async with aiohttp.ClientSession() as session:
                for part_number, part_url in enumerate(parts_urls):
                    if part_number == len(parts_urls) - 1:
                        start = part_number * part_size
                        size = last_part_size
                    else:
                        start = part_number * part_size
                        size = part_size
    
                    tasks.append(self.upload_chunk_with_retries(
                        session, part_url, file_path, start, size, chunk_size, semaphore, parallel_failures, max_retries
                    ))
    
                if show_progress:
                    progress_bar = tqdm(total=file_size, unit="B", unit_scale=True, desc=progress_desc)
    
                for chunk_result in asyncio.as_completed(tasks):
                    uploaded = await chunk_result
                    if show_progress:
                        progress_bar.update(uploaded)
                    if callback:
                        await callback(uploaded)
    
                if show_progress:
                    progress_bar.close()
    
        except Exception as e:
            print(f"Error in upload_file: {e}")

    async def upload_chunk_with_retries(
        self, session: ClientSession, url: str, file_path: str, start: int, part_size: int, chunk_size: int, 
        semaphore: asyncio.Semaphore, parallel_failures: int, max_retries: int
    ):
        async with semaphore:
            attempt = 0
            while attempt <= max_retries:
                try:
                    # Adjust chunk upload for each part
                    return await self.upload_chunks(session, url, file_path, start, part_size, chunk_size)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    await asyncio.sleep(self.exponential_backoff(BASE_WAIT_TIME, attempt, MAX_WAIT_TIME))
                    attempt += 1

    async def upload_chunks(
        self, session: ClientSession, url: str, file_path: str, start: int, part_size: int, chunk_size: int
    ):
        try:
            # Upload in smaller chunks within each part range
            total_uploaded = 0
            async with aiofiles.open(file_path, 'rb') as f:
                while total_uploaded < part_size:
                    await f.seek(start + total_uploaded)
                    chunk = await f.read(min(chunk_size, part_size - total_uploaded))
                    if not chunk:
                        break

                    headers = {'Content-Length': str(len(chunk))}
                    async with session.put(url, data=chunk, headers=headers) as response:
                        response.raise_for_status()

                    total_uploaded += len(chunk)
            return total_uploaded
        except Exception as e:
            print(f"Error in upload_chunks: {e}")
            return 0

    def download(self, urls: Union[str, List[str]], filenames: Optional[Union[str, List[str]]] = None, headers: Optional[Dict[str, str]] = None, max_files: int = 10, chunk_size: int = 2 * 1024 * 1024, show_progress: Optional[bool] = None) -> List[str]:
        """
        Downloads files from a given URL or a list of URLs asynchronously in chunks, with support for parallel downloads.
    
        Args:
            urls (Union[str, List[str]]): The URL or list of URLs of the files to download.
            filenames (Optional[Union[str, List[str]]]): The filename or list of filenames to save locally. 
                If not provided, filenames will be extracted from the URLs.
            headers (Optional[Dict[str, str]]): Headers to include in the download requests.
            max_files (int): The maximum number of concurrent file download chunks. Defaults to 10.
            chunk_size (int): The size of each chunk to download, in bytes. Defaults to 2MB.
            show_progress (Optional[bool]): Whether to show a progress bar. Defaults to True for single file, False for multiple files.
    
        Usage:
            - This function downloads the files in parallel chunks, speeding up the process.
        """
        if isinstance(urls, str):
            urls = [urls]
        if isinstance(filenames, str):
            filenames = [filenames]
    
        if filenames is None:
            filenames = [os.path.basename(urlparse(url).path) for url in urls]
        elif len(filenames) != len(urls):
            raise ValueError("The number of filenames must match the number of URLs")
    
        # Set default for show_progress based on whether it's a single file or list
        if show_progress is None:
            show_progress = len(urls) == 1
    
        async def download_all():
            tasks = [self.download_file(url, filename, max_files, chunk_size, headers, show_progress=show_progress) for url, filename in zip(urls, filenames)]
            await asyncio.gather(*tasks)
    
        asyncio.run(download_all())
        
        return filenames

    def upload(self, file_path: str, parts_urls: List[str], chunk_size: int = 2 * 1024 * 1024, max_files: int = 10, show_progress: Optional[bool] = True):
        """
        Uploads a file to multiple URLs in chunks asynchronously, with support for parallel uploads.
    
        Args:
            file_path (str): The local path to the file to upload.
            parts_urls (List[str]): A list of URLs where each part of the file will be uploaded.
            chunk_size (int): The size of each chunk to upload, in bytes. Defaults to 2MB.
            max_files (int): The maximum number of concurrent file upload chunks. Defaults to 10.
            show_progress (bool): Whether to show a progress bar during upload. Defaults to True.
    
        Usage:
            - The function divides the file into smaller chunks and uploads them in parallel to different URLs.
        """
        asyncio.run(self.upload_file(file_path, parts_urls, chunk_size, max_files, show_progress=show_progress))

    def normal_download(self, url: str, filename: str):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, desc="Normal Download 🐌")
        with open(filename, 'wb') as f:
            for data in response.iter_content(2 * 1024 * 1024):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()

    def compare(self, url: str, filename: Optional[str] = None):
        """
        Compares the time taken to download a file using both the normal (synchronous) method and the asynchronous method.
    
        Args:
            url (str): The URL of the file to download.
            filename (Optional[str]): The name of the file to save locally. If not provided, it will be extracted from the URL.
    
        Usage:
            - The function first downloads the file using the traditional `requests` method and measures the time taken.
            - It then downloads the same file using the asynchronous `firerequests` method and measures the time taken.
            - Finally, it prints a comparison of both download times.
        """
        if filename is None:
            filename = os.path.basename(urlparse(url).path)
        try:
            start_time = time.time()
            self.normal_download(url, filename)
            normal_time = time.time() - start_time
    
            os.remove(filename)
    
            start_time = time.time()
            asyncio.run(self.download_file(url, filename, max_files=10, chunk_size=2 * 1024 * 1024))
            fire_time = time.time() - start_time
    
            print(f"\n🐌 Download Time: {normal_time:.2f} seconds")
            print(f"🔥 Download Time: {fire_time:.2f} seconds\n")
        except Exception as e:
            print(f"Error in compare: {e}")

    def op(self, max_reqs: int = 10, prompts: Optional[List[str]] = None):
        """
        Decorator to parallelize a user-defined prompt function over a list of prompts.

        Args:
            max_reqs (int): Maximum number of parallel tasks.
            prompts (List[str]): Prompts to process.

        Returns:
            Decorated function executed in parallel using asyncio.
        """
        def decorator(func):
            async def run_batch(prompts_batch):
                tasks = [asyncio.to_thread(func, prompt=prompt) for prompt in prompts_batch]
                return await asyncio.gather(*tasks)

            def wrapper(*args, **kwargs):
                if prompts is None:
                    raise ValueError("You must pass a list of prompts to the decorator.")
                results = []

                async def run_all():
                    for i in range(0, len(prompts), max_reqs):
                        batch = prompts[i:i + max_reqs]
                        batch_results = await run_batch(batch)
                        results.extend(batch_results)
                    return results

                return self.loop.run_until_complete(run_all())

            return wrapper
        return decorator

def main():
    fire.Fire(FireRequests)
