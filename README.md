# FireRequests 🔥

[![PyPI version](https://badge.fury.io/py/firerequests.svg)](https://badge.fury.io/py/firerequests)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

FireRequests is a cutting-edge, high-performance asynchronous HTTP client library designed for blazing-fast file transfers. Leveraging advanced concurrency paradigms and innovative networking techniques, FireRequests achieves up to 5x real-world speed improvements over traditional synchronous methods.

## Key Features

- **Asynchronous Architecture**: Utilizes `asyncio` for non-blocking I/O operations, maximizing throughput and minimizing latency.
- **Concurrent Chunk Processing**: Implements parallel downloading and uploading of file chunks for optimal resource utilization.
- **Adaptive Exponential Backoff**: Incorporates a sophisticated retry mechanism with jitter for robust error handling and network resilience.
- **Semaphore-based Concurrency Control**: Employs fine-grained concurrency management to prevent resource exhaustion and ensure system stability.
- **Progress Visualization**: Integrates `tqdm` for real-time progress tracking, enhancing user experience and operational visibility.
- **Flexible API**: Supports both high-level convenience methods and low-level customization options for advanced use cases.

## Installation

```bash
pip install firerequests
```

## Usage Examples

### High-Speed File Download

```python
from firerequests import FireRequests

fr = FireRequests()
url = "https://example.com/large-file.iso"
filename = "large-file.iso"

# Asynchronous download with optimized parameters
fr.run_download(url, filename, max_files=10, chunk_size=2 * 1024 * 1024)
```

### Accelerated File Upload

```python
from firerequests import FireRequests

fr = FireRequests()
file_path = "large-file.iso"
parts_urls = ["https://example.com/upload/part1", "https://example.com/upload/part2", ...]

# Parallel multi-part upload
fr.run_upload(file_path, parts_urls, chunk_size=5 * 1024 * 1024, max_files=8)
```

### Performance Comparison

```python
fr = FireRequests()
url = "https://mirror.example.com/large-dataset.zip"
filename = "large-dataset.zip"

# Benchmark FireRequests against traditional methods
fr.compare_speed(url, filename)
```

## Advanced Usage

### Custom Callback Integration

```python
import asyncio
from firerequests import FireRequests

async def progress_callback(bytes_transferred):
    print(f"Transferred: {bytes_transferred / 1024 / 1024:.2f} MB")

fr = FireRequests()
url = "https://example.com/massive-file.tar.gz"
filename = "massive-file.tar.gz"

asyncio.run(fr.download_file(
    url, filename, max_files=12, chunk_size=4 * 1024 * 1024,
    callback=progress_callback
))
```

## Performance Metrics

In real-world tests, FireRequests demonstrated exceptional performance gains:

- **Traditional Download**: 376.77 seconds
- **FireRequests Download**: 75.75 seconds
- **Speed Improvement**: 4.98x faster

These results showcase the significant efficiency enhancements achievable through FireRequests' advanced asynchronous architecture and optimized networking strategies.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

FireRequests is released under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.