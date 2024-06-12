import subprocess
import time
import logging
import sys
import threading

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='run.log')
logger = logging.getLogger()

# Set up console logger for pause and continue statements
console_logger = logging.getLogger('console_logger')
console_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_format = logging.Formatter('%(message)s')
console_handler.setFormatter(console_format)
console_logger.addHandler(console_handler)
console_logger.propagate = False

# Timing intervals for the desired schedule (in seconds for testing)
RUN_PAUSE_SCHEDULE = [(30 * 60, 15 * 60), (35 * 60, 15 * 60), (25 * 60, 15 * 60)]  # Change to the actual desired schedule


# Function to install required packages
def install_packages():
    required_packages = ["opencv-python-headless", "pillow", "torch"]
    for package in required_packages:
        logger.debug(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def start_script():
    logger.debug("Starting bulk_watermark_remover_and_replacer.py script")
    return subprocess.Popen([sys.executable, "bulk_watermark_remover_and_replacer.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def stop_script(process):
    logger.debug("Stopping bulk_watermark_remover_and_replacer.py script")
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
    logger.debug("bulk_watermark_remover_and_replacer.py script stopped")

def stream_output(process):
    def read_output(pipe, logger):
        for line in iter(pipe.readline, ''):
            logger.info(line.strip())
        pipe.close()
        
    threading.Thread(target=read_output, args=(process.stdout, console_logger)).start()
    threading.Thread(target=read_output, args=(process.stderr, console_logger)).start()

def run_with_intervals(schedule):
    while True:
        for run_time, pause_time in schedule:
            console_logger.info(f"Running for {run_time / 60:.0f} minutes...")
            process = start_script()
            stream_output(process)
            
            time.sleep(run_time)
            
            stop_script(process)
            console_logger.info(f"Pausing for {pause_time / 60:.0f} minutes...")
            time.sleep(pause_time)

if __name__ == "__main__":
    install_packages()
    run_with_intervals(RUN_PAUSE_SCHEDULE)
