# Bulk Image Processing Scripts

## Overview
This repository contains a collection of Python scripts designed to automate various image processing tasks, including downloading images from an Excel dataset, categorizing images into folders, removing and replacing watermarks in bulk, and checking the completion status of the image processing. These scripts utilize multi-threading for optimized performance and employ the LaMa inpainting model to ensure high-quality results.

## Scripts

### 1. `bulk_image_downloader_from_dataset.py`
This script automates the process of downloading images from URLs provided in an Excel dataset and categorizing them into folders.

#### Features:
- Downloads images from Excel dataset.
- Categorizes images into specific folders.
- Handles various image formats.

#### Usage:
1. Ensure you have the required libraries: `pandas`, `requests`, `openpyxl`.
2. Modify the script to specify the path to your Excel file and the destination folder.
3. Run the script.

### 2. `lama.py`
This script contains the LaMa inpainting model, which is used for high-quality watermark removal.

#### Features:
- Implements the LaMa inpainting model.
- Processes images to remove watermarks effectively.

#### Usage:
1. Ensure you have the required dependencies: `torch`, `PIL`.
2. The script is used as a module in other scripts for inpainting tasks.

### 3. `bulk_watermark_remover_and_replacer.py`
This script removes existing watermarks and adds new watermarks to images in bulk.

#### Features:
- Removes existing watermarks using the LaMa inpainting model.
- Adds new watermarks to images.
- Processes images in multi-threaded fashion for better performance.
- Supports checkpointing to resume interrupted processing.
- Comprehensive logging for easy debugging and monitoring.

#### Usage:
1. Ensure you have the required libraries: `cv2`, `numpy`, `torch`, `PIL`.
2. Configure the paths for the root folder, watermark image, and the LaMa model.
3. Run the script to process the images.

### 4. `run_replacer_with_break.py`
This script manages the execution of `bulk_watermark_remover_and_replacer.py` with scheduled breaks to optimize CPU load, especially for low-end systems.

#### Features:
- Dynamically starts and stops the watermark processing script based on a predefined schedule.
- Ensures the system does not overheat by taking breaks.

#### Usage:
1. Ensure `bulk_watermark_remover_and_replacer.py` is configured correctly.
2. Run this script to manage the watermark removal and replacement process with breaks.

### 5. `check_all_the_images_are_completed.py`
This script checks whether all images in the `task_folder` have been processed and saved in the `Replaced_images` folder. It also provides statistics on the processing status.

#### Features:
- Compares images in `task_folder` and `Replaced_images` to identify unprocessed images.
- Provides statistics on folders and images.
- Logs missing images and processing status.

#### Usage:
1. Ensure you have the required libraries: `os`, `logging`.
2. Run the script to check the completeness of the image processing and obtain statistics.

## Setup and Installation

### Prerequisites
- Python 3.6 or higher
- Install the required libraries using pip:
  ```sh
  pip install -r requirements.txt
  ```

### Running the Scripts
1. **Bulk Image Downloader**: 
   ```sh
   python3 bulk_image_downloader_from_dataset.py
   ```
2. **Watermark Remover and Replacer**:
   ```sh
   python3 bulk_watermark_remover_and_replacer.py
   ```
3. **Run Replacer with Breaks**:
   ```sh
   python3 run_replacer_with_break.py
   ```
4. **Check Image Completion**:
   ```sh
   python3 check_all_the_images_are_completed.py
   ```

## References
- [lama-single-file](https://github.com/ironjr/lama-single-file)
- [advimman/lama](https://github.com/advimman/lama)

These repositories were instrumental in developing the LaMa inpainting model and related image processing tasks.

## Contribution
Feel free to submit issues or pull requests if you find any bugs or have suggestions for improvements.

## License
This project is licensed under the MIT License - see the LICENSE file for details.