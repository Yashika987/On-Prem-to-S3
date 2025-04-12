# On-Prem-to-S3
A lightweight Python script that automates the upload of agency-specific PDF reports from an on-prem shared directory to versioned AWS S3 buckets. Includes content-based deduplication using MD5 checksums, secure IAM-based access, and weekly scheduling via cron or Task Scheduler.

# 📂 Submission-Reports from On-Prem to AWS S3 Automation

This project automates the secure transfer of PDF reports from an **on-premises shared folder** to **AWS S3**, specifically for agencies like **Agency-1**, **Agency-2**, and **Agency-3**. It ensures only **new or updated files** are uploaded, using **MD5 checksums** to prevent duplicate uploads.

---

## 🚀 Use Case

The Submission tool generates PDF reports daily/weekly and stores them in a shared folder accessible from an on-prem application server. This script:
- Scans the shared directory
- Filters only `.pdf` files modified in the last 7 days
- Calculates file checksum for change detection
- Uploads to the correct S3 bucket (based on folder name)
- Supports S3 **versioning**, IAM-secured access, and cron scheduling

---

## 🧠 Features

✅ Runs on any on-prem Linux/Windows machine  
✅ Filters modified files (default: last 7 days)  
✅ Detects changes using MD5 checksums  
✅ Uploads only changed files  
✅ S3 versioning enabled (retains file history)  
✅ Secure upload via IAM credentials  
✅ Schedule with cron (Linux) or Task Scheduler (Windows)

---

## 📁 Directory Structure

```bash
📂 E:\Project\Submission Agency Integration
   ├── Agency-1
   │   └── Submission1-Report.pdf
           Submission2-Report.pdf
           .
           .
   ├── Agency-2
   │   └── Submission1-Report.pdf
           Submission2-Report.pdf
           .
           .
   └── Agency-3
       └── Submission1-Report.pdf
           Submission2-Report.pdf
           .
           .
   .
   .

## 🛠️ Setup

1. **Install dependencies**:
   ```bash
   pip install boto3
2. Set up AWS credentials:
   Create new IAM User
     🔐 IAM Policy Example
         Ensure your IAM role/user has permissions like:
            json
            Copy
            Edit
            {
              "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:PutObjectVersionAcl",
                "s3:GetObjectVersion"
              ],
              "Effect": "Allow",
              "Resource": "arn:aws:s3:::your-bucket-name/*"
            }
3. Enable versioning on target S3 buckets.

## 🧪 How to Run manually:
   python upload_reports.py

## 📓 Logging & Error Handling
   Error logs are getting stored in submission_Report_Update.log
