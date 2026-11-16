from pathlib import Path

import pytest

from docs_navigator.corpus import Corpus, make_snippet, split_passages, tokenize

DOCS = Path(__file__).resolve().parent.parent / "docs"


@pytest.fixture(scope="module")
def corpus():
    return Corpus(DOCS)


def test_indexes_sample_docs(corpus):
    stats = corpus.stats()
    assert stats["documents"] >= 10
    assert stats["passages"] > 100


def test_search_finds_relevant_file(corpus):
    hits = corpus.search("how do I deploy", limit=5)
    assert hits and any("eploy" in h.doc or "eploy" in h.text for h in hits)
    assert hits == sorted(hits, key=lambda h: h.score, reverse=True)


def test_search_filters_by_file(corpus):
    hits = corpus.search("api", limit=5, doc="text/configuration.md")
    assert hits and all(h.doc == "text/configuration.md" for h in hits)


def test_unknown_terms_return_nothing(corpus):
    assert corpus.search("zzzqqqxxx") == []


def test_read_blocks_path_traversal(corpus):
    with pytest.raises(FileNotFoundError):
        corpus.read("../app.py")
    with pytest.raises(FileNotFoundError):
        corpus.read("/etc/passwd")


def test_reindexes_when_files_change(tmp_path):
    (tmp_path / "a.md").write_text("# Alpha\n\nThe flux capacitor needs 1.21 gigawatts.")
    c = Corpus(tmp_path)
    assert c.search("flux capacitor")
    (tmp_path / "b.md").write_text("# Beta\n\nThe zebra crossing is on Main Street.")
    assert c.search("zebra")


def test_long_blocks_are_split():
    text = "Sentence number one. " * 400
    assert all(len(p.text) < 1800 for p in split_passages("x.md", text))


def test_snippet_escapes_html_and_marks_terms():
    out = make_snippet("<script>alert(1)</script> mark the rate limit", tokenize("rate limit mark"))
    assert "<script>" not in out and "&lt;script&gt;" in out
    assert out.count("<mark>") >= 2


def test_compound_terms_match_pieces():
    assert {"base_url", "base", "url"} <= set(tokenize("api.base_url") + tokenize("base_url"))
