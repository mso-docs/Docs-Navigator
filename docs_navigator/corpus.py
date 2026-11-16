"""Load a folder of documents, split it into passages, and rank them with BM25.

No network and no API key are needed for anything in this module. It is the
retrieval layer behind both the web UI and the MCP tools.
"""

from __future__ import annotations

import html
import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

TEXT_SUFFIXES = {".md", ".txt", ".rst"}
SPREADSHEET_SUFFIXES = {".xlsx"}
PDF_SUFFIXES = {".pdf"}
SUPPORTED_SUFFIXES = TEXT_SUFFIXES | SPREADSHEET_SUFFIXES | PDF_SUFFIXES

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_.\-]*[a-z0-9]|[a-z0-9]")
_STOPWORDS = frozenset(
    "a an and are as at be by for from has have how i in is it its of on or that the "
    "this to was what when where which who why with you your do does can".split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens. Keeps dotted and hyphenated terms such as `api.base_url`."""
    tokens = []
    for raw in _TOKEN_RE.findall(text.lower()):
        tokens.append(raw)
        # Also index the pieces of compound terms so "base_url" matches "base" and "url".
        if any(ch in raw for ch in "._-"):
            tokens.extend(p for p in re.split(r"[._\-]+", raw) if p)
    return [t for t in tokens if t not in _STOPWORDS]


@dataclass
class Passage:
    doc: str
    index: int
    text: str
    heading: str = ""
    tokens: Counter = field(default_factory=Counter, repr=False)
    length: int = 0


@dataclass
class Hit:
    doc: str
    heading: str
    score: float
    text: str
    snippet: str

    def as_dict(self) -> dict:
        return {
            "file": self.doc,
            "section": self.heading,
            "score": round(self.score, 3),
            "text": self.text,
        }


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # a damaged page should not hide the others
            text = f"[page {number} could not be read: {exc.__class__.__name__}]"
        if not text.strip():
            text = _ocr_pdf_page(path, number)
        text = _tidy_pdf_text(text)
        if text:
            pages.append(f"## Page {number}\n\n{text}")
    return "\n\n".join(pages)


def _tidy_pdf_text(text: str) -> str:
    """Some PDF exports put every word on its own line. Re-join lines, keeping bullets apart."""
    flat = re.sub(r"\s*\n\s*", " ", text).strip()
    flat = re.sub(r"\s*([●○•▪■◦])\s*", r"\n\1 ", flat)
    return flat.strip()


def _ocr_pdf_page(path: Path, number: int) -> str:
    """Optional OCR for scanned pages. Returns "" when the OCR extras are not installed."""
    try:
        import pytesseract
        from pdf2image import convert_from_path

        images = convert_from_path(str(path), first_page=number, last_page=number)
        return pytesseract.image_to_string(images[0]) if images else ""
    except Exception:
        return ""


def _read_xlsx(path: Path) -> str:
    from openpyxl import load_workbook

    workbook = load_workbook(str(path), read_only=True, data_only=True)
    parts = []
    for sheet in workbook.worksheets:
        rows = []
        for row in sheet.iter_rows(values_only=True):
            cells = [str(c) for c in row if c is not None and str(c).strip()]
            if cells:
                rows.append(" | ".join(cells))
        if rows:
            parts.append(f"## Sheet: {sheet.title}\n\n" + "\n".join(rows))
    workbook.close()
    return "\n\n".join(parts)


def read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in PDF_SUFFIXES:
        return _read_pdf(path)
    if suffix in SPREADSHEET_SUFFIXES:
        return _read_xlsx(path)
    return path.read_text(encoding="utf-8", errors="replace")


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def _break_long(block: str, max_chars: int) -> list[str]:
    """Split a block that is longer than max_chars at sentence ends, then at spaces."""
    if len(block) <= max_chars * 1.5:
        return [block]
    pieces, current = [], ""
    for sentence in re.split(r"(?<=[.!?])\s+|\n", block):
        while len(sentence) > max_chars:
            cut = sentence.rfind(" ", 0, max_chars) or max_chars
            pieces.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if current and len(current) + len(sentence) + 1 > max_chars:
            pieces.append(current)
            current = ""
        current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return [p for p in pieces if p]


def split_passages(doc: str, text: str, max_chars: int = 900) -> list[Passage]:
    """Split on headings first, then on paragraphs, so a passage stays on one topic."""
    passages: list[Passage] = []
    heading = ""
    buffer: list[str] = []
    size = 0

    def flush() -> None:
        nonlocal buffer, size
        body = "\n\n".join(buffer).strip()
        if body:
            passages.append(Passage(doc=doc, index=len(passages), text=body, heading=heading))
        buffer, size = [], 0

    in_fence = False
    for block in re.split(r"\n\s*\n", text):
        stripped = block.strip()
        if not stripped:
            continue
        if stripped.count("```") % 2 == 1:
            in_fence = not in_fence
        first_line = stripped.splitlines()[0]
        match = None if in_fence else _HEADING_RE.match(first_line)
        if match:
            flush()
            heading = match.group(2).strip("# ").strip()
        for piece in _break_long(stripped, max_chars):
            if size + len(piece) > max_chars and buffer:
                flush()
            buffer.append(piece)
            size += len(piece)
    flush()
    return passages


class Corpus:
    """An in-memory BM25 index over every supported file under `root`."""

    def __init__(self, root: str | os.PathLike, k1: float = 1.5, b: float = 0.75):
        self.root = Path(root).resolve()
        self.k1, self.b = k1, b
        self.passages: list[Passage] = []
        self.files: dict[str, dict] = {}
        self._df: Counter = Counter()
        self._avg_len = 0.0
        self._signature: tuple | None = None
        self.refresh()

    # ----- indexing -----
    def _scan(self) -> list[Path]:
        if not self.root.is_dir():
            return []
        found = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue
            if path.suffix.lower() in SUPPORTED_SUFFIXES:
                found.append(path)
        return found

    def refresh(self) -> bool:
        """Re-read the folder if any file was added, removed, or changed."""
        paths = self._scan()
        signature = tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths)
        if signature == self._signature:
            return False
        self._signature = signature
        self.passages, self.files = [], {}
        for path in paths:
            rel = path.relative_to(self.root).as_posix()
            try:
                text = read_file(path)
            except Exception as exc:
                self.files[rel] = {"chars": 0, "passages": 0, "error": exc.__class__.__name__}
                continue
            chunks = split_passages(rel, text)
            for p in chunks:
                p.tokens = Counter(tokenize(f"{p.heading} {p.text}"))
                p.length = sum(p.tokens.values())
            self.files[rel] = {"chars": len(text), "passages": len(chunks), "type": path.suffix.lower().lstrip(".")}
            self.passages.extend(chunks)
        self._df = Counter()
        for p in self.passages:
            self._df.update(p.tokens.keys())
        total = sum(p.length for p in self.passages)
        self._avg_len = total / len(self.passages) if self.passages else 0.0
        return True

    # ----- queries -----
    def stats(self) -> dict:
        return {
            "root": str(self.root),
            "documents": len(self.files),
            "passages": len(self.passages),
            "characters": sum(f["chars"] for f in self.files.values()),
        }

    def list_docs(self) -> list[dict]:
        return [{"file": name, **info} for name, info in self.files.items()]

    def read(self, name: str) -> str:
        """Return the full text of one file. Only files inside the docs folder can be read."""
        self.refresh()
        target = (self.root / name).resolve()
        if self.root not in target.parents or not target.is_file():
            raise FileNotFoundError(f"No document named '{name}'. Use list_docs to see what is available.")
        if target.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(f"Unsupported file type: {target.suffix}")
        return read_file(target)

    def search(self, query: str, limit: int = 5, doc: str | None = None) -> list[Hit]:
        self.refresh()
        terms = [t for t in tokenize(query) if t in self._df]
        if not terms or not self.passages:
            return []
        n = len(self.passages)
        scored: list[tuple[float, Passage]] = []
        for p in self.passages:
            if doc and p.doc != doc:
                continue
            score = 0.0
            for t in set(terms):
                tf = p.tokens.get(t, 0)
                if not tf:
                    continue
                idf = math.log(1 + (n - self._df[t] + 0.5) / (self._df[t] + 0.5))
                denom = tf + self.k1 * (1 - self.b + self.b * p.length / (self._avg_len or 1))
                score += idf * tf * (self.k1 + 1) / denom
            # A match in the heading is a strong signal.
            heading_tokens = set(tokenize(p.heading))
            score += 0.5 * len(heading_tokens.intersection(terms))
            if score > 0:
                scored.append((score, p))
        scored.sort(key=lambda sp: sp[0], reverse=True)
        hits = []
        for score, p in scored[: max(1, limit)]:
            hits.append(Hit(p.doc, p.heading, score, p.text, make_snippet(p.text, terms)))
        return hits


def make_snippet(text: str, terms: list[str], width: int = 320) -> str:
    """A short excerpt around the first match, HTML-escaped, with matches in <mark>."""
    flat = re.sub(r"\s+", " ", text).strip()
    lowered = flat.lower()
    positions = [lowered.find(t) for t in terms if lowered.find(t) >= 0]
    start = max(0, (min(positions) if positions else 0) - 60)
    excerpt = flat[start : start + width]
    prefix = "…" if start > 0 else ""
    suffix = "…" if start + width < len(flat) else ""
    escaped = html.escape(excerpt)
    wanted = sorted({html.escape(t) for t in terms}, key=len, reverse=True)
    if wanted:
        pattern = re.compile("(" + "|".join(re.escape(t) for t in wanted) + ")", re.IGNORECASE)
        escaped = pattern.sub(r"<mark>\1</mark>", escaped)
    return f"{prefix}{escaped}{suffix}"
