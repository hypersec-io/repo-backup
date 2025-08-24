"""
repo-backup - Enterprise repository backup tool

Syncs corporate Git repositories from GitHub, GitLab, and Bitbucket 
to local storage or AWS S3 with professional security and lifecycle management.

MIT License
Copyright (c) 2025 HyperSec
"""

__version__ = "1.0.0"
__author__ = "Derek"
__license__ = "MIT"
__description__ = "Enterprise repository backup tool that syncs corporate Git repositories to local storage or AWS S3"

from .base import Repository, RepositoryManager
from .github_manager import GitHubManager
from .gitlab_manager import GitLabManager
from .bitbucket_manager import BitbucketManager
from .s3_uploader import S3Uploader
from .main import main

__all__ = [
    'Repository',
    'RepositoryManager',
    'GitHubManager',
    'GitLabManager',
    'BitbucketManager',
    'S3Uploader',
    'main'
]