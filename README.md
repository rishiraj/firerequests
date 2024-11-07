# FireRequests 🔥

<p align="center">
    <a href="https://github.com/rishiraj/firerequests/releases"><img alt="GitHub release" src="https://img.shields.io/github/release/rishiraj/firerequests.svg"></a>
    <a href="https://github.com/rishiraj/firerequests"><img alt="PyPi version" src="https://img.shields.io/pypi/pyversions/firerequests.svg"></a>
    <a href="https://pepy.tech/project/firerequests"><img src="https://static.pepy.tech/badge/firerequests" alt="PyPI Downloads"></a>
    <a href="https://colab.research.google.com/drive/1BIi46kmPQLotG1w9ofTBptlhmnKiKugZ?usp=sharing"><img alt="Open In Colab" src="https://colab.research.google.com/assets/colab-badge.svg"></a>
</p>

**FireRequests** is a high-performance, asynchronous HTTP client library for Python, engineered to accelerate your file transfers. By harnessing advanced concepts like semaphores, exponential backoff with jitter, concurrency, and fault tolerance, FireRequests can achieve up to a **10x real-world speedup** in file downloads and uploads compared to traditional synchronous methods and enables scalable, parallelized LLM interactions with providers like OpenAI and Google.

## Features 🚀

- **Asynchronous I/O**: Non-blocking network and file operations using `asyncio`, `aiohttp`, and `aiofiles`, boosting throughput for I/O-bound tasks.
- **Concurrent Transfers**: Uses `asyncio.Semaphore` to limit simultaneous tasks, optimizing performance by managing system resources effectively.
- **Fault Tolerance**: Retries failed tasks with exponentially increasing wait times, adding random jitter to prevent network congestion.
- **Chunked Processing**: Files are split into configurable chunks for parallel processing, significantly accelerating uploads/downloads.
- **Parallel LLM Calls**: Efficiently handles large-scale language model requests from OpenAI and Google with configurable parallelism.
- **Compatibility**: Supports environments like Jupyter through `nest_asyncio`, enabling reusable `asyncio` loops for both batch and interactive Jupyter use.

## Installation 📦

Install FireRequests using pip:

```bash
!pip install firerequests
```

## Quick Start 🏁

Accelerate your downloads with just a few lines of code:

### Python Usage

```python
from firerequests import FireRequests

url = "https://mirror.clarkson.edu/zorinos/isos/17/Zorin-OS-17.2-Core-64-bit.iso"

fr = FireRequests()
fr.download(url)
```

### Command Line Interface

```bash
!fr download https://mirror.clarkson.edu/zorinos/isos/17/Zorin-OS-17.2-Core-64-bit.iso
```

#### Parameters:
- `urls` (required): The URL to download the file from.
- `--filenames` (optional): The name to save the downloaded file. Defaults to filename from URL.
- `--max_files` (optional): The number of concurrent file chunks. Defaults to 10.
- `--chunk_size` (optional): The size of each chunk in bytes. Defaults to `2 * 1024 * 1024` (2 MB).
- `--headers` (optional): A dictionary of headers to include in the download request.
- `--show_progress` (optional): Whether to show a progress bar. Defaults to True for single file downloads, and False for multiple files.

## Real-World Speed Test 🏎️

FireRequests delivers significant performance improvements over traditional download methods. Below is the result of a real-world speed test:

```plaintext
Normal Download 🐌: 100%|██████████| 3.42G/3.42G [18:24<00:00, 3.10MB/s]
Downloading on 🔥: 100%|██████████| 3.42G/3.42G [02:38<00:00, 21.6MB/s]

🐌 Download Time: 1104.84 seconds
🔥 Download Time: 158.22 seconds
```

> [!TIP]
> For Hugging Face Hub downloads it is recommended to use `hf_transfer` for maximum speed gains!
> For more details, please take a look at this [section](https://huggingface.co/docs/huggingface_hub/hf_transfer).

## Advanced Usage ⚙️

### Downloading Files

```python
from firerequests import FireRequests

urls = ["https://example.com/file1.iso", "https://example.com/file2.iso"]
filenames = ["file1.iso", "file2.iso"]

fr = FireRequests()
fr.download(urls, filenames, max_files=10, chunk_size=2 * 1024 * 1024, headers={"Authorization": "Bearer token"}, show_progress=True)
```

- **`urls`**: The URL or list of URLs of the file(s) to download.
- **`filenames`**: The filename(s) to save the downloaded file(s). If not provided, filenames are extracted from the URLs.
- **`max_files`**: The maximum number of concurrent chunk downloads. Defaults to 10.
- **`chunk_size`**: The size of each chunk in bytes. Defaults to `2 * 1024 * 1024` (2 MB).
- **`headers`**: A dictionary of headers to include in the download request (optional).
- **`show_progress`**: Whether to show a progress bar during download. Defaults to `True` for a single file, and `False` for multiple files (optional).

### Uploading Files

```python
from firerequests import FireRequests

file_path = "largefile.iso"
parts_urls = ["https://example.com/upload_part1", "https://example.com/upload_part2", ...]

fr = FireRequests()
fr.upload(file_path, parts_urls, chunk_size=2 * 1024 * 1024, max_files=10, show_progress=True)
```

- **`file_path`**: The local path to the file to upload.
- **`parts_urls`**: A list of URLs where each part of the file will be uploaded.
- **`chunk_size`**: The size of each chunk in bytes. Defaults to `2 * 1024 * 1024` (2 MB).
- **`max_files`**: The maximum number of concurrent chunk uploads. Defaults to 10.
- **`show_progress`**: Whether to show a progress bar during upload. Defaults to `True`.

### Comparing Download Speed

```python
from firerequests import FireRequests

url = "https://example.com/largefile.iso"

fr = FireRequests()
fr.compare(url)
```

### Generating Text with LLMs

FireRequests supports generating responses from LLMs like OpenAI’s and Google’s generative models in parallel batches. This currently doesn't work in Colab.

```python
from firerequests import FireRequests

# Initialize FireRequests
fr = FireRequests()

# Set parameters
provider = "openai"
model = "gpt-4o-mini"
system_prompt = "Provide concise answers."
user_prompts = ["What is AI?", "Explain quantum computing.", "What is Bitcoin?", "Explain neural networks."]
parallel_requests = 2

# Generate responses
responses = fr.generate(
    provider=provider,
    model=model,
    system_prompt=system_prompt,
    user_prompts=user_prompts,
    parallel_requests=parallel_requests
)

print(responses)
```

## License 📄

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/rishiraj/firerequests/blob/main/LICENSE) file for details.

Sponsors ❤️
--------
<a href="https://x.com/soumikRakshit96" target="_blank"><img src="https://pbs.twimg.com/profile_images/1791522152954429440/TqGn_kos_400x400.jpg" height="72"></a>

Become a sponsor and get a logo here. The funds are used to defray the cost of development.

<a href="https://www.buymeacoffee.com/rishiraj"><img width="200" alt="bmc-button" src="https://github.com/user-attachments/assets/a362b162-c419-4888-bdc9-c33d00d767ad"></a>
