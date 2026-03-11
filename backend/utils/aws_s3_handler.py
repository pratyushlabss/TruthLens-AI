"""AWS S3 integration for file storage."""

import logging
from typing import Optional, BinaryIO, Dict
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class S3Handler:
    """Handles S3 storage operations."""

    def __init__(
        self,
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        region_name: str = "us-east-1",
        bucket_name: str = "truthlens-ai",
    ):
        """
        Initialize S3 handler.

        Args:
            aws_access_key: AWS access key ID
            aws_secret_key: AWS secret access key
            region_name: AWS region
            bucket_name: S3 bucket name
        """
        self.bucket_name = bucket_name
        self.region_name = region_name

        try:
            if aws_access_key and aws_secret_key:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=region_name,
                )
            else:
                # Use default credentials from environment
                self.s3_client = boto3.client("s3", region_name=region_name)

            logger.info(f"Initialized S3 client for bucket: {bucket_name}")
        except Exception as e:
            logger.error(f"S3 initialization failed: {e}")
            self.s3_client = None

    def bucket_exists(self) -> bool:
        """Check if bucket exists."""
        if not self.s3_client:
            return False

        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logger.error(f"Error checking bucket: {e}")
            return False

    def create_bucket(self) -> bool:
        """Create S3 bucket."""
        if not self.s3_client:
            return False

        try:
            if self.region_name == "us-east-1":
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self.region_name},
                )

            logger.info(f"Created S3 bucket: {self.bucket_name}")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "BucketAlreadyExists":
                logger.warning(f"Bucket already exists: {self.bucket_name}")
                return True
            logger.error(f"Error creating bucket: {e}")
            return False

    def upload_file(
        self,
        file_path: str,
        s3_key: Optional[str] = None,
        public: bool = False,
    ) -> Optional[str]:
        """
        Upload file to S3.

        Args:
            file_path: Local file path
            s3_key: S3 object key (if None, uses filename)
            public: Make file publicly readable

        Returns:
            S3 URL or None on failure
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return None

        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None

            # Use filename if S3 key not provided
            if s3_key is None:
                s3_key = f"uploads/{file_path.name}"

            # Upload file
            extra_args = {}
            if public:
                extra_args["ACL"] = "public-read"

            self.s3_client.upload_file(
                str(file_path), self.bucket_name, s3_key, ExtraArgs=extra_args
            )

            # Generate URL
            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"
            logger.info(f"Uploaded file to S3: {url}")
            return url

        except ClientError as e:
            logger.error(f"Upload error: {e}")
            return None

    def upload_fileobj(
        self,
        fileobj: BinaryIO,
        s3_key: str,
        public: bool = False,
    ) -> Optional[str]:
        """
        Upload file object to S3.

        Args:
            fileobj: File-like object
            s3_key: S3 object key
            public: Make file publicly readable

        Returns:
            S3 URL or None on failure
        """
        if not self.s3_client:
            return None

        try:
            extra_args = {}
            if public:
                extra_args["ACL"] = "public-read"

            self.s3_client.upload_fileobj(
                fileobj, self.bucket_name, s3_key, ExtraArgs=extra_args
            )

            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"
            logger.info(f"Uploaded file object to S3: {url}")
            return url

        except ClientError as e:
            logger.error(f"Upload error: {e}")
            return None

    def download_file(self, s3_key: str, file_path: str) -> bool:
        """
        Download file from S3.

        Args:
            s3_key: S3 object key
            file_path: Local file path

        Returns:
            True on success
        """
        if not self.s3_client:
            return False

        try:
            self.s3_client.download_file(self.bucket_name, s3_key, file_path)
            logger.info(f"Downloaded file from S3: {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Download error: {e}")
            return False

    def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3.

        Args:
            s3_key: S3 object key

        Returns:
            True on success
        """
        if not self.s3_client:
            return False

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Deleted file from S3: {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Delete error: {e}")
            return False

    def list_files(self, prefix: str = "") -> list:
        """
        List files in S3 bucket.

        Args:
            prefix: Filter by key prefix

        Returns:
            List of file keys
        """
        if not self.s3_client:
            return []

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )

            files = []
            if "Contents" in response:
                files = [obj["Key"] for obj in response["Contents"]]

            logger.info(f"Listed {len(files)} files in S3")
            return files

        except ClientError as e:
            logger.error(f"List error: {e}")
            return []

    def get_file_url(self, s3_key: str, expiration_hours: int = 24) -> Optional[str]:
        """
        Generate presigned URL for file access.

        Args:
            s3_key: S3 object key
            expiration_hours: URL expiration time in hours

        Returns:
            Presigned URL or None on failure
        """
        if not self.s3_client:
            return None

        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration_hours * 3600,
            )
            logger.info(f"Generated presigned URL: {s3_key}")
            return url
        except ClientError as e:
            logger.error(f"URL generation error: {e}")
            return None

    def upload_analysis_result(
        self, analysis_id: str, result_data: Dict
    ) -> Optional[str]:
        """
        Upload analysis result to S3.

        Args:
            analysis_id: Analysis ID
            result_data: Analysis result dictionary

        Returns:
            S3 URL or None on failure
        """
        if not self.s3_client:
            return None

        try:
            s3_key = f"analysis_results/{analysis_id}.json"
            json_data = json.dumps(result_data, indent=2)

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data.encode(),
                ContentType="application/json",
            )

            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"
            logger.info(f"Uploaded analysis result: {url}")
            return url

        except ClientError as e:
            logger.error(f"Analysis upload error: {e}")
            return None

    def get_bucket_size(self) -> int:
        """
        Get total bucket size in bytes.

        Returns:
            Total size in bytes
        """
        if not self.s3_client:
            return 0

        try:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name)

            total_size = 0
            for page in pages:
                if "Contents" in page:
                    total_size += sum(obj["Size"] for obj in page["Contents"])

            return total_size
        except ClientError as e:
            logger.error(f"Size calculation error: {e}")
            return 0

    def cleanup_old_files(self, prefix: str, days: int = 30) -> int:
        """
        Delete files older than specified days.

        Args:
            prefix: Key prefix to filter
            days: Age threshold

        Returns:
            Number of files deleted
        """
        if not self.s3_client:
            return 0

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = 0

            files = self.list_files(prefix)
            for file_key in files:
                response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
                last_modified = response["LastModified"].replace(tzinfo=None)

                if last_modified < cutoff_date:
                    self.delete_file(file_key)
                    deleted_count += 1

            logger.info(f"Deleted {deleted_count} old files")
            return deleted_count

        except ClientError as e:
            logger.error(f"Cleanup error: {e}")
            return 0

    def get_storage_stats(self) -> Dict:
        """Get bucket storage statistics."""
        total_size = self.get_bucket_size()
        files = self.list_files()

        return {
            "bucket_name": self.bucket_name,
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_gb": total_size / (1024 ** 3),
            "region": self.region_name,
        }
