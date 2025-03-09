# cleanSmut

### Abstract

This script is designed to help you sort through a directory of images and videos, identifying potentially NSFW content and moving it to a separate folder. It uses the OpenNSFW2 library to analyze images and videos, predicting the likelihood that they contain NSFW content.

Here's how it works: The script first sets up the necessary directories and logging configuration. It then scans the target directory and its subdirectories for files with specific extensions (like .jpg, .png, .mp4, etc.). For each file, it calculates the NSFW probability using the neural model you can find in the repo (.h5) and logs the result. If the probability exceeds a certain threshold, the file is moved to a "high_prob_nsfw" directory.

To ensure smooth operation, the script processes files in parallel using a thread pool, which speeds up the sorting process. It also keeps track of which files have already been processed to avoid redundant work. Safety measures are built in to handle errors gracefully, such as skipping non-image files, handling corrupted files, and verifying successful file moves.

Overall, this script provides an efficient and automated way to manage and sort potentially sensitive content, making it easier to keep your directories organized and safe.

### Pseudocode

1. Import necessary modules: hashlib, logging, os, re, shutil, ThreadPoolExecutor, cv2, opennsfw2, colorama, rich.console, random, string.
2. Initialize colorama and rich.console.
3. Set up logging configuration.
4. Define allowed file extensions for images and videos.

5. Function generate_random_string:
    - Generate a random string of specified length.

6. Function move_file:
    - Check if the source file exists.
    - Generate a unique destination path if the file already exists at the destination.
    - Move the file to the destination.
    - Verify the move was successful.

7. Function calculate_md5:
    - Calculate the MD5 hash of a file.

8. Function get_color:
    - Return a color based on the NSFW probability.

9. Function process_image:
    - Log the start of processing.
    - Check if the file is a jpg, png, or heic.
    - Read the image file.
    - Predict NSFW probability using opennsfw2.
    - Log the NSFW probability.
    - Move the file to the high_prob_nsfw directory if the probability exceeds the threshold.
    - Log the move.

10. Function process_images_in_directory:
    - Create the high_prob_nsfw directory if it doesn't exist.
    - Read the log file and populate a hashmap of processed files.
    - Collect all image files in the target directory and its subdirectories.
    - Process images in parallel using ThreadPoolExecutor.
    - Log the processing status and handle timeouts and errors.

11. Main script execution:
    - Define the target directory.
    - Call process_images_in_directory with the target directory.
   
---------------------------------------------------------------------------------------------------------

I created this script as part of an effort to digitalise old family media (hi8, vhs, jvhs, pictures, restored hard drives etc.), and to root out any nsfw pictures from old phone backups from family and/or myself, that might have been stored in old browser caches or, lets be fair, downloaded in puberty.
