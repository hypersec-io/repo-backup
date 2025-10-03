#!/usr/bin/env python3
"""
Uninstaller for repo-backup
Removes the installation directory and symlink
"""

import os
import sys
import shutil
from pathlib import Path


def check_root():
    """Check if running as root"""
    if os.geteuid() != 0:
        print("This uninstaller needs sudo privileges to remove symlinks from /usr/local/bin")
        print("Please run with: sudo python3 uninstall.py")
        sys.exit(1)


def uninstall_repo_backup():
    """Uninstall repo-backup"""
    install_dir = Path("/opt/repo-backup")
    symlink_path = Path("/usr/local/bin/repo-backup")
    
    print("Uninstalling repo-backup...")
    
    # Remove symlink
    if symlink_path.exists() or symlink_path.is_symlink():
        print(f"Removing symlink: {symlink_path}")
        symlink_path.unlink()
    else:
        print(f"Symlink {symlink_path} not found")
    
    # Remove installation directory
    if install_dir.exists():
        print(f"Removing installation directory: {install_dir}")
        shutil.rmtree(install_dir)
    else:
        print(f"Installation directory {install_dir} not found")
    
    print("OK repo-backup uninstalled successfully!")


if __name__ == "__main__":
    check_root()
    uninstall_repo_backup()