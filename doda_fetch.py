import os
import sys
import urllib.request
import urllib.error

def print_progress(blocks_transferred, block_size, total_size):
    if total_size <= 0:
        sys.stdout.write(f"\rDownloading... {blocks_transferred * block_size} bytes")
    else:
        percent = min(100, (blocks_transferred * block_size * 100) // total_size)
        bar_len = 40
        filled_len = int(bar_len * percent // 100)
        bar = '█' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write(f"\r[{bar}] {percent}%")
    sys.stdout.flush()

def download_file(url, out_path=None):
    if not out_path:
        out_path = os.path.basename(url) or 'index.html'

    print(f"URL: {url}")
    print(f"Target: {out_path}")
    print("-" * 50)

    try:
        urllib.request.urlretrieve(url, out_path, reporthook=print_progress)
        print(f"\n\nSuccess: File saved to {out_path}")
    except Exception as e:
        print(f"\n\nError: Failed to download file. {e}")

def main():
    if len(sys.argv) < 2:
        print("Doda Fetch - Retro Downloader")
        print("Usage: python doda_fetch.py <url> [output_file]")
        sys.exit(1)

    url = sys.argv[1]

    # We could implement actual gemini protocol, but for now we focus on standard downloads
    # and provide HTTP/HTTPS fallback to simple urllib.
    if not url.startswith('http'):
        url = 'http://' + url

    out_path = sys.argv[2] if len(sys.argv) > 2 else None

    download_file(url, out_path)

if __name__ == "__main__":
    main()
