#!/usr/bin/env python3
"""
Local system installer for repo-backup
Creates a virtual environment and installs the tool with symlink to /usr/local/bin
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, check=True):
    """Run command and handle errors"""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    
    return result


def check_requirements():
    """Check system requirements"""
    # Check if running as root for /usr/local/bin access
    if os.geteuid() != 0:
        print("This installer needs sudo privileges to create symlinks in /usr/local/bin")
        print("Please run with: sudo python3 install.py")
        sys.exit(1)
    
    # Check python3 is available
    if not shutil.which('python3'):
        print("python3 is required but not found. Please install Python 3.9+ first.")
        sys.exit(1)
    
    # Check pip is available
    if not shutil.which('pip3') and not shutil.which('pip'):
        print("pip is required but not found. Please install pip first.")
        sys.exit(1)
    
    # Check git is available
    if not shutil.which('git'):
        print("git is required but not found. Please install git first.")
        sys.exit(1)


def install_repo_backup():
    """Install repo-backup with dedicated venv"""
    project_root = Path(__file__).parent.absolute()
    install_dir = Path("/opt/repo-backup")
    
    print(f"Installing repo-backup to {install_dir}")
    
    # Create install directory
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy project files to install directory
    print("Copying project files...")
    for item in project_root.iterdir():
        if item.name in ['.git', '__pycache__', '.pytest_cache', 'logs', 'tmp']:
            continue
        
        target = install_dir / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    
    # Create virtual environment and install
    print("Creating virtual environment...")
    os.chdir(install_dir)
    run_command(['python3', '-m', 'venv', '.venv'])
    
    # Determine pip command
    pip_cmd = '.venv/bin/pip'
    
    print("Upgrading pip...")
    run_command([pip_cmd, 'install', '--upgrade', 'pip'])
    
    print("Installing dependencies...")
    run_command([pip_cmd, 'install', '-e', '.'])
    
    # Create wrapper script
    wrapper_script = install_dir / "repo-backup-wrapper"
    wrapper_content = f"""#!/bin/bash
cd {install_dir}
exec .venv/bin/python -m src.main "$@"
"""
    
    with open(wrapper_script, 'w') as f:
        f.write(wrapper_content)
    
    # Make wrapper executable
    wrapper_script.chmod(0o755)
    
    # Create symlink in /usr/local/bin
    symlink_path = Path("/usr/local/bin/repo-backup")
    if symlink_path.exists() or symlink_path.is_symlink():
        print(f"Removing existing {symlink_path}")
        symlink_path.unlink()
    
    print(f"Creating symlink {symlink_path} -> {wrapper_script}")
    symlink_path.symlink_to(wrapper_script)
    
    print(f"""
Installation complete!

repo-backup is now installed at: {install_dir}
Executable available as: repo-backup

Test the installation:
  repo-backup --help

To uninstall:
  sudo rm -rf {install_dir}
  sudo rm {symlink_path}
""")


def test_installation():
    """Test the installed tool"""
    print("Testing installation...")
    result = run_command(['repo-backup', '--help'], check=False)
    if result.returncode == 0:
        print("✓ Installation test passed!")
        return True
    else:
        print("✗ Installation test failed!")
        print(f"Error: {result.stderr}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_installation()
        sys.exit(0)
    
    check_requirements()
    install_repo_backup()
    
    # Test installation
    if test_installation():
        print("\n🎉 repo-backup installed successfully!")
    else:
        print("\n❌ Installation completed but test failed. Please check the logs above.")
        sys.exit(1)