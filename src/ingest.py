import os
import time
from git import Repo
from langchain_community.document_loaders import DirectoryLoader, TextLoader, GitHubIssuesLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import shutil
import re

load_dotenv()  # Load from .env file if it exists (for local development)

GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

# Check if required environment variable is set
if not GITHUB_TOKEN:
    raise ValueError(
        "GitHub access token not found. "
        "Set GITHUB_ACCESS_TOKEN environment variable or add to .env file"
    )

REPOSITORIES = {
    "pypsa": "https://github.com/PyPSA/pypsa.git",
    "pypsa-eur": "https://github.com/PyPSA/pypsa-eur.git",
    "pypsa-earth": "https://github.com/pypsa-meets-earth/pypsa-earth.git",
}

# Parent directory to store all cloned repositories
CLONE_DIR = "cloned_repos"
os.makedirs(CLONE_DIR, exist_ok=True)

# --- 2. Loop through repos, clone them, and load documents ---
all_documents = []

for name, url in REPOSITORIES.items():
    repo_path = os.path.join(CLONE_DIR, name)

    # Clone the repo if it doesn't exist
    if not os.path.exists(repo_path):
        print(f"Cloning {name} from {url} into {repo_path}...")
        Repo.clone_from(url, to_path=repo_path)
    else:
        print(f"Repository {name} already exists in {repo_path}.")

    # --- NEW: Define multiple loading targets for each repo (docs and code) ---
    targets_to_load = []
    if name == "pypsa":
        targets_to_load.append({'path': os.path.join(
            repo_path, "docs"), 'pattern': "**/*.md"})
        targets_to_load.append({'path': os.path.join(
            repo_path, "test"), 'pattern': "**/*.py"})
        targets_to_load.append({'path': os.path.join(
            repo_path, "pypsa"), 'pattern': "**/*.py"})
        targets_to_load.append({'path': repo_path, 'pattern': "**/*.y*ml"})
    elif name == "pypsa-eur":
        targets_to_load.append({'path': os.path.join(
            repo_path, "doc"), 'pattern': "**/*.rst"})
        targets_to_load.append({'path': os.path.join(
            repo_path, "scripts"), 'pattern': "**/*.py"})
        targets_to_load.append({'path': repo_path, 'pattern': "**/*.y*ml"})
    elif name == "pypsa-earth":
        targets_to_load.append({'path': os.path.join(
            repo_path, "doc"), 'pattern': "**/*.rst"})
        targets_to_load.append({'path': os.path.join(
            repo_path, "scripts"), 'pattern': "**/*.py"})
        targets_to_load.append({'path': repo_path, 'pattern': "**/*.y*ml"})

    # --- NEW: Loop through the defined targets and load documents ---
    for target in targets_to_load:
        docs_path = target['path']
        glob_pattern = target['pattern']

        if not os.path.exists(docs_path):
            print(
                f"Warning: Path '{docs_path}' not found for repo '{name}'. Skipping.")
            continue

        print(
            f"Loading files from '{docs_path}' with pattern '{glob_pattern}'...")
        loader = DirectoryLoader(
            docs_path,
            glob=glob_pattern,
            loader_cls=TextLoader,
            show_progress=True,
            use_multithreading=True,
        )
        documents = loader.load()
        print(f"Loaded {len(documents)} documents from this target.")
        all_documents.extend(documents)

        # --- Part B: Load GitHub Issues and Pull Requests via API ---
        print(f"\n--- Loading Issues and PRs for {name} ---")
        # Extract "owner/repo" from the git URL
        match = re.search(r"github\.com/([^/]+/[^/]+)\.git", url)
        if not match:
            print(
                f"Could not parse owner/repo from URL: {url}. Skipping issues.")
            continue

        repo_spec = match.group(1)
        print(f"Fetching from GitHub repository: {repo_spec}")

        try:
            issues_loader = GitHubIssuesLoader(
                repo=repo_spec,
                access_token=GITHUB_TOKEN,  # Now type-safe after validation
                include_prs=True,  # We want Pull Requests too
                state="all",
            )
            issue_docs = issues_loader.load()
            print(f"Loaded {len(issue_docs)} issues and PRs from {name}.")
            all_documents.extend(issue_docs)
        except Exception as e:
            print(f"Error fetching issues for {name}: {e}")


print(f"\nTotal documents loaded from all repositories: {len(all_documents)}")

# --- 3. Split documents using a code-aware splitter ---
print("Splitting all documents into chunks...")
# Using a text splitter that understands Python syntax is better for .py files
text_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=2000,  # Code can be dense, slightly larger chunks can help maintain context
    chunk_overlap=200
)
docs = text_splitter.split_documents(all_documents)
print(f"Split into {len(docs)} chunks.")

# --- 4. Create Embeddings and Store in FAISS ---
print("Creating embeddings with BAAI BGE Large model and building FAISS vector store...")
print("Using high-quality 1024-dimensional embeddings for better retrieval...")

# Using BAAI BGE Large model - runs locally, no API key needed
embeddings = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-large-en-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# Process documents in batches for progress tracking
batch_size = 100  # Process 100 documents at a time
total_batches = (len(docs) + batch_size - 1) // batch_size
print(
    f"Processing {len(docs)} chunks in {total_batches} batches of {batch_size}...")

# Create the first batch to initialize the vector store
first_batch = docs[:batch_size]
vector_store = FAISS.from_documents(first_batch, embeddings)
print(f"Batch 1/{total_batches} completed")

# Add remaining batches
for i in range(1, total_batches):
    start_idx = i * batch_size
    end_idx = min(start_idx + batch_size, len(docs))
    batch = docs[start_idx:end_idx]

    vector_store.add_documents(batch)
    print(
        f"Batch {i+1}/{total_batches} completed ({end_idx}/{len(docs)} chunks processed)")

print("All embeddings created successfully!")


# --- 5. Save the Vector Store Locally ---
vector_store_path = "pypsa_ecosystem_faiss_index"
if os.path.exists(vector_store_path):
    print(f"Removing old vector store at {vector_store_path}")
    shutil.rmtree(vector_store_path)

vector_store.save_local(vector_store_path)
print(
    f"Consolidated PyPSA ecosystem vector store saved locally at {vector_store_path}")
