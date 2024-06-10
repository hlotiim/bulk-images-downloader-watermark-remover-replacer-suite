import os
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
from collections import defaultdict

# Constants
TASK_FOLDER = 'task_folder'
BROKEN_URLS_TEXT_FILE = 'broken_urls.txt'
RETRY_COUNT = 5
TIMEOUT_SECONDS = 120
MAX_WORKERS = 500  # Number of threads for downloading images
REQUESTS_PER_PROXY = 5000
PROXY_SLEEP_TIME = 300  # 5 minutes

# Provided proxies
PROVIDED_PROXIES = [
    '192.3.166.12:12345:june:Pass',
    '196.247.229.207:12345:june:Pass',
    '107.172.71.35:12345:june:Pass',
    '192.3.166.48:12345:june:Pass',
    '192.3.158.108:12345:june:Pass',
    '23.94.248.238:12345:june:Pass',
    '107.174.148.2:12345:june:Pass',
    '107.174.5.56:12345:june:Pass',
    '107.175.38.188:12345:june:Pass',
    '107.174.148.8:12345:june:Pass',
    '107.175.38.185:12345:june:Pass',
    '107.174.148.92:12345:june:Pass',
    '23.108.50.134:12345:june:Pass',
    '192.3.147.88:12345:june:Pass',
    '107.174.239.140:12345:june:Pass',
    '107.172.64.241:12345:june:Pass',
    '23.108.50.14:12345:june:Pass',
    '23.108.50.159:12345:june:Pass',
    '107.175.38.142:12345:june:Pass',
    '107.172.64.246:12345:june:Pass',
    '172.245.73.11:12345:june:Pass',
    '23.108.50.175:12345:june:Pass',
    '192.3.158.84:12345:june:Pass',
    '107.172.69.98:12345:june:Pass',
    '107.174.148.39:12345:june:Pass',
    '192.3.236.136:12345:june:Pass',
    '172.245.91.246:12345:june:Pass',
    '196.247.229.176:12345:june:Pass',
    '107.174.139.183:12345:june:Pass',
    '107.174.143.43:12345:june:Pass',
    '107.174.151.20:12345:june:Pass',
    '107.174.5.111:12345:june:Pass',
    '192.3.188.101:12345:june:Pass',
    '172.245.91.228:12345:june:Pass',
    '172.245.91.234:12345:june:Pass',
    '107.174.139.146:12345:june:Pass',
    '192.3.228.116:12345:june:Pass',
    '23.108.46.217:12345:june:Pass',
    '23.94.248.220:12345:june:Pass',
    '172.245.73.22:12345:june:Pass',
    '107.172.71.16:12345:june:Pass',
    '107.172.42.102:12345:june:Pass',
    '23.108.50.29:12345:june:Pass',
    '196.247.229.215:12345:june:Pass',
    '23.108.48.156:12345:june:Pass',
    '196.247.229.168:12345:june:Pass',
    '23.108.47.167:12345:june:Pass',
    '23.108.46.224:12345:june:Pass',
    '107.174.148.28:12345:june:Pass',
    '192.3.147.144:12345:june:Pass'
]

# Global variables for proxy management
proxy_list = []
proxy_index = 0
proxy_lock = threading.Lock()
proxy_usage = defaultdict(int)
proxy_sleep_times = {}

def parse_proxies(proxies):
    """Parses the provided proxies into a format usable by the requests library."""
    proxy_list = []
    for proxy in proxies:
        parts = proxy.split(':')
        if len(parts) == 4:
            ip, port, user, password = parts
            proxy_url = f'http://{user}:{password}@{ip}:{port}'
            proxy_list.append(proxy_url)
    return proxy_list

def get_next_proxy():
    global proxy_index
    with proxy_lock:
        while True:
            if proxy_list:
                proxy = proxy_list[proxy_index]
                proxy_index = (proxy_index + 1) % len(proxy_list)
                # Check if the proxy needs to sleep
                if proxy in proxy_sleep_times:
                    sleep_until = proxy_sleep_times[proxy]
                    if time.time() < sleep_until:
                        continue
                    else:
                        del proxy_sleep_times[proxy]
                # Check proxy usage and reset if necessary
                if proxy_usage[proxy] >= REQUESTS_PER_PROXY:
                    proxy_sleep_times[proxy] = time.time() + PROXY_SLEEP_TIME
                    proxy_usage[proxy] = 0
                    continue
                return proxy
            else:
                return None

def log_broken_url(url, status_code, reason, sheet_name, row_name, row_id):
    """Logs broken URLs with response details to a text file."""
    with open(BROKEN_URLS_TEXT_FILE, 'a') as file:
        file.write(f"URL: {url}\nSTATUS CODE: {status_code}\nREASON: {reason}\nSHEET NAME: {sheet_name}\nROW NAME: {row_name}\nROW ID: {row_id}\n\n\n")

def download_and_save_image(url, save_path, sheet_name, row_name, row_id):
    """Attempts to download an image from url and save it appropriately."""
    for attempt in range(RETRY_COUNT):
        proxy = get_next_proxy()
        if not proxy:
            break
        proxies = {
            'http': proxy,
            'https': proxy
        }
        try:
            response = requests.get(url, proxies=proxies, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()  # Raises an exception for 4xx/5xx errors
            image = Image.open(BytesIO(response.content))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(save_path, format='JPEG')
            proxy_usage[proxy] += 1
            return True
        except requests.RequestException as e:
            log_broken_url(url, getattr(e.response, 'status_code', 'No response'), e, sheet_name, row_name, row_id)
            time.sleep(2)  # Simple back-off strategy
    return False

def process_sheet(sheet_name, df):
    """Process each sheet independently, downloading images in parallel."""
    sheet_folder = os.path.join(TASK_FOLDER, sheet_name)
    os.makedirs(sheet_folder, exist_ok=True)
    total_images_downloaded = 0
    total_images = sum(len(row['Images'].split(',')) for _, row in df.iterrows())
    print(f"Processing Sheet: {sheet_name}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_info = {}
        for idx, row in df.iterrows():
            row_name = row['Property Name'].replace('/', '_').replace(',', '_')
            folder_path = os.path.join(sheet_folder, f"{row_name}_{idx}")
            os.makedirs(folder_path, exist_ok=True)
            image_urls = row['Images'].split(',')
            for url_index, url in enumerate(image_urls):
                img_path = os.path.join(folder_path, f"image_{url_index}.jpg")
                future = executor.submit(download_and_save_image, url, img_path, sheet_name, row_name, idx)
                future_to_info[future] = (url, img_path)
        for future in as_completed(future_to_info):
            url, img_path = future_to_info[future]
            if future.result():
                total_images_downloaded += 1
            print(f"Sheet: {sheet_name}, Images Downloaded: {total_images_downloaded}/{total_images}")

def main(excel_file_path):
    global proxy_list
    proxy_list = parse_proxies(PROVIDED_PROXIES)
    if not proxy_list:
        print("No proxies parsed. Exiting.")
        return

    print(f"Working proxies: {len(proxy_list)}")
    sheets = pd.read_excel(excel_file_path, sheet_name=None)
    for sheet_name, df in sheets.items():
        process_sheet(sheet_name, df)

if __name__ == "__main__":
    main('data.xlsx')
