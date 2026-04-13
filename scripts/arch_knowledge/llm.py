"""
llm.py - LLM provider abstraction for arch-knowledge.

Supports:
- anthropic  (via the anthropic SDK)
- openai     (via the openai SDK, also covers Azure OpenAI)
- ollama     (via openai SDK pointed at the local Ollama endpoint)

Usage:
    from arch_knowledge.llm import call_llm
    from arch_knowledge.config import find_knowledge_root, get_llm_config

    root = find_knowledge_root()
    cfg  = get_llm_config(root)
    response = call_llm("Summarise this page.", system="You are an architecture assistant.", config=cfg)
    print(response)
"""

from __future__ import annotations

import os
from typing import Any


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def call_llm(
    prompt: str,
    *,
    system: str = "",
    config: dict[str, Any] | None = None,
    max_tokens: int = 4096,
) -> str:
    """
    Send *prompt* to the configured LLM and return the text response.

    Args:
        prompt:     The user message to send.
        system:     Optional system prompt.
        config:     LLM config dict (from get_llm_config()).  If None, a
                    minimal default config is used (anthropic provider,
                    claude-3-5-haiku-20241022 model).
        max_tokens: Maximum tokens for the response.

    Returns:
        The model's response as a plain string.

    Raises:
        ValueError:  If the provider is unknown.
        RuntimeError: If the API call fails.
    """
    cfg = config or {}
    provider = cfg.get("provider", "anthropic").lower()

    if provider == "anthropic":
        return _call_anthropic(prompt, system=system, config=cfg, max_tokens=max_tokens)
    elif provider in ("openai", "azure"):
        return _call_openai(prompt, system=system, config=cfg, max_tokens=max_tokens)
    elif provider == "ollama":
        return _call_ollama(prompt, system=system, config=cfg, max_tokens=max_tokens)
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider!r}. "
            "Supported providers: anthropic, openai, azure, ollama."
        )


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------


def _call_anthropic(
    prompt: str,
    *,
    system: str,
    config: dict[str, Any],
    max_tokens: int,
) -> str:
    """Call the Anthropic Messages API."""
    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError(
            "The 'anthropic' package is required for the anthropic provider. "
            "Install it with: pip install anthropic"
        ) from exc

    api_key = config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
    model = config.get("model", "claude-3-5-haiku-20241022")

    client_kwargs: dict[str, Any] = {}
    if api_key:
        client_kwargs["api_key"] = api_key

    client = anthropic.Anthropic(**client_kwargs)

    messages = [{"role": "user", "content": prompt}]
    create_kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        create_kwargs["system"] = system

    try:
        response = client.messages.create(**create_kwargs)
        # response.content is a list of ContentBlock objects
        parts = [block.text for block in response.content if hasattr(block, "text")]
        return "\n".join(parts)
    except Exception as exc:
        raise RuntimeError(f"Anthropic API call failed: {exc}") from exc


def _call_openai(
    prompt: str,
    *,
    system: str,
    config: dict[str, Any],
    max_tokens: int,
) -> str:
    """Call an OpenAI-compatible Chat Completions API."""
    try:
        import openai
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is required for the openai provider. "
            "Install it with: pip install openai"
        ) from exc

    api_key = config.get("api_key") or os.environ.get("OPENAI_API_KEY")
    model = config.get("model", "gpt-4o-mini")
    base_url = config.get("base_url")

    client_kwargs: dict[str, Any] = {}
    if api_key:
        client_kwargs["api_key"] = api_key
    if base_url:
        client_kwargs["base_url"] = base_url

    client = openai.OpenAI(**client_kwargs)

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore[arg-type]
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        raise RuntimeError(f"OpenAI API call failed: {exc}") from exc


def _call_ollama(
    prompt: str,
    *,
    system: str,
    config: dict[str, Any],
    max_tokens: int,
) -> str:
    """
    Call a local Ollama instance via its OpenAI-compatible endpoint.

    Defaults to http://localhost:11434/v1 if no base_url is configured.
    """
    ollama_config = dict(config)
    if not ollama_config.get("base_url"):
        ollama_config["base_url"] = "http://localhost:11434/v1"
    # Ollama doesn't validate API keys but openai SDK requires a non-empty value
    if not ollama_config.get("api_key"):
        ollama_config["api_key"] = "ollama"

    return _call_openai(prompt, system=system, config=ollama_config, max_tokens=max_tokens)
