# FireRequests 🔥

[![PyPI version](https://img.shields.io/pypi/v/firerequests.svg)](https://pypi.org/project/firerequests/)  [![License](https://img.shields.io/pypi/l/firerequests.svg)](https://github.com/rishiraj/firerequests/blob/main/LICENSE)  [![Python version](https://img.shields.io/pypi/pyversions/firerequests.svg)](https://pypi.org/project/firerequests/)

**FireRequests** is a high-performance, asynchronous HTTP client library for Python, engineered to accelerate your file transfers. By harnessing advanced concepts like semaphores, exponential backoff with jitter, concurrency, and fault tolerance, FireRequests can achieve up to a **6x real-world speedup** in file downloads and uploads compared to traditional synchronous methods.

## Features 🚀

- **Asynchronous I/O**: Non-blocking network and file operations using `asyncio`, `aiohttp`, and `aiofiles`, boosting throughput for I/O-bound tasks.
- **Concurrent Transfers**: Uses `asyncio.Semaphore` to limit simultaneous tasks, optimizing performance by managing system resources effectively.
- **Fault Tolerance**: Retries failed tasks with exponentially increasing wait times, adding random jitter to prevent network congestion.
- **Chunked Processing**: Files are split into configurable chunks for parallel processing, significantly accelerating uploads/downloads.
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
- `url` (required): The URL to download the file from.
- `--filename` (optional): The name to save the downloaded file. Defaults to filename from URL.
- `--max_files` (optional): The number of concurrent file chunks. Defaults to 10.
- `--chunk_size` (optional): The size of each chunk in bytes. Defaults to `2 * 1024 * 1024` (2 MB).

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

url = "https://example.com/largefile.iso"
filename = "largefile.iso"

fr = FireRequests()
fr.download(url, filename, max_files=10, chunk_size=2 * 1024 * 1024)
```

- **`url`**: The URL of the file to download.
- **`filename`**: The local filename to save the downloaded file.
- **`max_files`**: The maximum number of concurrent chunk downloads.
- **`chunk_size`**: The size of each chunk in bytes.

### Uploading Files

```python
from firerequests import FireRequests

file_path = "largefile.iso"
parts_urls = ["https://example.com/upload_part1", "https://example.com/upload_part2", ...]

fr = FireRequests()
fr.upload(file_path, parts_urls, chunk_size=2 * 1024 * 1024, max_files=10)
```

### Comparing Download Speed

```python
from firerequests import FireRequests

url = "https://example.com/largefile.iso"

fr = FireRequests()
fr.compare(url)
```

## License 📄

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/rishiraj/firerequests/blob/main/LICENSE) file for details.
