"""
AWS S3 uploader for repository backups

Copyright 2025 HyperSec

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
import os
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
from tqdm import tqdm

from .base import Repository


class S3Uploader:
    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        prefix: str = "repos",
        work_dir: Optional[str] = None,
    ):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.logger = logging.getLogger(self.__class__.__name__)

        session_kwargs = {"region_name": region}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key

        session = boto3.Session(**session_kwargs)
        self.s3_client = session.client("s3")
        self.s3_resource = session.resource("s3")
        self.bucket = self.s3_resource.Bucket(bucket_name)

        # Create temp directory for operations
        if work_dir:
            # Use explicitly provided work directory
            self.temp_dir = os.path.join(work_dir, "repo-backup")
        else:
            # Default to /var/tmp/repo-backup for S3 operations
            self.temp_dir = "/var/tmp/repo-backup"

        try:
            os.makedirs(self.temp_dir, exist_ok=True)
            self.logger.info(f"[CONFIG] Working directory: {self.temp_dir}")
        except Exception as e:
            self.logger.error(
                f"[ERROR] Failed to create working directory {self.temp_dir}: {e}"
            )
            raise

    def upload_repository(
        self, repo: Repository, method: str = "direct", local_backup_path: str = None
    ) -> bool:
        print(f"[S3_UPLOADER] upload_repository called for {repo.name}")
        """
        Upload repository to S3
        Args:
            repo: Repository object
            method: 'direct' for streaming or 'archive' for tar.gz
            local_backup_path: Check this path for existing local backups first
        """
        try:
            self.logger.info(
                f"[UPLOAD_REPO] Starting upload for {repo.name} with method={method}, local_backup_path={local_backup_path}"
            )

            # SMART OPTIMIZATION: Check for existing local backup first
            if local_backup_path:
                self.logger.info(
                    f"[SMART] Checking for existing local backup for {repo.name}"
                )
                local_bundle = self._find_local_backup(repo, local_backup_path)
                if local_bundle:
                    self.logger.info(
                        f"[SMART] Found existing local backup for {repo.name}, uploading from local file"
                    )
                    return self._upload_existing_bundle(repo, local_bundle)
                else:
                    self.logger.info(
                        f"[SMART] No existing local backup found for {repo.name}"
                    )

            # Fallback to regular upload methods
            self.logger.info(f"[UPLOAD_REPO] Using regular upload method: {method}")
            if method == "direct":
                self.logger.info(
                    f"[UPLOAD_REPO] Calling _direct_upload for {repo.name}"
                )
                return self._direct_upload(repo)
            else:
                self.logger.info(
                    f"[UPLOAD_REPO] Calling _archive_upload for {repo.name}"
                )
                return self._archive_upload(repo)

        except Exception as e:
            self.logger.error(f"Failed to upload {repo.name}: {e}")
            import traceback

            self.logger.error(f"Exception traceback: {traceback.format_exc()}")
            return False

    def _direct_upload(self, repo: Repository) -> bool:
        """Stream repository directly to S3 using git bundle"""
        print(f"[S3_UPLOADER] _direct_upload called for {repo.name}")
        print(f"[S3_UPLOADER] repo.platform={repo.platform}, repo.owner={repo.owner}")
        try:
            self.logger.info(f"[DIRECT_UPLOAD] Starting direct upload for {repo.name}")
            print(f"[S3_UPLOADER] Point 1: Setting up paths")
            repo_path = os.path.join(self.temp_dir, f"{repo.name}_clone")
            bundle_path = os.path.join(self.temp_dir, f"{repo.name}.bundle")
            print(
                f"[S3_UPLOADER] Point 2: repo_path={repo_path}, bundle_path={bundle_path}"
            )

            # For subprocess call, use relative paths since cwd will be set to temp_dir
            relative_repo_path = f"{repo.name}_clone"

            # Clone with minimal depth first
            print(f"[S3_UPLOADER] Point 3: About to clone")
            self.logger.info(f"Cloning {repo.name}...")
            self.logger.debug(f"Repository path: {repo_path}")
            self.logger.debug(f"Bundle path: {bundle_path}")
            self.logger.debug(f"Temp directory: {self.temp_dir}")
            self.logger.debug(f"Working directory: {os.getcwd()}")
            print(f"[S3_UPLOADER] Point 4: After logging debug info")

            clone_cmd = ["git", "clone", "--mirror", repo.clone_url, relative_repo_path]
            self.logger.debug(
                f"Clone command: git clone --mirror [REDACTED_URL] {relative_repo_path}"
            )
            print(f"[S3_UPLOADER] Point 5: About to run git clone")

            result = subprocess.run(
                clone_cmd, capture_output=True, text=True, cwd=self.temp_dir
            )
            print(
                f"[S3_UPLOADER] Point 6: Git clone completed with return code: {result.returncode}"
            )

            if result.returncode != 0:
                self.logger.error(f"Clone failed for {repo.name}")
                self.logger.error(f"  Command: {' '.join(clone_cmd)}")
                self.logger.error(f"  stdout: {result.stdout}")
                self.logger.error(f"  stderr: {result.stderr}")
                self.logger.error(f"  return code: {result.returncode}")
                return False

            # Fetch LFS objects if LFS is used in the repository
            lfs_check = subprocess.run(
                ["git", "--git-dir", repo_path, "lfs", "ls-files"],
                capture_output=True,
                text=True,
            )

            if lfs_check.returncode == 0 and lfs_check.stdout.strip():
                self.logger.info(f"Fetching LFS objects for {repo.name}...")
                lfs_fetch = subprocess.run(
                    ["git", "--git-dir", repo_path, "lfs", "fetch", "--all"],
                    capture_output=True,
                    text=True,
                )
                if lfs_fetch.returncode != 0:
                    self.logger.warning(
                        f"LFS fetch failed for {repo.name}: {lfs_fetch.stderr}"
                    )
                    # Continue anyway - bundle will still work without LFS objects

            self.logger.debug(
                f"Clone command completed - checking repository path exists: {os.path.exists(repo_path)}"
            )
            if not os.path.exists(repo_path):
                self.logger.error(
                    f"Clone appeared successful but repository directory does not exist: {repo_path}"
                )
                self.logger.error(f"Git clone stdout: {result.stdout}")
                self.logger.error(f"Git clone stderr: {result.stderr}")
                return False

            if os.path.exists(repo_path):
                self.logger.debug(
                    f"Repository directory contents: {os.listdir(repo_path) if os.path.isdir(repo_path) else 'Not a directory'}"
                )

            # Get the last commit date from the repository (bare repo needs --git-dir)
            print(f"[S3_UPLOADER] Point 7: Getting last commit date")
            # For bare repositories, we need to use --git-dir or run from within the repo
            last_commit_cmd = [
                "git",
                "--git-dir",
                repo_path,
                "log",
                "-1",
                "--format=%cd",
                "--date=format:%Y%m%d_%H%M%S",
                "--all",
            ]
            last_commit_result = subprocess.run(
                last_commit_cmd, capture_output=True, text=True
            )
            print(
                f"[S3_UPLOADER] Point 8: Last commit result: returncode={last_commit_result.returncode}, stdout='{last_commit_result.stdout.strip()}'"
            )

            if last_commit_result.returncode != 0:
                # Check if it's an empty repository (also use --git-dir for bare repo)
                check_empty = subprocess.run(
                    ["git", "--git-dir", repo_path, "rev-list", "-n", "1", "--all"],
                    capture_output=True,
                    text=True,
                )
                if check_empty.returncode != 0 or not check_empty.stdout.strip():
                    print(
                        f"[S3_UPLOADER] CRITICAL: Treating repo as empty! returncode={check_empty.returncode}, stdout='{check_empty.stdout.strip()}'"
                    )
                    self.logger.info(
                        f"[SKIP] Skipping {repo.name} - repository is empty (no commits)"
                    )
                    if os.path.exists(repo_path):
                        shutil.rmtree(repo_path)
                    return True
                else:
                    self.logger.error(f"Failed to get last commit date for {repo.name}")
                    return False

            last_commit_date = last_commit_result.stdout.strip()
            if not last_commit_date:
                # Empty repo, use current date as fallback
                last_commit_date = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Check if this version already exists in S3
            s3_key = f"{self.prefix}/{repo.platform}/{repo.owner}/{repo.name}_{last_commit_date}.bundle"
            self.logger.debug(f"Checking if S3 key already exists: {s3_key}")
            print(f"[S3_UPLOADER] Checking S3 key: {s3_key}")

            try:
                # Check if object exists in S3
                response = self.s3_client.head_object(
                    Bucket=self.bucket_name, Key=s3_key
                )
                file_size = response.get("ContentLength", 0)
                print(f"[S3_UPLOADER] File already exists in S3! Size: {file_size}")
                self.logger.info(
                    f"[SKIP] Backup already exists in S3 for {repo.name} with commit date {last_commit_date}: "
                    f"{s3_key} ({file_size / 1024 / 1024:.2f} MB)"
                )
                # Cleanup
                if os.path.exists(repo_path):
                    shutil.rmtree(repo_path)
                if os.path.exists(bundle_path):
                    os.remove(bundle_path)
                return True
            except (
                self.s3_client.exceptions.NoSuchKey,
                self.s3_client.exceptions.ClientError,
            ) as e:
                # Object doesn't exist, proceed with backup
                self.logger.debug(
                    f"S3 object does not exist (expected), proceeding with backup: {e}"
                )
                pass
            except Exception as e:
                self.logger.error(f"Error checking S3 object existence: {e}")

            # Create git bundle (for bare repo, use --git-dir)
            self.logger.info(f"Creating bundle for {repo.name}...")
            # For bare repositories, create bundle with absolute path
            bundle_cmd = [
                "git",
                "--git-dir",
                repo_path,
                "bundle",
                "create",
                bundle_path,
                "--all",
            ]

            result = subprocess.run(bundle_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                # Check if it's an empty repository
                if "Refusing to create empty bundle" in result.stderr:
                    self.logger.info(
                        f"[SKIP] Skipping {repo.name} - repository is empty (no commits)"
                    )
                    # Cleanup
                    if os.path.exists(repo_path):
                        shutil.rmtree(repo_path)
                    return True  # Return True to indicate this was handled successfully
                else:
                    self.logger.error(f"Bundle creation failed: {result.stderr}")
                    return False

            # Upload bundle to S3 (s3_key already set above with last commit date)
            file_size = os.path.getsize(bundle_path)

            self.logger.info(
                f"Uploading {repo.name} to S3 ({file_size / 1024 / 1024:.2f} MB)..."
            )
            self.logger.debug(
                f"Upload details - Bundle: {bundle_path}, Bucket: {self.bucket_name}, Key: {s3_key}"
            )

            try:
                with tqdm(
                    total=file_size, unit="B", unit_scale=True, desc=repo.name
                ) as pbar:

                    def upload_callback(bytes_transferred):
                        pbar.update(bytes_transferred)

                    self.s3_client.upload_file(
                        bundle_path,
                        self.bucket_name,
                        s3_key,
                        Callback=upload_callback,
                        ExtraArgs={
                            "ServerSideEncryption": "AES256",
                            "Metadata": {
                                "platform": repo.platform,
                                "owner": repo.owner,
                                "is_private": str(repo.is_private),
                                "default_branch": repo.default_branch or "unknown",
                            },
                        },
                    )

                self.logger.info(
                    f"Successfully uploaded {repo.name} to s3://{self.bucket_name}/{s3_key}"
                )

                # Verify upload immediately
                try:
                    verify_response = self.s3_client.head_object(
                        Bucket=self.bucket_name, Key=s3_key
                    )
                    uploaded_size = verify_response.get("ContentLength", 0)
                    self.logger.info(
                        f"[VERIFY] Upload verified - file exists in S3 with size {uploaded_size} bytes"
                    )
                except Exception as verify_error:
                    self.logger.error(
                        f"[VERIFY] Upload verification failed: {verify_error}"
                    )

            except Exception as upload_error:
                self.logger.error(f"[UPLOAD] S3 upload failed: {upload_error}")
                raise upload_error

            # Cleanup
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            if os.path.exists(bundle_path):
                os.remove(bundle_path)

            return True

        except Exception as e:
            self.logger.error(f"Direct upload failed for {repo.name}: {e}")
            return False

    def _archive_upload(self, repo: Repository) -> bool:
        """Clone and archive repository before uploading"""
        try:
            repo_path = os.path.join(self.temp_dir, f"{repo.name}_clone")
            archive_path = os.path.join(self.temp_dir, f"{repo.name}.tar.gz")

            # Clone repository
            self.logger.info(f"Cloning {repo.name}...")
            clone_cmd = ["git", "clone", "--mirror", repo.clone_url, repo_path]

            result = subprocess.run(
                clone_cmd, capture_output=True, text=True, cwd=self.temp_dir
            )

            if result.returncode != 0:
                self.logger.error(f"Clone failed: {result.stderr}")
                return False

            # Create tar.gz archive
            self.logger.info(f"Archiving {repo.name}...")
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(repo_path, arcname=repo.name)

            # Upload to S3
            s3_key = f"{s3_key_base}.tar.gz"
            file_size = os.path.getsize(archive_path)

            self.logger.info(
                f"Uploading {repo.name} to S3 ({file_size / 1024 / 1024:.2f} MB)..."
            )

            with tqdm(
                total=file_size, unit="B", unit_scale=True, desc=repo.name
            ) as pbar:

                def upload_callback(bytes_transferred):
                    pbar.update(bytes_transferred)

                self.s3_client.upload_file(
                    archive_path,
                    self.bucket_name,
                    s3_key,
                    Callback=upload_callback,
                    ExtraArgs={
                        "ServerSideEncryption": "AES256",
                        "Metadata": {
                            "platform": repo.platform,
                            "owner": repo.owner,
                            "is_private": str(repo.is_private),
                            "default_branch": repo.default_branch or "unknown",
                        },
                    },
                )

            self.logger.info(
                f"Successfully uploaded {repo.name} to s3://{self.bucket_name}/{s3_key}"
            )

            # Cleanup
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            if os.path.exists(archive_path):
                os.remove(archive_path)

            return True

        except Exception as e:
            self.logger.error(f"Archive upload failed for {repo.name}: {e}")
            return False

    def list_backups(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """List all backups in S3"""
        prefix = f"{self.prefix}/{platform}" if platform else self.prefix

        backups = []
        paginator = self.s3_client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            if "Contents" in page:
                for obj in page["Contents"]:
                    backups.append(
                        {
                            "key": obj["Key"],
                            "size_mb": obj["Size"] / 1024 / 1024,
                            "last_modified": obj["LastModified"].isoformat(),
                        }
                    )

        return backups

    def cleanup_temp(self):
        """Clean up temporary directory completely"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.logger.info(f"[CLEANUP] Removed working directory: {self.temp_dir}")

    def test_connection(self) -> bool:
        """Test S3 connectivity and permissions"""
        try:
            # Test bucket access by listing objects (limited to 1)
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, MaxKeys=1
            )

            # Test write permissions by uploading a small test file
            test_key = f"{self.prefix}/health_check_test.txt"
            test_content = f"Health check test - {datetime.now().isoformat()}"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=test_key,
                Body=test_content.encode("utf-8"),
                Metadata={"test": "health_check"},
            )

            # Clean up test file
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=test_key)

            return True

        except Exception as e:
            self.logger.error(f"S3 connection test failed: {str(e)}")
            return False

    def _find_local_backup(
        self, repo: Repository, local_backup_path: str
    ) -> Optional[str]:
        """
        Find existing local backup bundle for repository
        Args:
            repo: Repository object
            local_backup_path: Path to search for local backups
        Returns:
            Path to bundle file if found, None otherwise
        """
        try:
            base_path = Path(local_backup_path)
            # Look for bundles in platform/owner/ structure
            search_path = base_path / repo.platform / repo.owner

            if not search_path.exists():
                return None

            # Look for bundle files matching this repository
            pattern = f"{repo.name}_*.bundle"
            bundle_files = list(search_path.glob(pattern))

            if not bundle_files:
                return None

            # Return the most recent bundle (sorted by name, which includes timestamp)
            latest_bundle = sorted(bundle_files)[-1]
            self.logger.debug(f"[SMART] Found local bundle: {latest_bundle}")
            return str(latest_bundle)

        except Exception as e:
            self.logger.debug(
                f"[SMART] Error finding local backup for {repo.name}: {e}"
            )
            return None

    def _upload_existing_bundle(self, repo: Repository, bundle_path: str) -> bool:
        """
        Upload existing bundle file to S3
        Args:
            repo: Repository object
            bundle_path: Path to existing bundle file
        Returns:
            Success status
        """
        try:
            # Generate S3 key with current timestamp to avoid duplicates
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"{self.prefix}/{repo.platform}/{repo.owner}/{repo.name}_{timestamp}.bundle"

            file_size = os.path.getsize(bundle_path)
            self.logger.info(
                f"[SMART] Uploading existing bundle for {repo.name} ({file_size / 1024 / 1024:.2f} MB)..."
            )

            with tqdm(
                total=file_size, unit="B", unit_scale=True, desc=f"Upload {repo.name}"
            ) as pbar:

                def upload_callback(bytes_transferred):
                    pbar.update(bytes_transferred)

                self.s3_client.upload_file(
                    bundle_path,
                    self.bucket_name,
                    s3_key,
                    Callback=upload_callback,
                    ExtraArgs={
                        "ServerSideEncryption": "AES256",
                        "Metadata": {
                            "platform": repo.platform,
                            "owner": repo.owner,
                            "is_private": str(repo.is_private),
                            "default_branch": repo.default_branch or "unknown",
                            "source": "local_backup_optimization",
                        },
                    },
                )

            self.logger.info(
                f"[SMART] Successfully uploaded {repo.name} from local backup to s3://{self.bucket_name}/{s3_key}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"[SMART] Failed to upload existing bundle for {repo.name}: {e}"
            )
            return False
