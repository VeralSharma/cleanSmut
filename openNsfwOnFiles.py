import hashlib
import logging
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import cv2
import opennsfw2 as n2
from colorama import Fore, Style, init
from rich.console import Console
import random
import string

init(autoreset=True)

console = Console()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

allowed_extensions = (
    '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff', '.svg',  # Image formats
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.mpeg', '.mpg'  # Video formats
)

# move the file to the high_prob_nsfw directory, do not leave a file behind
# from file path to destination path

def generate_random_string(length=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def move_file(src_path, dest_dir):
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"The source file {src_path} does not exist.")

    base_name = os.path.basename(src_path)
    dest_path = os.path.join(dest_dir, base_name)

    while os.path.exists(dest_path):
        name, ext = os.path.splitext(base_name)
        new_name = f"{name}_{generate_random_string()}{ext}"
        dest_path = os.path.join(dest_dir, new_name)

    os.rename(src_path, dest_path)
    print(f"File moved to {dest_path}")

    # Check if the move was successful
    if os.path.isfile(dest_path) and not os.path.isfile(src_path):
        print(f"File successfully moved to {dest_path}")
    else:
        raise Exception("File move failed")

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_color(probability):
    if probability < 0.5:
        return Fore.GREEN
    elif probability < 0.70:
        return Fore.YELLOW
    else:
        return Fore.RED

def process_image(file_path, high_prob_nsfw_dir, log_file, threshold, frame_interval=120):
    logging.info(f"Processing {os.path.basename(file_path)}")

    try:
        try:
            # Check if the file is a jpg, png, or heic
            if not file_path.lower().endswith(('.jpg', '.png', '.heic')):
                logging.info(f"Skipping {os.path.basename(file_path)} as it is not a jpg, png, or heic file")
                return  # Skip non-jpg, non-png, and non-heic files

            # Process image file
            image = cv2.imread(file_path)
            if image is None:
                logging.warning(f"{os.path.basename(file_path)} is not an image file")
                return  # Skip non-image files
        except Exception as e:
            logging.error(f"Error reading file {os.path.basename(file_path)}: {e}")
            return  # Skip corrupted files

        nsfw_probability = n2.predict_image(file_path)
        color = get_color(nsfw_probability)
        logging.info(f"{color}NSFW probability of {os.path.basename(file_path)}: {nsfw_probability}{Style.RESET_ALL}")
        log_file.write(f"{os.path.basename(file_path)}: {nsfw_probability}\n")

        if nsfw_probability > threshold:

            move_file(file_path, high_prob_nsfw_dir)

            logging.info(f"{Fore.RED}Moved {os.path.basename(file_path)} to high_prob_nsfw directory{Style.RESET_ALL}")

            log_file.write(f"{os.path.basename(file_path)}: {nsfw_probability}\n")

    except Exception as e:
        logging.error(f"Error processing file {os.path.basename(file_path)}: {e}")

def process_images_in_directory(target_directory, threshold=0.5, timeout=50000, frame_interval=120):
    # Create the high_prob_nsfw directory if it doesn't exist
    high_prob_nsfw_dir = os.path.join(target_directory, 'high_prob_nsfw')
    if not os.path.exists(high_prob_nsfw_dir):
        os.makedirs(high_prob_nsfw_dir)

    # Path to the log file
    log_file_path = os.path.join(high_prob_nsfw_dir, 'log.txt')

    # Create a hashmap to store filenames
    processed_files = {}

    # Check if the log file exists and populate the hashmap
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                match = re.match(r'^(.*?):', line)
                if match:
                    processed_files[match.group(1)] = True

    # Collect all image files in the target directory and its subdirectories
    image_files = []
    for root, dirs, files in os.walk(target_directory):
        for filename in files:
            if filename.lower().endswith(allowed_extensions):
                # Append the full path of the file, including subfolders
                image_files.append(os.path.join(root, filename))
            else:
                logging.info(f"Skipping {filename}")

    # Process images in parallel with progress bar and timeout
    with open(log_file_path, 'a') as log_file:
        with ThreadPoolExecutor() as executor:
            futures = {}
            for file_path in image_files:
                if os.path.basename(file_path) not in processed_files:
                    logging.info(f"Submitting {file_path} for processing")
                    future = executor.submit(process_image, file_path, high_prob_nsfw_dir, log_file, threshold, frame_interval)
                    futures[future] = file_path
            for future in as_completed(futures, timeout=timeout):
                file_path = futures[future]
                try:
                    future.result()
                    processed_files[os.path.basename(file_path)] = True
                except TimeoutError:
                    logging.error(f"Timeout reached for file {os.path.basename(file_path)}. Process canceled.")
                except Exception as e:
                    logging.error(f"Error processing file {os.path.basename(file_path)}: {e}")

target = 'D:\\needToSort'

# call upon the root directory
process_images_in_directory(target)