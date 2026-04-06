"""Discord bot client with RAG integration."""

import asyncio
import discord

from pypsa_bot.config import Config
from pypsa_bot.bot.formatter import format_response, chunk_message
from pypsa_bot.bot.rate_limiter import RateLimiter
from pypsa_bot.rag.pipeline import RAGPipeline
from pypsa_bot.utils.logging import logger


class PyPSABot:
    """Discord bot that answers PyPSA questions via RAG."""

    def __init__(self, config: Config):
        self._config = config

        intents = discord.Intents.default()
        intents.message_content = True
        self._client = discord.Client(intents=intents)
        self._rate_limiter = RateLimiter(config.groq_cooldown_seconds)
        self._pipeline: RAGPipeline | None = None  # Lazy init

        # Register event handlers
        self._client.event(self.on_ready)
        self._client.event(self.on_message)

    def _get_pipeline(self) -> RAGPipeline:
        """Lazily initialize the RAG pipeline (loads embedding model)."""
        if self._pipeline is None:
            self._pipeline = RAGPipeline(self._config)
        return self._pipeline

    async def on_ready(self):
        logger.info(f"{self._client.user} connected to Discord!")
        logger.info("Ready to answer PyPSA questions.")

    async def _summarize_thread(self, channel, before_message) -> str:
        """Summarize thread context if it exceeds 4 turns."""
        messages = []
        async for msg in channel.history(limit=10, before=before_message):
            messages.append(msg)
        messages.reverse()

        if len(messages) <= 4:
            # Short thread — use raw messages as context
            return "\n".join(
                f"{'Bot' if msg.author == self._client.user else 'User'}: {msg.content}"
                for msg in messages[-4:]
            )

        # Long thread — summarize
        summary_parts = []
        for msg in messages:
            role = "Bot" if msg.author == self._client.user else "User"
            summary_parts.append(f"{role}: {msg.content[:200]}")
        return "Previous conversation summary:\n" + "\n".join(summary_parts[-6:])

    async def on_message(self, message: discord.Message):
        if message.author == self._client.user:
            return
        if message.author.bot:
            return

        # Only respond to mentions
        if self._client.user and not self._client.user.mentioned_in(message):
            return

        async with message.channel.typing():
            # Extract question (strip mention)
            question = message.content
            if self._client.user:
                question = question.replace(f"<@{self._client.user.id}>", "").strip()
                question = question.replace(f"<@!{self._client.user.id}>", "").strip()

            if not question:
                await message.reply("Please ask me a question about PyPSA! 🔌")
                return

            # Add thread context if applicable
            thread_context = await self._summarize_thread(
                message.channel, message
            )
            if thread_context:
                full_query = f"{thread_context}\n\nLatest question: {question}"
            else:
                full_query = question

            # Rate-limited RAG query
            async with self._rate_limiter:
                try:
                    pipeline = self._get_pipeline()
                    result = await asyncio.to_thread(
                        pipeline.query, full_query
                    )
                except Exception as e:
                    logger.error(f"RAG pipeline error: {e}")
                    await message.reply(
                        "❌ I encountered an error processing your question. "
                        "Please try again in a moment."
                    )
                    return

            # Format and send response
            response_text = format_response(result)
            chunks = chunk_message(response_text)

            for chunk in chunks:
                await message.channel.send(chunk)

    def run(self):
        """Start the bot."""
        self._client.run(self._config.discord_token)


def start_bot(config: Config):
    """Entry point called from CLI."""
    bot = PyPSABot(config)
    bot.run()
