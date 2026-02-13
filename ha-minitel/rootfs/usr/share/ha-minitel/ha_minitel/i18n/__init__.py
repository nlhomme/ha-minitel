"""Internationalization support."""

import json
import os
from typing import Any


class I18n:
    """Simple i18n with JSON locale files and dot-key lookup."""

    def __init__(self, language: str = "fr"):
        self._language = language
        self._strings: dict[str, Any] = {}
        self._load(language)

    def _load(self, language: str):
        locale_dir = os.path.join(os.path.dirname(__file__), "locales")
        path = os.path.join(locale_dir, f"{language}.json")
        if not os.path.exists(path):
            path = os.path.join(locale_dir, "fr.json")
        with open(path, "r", encoding="utf-8") as f:
            self._strings = json.load(f)

    def t(self, key: str, **kwargs) -> str:
        """Look up a translation by dot-notation key, with optional formatting."""
        parts = key.split(".")
        value: Any = self._strings
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return key  # fallback: return the key itself
        if isinstance(value, str):
            if kwargs:
                return value.format(**kwargs)
            return value
        return key
