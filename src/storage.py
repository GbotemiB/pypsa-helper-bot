""""""

import timeimport time
from typing import Optional, Tuplefrom typing import Optional
from pathlib import Pathfrom pathlib import Path
import shutilimport shutil
import requestsimport requests
import tarfileimport tarfile
import osimport os
Storage utilities for downloading and managing FAISS index from GitHub ReleasesStorage utilities for downloading and managing FAISS index from GitHub Releases

""""""


class IndexStorage:
    class IndexStorage:

    """Manages FAISS index storage and retrieval"""    """Manages FAISS index storage and retrieval"""

    def __init__(self, local_path: str = "pypsa_ecosystem_faiss_index"): def __init__(self, local_path: str = "pypsa_ecosystem_faiss_index"):

        self.local_path = Path(local_path)        self.local_path = Path(local_path)

        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "GbotemiB")        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "GbotemiB")

        self.repo_name = os.getenv("GITHUB_REPO_NAME", "pypsa-helper-bot")        self.repo_name = os.getenv("GITHUB_REPO_NAME", "pypsa-helper-bot")

        self.github_token = os.getenv("GITHUB_TOKEN")        self.github_token = os.getenv("GITHUB_TOKEN")

    def get_latest_release_url(self) -> Tuple[Optional[str], Optional[str]]: def get_latest_release_url(self) -> Optional[str]:
        """Get the download URL for the latest FAISS index release"""        """Get the download URL for the latest FAISS index release"""

        api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases"        api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases"

        headers = {}        headers = {}

        if self.github_token:
            if self.github_token:

            headers["Authorization"] = f"token {self.github_token}"            headers["Authorization"] = f"token {self.github_token}"

        try:
            try:

            response = requests.get(api_url, headers=headers, timeout=30)            response = requests.get(api_url, headers=headers, timeout=30)

            response.raise_for_status()            response.raise_for_status()

            releases = response.json()            releases = response.json()

            # Find the latest release with index tag            # Find the latest release with index tag

            for release in releases:
                for release in releases:

                if release["tag_name"].startswith("index-"):
                    if release["tag_name"].startswith("index-"):

                        # Get the asset download URL                    # Get the asset download URL

                    for asset in release.get("assets", []):
                        for asset in release.get("assets", []):

                        if asset["name"] == "faiss-index.tar.gz":
                            if asset["name"] == "faiss-index.tar.gz":

                            return asset["browser_download_url"], release["tag_name"] return asset["browser_download_url"], release["tag_name"]

            return None, None return None, None

        except Exception as e:
            except Exception as e:

            print(f"Error fetching latest release: {e}") print(f"Error fetching latest release: {e}")

            return None, None return None, None

    def download_index(self, force: bool = False) -> bool: def download_index(self, force: bool = False) -> bool:
        """        """

        Download the latest FAISS index from GitHub Releases        Download the latest FAISS index from GitHub Releases

        Args:        Args:

            force: Force download even if local index exists            force: Force download even if local index exists

        Returns:        Returns:

            True if download successful, False otherwise            True if download successful, False otherwise

        """        """

        # Check if index already exists and is recent        # Check if index already exists and is recent

        if not force and self.local_path.exists():
            if not force and self.local_path.exists():

            last_updated_file = self.local_path / "last_updated.txt"            last_updated_file = self.local_path / "last_updated.txt"

            if last_updated_file.exists():
                if last_updated_file.exists():

                    # Check if less than 24 hours old                # Check if less than 24 hours old

                age_hours = (time.time() - last_updated_file.stat().st_mtime) / 3600                age_hours = (time.time() - last_updated_file.stat().st_mtime) / 3600

                if age_hours < 24:
                    if age_hours < 24:

                    print(f"Local index is recent ({age_hours:.1f} hours old). Skipping download.") print(f"Local index is recent ({age_hours:.1f} hours old). Skipping download.")

                    return True return True

        print("Downloading latest FAISS index from GitHub Releases...") print("Downloading latest FAISS index from GitHub Releases...")

        download_url, tag = self.get_latest_release_url()        download_url, tag = self.get_latest_release_url()

        if not download_url:
            if not download_url:

            print("❌ No FAISS index release found. Using local index if available.") print("❌ No FAISS index release found. Using local index if available.")

            return self.local_path.exists() return self.local_path.exists()

        print(f"Found release: {tag}") print(f"Found release: {tag}")

        print(f"Downloading from: {download_url}") print(f"Downloading from: {download_url}")

        try:
            try:

                # Download the tar.gz file            # Download the tar.gz file

            response = requests.get(download_url, stream=True, timeout=300)            response = requests.get(download_url, stream=True, timeout=300)

            response.raise_for_status()            response.raise_for_status()

            # Save to temporary file            # Save to temporary file

            temp_file = Path("faiss-index.tar.gz")            temp_file = Path("faiss-index.tar.gz")

            with open(temp_file, "wb") as f:
                with open(temp_file, "wb") as f:

                for chunk in response.iter_content(chunk_size=8192):
                    for chunk in response.iter_content(chunk_size=8192):

                    f.write(chunk)                    f.write(chunk)

            print(f"Downloaded {temp_file.stat().st_size / 1024 / 1024:.1f} MB") print(f"Downloaded {temp_file.stat().st_size / 1024 / 1024:.1f} MB")

            # Extract the archive            # Extract the archive

            print("Extracting index...") print("Extracting index...")

            # Remove old index if exists            # Remove old index if exists

            if self.local_path.exists():
                if self.local_path.exists():

                shutil.rmtree(self.local_path)                shutil.rmtree(self.local_path)

            with tarfile.open(temp_file, "r:gz") as tar:
                with tarfile.open(temp_file, "r:gz") as tar:

                tar.extractall()                tar.extractall()

            # Clean up temp file            # Clean up temp file

            temp_file.unlink()            temp_file.unlink()

            print("✅ FAISS index downloaded and extracted successfully") print("✅ FAISS index downloaded and extracted successfully")

            return True return True

        except Exception as e:
            except Exception as e:

            print(f"❌ Error downloading index: {e}") print(f"❌ Error downloading index: {e}")

            return False return False

    def check_for_updates(self) -> bool: def check_for_updates(self) -> bool:
        """        """

        Check if a newer index is available        Check if a newer index is available

        Returns:        Returns:

            True if update available, False otherwise            True if update available, False otherwise

        """        """

        _, latest_tag = self.get_latest_release_url()        _, latest_tag = self.get_latest_release_url()

        if not latest_tag:
            if not latest_tag:

            return False return False

        # Check local tag        # Check local tag

        local_tag_file = self.local_path / "release_tag.txt"        local_tag_file = self.local_path / "release_tag.txt"

        if not local_tag_file.exists():
            if not local_tag_file.exists():

            return True return True

        local_tag = local_tag_file.read_text().strip()        local_tag = local_tag_file.read_text().strip()

        return latest_tag != local_tag return latest_tag != local_tag

    def save_release_tag(self, tag: str): def save_release_tag(self, tag: str):
        """Save the current release tag locally"""        """Save the current release tag locally"""

        tag_file = self.local_path / "release_tag.txt"        tag_file = self.local_path / "release_tag.txt"

        tag_file.write_text(tag)        tag_file.write_text(tag)

    def get_index_info(self) -> dict: def get_index_info(self) -> dict:
        """Get information about the current index"""        """Get information about the current index"""

        info = {info = {

            "exists": self.local_path.exists(),            "exists": self.local_path.exists(),

            "path": str(self.local_path),            "path": str(self.local_path),

        }}

        if self.local_path.exists():
            if self.local_path.exists():

            last_updated_file = self.local_path / "last_updated.txt"            last_updated_file = self.local_path / "last_updated.txt"

            if last_updated_file.exists():
                if last_updated_file.exists():

                info["last_updated"] = last_updated_file.read_text().strip()                info["last_updated"] = last_updated_file.read_text().strip()

            tag_file = self.local_path / "release_tag.txt"            tag_file = self.local_path / "release_tag.txt"

            if tag_file.exists():
                if tag_file.exists():

                info["release_tag"] = tag_file.read_text().strip()                info["release_tag"] = tag_file.read_text().strip()

            # Get file sizes            # Get file sizes

            index_file = self.local_path / "index.faiss"            index_file = self.local_path / "index.faiss"

            pkl_file = self.local_path / "index.pkl"            pkl_file = self.local_path / "index.pkl"

            if index_file.exists():
                if index_file.exists():

                info["index_size_mb"] = index_file.stat().st_size / 1024 / 1024                info["index_size_mb"] = index_file.stat().st_size / 1024 / 1024

            if pkl_file.exists():
                if pkl_file.exists():

                info["pkl_size_mb"] = pkl_file.stat().st_size / 1024 / 1024                info["pkl_size_mb"] = pkl_file.stat().st_size / 1024 / 1024

        return info return info


def ensure_index_available() -> bool: def ensure_index_available() -> bool:
    """    """

    Ensure FAISS index is available locally    Ensure FAISS index is available locally

    Downloads from GitHub Releases if not present    Downloads from GitHub Releases if not present

    Returns:    Returns:

        True if index is available, False otherwise        True if index is available, False otherwise

    """    """

    storage = IndexStorage()    storage = IndexStorage()

    # Check if index exists locally    # Check if index exists locally

    if not storage.local_path.exists():
        if not storage.local_path.exists():

        print("FAISS index not found locally. Downloading from GitHub Releases...") print("FAISS index not found locally. Downloading from GitHub Releases...")

        return storage.download_index(force=True) return storage.download_index(force=True)

    print("✅ FAISS index found locally") print("✅ FAISS index found locally")

    return True return True
