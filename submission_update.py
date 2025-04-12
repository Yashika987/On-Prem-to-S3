import os
import time
import logging
import boto3
from botocore.exceptions import ClientError

# =============================
# Logging Configuration
# =============================
LOG_FILE = "submission_Report_Update.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE)
        # logging.StreamHandler()  # Uncomment if you also want to print to console
    ]
)
log = logging.getLogger()

# =============================
# Environment Setup
# =============================
SHARED_DIR = os.getenv("SHARED_submission_DIR", r"E:\\Project\\submissions")
ENV = os.getenv("ENV", "test")

BUCKET_MAP = {
    'agency1': os.getenv("agency1_BUCKET", 'agency1-s3-bucket'),
    'agency2': os.getenv("agency2_BUCKET", 'agency2-s3-bucket'),
    'agency3': os.getenv("agency3_BUCKET", 'agency3-s3-bucket'),
}

# =============================
# AWS S3 Client
# =============================
def get_s3_client():
    return boto3.client('s3')

s3 = get_s3_client()

# =============================
# Utility: File Modified Filter
# =============================
def is_modified_within_days(file_path, days=7):
    file_mtime = os.path.getmtime(file_path)
    return (time.time() - file_mtime) <= days * 86400

# =============================
# Check If File Changed in S3
# =============================
def has_file_changed(file_path, bucket_name):
    file_name = os.path.basename(file_path)
    try:
        response = s3.head_object(Bucket=bucket_name, Key=file_name)
        s3_last_modified = response['LastModified'].timestamp()
        file_mtime = os.path.getmtime(file_path)
        return file_mtime > s3_last_modified
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            # File doesn't exist in S3, so upload it
            return True
        else:
            log.error(f"Error checking object in S3: {e}")
            return False

# =============================
# Scan and Collect Eligible Files
# =============================
def get_filtered_files(base_dir):
    filtered = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith("Report.pdf"):
                full_path = os.path.join(root, file)

                if not is_modified_within_days(full_path, 7):
                    continue

                agency_folder = os.path.basename(os.path.dirname(full_path)).lower()
                bucket_name = BUCKET_MAP.get(agency_folder)

                if bucket_name:
                    filtered.append((full_path, bucket_name))
                    log.info(f"Eligible file: {full_path}")
                else:
                    log.warning(f"Unknown folder '{agency_folder}' for file: {file}")
    return filtered

# =============================
# Upload with Retry
# =============================
def upload_with_retry(file_path, bucket_name, retries=3):
    file_name = os.path.basename(file_path)
    for attempt in range(retries):
        try:
            s3.upload_file(file_path, bucket_name, file_name)
            log.info(f"Uploaded '{file_name}' to bucket '{bucket_name}'")
            return
        except Exception as e:
            log.warning(f"Attempt {attempt+1} failed for '{file_name}': {e}")
            time.sleep(2)
    log.error(f"Failed to upload '{file_name}' after {retries} attempts")

# =============================
# Main Upload Logic
# =============================
def main_handler():
    log.info(f"Scanning directory: {SHARED_DIR}")
    files_to_upload = get_filtered_files(SHARED_DIR)
    log.info(f"Total files to upload: {len(files_to_upload)}")

    for file_path, bucket_name in files_to_upload:
        if has_file_changed(file_path, bucket_name):
            log.info(f"File changed or doesn't exist in S3, pragency2ring to upload: {file_path}")
            upload_with_retry(file_path, bucket_name)
        else:
            log.info(f"No changes detected for file: {file_path}, skipping upload.")

# =============================
# Lambda Handler Entry Point
# =============================
def lambda_handler(event=None, context=None):
    main_handler()

# For local testing
if __name__ == "__main__":
    main_handler()
