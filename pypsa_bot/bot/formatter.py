"""Discord message formatting utilities."""

from pypsa_bot.rag.pipeline import RAGResult

LOW_CONFIDENCE_PREFIX = (
    "⚠️ **I'm not confident I have relevant information for this.** "
    "Here's my best attempt, but please verify against the docs directly.\n\n"
)

MAX_DISCORD_LENGTH = 2000


def format_response(result: RAGResult) -> str:
    """Format a RAGResult into a Discord-ready message.

    Adds confidence warning if retrieval quality is low.
    Appends source citations from retrieved documents.
    """
    parts = []

    # Confidence warning
    if not result.is_confident:
        parts.append(LOW_CONFIDENCE_PREFIX)

    # Main answer
    parts.append(result.answer)

    # Source citations
    sources = []
    seen_urls = set()
    for doc in result.documents:
        url = doc.metadata.get("url", "")
        if url and url not in seen_urls:
            lib = doc.metadata.get("library", "")
            title = doc.metadata.get("title", "")
            label = f"{lib}: {title}" if title else lib
            sources.append(f"- [{label}]({url})")
            seen_urls.add(url)

    if sources:
        parts.append("\n\n📚 **Sources:**")
        parts.extend(sources[:5])  # Limit to 5 sources

    return "\n".join(parts)


def chunk_message(text: str) -> list[str]:
    """Split a message into chunks that fit Discord's 2000-char limit.

    Tries to split at paragraph or line boundaries.
    """
    if len(text) <= MAX_DISCORD_LENGTH:
        return [text]

    chunks = []
    while text:
        if len(text) <= MAX_DISCORD_LENGTH:
            chunks.append(text)
            break

        # Try to break at a paragraph boundary
        split_at = text.rfind("\n\n", 0, MAX_DISCORD_LENGTH)
        if split_at == -1:
            split_at = text.rfind("\n", 0, MAX_DISCORD_LENGTH)
        if split_at == -1:
            split_at = MAX_DISCORD_LENGTH

        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()

    return chunks
