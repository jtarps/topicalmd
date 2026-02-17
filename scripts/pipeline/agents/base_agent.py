"""Shared LLM calling logic with multi-provider support (OpenAI, Anthropic, Google)."""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

from scripts.pipeline.config import (
    ANTHROPIC_API_KEY,
    GOOGLE_API_KEY,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    PROMPTS_DIR,
)

log = logging.getLogger(__name__)

# ── Lazy-initialized clients ────────────────────────────────────────────────
_openai_client = None
_anthropic_client = None
_google_genai = None


def _get_openai():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def _get_anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _anthropic_client


def _get_google():
    global _google_genai
    if _google_genai is None:
        from google import genai
        _google_genai = genai.Client(api_key=GOOGLE_API_KEY)
    return _google_genai


def _parse_provider_model(model_str: str) -> tuple:
    """Parse 'provider/model-name' into (provider, model_name).

    Falls back to ('openai', OPENAI_MODEL) if no provider prefix.
    """
    if "/" in model_str:
        provider, model_name = model_str.split("/", 1)
        return provider.lower(), model_name
    return "openai", model_str


def _has_key_for_provider(provider: str) -> bool:
    """Check if the API key is configured for a provider."""
    return {
        "openai": bool(OPENAI_API_KEY),
        "anthropic": bool(ANTHROPIC_API_KEY),
        "google": bool(GOOGLE_API_KEY),
    }.get(provider, False)


def _resolve_model(model_str: str) -> tuple:
    """Resolve model string to (provider, model_name), falling back to OpenAI if key missing."""
    provider, model_name = _parse_provider_model(model_str)
    if _has_key_for_provider(provider):
        return provider, model_name
    log.warning(
        "No API key for %s — falling back to openai/%s",
        provider, OPENAI_MODEL,
    )
    return "openai", OPENAI_MODEL


# ── Provider-specific call implementations ──────────────────────────────────

def _call_openai(
    model: str,
    system_prompt: str,
    user_prompt: str,
    json_mode: bool,
    temperature: float,
    max_tokens: Optional[int],
) -> Dict[str, Any]:
    client = _get_openai()
    kwargs: Dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    if max_tokens:
        kwargs["max_tokens"] = max_tokens

    resp = client.chat.completions.create(**kwargs)
    raw = resp.choices[0].message.content or ""
    usage = resp.usage
    return {
        "content": json.loads(raw) if json_mode else raw,
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
    }


def _call_anthropic(
    model: str,
    system_prompt: str,
    user_prompt: str,
    json_mode: bool,
    temperature: float,
    max_tokens: Optional[int],
) -> Dict[str, Any]:
    client = _get_anthropic()

    # For JSON mode, prepend instruction since Anthropic doesn't have a native JSON mode
    effective_system = system_prompt
    if json_mode:
        effective_system = system_prompt + "\n\nIMPORTANT: Return ONLY valid JSON with no markdown code fences, no explanation, no extra text."

    kwargs: Dict[str, Any] = {
        "model": model,
        "system": effective_system,
        "messages": [{"role": "user", "content": user_prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens or 4096,
    }

    resp = client.messages.create(**kwargs)
    raw = resp.content[0].text if resp.content else ""

    if json_mode:
        raw = _strip_code_fences(raw)

    return {
        "content": json.loads(raw) if json_mode else raw,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
    }


def _call_google(
    model: str,
    system_prompt: str,
    user_prompt: str,
    json_mode: bool,
    temperature: float,
    max_tokens: Optional[int],
) -> Dict[str, Any]:
    client = _get_google()
    from google.genai import types

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
    )
    if max_tokens:
        config.max_output_tokens = max_tokens
    if json_mode:
        config.response_mime_type = "application/json"

    resp = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=config,
    )
    raw = resp.text or ""
    if json_mode:
        raw = _strip_code_fences(raw)
    input_tokens = resp.usage_metadata.prompt_token_count if resp.usage_metadata else 0
    output_tokens = resp.usage_metadata.candidates_token_count if resp.usage_metadata else 0
    return {
        "content": json.loads(raw) if json_mode else raw,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def _strip_code_fences(text: str) -> str:
    """Strip markdown code fences (```json ... ```) that some models wrap around JSON."""
    stripped = text.strip()
    if stripped.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = stripped.index("\n") if "\n" in stripped else len(stripped)
        stripped = stripped[first_newline + 1:]
        # Remove closing fence
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3].rstrip()
    return stripped


_PROVIDER_DISPATCH = {
    "openai": _call_openai,
    "anthropic": _call_anthropic,
    "google": _call_google,
}


# ── Public API ──────────────────────────────────────────────────────────────

def load_prompt(filename: str) -> str:
    """Load a system prompt from the prompts/ directory."""
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8").strip()


def call_llm(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = False,
    temperature: Optional[float] = None,
    max_retries: int = 2,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Call an LLM with automatic provider routing, retries, and token tracking.

    Args:
        model: Provider/model string like "anthropic/claude-sonnet-4-5-20250929"
               or "google/gemini-2.0-flash". Defaults to openai/gpt-4o.

    Returns {"content": str | dict, "input_tokens": int, "output_tokens": int}.
    In json_mode the content value is a parsed dict.
    """
    if model is None:
        model = f"openai/{OPENAI_MODEL}"

    provider, model_name = _resolve_model(model)
    call_fn = _PROVIDER_DISPATCH.get(provider)
    if not call_fn:
        raise RuntimeError(f"Unknown LLM provider: {provider}")

    temp = temperature if temperature is not None else OPENAI_TEMPERATURE

    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 2):
        try:
            result = call_fn(
                model=model_name,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_mode=json_mode,
                temperature=temp,
                max_tokens=max_tokens,
            )
            log.debug(
                "LLM call OK (%s/%s, attempt %d): %d in / %d out tokens",
                provider, model_name, attempt,
                result["input_tokens"], result["output_tokens"],
            )
            return result

        except json.JSONDecodeError as e:
            log.warning("JSON parse failed (%s, attempt %d): %s", provider, attempt, e)
            last_error = e
        except Exception as e:
            log.warning("LLM call failed (%s, attempt %d): %s", provider, attempt, e)
            last_error = e

        if attempt <= max_retries:
            time.sleep(2 ** attempt)

    raise RuntimeError(f"LLM call failed after {max_retries + 1} attempts ({provider}/{model_name}): {last_error}")
