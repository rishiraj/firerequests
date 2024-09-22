import asyncio
import aiohttp
import aiofiles
import os
import time
import requests
import nest_asyncio
from aiohttp import ClientSession
from aiofiles.os import remove
from tqdm.asyncio import tqdm
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional

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
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            content = await response.read()

            async with aiofiles.open(filename, "r+b") as f:
                await f.seek(start)
                await f.write(content)

    async def download_file(
        self, url: str, filename: str, max_files: int, chunk_size: int, headers: Optional[Dict[str, str]] = None, 
        parallel_failures: int = 0, max_retries: int = 0, callback: Optional[Any] = None
    ):
        headers = headers or {}
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as resp:
                file_size = int(resp.headers['Content-Length'])
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
            
            progress_bar = tqdm(total=file_size, unit="B", unit_scale=True, desc="Downloading")
            for chunk_result in asyncio.as_completed(tasks):
                downloaded = await chunk_result
                progress_bar.update(downloaded)
                if callback:
                    await callback(downloaded)
            progress_bar.close()

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
        parallel_failures: int = 0, max_retries: int = 0, callback: Optional[Any] = None
    ):
        file_size = os.path.getsize(file_path)
        tasks = []
        semaphore = asyncio.Semaphore(max_files)

        async with aiohttp.ClientSession() as session:
            for part_number, part_url in enumerate(parts_urls):
                start = part_number * chunk_size
                tasks.append(self.upload_chunk_with_retries(
                    session, part_url, file_path, start, chunk_size, semaphore, parallel_failures, max_retries
                ))

            progress_bar = tqdm(total=file_size, unit="B", unit_scale=True, desc="Uploading")
            for chunk_result in asyncio.as_completed(tasks):
                uploaded = await chunk_result
                progress_bar.update(uploaded)
                if callback:
                    await callback(uploaded)
            progress_bar.close()

    async def upload_chunk_with_retries(
        self, session: ClientSession, url: str, file_path: str, start: int, chunk_size: int, 
        semaphore: asyncio.Semaphore, parallel_failures: int, max_retries: int
    ):
        async with semaphore:
            attempt = 0
            while attempt <= max_retries:
                try:
                    return await self.upload_chunk(session, url, file_path, start, chunk_size)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    await asyncio.sleep(self.exponential_backoff(BASE_WAIT_TIME, attempt, MAX_WAIT_TIME))
                    attempt += 1

    async def upload_chunk(
        self, session: ClientSession, url: str, file_path: str, start: int, chunk_size: int
    ):
        async with aiofiles.open(file_path, 'rb') as f:
            await f.seek(start)
            chunk = await f.read(chunk_size)
            headers = {'Content-Length': str(len(chunk))}
            async with session.put(url, data=chunk, headers=headers) as response:
                response.raise_for_status()
        return len(chunk)

    def run_download(self, url: str, filename: str, max_files: int, chunk_size: int):
        asyncio.run(self.download_file(url, filename, max_files, chunk_size))

    def run_upload(self, file_path: str, parts_urls: List[str], chunk_size: int, max_files: int):
        asyncio.run(self.upload_file(file_path, parts_urls, chunk_size, max_files))

    def normal_download(self, url: str, filename: str):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, desc="Normal Download")
        with open(filename, 'wb') as f:
            for data in response.iter_content(1024):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()

    def compare_speed(self, url: str, filename: str):
        start_time = time.time()
        self.normal_download(url, filename)
        normal_time = time.time() - start_time

        os.remove(filename)

        start_time = time.time()
        asyncio.run(self.download_file(url, filename, max_files=10, chunk_size=2 * 1024 * 1024))
        fast_time = time.time() - start_time

        print(f"\nNormal Download Time: {normal_time:.2f} seconds")
        print(f"Fast Download Time: {fast_time:.2f} seconds\n")


if __name__ == "__main__":
    url = "https://mirror.clarkson.edu/zorinos/isos/17/Zorin-OS-17.2-Core-64-bit.iso"
    filename = "Zorin-OS-17.2-Core-64-bit.iso"
    fr = FireRequests()
    fr.compare_speed(url, filename)