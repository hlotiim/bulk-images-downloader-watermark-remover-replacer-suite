# Bulk Image Downloader, Watermark Remover, and Replacer Suite

## Overview
This repository contains a collection of Python scripts designed to automate various image processing tasks, including downloading images from an Excel dataset, categorizing images into folders, removing and replacing watermarks in bulk, and checking the completion status of the image processing. These scripts utilize multi-threading for optimized performance and employ the LaMa inpainting model to ensure high-quality results.

## Combined Details
## Features

1. **Bulk Image Downloading**:
    - Automatically download images from a dataset.
    - Categorize and save images into specified folders.

2. **Watermark Removal**:
    - Remove watermarks from images in bulk using the LaMa inpainting model.
    - Supports multi-threaded processing for faster performance.

3. **Watermark Replacement**:
    - Add new watermarks to images after removing existing ones.
    - Customizable watermark size and position.

4. **Dynamic Scheduling**:
    - Run scripts with specified intervals to manage CPU load.
    - Automatically pause and resume processing based on the schedule.

5. **Checkpointing**:
    - Save progress at regular intervals to avoid reprocessing.
    - Resume from the last checkpoint in case of interruptions.

6. **Comprehensive Logging**:
    - Detailed logging of processing steps and errors.
    - Separate logs for debugging and console output.

7. **Empty Folder Skipping**:
    - Automatically skip folders with no images.
    - Log details about skipped folders.

8. **Image Completion Check**:
    - Verify if all images in the task folder are processed.
    - Generate statistics on completed and pending images.

9. **Error Handling**:
    - Robust error handling to manage processing issues.
    - Log exceptions and continue processing remaining images.

10. **Multi-threading**:
    - Use multi-threading for efficient image processing.
    - Adjustable number of worker threads based on system capability.

## Use Cases

1. **E-commerce Platforms**:
    - Bulk download product images, remove old watermarks, and add new ones.
    - Organize images into categories for easy management.

2. **Real Estate Listings**:
    - Process property images by removing and replacing watermarks.
    - Ensure all images are correctly processed and categorized.

3. **Photography Services**:
    - Manage client photos by downloading, watermarking, and categorizing.
    - Automate the process to save time and ensure consistency.

4. **Social Media Management**:
    - Prepare images for social media by adding branding watermarks.
    - Schedule processing to optimize system performance.

5. **Digital Marketing**:
    - Download and process images for marketing campaigns.
    - Add campaign-specific watermarks and organize images.

6. **Content Creation**:
    - Automate image preparation for blogs, websites, and other content platforms.
    - Ensure all images are watermark-free and properly branded.

7. **Archives and Libraries**:
    - Process large image datasets for archival purposes.
    - Ensure images are organized and free from unwanted watermarks.

8. **Educational Institutions**:
    - Manage images for school events, yearbooks, and online galleries.
    - Automate the downloading and watermarking process.

9. **Corporate Branding**:
    - Maintain consistency in corporate images by adding standardized watermarks.
    - Process images in bulk for internal and external use.

10. **Media and Entertainment**:
    - Prepare promotional images by removing existing watermarks and adding new ones.
    - Automate the categorization and organization of images for easy access.

## Scripts Details

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