import os
import cv2
import numpy as np
import torch
import time
import logging
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from lama import LaMa  # Assuming LaMa is imported from lama module

# Define constants and paths
MODEL_PATH = 'lama.pt'
ROOT_FOLDER = 'task_folder'
WATERMARK_PATH = 'watermark.png'
WATERMARK_SIZE = (200, 100)
PROCESSED_FOLDER = 'Replaced_images'
LOG_FILE = 'processing_log.txt'
NUM_WORKERS = 3  # Reduced number of workers to reduce CPU load
PROCESSING_DELAY = 0.1  # Delay between processing images to reduce CPU load

# Set up debug logger
debug_logger = logging.getLogger('debug_logger')
debug_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('debug.log')
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)
debug_logger.addHandler(file_handler)
debug_logger.propagate = False

# Set up console logger
console_logger = logging.getLogger('console_logger')
console_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(message)s')
console_handler.setFormatter(console_format)
console_logger.addHandler(console_handler)
console_logger.propagate = False

# Set up processing log file
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as log_file:
        log_file.write("")

def load_image(image_path, mode='RGB'):
    return np.array(Image.open(image_path).convert(mode))

def center_based_watermark_detection(image, size=(200, 100)):
    h, w = image.shape[:2]
    x, y = w // 2, h // 2
    tl, br = (x - size[0] // 2, y - size[1] // 2), (x + size[0] // 2, y + size[1] // 2)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(mask, tl, br, 255, -1)
    return mask, tl, br

def inpaint_image(image, mask, model):
    img_pil, mask_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)), Image.fromarray(mask)
    inpainted_img = model(np.array(img_pil), np.array(mask_pil))
    return Image.fromarray(inpainted_img.astype(np.uint8))

def add_watermark(image, watermark_path, position, size):
    watermark = Image.open(watermark_path).convert('RGBA').resize(size, Image.LANCZOS)
    layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
    layer.paste(watermark, position, watermark)
    return Image.alpha_composite(image.convert('RGBA'), layer).convert('RGB')

def process_image(image_path, model, watermark_path):
    try:
        debug_logger.debug(f"Processing image: {image_path}")
        image = cv2.imread(image_path)
        if image is None:
            debug_logger.error(f"Failed to load image: {image_path}")
            return False
        mask, tl, br = center_based_watermark_detection(image)
        inpainted_img = inpaint_image(image, mask, model)
        watermarked_img = add_watermark(inpainted_img, watermark_path, tl, (br[0] - tl[0], br[1] - tl[1]))

        save_path = image_path.replace(ROOT_FOLDER, PROCESSED_FOLDER)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        watermarked_img.save(save_path)
        debug_logger.debug(f"Image processed and saved: {save_path}")
        return True
    except Exception as e:
        debug_logger.exception(f"Exception occurred while processing image {image_path}: {e}")
        return False

def process_images_in_sub_folder(sub_folder_path, watermark_path, model, num_workers):
    image_paths = [os.path.join(sub_folder_path, file) for file in os.listdir(sub_folder_path)
                   if file.endswith(('jpg', 'jpeg', 'png'))]
    image_paths.sort()

    total_images = len(image_paths)
    processed_images = 0

    if total_images == 0:
        console_logger.info(f"Skipping {os.path.basename(sub_folder_path)} (empty folder)")
        return processed_images, total_images

    console_logger.info(f"Processing {os.path.basename(sub_folder_path)}:")

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {}
        for image_path in image_paths:
            save_path = image_path.replace(ROOT_FOLDER, PROCESSED_FOLDER)
            if not os.path.exists(save_path):
                futures[executor.submit(process_image, image_path, model, watermark_path)] = image_path

        for future in as_completed(futures):
            image_path = futures[future]
            if future.result():
                processed_images += 1

            console_logger.info(f"- Processing {os.path.basename(sub_folder_path)}: {processed_images} / {total_images}")
            console_handler.flush()  # Ensure real-time update in IDLE
            time.sleep(PROCESSING_DELAY)  # Introduce delay to reduce CPU load

    return processed_images, total_images

def process_images_in_main_folder(main_folder_path, watermark_path, model, num_workers):
    total_processed = 0
    total_images = 0

    for sub_folder in sorted(os.listdir(main_folder_path)):
        sub_folder_path = os.path.join(main_folder_path, sub_folder)
        if os.path.isdir(sub_folder_path):
            processed, total = process_images_in_sub_folder(sub_folder_path, watermark_path, model, num_workers)
            total_processed += processed
            total_images += total

            console_logger.info(f"\n ✔️COMPLETED {sub_folder} \n===============================\n")
            console_handler.flush()  # Ensure real-time update in IDLE

            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"Processed {sub_folder} in {os.path.basename(main_folder_path)}: {processed} / {total}\n")
                log_file.write(f"Total progress: {total_processed} / {total_images}\n")
                log_file.flush()  # Ensure the log is written immediately

            # Save checkpoint
            with open(f"{LOG_FILE}.checkpoint", 'w') as checkpoint_file:
                checkpoint_file.write(f"{os.path.basename(main_folder_path)},{sub_folder},{processed},{total_processed},{total_images}\n")

    return total_processed, total_images

def run_once(root_folder, watermark_path, model_path, num_workers):
    try:
        model = LaMa(torch.device("cuda:0" if torch.cuda.is_available() else "cpu"))
        processed_folder = PROCESSED_FOLDER

        if not os.path.exists(processed_folder):
            os.makedirs(processed_folder)

        main_folders = sorted(os.listdir(root_folder))
        
        for main_folder in main_folders:
            main_folder_path = os.path.join(root_folder, main_folder)
            if os.path.isdir(main_folder_path):
                process_images_in_main_folder(main_folder_path, watermark_path, model, num_workers)
        
    except Exception as e:
        debug_logger.exception(f"Exception occurred in run_once function: {e}")
        console_logger.error(f"Exception occurred in run_once function: {e}")

if __name__ == "__main__":
    run_once(ROOT_FOLDER, WATERMARK_PATH, MODEL_PATH, NUM_WORKERS)
