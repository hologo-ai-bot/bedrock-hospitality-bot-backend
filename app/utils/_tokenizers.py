from __future__ import annotations

from typing import TYPE_CHECKING, cast
from pathlib import Path
from anyio import Path as AsyncPath

# tokenizers is untyped, https://github.com/huggingface/tokenizers/issues/811
# note: this comment affects the entire file
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
if TYPE_CHECKING:
    # We only import this at the type-level as deferring the import
    # avoids issues like this: https://github.com/anthropics/anthropic-sdk-python/issues/280
    from tokenizers import Tokenizer as TokenizerType  # type: ignore[import]
else:
    TokenizerType = None


class TokenizerManager:
    """A class to manage loading and accessing a tokenizer from a cached JSON file."""

    _tokenizer: TokenizerType | None = None

    def __init__(self, cache_path: Path | None = None):
        """Initialize the TokenizerManager with an optional custom cache path."""
        self.cache_path = cache_path or self._get_default_cache_path()

    @staticmethod
    def _get_default_cache_path() -> Path:
        """Return the default cache path for the tokenizer JSON."""
        return Path(__file__).parent / "tokenizer.json"

    def _load_tokenizer(self, raw: str) -> TokenizerType:
        """Load the tokenizer from a raw JSON string."""
        global _tokenizer

        from tokenizers import Tokenizer

        _tokenizer = cast(TokenizerType, Tokenizer.from_str(raw))
        return _tokenizer

    def sync_get_tokenizer(self) -> TokenizerType:
        """Synchronously get the tokenizer instance, loading it if necessary."""
        if self._tokenizer is not None:
            return self._tokenizer

        tokenizer_path = self.cache_path
        text = tokenizer_path.read_text(encoding="utf-8")
        return self._load_tokenizer(text)

    async def async_get_tokenizer(self) -> TokenizerType:
        """Asynchronously get the tokenizer instance, loading it if necessary."""
        if self._tokenizer is not None:
            return self._tokenizer

        tokenizer_path = AsyncPath(self.cache_path)
        text = await tokenizer_path.read_text(encoding="utf-8")
        return self._load_tokenizer(text)
