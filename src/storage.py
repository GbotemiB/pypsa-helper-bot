"""
Storage utilities for downloading and managing FAISS index from GitHub Releases
"""
import os
import tarfile
import requests
import shutil
from pathlib import Path
from typing import Optional
import time


class IndexStorage:
    """Manages FAISS index storage and retrieval"""
    
    def __init__(self, local_path: str = "pypsa_ecosystem_faiss_index"):
        self.local_path = Path(local_path)
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "GbotemiB")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "pypsa-helper-bot")
        self.github_token = os.getenv("GITHUB_TOKEN")
        
    def get_latest_release_url(self) -> Optional[str]:
        """Get the download URL for the latest FAISS index release"""
        api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases"
        
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()
            releases = response.json()
            
            # Find the latest release with index tag
            for release in releases:
                if release["tag_name"].startswith("index-"):
                    # Get the asset download URL
                    for asset in release.get("assets", []):
                        if asset["name"] == "faiss-index.tar.gz":
                            return asset["browser_download_url"], release["tag_name"]
            
            return None, None
        except Exception as e:
            print(f"Error fetching latest release: {e}")
            return None, None
    
    def download_index(self, force: bool = False) -> bool:
        """
        Download the latest FAISS index from GitHub Releases
        
        Args:
            force: Force download even if local index exists
            
        Returns:
            True if download successful, False otherwise
        """
        # Check if index already exists and is recent
        if not force and self.local_path.exists():
            last_updated_file = self.local_path / "last_updated.txt"
            if last_updated_file.exists():
                # Check if less than 24 hours old
                age_hours = (time.time() - last_updated_file.stat().st_mtime) / 3600
                if age_hours < 24:
                    print(f"Local index is recent ({age_hours:.1f} hours old). Skipping download.")
                    return True
        
        print("Downloading latest FAISS index from GitHub Releases...")
        
        download_url, tag = self.get_latest_release_url()
        if not download_url:
            print("❌ No FAISS index release found. Using local index if available.")
            return self.local_path.exists()
        
        print(f"Found release: {tag}")
        print(f"Downloading from: {download_url}")
        
        try:
            # Download the tar.gz file
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            # Save to temporary file
            temp_file = Path("faiss-index.tar.gz")
            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded {temp_file.stat().st_size / 1024 / 1024:.1f} MB")
            
            # Extract the archive
            print("Extracting index...")
            
            # Remove old index if exists
            if self.local_path.exists():
                shutil.rmtree(self.local_path)
            
            with tarfile.open(temp_file, "r:gz") as tar:
                tar.extractall()
            
            # Clean up temp file
            temp_file.unlink()
            
            print("✅ FAISS index downloaded and extracted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading index: {e}")
            return False
    
    def check_for_updates(self) -> bool:
        """
        Check if a newer index is available
        
        Returns:
            True if update available, False otherwise
        """
        _, latest_tag = self.get_latest_release_url()
        if not latest_tag:
            return False
        
        # Check local tag
        local_tag_file = self.local_path / "release_tag.txt"
        if not local_tag_file.exists():
            return True
        
        local_tag = local_tag_file.read_text().strip()
        return latest_tag != local_tag
    
    def save_release_tag(self, tag: str):
        """Save the current release tag locally"""
        tag_file = self.local_path / "release_tag.txt"
        tag_file.write_text(tag)
    
    def get_index_info(self) -> dict:
        """Get information about the current index"""
        info = {
            "exists": self.local_path.exists(),
            "path": str(self.local_path),
        }
        
        if self.local_path.exists():
            last_updated_file = self.local_path / "last_updated.txt"
            if last_updated_file.exists():
                info["last_updated"] = last_updated_file.read_text().strip()
            
            tag_file = self.local_path / "release_tag.txt"
            if tag_file.exists():
                info["release_tag"] = tag_file.read_text().strip()
            
            # Get file sizes
            index_file = self.local_path / "index.faiss"
            pkl_file = self.local_path / "index.pkl"
            
            if index_file.exists():
                info["index_size_mb"] = index_file.stat().st_size / 1024 / 1024
            if pkl_file.exists():
                info["pkl_size_mb"] = pkl_file.stat().st_size / 1024 / 1024
        
        return info


def ensure_index_available() -> bool:
    """
    Ensure FAISS index is available locally
    Downloads from GitHub Releases if not present
    
    Returns:
        True if index is available, False otherwise
    """
    storage = IndexStorage()
    
    # Check if index exists locally
    if not storage.local_path.exists():
        print("FAISS index not found locally. Downloading from GitHub Releases...")
        return storage.download_index(force=True)
    
    print("✅ FAISS index found locally")
    return True
