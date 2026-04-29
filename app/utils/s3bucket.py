import boto3
import os
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


# ===============================
# 🔹 SINGLE S3 CLIENT
# ===============================
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


# ===============================
# 🔹 ALLOWED FILE TYPES
# ===============================
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}


# ===============================
# 🔹 UPLOAD FILE (NO BREAK VERSION)
# ===============================
def upload_file_to_s3(file_bytes: bytes, s3_key: str, content_type: str):
    try:
        if not file_bytes:
            raise Exception("File is empty")

        if not content_type:
            content_type = "application/octet-stream"

        if content_type not in ALLOWED_CONTENT_TYPES:
            raise Exception(f"Unsupported file type: {content_type}")

        file_obj = BytesIO(file_bytes)

        s3.upload_fileobj(
            file_obj,
            BUCKET_NAME,
            s3_key,
            ExtraArgs={
                "ContentType": content_type,
                "ContentDisposition": "inline",

                # ⚠️ KEEP THIS (for now, to avoid breaking app)
                "ACL": "public-read"
            }
        )

        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

        return file_url

    except Exception as e:
        raise Exception(f"S3 upload failed: {str(e)}")


# ===============================
# 🔹 EXTRACT S3 KEY FROM URL
# ===============================
def extract_s3_key(file_url: str):
    try:
        if not file_url:
            raise Exception("Empty file URL")

        if ".amazonaws.com/" not in file_url:
            raise Exception("Invalid S3 URL format")

        key = file_url.split(".amazonaws.com/")[-1]

        # 🔥 HANDLE WINDOWS PATH ISSUE
        key = key.replace("\\", "/")

        return key

    except Exception as e:
        raise Exception(f"Invalid S3 URL: {str(e)}")


# ===============================
# 🔹 GENERATE VIEW URL
# ===============================
def generate_presigned_view_url(file_key: str, expiry=3600):
    try:
        if not file_key:
            raise Exception("File key is empty")

        return s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key,
                "ResponseContentDisposition": "inline"
            },
            ExpiresIn=expiry
        )
    except Exception as e:
        raise Exception(f"Failed to generate view URL: {str(e)}")


# ===============================
# 🔹 GENERATE DOWNLOAD URL
# ===============================
def generate_presigned_download_url(file_key: str, expiry=3600):
    try:
        if not file_key:
            raise Exception("File key is empty")

        return s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key,
                "ResponseContentDisposition": "attachment"
            },
            ExpiresIn=expiry
        )
    except Exception as e:
        raise Exception(f"Failed to generate download URL: {str(e)}")