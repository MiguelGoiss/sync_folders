import os
import shutil
from filecmp import cmp
import logging
import time
import argparse

def sync_folders(source, destination, logger):
  # Walk through source
  for root, _, files in os.walk(source):
    # Path to copy
    source_path = os.path.relpath(root, source)
    destination_path = os.path.join(destination, source_path)
    
    # Create any missing directories
    if not os.path.exists(destination_path):
      os.makedirs(destination_path)
      logger.info(f"Created directory: {destination_path}")
    
    # Copy each file
    for file in files:
      source_file = os.path.join(root, file)
      destination_file = os.path.join(destination_path, file)
      
      # Copy file if it doesn't exist or is different
      if not os.path.exists(destination_file) or not cmp(source_file, destination_file, shallow=False):
        shutil.copy2(source_file, destination_file)
        logger.info(f"Copied: {source_file} -> {destination_file}")
  
  # Cleanup function to remove extra files and folders
  remove_extra_files_and_folders(source, destination, logger)
  
def remove_extra_files_and_folders(source, destination, logger):
  """Remove files and folders in the destinationination that don't exist in the source."""
  logger.info("Starting cleanup process")
  for root, dirs, files in os.walk(destination, topdown=False):
    rel_path = os.path.relpath(root, destination)
    source_path = os.path.join(source, rel_path)
    
    # Remove files that don't exist in source
    for file in files:
      destination_file = os.path.join(root, file)
      source_file = os.path.join(source_path, file)
      
      if not os.path.exists(source_file):
        os.remove(destination_file)
        logger.info(f"Removed file: {destination_file}")
    
    # Remove directories that don't exist in source
    for dir_name in dirs:
      destination_dir = os.path.join(root, dir_name)
      source_dir = os.path.join(source_path, dir_name)
      
      if not os.path.exists(source_dir):
        shutil.rmtree(destination_dir)
        logger.info(f"Removed folder: {destination_dir}")

def setup_logger(log_file):
  # Set up logging to a file
  logging.basicConfig(
    filename=log_file,                                  # Log file name
    level=logging.INFO,                                 # Log level
    format="%(asctime)s - %(levelname)s - %(message)s", # Log message format
    datefmt="%Y-%m-%d %H:%M:%S"                         # Log date
  )
  return logging.getLogger()

if __name__ == "__main__":
  # Parse command-line arguments
  parser = argparse.ArgumentParser(description="Sync two folders with optional interval and logging.")
  parser.add_argument("source_folder", help="Path to the source folder")
  parser.add_argument("replica_folder", help="Path to the replica folder")
  parser.add_argument("--interval", type=int, default=600, help="Sync interval in seconds (default: 600 seconds)")
  parser.add_argument("--log_file", default="sync_log.txt", help="Path to the log file (default: sync_log.txt)")

  args = parser.parse_args()

  # Set up the logger
  logger = setup_logger(args.log_file)

  # Run the sync at the specified interval
  while True:
    sync_folders(args.source_folder, args.replica_folder, logger)
    logger.info(f"Sync completed. Waiting {args.interval} seconds before the next run.")
    time.sleep(args.interval)
