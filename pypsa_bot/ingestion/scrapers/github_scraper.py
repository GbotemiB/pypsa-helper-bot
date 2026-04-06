"""GitHub issues scraper with quality filtering."""

from __future__ import annotations

from github import Github, GithubException

from pypsa_bot.config import Config
from pypsa_bot.ingestion.metadata import ChunkMetadata
from pypsa_bot.ingestion.scrapers.docs_scraper import ScrapedDocument
from pypsa_bot.utils.logging import logger

SKIP_LABELS = {"duplicate", "wontfix", "invalid", "stale"}

# GitHub usernames that are bots (extend as needed)
BOT_SUFFIXES = {"[bot]", "-bot"}


def _is_bot(login: str) -> bool:
    """Return True if the GitHub login looks like a bot account."""
    lower = login.lower()
    return lower.endswith("[bot]") or lower.endswith("-bot") or "bot" in lower.split("-")


def is_quality_issue(issue) -> bool:
    """Return True if the issue meets the quality bar for indexing.

    Criteria:
    - Not authored by a bot
    - Does not carry skip labels (duplicate, wontfix, invalid, stale)
    - Has at least 1 human comment
    """
    # Skip bots
    if issue.user and _is_bot(issue.user.login):
        return False

    # Skip issues with disqualifying labels
    issue_labels = {lbl.name.lower() for lbl in issue.labels}
    if issue_labels & SKIP_LABELS:
        return False

    # Require at least 1 comment
    if issue.comments < 1:
        return False

    return True


def format_issue_text(issue) -> str:
    """Build the full text for an issue, including body and human comments."""
    parts: list[str] = []

    title = issue.title or ""
    parts.append(f"# {title}")

    if issue.body:
        parts.append(issue.body)

    try:
        for comment in issue.get_comments():
            if comment.user and _is_bot(comment.user.login):
                continue
            if comment.body:
                parts.append(f"---\n**Comment by {comment.user.login}:**\n{comment.body}")
    except GithubException as exc:
        logger.warning("Could not fetch comments for issue #%d: %s", issue.number, exc)

    return "\n\n".join(parts)


def _count_reactions(issue) -> int:
    """Return total reaction count for an issue."""
    try:
        return issue.reactions.get("total_count", 0)
    except Exception:
        return 0


def scrape_github_issues(
    config: Config, target_repo: str | None = None
) -> list[ScrapedDocument]:
    """Fetch GitHub issues from the configured repos and apply quality filtering.

    Args:
        config: Application configuration (provides github_token and target_repos).
        target_repo: If set, only fetch issues for that library key (e.g. "pypsa").

    Returns:
        List of ScrapedDocument instances for each qualifying issue.
    """
    gh = Github(config.github_token) if config.github_token else Github()
    documents: list[ScrapedDocument] = []

    repos_to_scrape = (
        {target_repo: config.target_repos[target_repo]}
        if target_repo and target_repo in config.target_repos
        else config.target_repos
    )

    for library, repo_info in repos_to_scrape.items():
        repo_slug = repo_info["github"]
        logger.info("Fetching issues from %s (%s)", repo_slug, library)

        try:
            gh_repo = gh.get_repo(repo_slug)
        except GithubException as exc:
            logger.error("Could not access repo %s: %s", repo_slug, exc)
            continue

        count = 0
        try:
            for issue in gh_repo.get_issues(state="all"):
                # Skip pull requests (GitHub returns PRs via issues API)
                if issue.pull_request is not None:
                    continue

                if not is_quality_issue(issue):
                    continue

                text = format_issue_text(issue)
                reactions = _count_reactions(issue)

                metadata = ChunkMetadata(
                    source="github_issue",
                    library=library,  # type: ignore[arg-type]
                    content_type="text",
                    url=issue.html_url,
                    title=issue.title or "",
                    reactions=reactions,
                    issue_number=issue.number,
                )
                documents.append(ScrapedDocument(content=text, metadata=metadata))
                count += 1

        except GithubException as exc:
            logger.error("Error fetching issues from %s: %s", repo_slug, exc)

        logger.info("Fetched %d qualifying issues from %s", count, repo_slug)

    gh.close()
    return documents
