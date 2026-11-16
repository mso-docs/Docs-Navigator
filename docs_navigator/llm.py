"""Answer questions from retrieved passages with an open model on Hugging Face Inference Providers.

The visitor's own Hugging Face token pays for the call (their free monthly credits),
so the app owner never carries the bill. When no token is available the UI falls back to
plain retrieval, which needs no model at all.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .corpus import Hit

# Open models that Inference Providers lists as live. The first one that answers is used.
DEFAULT_MODELS = (
    "meta-llama/Llama-3.3-70B-Instruct",
    "openai/gpt-oss-120b",
    "Qwen/Qwen3.5-35B-A3B",
)

SYSTEM_PROMPT = (
    "You answer questions about a documentation set. Use only the numbered passages you are given. "
    "Cite passages as [1], [2] after the claims they support. If the passages do not contain the "
    "answer, say so plainly and suggest what to search for next. Keep answers short and concrete."
)


class LLMUnavailable(RuntimeError):
    """Raised with a message that is safe to show to the visitor."""


@dataclass
class Answer:
    text: str
    model: str


def configured_models() -> list[str]:
    override = os.getenv("DOCSNAV_MODEL", "").strip()
    return [m.strip() for m in override.split(",") if m.strip()] if override else list(DEFAULT_MODELS)


def build_messages(question: str, hits: list[Hit]) -> list[dict]:
    context = "\n\n".join(
        f"[{i}] {h.doc}" + (f" > {h.heading}" if h.heading else "") + f"\n{h.text}" for i, h in enumerate(hits, 1)
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Passages:\n\n{context}\n\nQuestion: {question}"},
    ]


def _client(token: str):
    from huggingface_hub import InferenceClient

    base = os.getenv("DOCSNAV_BASE_URL", "").strip()  # optional OpenAI-compatible endpoint, used in tests
    if base:
        return InferenceClient(base_url=base, api_key=token)
    return InferenceClient(provider="auto", api_key=token)


def _explain(exc: Exception) -> str:
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status in (401, 403):
        return (
            "Your Hugging Face session does not allow Inference Providers calls. "
            "Sign in again and accept the inference permission."
        )
    if status in (402, 429):
        return "You have used your free Hugging Face inference credits for this month. Search still works without them."
    return f"The model service did not answer ({exc.__class__.__name__})."


def answer_question(question: str, hits: list[Hit], token: str, models: list[str] | None = None, max_tokens: int = 700) -> Answer:
    if not token:
        raise LLMUnavailable("Sign in with Hugging Face to turn passages into an answer.")
    if not hits:
        raise LLMUnavailable("No passages matched that question, so there is nothing to answer from.")
    client = _client(token)
    last: Exception | None = None
    for model in models or configured_models():
        try:
            response = client.chat_completion(
                model=model,
                messages=build_messages(question, hits),
                max_tokens=max_tokens,
                temperature=0.2,
            )
            text = (response.choices[0].message.content or "").strip()
            if text:
                return Answer(text=text, model=model)
        except Exception as exc:  # try the next model; remember why this one failed
            last = exc
            if getattr(getattr(exc, "response", None), "status_code", None) in (401, 402, 403, 429):
                break
    raise LLMUnavailable(_explain(last) if last else "The model returned an empty answer.")
