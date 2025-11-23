# server_docs.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from document_intelligence import DocumentIntelligence

# Import PDF processing library
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: PyPDF2 not installed. PDF support disabled.")

# Import OCR processing capabilities
try:
    from ocr_processor import extract_text_with_ocr, is_ocr_available, get_ocr_status
    OCR_SUPPORT = is_ocr_available()
    if OCR_SUPPORT:
        print("OCR support enabled for image-based PDFs and images")
    else:
        print("OCR libraries available but Tesseract not found")
except ImportError:
    OCR_SUPPORT = False
    print("Warning: OCR dependencies not installed. Image-based PDF processing disabled.")

# Name your server – this is what clients see
mcp = FastMCP("DocsNavigator")

DOCS_ROOT = Path(__file__).parent.parent.parent / "docs"
doc_intel = DocumentIntelligence(DOCS_ROOT)


def _iter_docs() -> list[Path]:
    exts = {".md", ".txt", ".rst"}
    if PDF_SUPPORT:
        exts.add(".pdf")
    
    # Add image formats if OCR is available
    if OCR_SUPPORT:
        image_exts = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif"}
        exts.update(image_exts)
    
    return [
        p for p in DOCS_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in exts
    ]


def _read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    
    if suffix == ".pdf":
        return _read_pdf_file(path)
    elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif"}:
        return _read_image_file(path)
    else:
        return path.read_text(encoding="utf-8", errors="ignore")


def _read_image_file(path: Path) -> str:
    """Extract text from image file using OCR."""
    if not OCR_SUPPORT:
        return f"OCR support not available for image {path.name}. Install OCR dependencies."
    
    try:
        result = extract_text_with_ocr(path)
        
        if result["success"]:
            confidence = result.get("confidence", 0)
            method = result.get("method", "OCR")
            
            extracted_text = f"--- Image: {path.name} (OCR, Confidence: {confidence:.1%}, Method: {method}) ---\n"
            extracted_text += result["text"]
            
            return extracted_text
        else:
            error_msg = result.get("error", "Unknown error")
            return f"--- Image: {path.name} (OCR Failed: {error_msg}) ---"
            
    except Exception as e:
        return f"Error processing image {path.name}: {str(e)}"


def _read_pdf_file(path: Path) -> str:
    """Extract text from PDF file with OCR fallback."""
    if not PDF_SUPPORT:
        return f"PDF support not available. Install PyPDF2 to read {path.name}"
    
    # If OCR is available, use hybrid approach
    if OCR_SUPPORT:
        try:
            result = extract_text_with_ocr(path)
            
            if result["success"]:
                confidence = result.get("confidence", 0)
                method = result.get("method", "unknown")
                pages_info = ""
                
                if "pages_processed" in result:
                    pages_successful = result.get("pages_successful", 0)
                    pages_total = result["pages_processed"]
                    pages_info = f", Pages: {pages_successful}/{pages_total}"
                
                header = f"--- PDF: {path.name} (Method: {method}, Confidence: {confidence:.1%}{pages_info}) ---\n"
                return header + result["text"]
            else:
                error_msg = result.get("error", "Unknown error")
                return f"--- PDF: {path.name} (Processing Failed: {error_msg}) ---"
                
        except Exception as e:
            # Fallback to basic text extraction on OCR error
            pass
    
    # Basic text extraction (original method)
    try:
        text = ""
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                except Exception as e:
                    text += f"\n--- Page {page_num + 1} (Error reading: {str(e)}) ---\n"
        
        if text.strip():
            return f"--- PDF: {path.name} (Method: text_extraction) ---\n{text}"
        else:
            if OCR_SUPPORT:
                return f"--- PDF: {path.name} (No text extracted, OCR also failed) ---"
            else:
                return f"--- PDF: {path.name} (No text extracted, OCR not available) ---"
                    
    except Exception as e:
        return f"Error reading PDF {path.name}: {str(e)}"


def _extract_hierarchical_sections(content: str) -> List[Dict[str, str]]:
    """Extract sections including their subsections for better content access."""
    lines = content.split('\n')
    headers = []
    
    # Identify all headers
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#'):
            level = len(stripped) - len(stripped.lstrip('#'))
            title = stripped.lstrip('#').strip()
            headers.append({
                'title': stripped,
                'clean_title': title,
                'level': level,
                'line_index': i
            })
    
    if not headers:
        return [{'title': 'Document Content', 'content': content.strip()}]
    
    hierarchical_sections = []
    
    # Extract content for each header including subsections
    for i, header in enumerate(headers):
        start_line = header['line_index']
        
        # Find content that belongs to this section (including subsections)
        end_line = len(lines)
        for j in range(i + 1, len(headers)):
            next_header = headers[j]
            # Only stop at headers of the same or higher level (lower number)
            if next_header['level'] <= header['level']:
                end_line = next_header['line_index']
                break
        
        # Extract all content for this section (header + content + subsections)
        section_lines = lines[start_line:end_line]
        section_content = '\n'.join(section_lines).strip()
        
        # Remove the header line itself from content for cleaner output
        if section_content.startswith('#'):
            content_lines = section_content.split('\n')[1:]
            clean_content = '\n'.join(content_lines).strip()
        else:
            clean_content = section_content
        
        hierarchical_sections.append({
            'title': header['title'],
            'content': clean_content,
            'level': header['level'],
            'includes_subsections': any(h['level'] > header['level'] for h in headers[i+1:] if h['line_index'] < end_line)
        })
    
    return hierarchical_sections


def _extract_sections(content: str) -> List[Dict[str, str]]:
    """Extract sections from markdown content based on headers with proper hierarchy."""
    lines = content.split('\n')
    headers = []
    
    # First pass: identify all headers with their positions
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#'):
            level = len(stripped) - len(stripped.lstrip('#'))
            title = stripped.lstrip('#').strip()
            headers.append({
                'title': stripped,
                'clean_title': title,
                'level': level,
                'line_index': i
            })
    
    if not headers:
        return [{'title': 'Document Content', 'content': content.strip()}]
    
    sections = []
    
    # Second pass: extract content for each header
    for i, header in enumerate(headers):
        start_line = header['line_index'] + 1
        
        # Find the end of this section (next header of same or higher level)
        end_line = len(lines)
        for j in range(i + 1, len(headers)):
            next_header = headers[j]
            if next_header['level'] <= header['level']:
                end_line = next_header['line_index']
                break
        
        # Extract content for this section
        section_lines = lines[start_line:end_line]
        section_content = '\n'.join(section_lines).strip()
        
        sections.append({
            'title': header['title'],
            'content': section_content,
            'level': header['level']
        })
    
    return sections


def _extract_headers(content: str) -> List[Dict[str, Any]]:
    """Extract header hierarchy from markdown content."""
    headers = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            level = len(stripped) - len(stripped.lstrip('#'))
            title = stripped.lstrip('#').strip()
            headers.append({
                'level': level,
                'title': title,
                'line': line_num
            })
    
    return headers


def _create_outline(headers: List[Dict[str, Any]]) -> List[str]:
    """Create a hierarchical outline from headers."""
    outline = []
    for header in headers:
        indent = "  " * (header['level'] - 1)
        outline.append(f"{indent}- {header['title']}")
    return outline


def _count_code_blocks(content: str) -> int:
    """Count code blocks in markdown content."""
    return content.count('```')


def _extract_links(content: str) -> List[str]:
    """Extract links from markdown content."""
    import re
    # Match markdown links [text](url) and bare URLs
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)|https?://[^\s\])]+'
    matches = re.findall(link_pattern, content)
    links = []
    for match in matches:
        if isinstance(match, tuple) and match[1]:
            links.append(match[1])  # URL from [text](url)
        elif isinstance(match, str):
            links.append(match)  # Bare URL
    return links


def _generate_overview_summary(content: str, sections: List[Dict[str, str]]) -> str:
    """Generate a concise overview summary."""
    if not sections:
        # If no sections, summarize the whole content
        words = content.split()[:100]  # First 100 words
        return ' '.join(words) + "..." if len(content.split()) > 100 else ' '.join(words)
    
    summary_parts = []
    
    # Process all meaningful sections (skip empty ones)
    for section in sections:
        title = section['title'].lstrip('#').strip()
        section_content = section['content'].strip()
        
        # Skip empty sections
        if not section_content:
            continue
            
        # For overview, take first 50 words of each section
        content_words = section_content.split()[:50]
        section_summary = ' '.join(content_words)
        if len(section['content'].split()) > 50:
            section_summary += "..."
            
        summary_parts.append(f"**{title}**: {section_summary}")
        
        # Limit to 5 sections for overview to avoid too much text
        if len(summary_parts) >= 5:
            break
    
    # If we still have no content, fall back to first 100 words
    if not summary_parts:
        words = content.split()[:100]
        return ' '.join(words) + "..." if len(content.split()) > 100 else ' '.join(words)
    
    return '\n\n'.join(summary_parts)


def _extract_key_points(content: str, sections: List[Dict[str, str]]) -> str:
    """Extract key points from content."""
    key_points = []
    
    # Look for bullet points and numbered lists in sections
    for section in sections:
        section_content = section['content']
        lines = section_content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            if (stripped.startswith('- ') or 
                stripped.startswith('* ') or 
                stripped.startswith('+ ') or
                (stripped and len(stripped) > 0 and stripped[0].isdigit() and '. ' in stripped)):
                # Clean up the bullet point
                clean_point = stripped.lstrip('- *+0123456789. ').strip()
                if clean_point:
                    key_points.append(f"• {clean_point}")
    
    if key_points:
        return '\n'.join(key_points[:15])  # Top 15 points
    
    # Fallback: extract sentences that contain key indicators from all content
    sentences = content.replace('\n', ' ').split('.')
    important_sentences = []
    keywords = ['important', 'note', 'warning', 'key', 'must', 'should', 'required', 'avoid', 'best', 'practice']
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and any(keyword in sentence.lower() for keyword in keywords):
            important_sentences.append(f"• {sentence}.")
    
    return '\n'.join(important_sentences[:8]) if important_sentences else "No specific key points identified."


def _generate_detailed_summary(content: str, sections: List[Dict[str, str]]) -> str:
    """Generate a detailed summary with all sections."""
    if not sections:
        return content[:1500] + "..." if len(content) > 1500 else content
    
    detailed_parts = []
    
    for section in sections:
        title = section['title'].lstrip('#').strip()
        section_content = section['content'].strip()
        
        # Skip empty sections
        if not section_content:
            continue
            
        # For detailed summary, include more content
        content_preview = section_content[:400]
        if len(section_content) > 400:
            content_preview += "..."
            
        detailed_parts.append(f"## {title}\n{content_preview}")
    
    # If no sections with content, return truncated full content
    if not detailed_parts:
        return content[:1500] + "..." if len(content) > 1500 else content
    
    return '\n\n'.join(detailed_parts)


def _extract_technical_details(content: str, sections: List[Dict[str, str]]) -> str:
    """Extract technical details like code, configurations, and specifications."""
    technical_parts = []
    
    # Extract code blocks
    import re
    code_blocks = re.findall(r'```[\s\S]*?```', content)
    if code_blocks:
        technical_parts.append("**Code Examples:**")
        for i, block in enumerate(code_blocks[:3], 1):
            technical_parts.append(f"Block {i}: {block[:100]}..." if len(block) > 100 else block)
    
    # Extract technical terms (words in backticks)
    tech_terms = re.findall(r'`([^`]+)`', content)
    if tech_terms:
        unique_terms = list(set(tech_terms))[:10]
        technical_parts.append(f"**Technical Terms:** {', '.join(unique_terms)}")
    
    # Look for configuration or specification patterns
    config_lines = []
    lines = content.split('\n')
    for line in lines:
        if ('config' in line.lower() or 
            'setting' in line.lower() or 
            '=' in line or 
            ':' in line and not line.strip().startswith('#')):
            config_lines.append(line.strip())
    
    if config_lines:
        technical_parts.append("**Configurations/Settings:**")
        technical_parts.extend(config_lines[:5])
    
    return '\n\n'.join(technical_parts) if technical_parts else "No specific technical details identified."


def _generate_brief_summary(content: str) -> str:
    """Generate a very brief summary (1-2 sentences)."""
    words = content.split()
    if len(words) <= 30:
        return content
    
    # Take first sentence or first 30 words
    sentences = content.split('.')
    first_sentence = sentences[0].strip() + '.' if sentences else ''
    
    if len(first_sentence.split()) <= 30:
        return first_sentence
    else:
        return ' '.join(words[:30]) + "..."


@mcp.resource("docs://list")
def list_docs_resource() -> list[str]:
    """
    Resource that returns a simple list of available doc paths.
    """
    return [str(p.relative_to(DOCS_ROOT)) for p in _iter_docs()]


@mcp.resource("docs://{relative_path}")
def read_doc(relative_path: str) -> str:
    """
    Read a specific doc by relative path (e.g. 'getting-started.md').
    """
    path = (DOCS_ROOT / relative_path).resolve()
    if not path.exists() or not path.is_file():
        return f"Document not found: {relative_path}"
    if DOCS_ROOT not in path.parents and DOCS_ROOT != path.parent:
        return "Access denied: path escapes docs root."
    return _read_file(path)


@mcp.tool()
def list_docs() -> List[str]:
    """
    List available documentation files relative to the docs/ folder.
    """
    return [str(p.relative_to(DOCS_ROOT)) for p in _iter_docs()]


@mcp.tool()
def search_docs(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Improved full-text search over docs with better matching.

    Args:
        query: Search query string.
        max_results: Max number of matches to return.
    Returns:
        List of {path, snippet} matches.
    """
    import re
    
    query_lower = query.lower()
    query_words = query_lower.split()
    results: list[dict[str, str]] = []

    for path in _iter_docs():
        text = _read_file(path)
        text_lower = text.lower()
        
        # Score based on how many query words are found
        matches = []
        
        # First, try exact phrase match (highest score)
        if query_lower in text_lower:
            idx = text_lower.find(query_lower)
            start = max(0, idx - 80)
            end = min(len(text), idx + 80)
            snippet = text[start:end].replace("\n", " ")
            matches.append({
                "score": 100,
                "snippet": snippet,
                "match_type": "exact_phrase"
            })
        
        # Then try to find sentences containing most query words
        sentences = re.split(r'[.!?]+|\n\n+', text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            word_matches = sum(1 for word in query_words if word in sentence_lower)
            
            if word_matches >= max(1, len(query_words) * 0.6):  # At least 60% of words
                # Calculate score based on word matches and total words
                score = (word_matches / len(query_words)) * 80
                if len(sentence.strip()) > 20:  # Prefer longer, more informative sentences
                    snippet = sentence.strip()[:160] + "..." if len(sentence.strip()) > 160 else sentence.strip()
                    matches.append({
                        "score": score,
                        "snippet": snippet,
                        "match_type": f"words_{word_matches}/{len(query_words)}"
                    })
        
        # Add the best matches for this document
        if matches:
            # Sort by score and take the best match
            best_match = max(matches, key=lambda x: x["score"])
            results.append({
                "path": str(path.relative_to(DOCS_ROOT)),
                "snippet": best_match["snippet"],
                "score": str(best_match["score"]),
                "match_type": best_match["match_type"]
            })

    # Sort results by score (highest first) and limit
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_results]


@mcp.tool()
def extract_section(relative_path: str, section_title: str, include_subsections: bool = True) -> Dict[str, Any]:
    """
    Extract a specific section from a document.
    
    Args:
        relative_path: Path to the document relative to docs/ folder
        section_title: Title of the section to extract (case-insensitive, partial matches allowed)
        include_subsections: Whether to include subsections in the extracted content
    Returns:
        Dictionary with section content and metadata
    """
    path = (DOCS_ROOT / relative_path).resolve()
    if not path.exists() or not path.is_file():
        return {"error": f"Document not found: {relative_path}"}
    if DOCS_ROOT not in path.parents and DOCS_ROOT != path.parent:
        return {"error": "Access denied: path escapes docs root."}
    
    content = _read_file(path)
    
    # Use hierarchical extraction if including subsections, otherwise flat extraction
    if include_subsections:
        sections = _extract_hierarchical_sections(content)
    else:
        sections = _extract_sections(content)
    
    # Find matching section (case-insensitive, partial match)
    section_title_lower = section_title.lower()
    matching_sections = []
    
    for section in sections:
        section_title_clean = section['title'].lstrip('#').strip().lower()
        if section_title_lower in section_title_clean or section_title_clean in section_title_lower:
            matching_sections.append(section)
    
    if not matching_sections:
        # List available sections for user reference
        available_sections = [s['title'].lstrip('#').strip() for s in sections if s['content'].strip()]
        return {
            "error": f"Section '{section_title}' not found",
            "available_sections": available_sections[:10],  # Limit to first 10 for readability
            "total_sections": str(len(available_sections))
        }
    
    if len(matching_sections) == 1:
        section = matching_sections[0]
        result = {
            "document": relative_path,
            "section_title": section['title'].lstrip('#').strip(),
            "content": section['content'].strip(),
            "word_count": str(len(section['content'].split())),
            "match_type": "single",
            "extraction_mode": "hierarchical" if include_subsections else "flat"
        }
        
        # Add metadata about subsections if available
        if 'includes_subsections' in section:
            result["includes_subsections"] = section['includes_subsections']
        if 'level' in section:
            result["header_level"] = section['level']
            
        return result
    else:
        # Multiple matches - return all
        results = []
        for section in matching_sections:
            section_info = {
                "section_title": section['title'].lstrip('#').strip(),
                "content": section['content'].strip(),
                "word_count": str(len(section['content'].split()))
            }
            if 'level' in section:
                section_info["header_level"] = section['level']
            if 'includes_subsections' in section:
                section_info["includes_subsections"] = section['includes_subsections']
            results.append(section_info)
        
        return {
            "document": relative_path,
            "match_type": "multiple",
            "matching_sections": results,
            "total_matches": str(len(results)),
            "extraction_mode": "hierarchical" if include_subsections else "flat"
        }


@mcp.tool()
def summarize_document(relative_path: str, summary_type: str = "overview") -> Dict[str, str]:
    """
    Generate a smart summary of a specific document.
    
    Args:
        relative_path: Path to the document relative to docs/ folder
        summary_type: Type of summary - 'overview', 'key_points', 'detailed', or 'technical'
    Returns:
        Dictionary with document info and structured summary
    """
    path = (DOCS_ROOT / relative_path).resolve()
    if not path.exists() or not path.is_file():
        return {"error": f"Document not found: {relative_path}"}
    if DOCS_ROOT not in path.parents and DOCS_ROOT != path.parent:
        return {"error": "Access denied: path escapes docs root."}
    
    content = _read_file(path)
    word_count = len(content.split())
    
    # Extract key sections based on markdown headers
    sections = _extract_sections(content)
    
    # Generate summary based on type
    if summary_type == "key_points":
        summary = _extract_key_points(content, sections)
    elif summary_type == "detailed":
        summary = _generate_detailed_summary(content, sections)
    elif summary_type == "technical":
        summary = _extract_technical_details(content, sections)
    else:  # overview
        summary = _generate_overview_summary(content, sections)
    
    return {
        "document": relative_path,
        "word_count": str(word_count),
        "sections": str(len(sections)),
        "summary_type": summary_type,
        "summary": summary
    }


@mcp.tool()
def analyze_document_structure(relative_path: str) -> Dict[str, Any]:
    """
    Analyze the structure and metadata of a document.
    
    Args:
        relative_path: Path to the document relative to docs/ folder
    Returns:
        Dictionary with structural analysis
    """
    path = (DOCS_ROOT / relative_path).resolve()
    if not path.exists() or not path.is_file():
        return {"error": f"Document not found: {relative_path}"}
    
    content = _read_file(path)
    
    # Extract headers and create outline
    headers = _extract_headers(content)
    sections = _extract_sections(content)
    
    # Basic statistics
    lines = content.split('\n')
    words = content.split()
    
    # Find code blocks and links
    code_blocks = _count_code_blocks(content)
    links = _extract_links(content)
    
    return {
        "document": relative_path,
        "statistics": {
            "lines": len(lines),
            "words": len(words),
            "characters": len(content),
            "sections": str(len(sections)),
            "code_blocks": code_blocks,
            "links": len(links)
        },
        "structure": {
            "headers": headers,
            "outline": _create_outline(headers)
        },
        "content_analysis": {
            "has_tables": "| " in content,
            "has_images": "![" in content,
            "has_code": "```" in content or "    " in content,
            "external_links": [link for link in links if link.startswith(('http', 'https'))]
        }
    }


@mcp.tool()
def generate_doc_overview() -> Dict[str, Any]:
    """
    Generate a comprehensive overview of the entire documentation set.
    
    Returns:
        Dictionary with overall documentation analysis
    """
    docs = _iter_docs()
    overview = {
        "total_documents": str(len(docs)),
        "documents_by_type": {},
        "total_content": {"words": 0, "lines": 0, "characters": 0},
        "structure_analysis": {"sections": 0, "code_blocks": 0},
        "document_summaries": []
    }
    
    for path in docs:
        content = _read_file(path)
        ext = path.suffix.lower()
        rel_path = str(path.relative_to(DOCS_ROOT))
        
        # Count by type
        overview["documents_by_type"][ext] = overview["documents_by_type"].get(ext, 0) + 1
        
        # Aggregate statistics
        words = len(content.split())
        lines = len(content.split('\n'))
        chars = len(content)
        
        overview["total_content"]["words"] += words
        overview["total_content"]["lines"] += lines
        overview["total_content"]["characters"] += chars
        
        # Structure analysis
        sections = len(_extract_sections(content))
        code_blocks = _count_code_blocks(content)
        
        overview["structure_analysis"]["sections"] += sections
        overview["structure_analysis"]["code_blocks"] += code_blocks
        
        # Brief summary for each doc
        brief_summary = _generate_brief_summary(content)
        overview["document_summaries"].append({
            "path": rel_path,
            "words": words,
            "sections": sections,
            "brief_summary": brief_summary
        })
    
    return overview


@mcp.tool()
def semantic_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Perform semantic search across documents using keyword matching and relevance scoring.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
    Returns:
        List of documents with relevance scores and context
    """
    query_words = set(query.lower().split())
    results = []
    
    for path in _iter_docs():
        content = _read_file(path)
        content_lower = content.lower()
        
        # Calculate relevance score
        score = 0
        context_snippets = []
        
        for word in query_words:
            word_count = content_lower.count(word)
            score += word_count * len(word)  # Longer words get higher weight
            
            # Find context for each query word
            word_positions = []
            start = 0
            while True:
                pos = content_lower.find(word, start)
                if pos == -1:
                    break
                word_positions.append(pos)
                start = pos + 1
            
            # Get context snippets around found words
            for pos in word_positions[:2]:  # Max 2 snippets per word
                snippet_start = max(0, pos - 60)
                snippet_end = min(len(content), pos + 60)
                snippet = content[snippet_start:snippet_end].replace('\n', ' ')
                context_snippets.append(snippet)
        
        if score > 0:
            # Normalize score by document length
            normalized_score = score / len(content.split())
            
            results.append({
                'path': str(path.relative_to(DOCS_ROOT)),
                'relevance_score': normalized_score,
                'context_snippets': context_snippets[:3],  # Max 3 snippets
                'word_count': len(content.split())
            })
    
    # Sort by relevance score
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:max_results]


@mcp.tool()
def compare_documents(doc1_path: str, doc2_path: str) -> Dict[str, Any]:
    """
    Compare two documents and identify similarities and differences.
    
    Args:
        doc1_path: Path to first document
        doc2_path: Path to second document
    Returns:
        Comparison analysis
    """
    path1 = (DOCS_ROOT / doc1_path).resolve()
    path2 = (DOCS_ROOT / doc2_path).resolve()
    
    if not path1.exists() or not path2.exists():
        return {"error": "One or both documents not found"}
    
    content1 = _read_file(path1)
    content2 = _read_file(path2)
    
    # Basic statistics comparison
    stats1 = {
        "words": len(content1.split()),
        "lines": len(content1.split('\n')),
        "characters": len(content1)
    }
    stats2 = {
        "words": len(content2.split()),
        "lines": len(content2.split('\n')),
        "characters": len(content2)
    }
    
    # Find common and unique words
    words1 = set(word.lower().strip('.,!?;:') for word in content1.split())
    words2 = set(word.lower().strip('.,!?;:') for word in content2.split())
    
    common_words = words1.intersection(words2)
    unique_to_doc1 = words1 - words2
    unique_to_doc2 = words2 - words1
    
    # Extract headers for structure comparison
    headers1 = [h['title'] for h in _extract_headers(content1)]
    headers2 = [h['title'] for h in _extract_headers(content2)]
    
    return {
        "document1": doc1_path,
        "document2": doc2_path,
        "statistics": {
            "doc1": stats1,
            "doc2": stats2,
            "size_ratio": stats1["words"] / stats2["words"] if stats2["words"] > 0 else float('inf')
        },
        "content_similarity": {
            "common_words_count": len(common_words),
            "unique_to_doc1_count": len(unique_to_doc1),
            "unique_to_doc2_count": len(unique_to_doc2),
            "similarity_ratio": len(common_words) / len(words1.union(words2)) if len(words1.union(words2)) > 0 else 0
        },
        "structure_comparison": {
            "doc1_headers": headers1,
            "doc2_headers": headers2,
            "common_headers": list(set(headers1).intersection(set(headers2))),
            "unique_headers_doc1": list(set(headers1) - set(headers2)),
            "unique_headers_doc2": list(set(headers2) - set(headers1))
        },
        "sample_unique_words": {
            "doc1": list(unique_to_doc1)[:10],
            "doc2": list(unique_to_doc2)[:10]
        }
    }


@mcp.tool()
def extract_definitions(relative_path: str) -> Dict[str, Any]:
    """
    Extract definitions, terms, and explanations from a document.
    
    Args:
        relative_path: Path to the document
    Returns:
        Extracted definitions and terms
    """
    path = (DOCS_ROOT / relative_path).resolve()
    if not path.exists():
        return {"error": f"Document not found: {relative_path}"}
    
    content = _read_file(path)
    definitions = []
    
    # Look for definition patterns
    import re
    
    # Pattern 1: "Term: Definition" or "Term - Definition"
    definition_patterns = [
        r'^([A-Z][^:\-\n]+):\s*(.+)$',  # Term: Definition
        r'^([A-Z][^:\-\n]+)\s*-\s*(.+)$',  # Term - Definition
        r'\*\*([^*]+)\*\*:\s*([^\n]+)',  # **Term**: Definition
        r'`([^`]+)`:\s*([^\n]+)'  # `Term`: Definition
    ]
    
    for pattern in definition_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            term, definition = match
            definitions.append({
                "term": term.strip(),
                "definition": definition.strip(),
                "type": "explicit"
            })
    
    # Look for glossary sections
    sections = _extract_sections(content)
    glossary_terms = []
    
    for section in sections:
        if any(keyword in section['title'].lower() for keyword in ['glossary', 'definition', 'terminology', 'terms']):
            lines = section['content'].split('\n')
            for line in lines:
                if ':' in line or '-' in line:
                    parts = line.split(':') if ':' in line else line.split('-')
                    if len(parts) == 2:
                        glossary_terms.append({
                            "term": parts[0].strip(),
                            "definition": parts[1].strip(),
                            "type": "glossary"
                        })
    
    # Extract technical terms (words in backticks)
    tech_terms = re.findall(r'`([^`]+)`', content)
    tech_terms_unique = list(set(tech_terms))
    
    return {
        "document": relative_path,
        "definitions": definitions,
        "glossary_terms": glossary_terms,
        "technical_terms": tech_terms_unique,
        "total_definitions": str(len(definitions) + len(glossary_terms)),
        "definition_density": (len(definitions) + len(glossary_terms)) / len(content.split()) if content.split() else 0
    }


@mcp.tool()
def generate_table_of_contents(relative_path: str = None) -> Dict[str, Any]:
    """
    Generate a table of contents for a specific document or all documents.
    
    Args:
        relative_path: Path to specific document, or None for all documents
    Returns:
        Table of contents structure
    """
    if relative_path:
        # Single document TOC
        path = (DOCS_ROOT / relative_path).resolve()
        if not path.exists():
            return {"error": f"Document not found: {relative_path}"}
        
        content = _read_file(path)
        headers = _extract_headers(content)
        
        return {
            "document": relative_path,
            "table_of_contents": _create_outline(headers),
            "header_count": len(headers),
            "max_depth": max([h['level'] for h in headers]) if headers else 0
        }
    else:
        # All documents TOC
        all_toc = {}
        for path in _iter_docs():
            content = _read_file(path)
            headers = _extract_headers(content)
            rel_path = str(path.relative_to(DOCS_ROOT))
            
            all_toc[rel_path] = {
                "outline": _create_outline(headers),
                "header_count": len(headers),
                "max_depth": max([h['level'] for h in headers]) if headers else 0
            }
        
        return {
            "type": "complete_documentation_toc",
            "documents": all_toc,
            "total_documents": str(len(all_toc))
        }


@mcp.tool()
def intelligent_summarize(relative_path: str, summary_type: str = "medium", focus_keywords: str = None) -> Dict[str, Any]:
    """
    Generate an intelligent summary using advanced text analysis.
    
    Args:
        relative_path: Path to the document
        summary_type: "short", "medium", or "long"
        focus_keywords: Optional comma-separated keywords to focus on
    Returns:
        Intelligent summary with analysis
    """
    path = (DOCS_ROOT / relative_path).resolve()
    if not path.exists():
        return {"error": f"Document not found: {relative_path}"}
    
    try:
        content = _read_file(path)
        
        # Use document intelligence for smart summary
        summary_result = doc_intel.generate_smart_summary(content, summary_type)
        
        # Add key concepts
        key_concepts = doc_intel.extract_key_concepts(content)
        
        # Add readability analysis
        readability = doc_intel.analyze_readability(content)
        
        # If focus keywords provided, highlight relevant sections
        focused_content = None
        if focus_keywords:
            keywords = [k.strip() for k in focus_keywords.split(',')]
            # Find sections that contain the keywords
            sections = _extract_sections(content)
            relevant_sections = []
            for section in sections:
                if section['content'].strip() and any(keyword.lower() in section['content'].lower() for keyword in keywords):
                    relevant_sections.append(section['title'].lstrip('#').strip())
            focused_content = relevant_sections
        
        return {
            "document": relative_path,
            "summary": summary_result,
            "key_concepts": key_concepts[:10],
            "readability": readability,
            "focused_sections": focused_content,
            "analysis_method": "advanced_intelligence"
        }
    except Exception as e:
        return {
            "error": f"Failed to analyze document: {str(e)}",
            "document": relative_path,
            "fallback_available": True
        }


@mcp.tool()
def extract_qa_pairs(relative_path: str = None) -> Dict[str, Any]:
    """
    Extract question-answer pairs from documents for FAQ generation.
    
    Args:
        relative_path: Specific document path, or None for all documents
    Returns:
        Extracted Q&A pairs
    """
    if relative_path:
        path = (DOCS_ROOT / relative_path).resolve()
        if not path.exists():
            return {"error": f"Document not found: {relative_path}"}
        
        content = _read_file(path)
        qa_pairs = doc_intel.extract_questions_and_answers(content)
        
        return {
            "document": relative_path,
            "qa_pairs": qa_pairs,
            "total_pairs": str(len(qa_pairs))
        }
    else:
        # Extract from all documents
        all_qa_pairs = {}
        total_pairs = 0
        
        for path in _iter_docs():
            content = _read_file(path)
            qa_pairs = doc_intel.extract_questions_and_answers(content)
            if qa_pairs:
                rel_path = str(path.relative_to(DOCS_ROOT))
                all_qa_pairs[rel_path] = qa_pairs
                total_pairs += len(qa_pairs)
        
        return {
            "type": "complete_documentation_qa",
            "qa_by_document": all_qa_pairs,
            "total_pairs": str(total_pairs)
        }


@mcp.tool()
def find_related_documents(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Find documents most related to a query using advanced similarity scoring.
    
    Args:
        query: Search query or topic
        max_results: Maximum number of related documents to return
    Returns:
        List of related documents with scores and explanations
    """
    all_docs = list(_iter_docs())
    related = doc_intel.find_related_content(query, all_docs, max_results)
    
    return {
        "query": query,
        "related_documents": related,
        "total_analyzed": len(all_docs),
        "method": "tf-idf_similarity"
    }


@mcp.tool()
def analyze_document_gaps() -> Dict[str, Any]:
    """
    Analyze the documentation set to identify potential gaps or areas needing improvement.
    
    Returns:
        Analysis of documentation completeness and suggestions
    """
    all_docs = list(_iter_docs())
    analysis = {
        "total_documents": len(all_docs),
        "coverage_analysis": {},
        "recommendations": [],
        "content_quality": {},
        "structure_issues": []
    }
    
    # Analyze each document
    total_words = 0
    short_docs = []
    long_docs = []
    low_readability_docs = []
    missing_sections = []
    
    common_sections = ['introduction', 'overview', 'getting started', 'configuration', 'examples', 'troubleshooting']
    section_coverage = {section: 0 for section in common_sections}
    
    for path in all_docs:
        content = _read_file(path)
        rel_path = str(path.relative_to(DOCS_ROOT))
        
        # Word count analysis
        word_count = len(content.split())
        total_words += word_count
        
        if word_count < 100:
            short_docs.append(rel_path)
        elif word_count > 3000:
            long_docs.append(rel_path)
        
        # Readability analysis
        readability = doc_intel.analyze_readability(content)
        if readability.get('flesch_score', 50) < 30:
            low_readability_docs.append(rel_path)
        
        # Section coverage analysis
        headers = [h['title'].lower() for h in _extract_headers(content)]
        doc_sections = []
        for section in common_sections:
            if any(section in header for header in headers):
                section_coverage[section] += 1
                doc_sections.append(section)
        
        missing = [s for s in common_sections if s not in doc_sections]
        if missing:
            missing_sections.append({"document": rel_path, "missing": missing})
    
    # Generate recommendations
    if short_docs:
        analysis["recommendations"].append(f"Consider expanding these short documents: {', '.join(short_docs[:3])}")
    
    if low_readability_docs:
        analysis["recommendations"].append(f"Improve readability of: {', '.join(low_readability_docs[:3])}")
    
    # Find least covered sections
    least_covered = min(section_coverage.values())
    missing_section_types = [section for section, count in section_coverage.items() if count <= least_covered]
    if missing_section_types:
        analysis["recommendations"].append(f"Consider adding {', '.join(missing_section_types)} sections to more documents")
    
    analysis["coverage_analysis"] = {
        "average_words_per_doc": total_words / len(all_docs) if all_docs else 0,
        "short_documents": short_docs,
        "long_documents": long_docs,
        "section_coverage": section_coverage
    }
    
    analysis["content_quality"] = {
        "low_readability": low_readability_docs,
        "missing_common_sections": missing_sections
    }
    
    return analysis


@mcp.tool()
def generate_documentation_index() -> Dict[str, Any]:
    """
    Generate a comprehensive searchable index of all documentation content.
    
    Returns:
        Searchable index with topics, concepts, and cross-references
    """
    index = {
        "concepts": {},  # concept -> [documents]
        "topics": {},    # topic -> documents
        "cross_references": {},  # document -> related documents
        "metadata": {}
    }
    
    all_docs = list(_iter_docs())
    
    # Build concept index
    all_concepts = {}
    
    for path in all_docs:
        content = _read_file(path)
        rel_path = str(path.relative_to(DOCS_ROOT))
        
        # Extract concepts from this document
        concepts = doc_intel.extract_key_concepts(content, min_frequency=1)
        
        # Add to global concept index
        for concept_info in concepts:
            concept = concept_info['concept']
            if concept not in all_concepts:
                all_concepts[concept] = []
            all_concepts[concept].append({
                "document": rel_path,
                "frequency": concept_info['frequency'],
                "type": concept_info['type']
            })
        
        # Find cross-references (documents with similar concepts)
        related_docs = doc_intel.find_related_content(
            ' '.join([c['concept'] for c in concepts[:5]]), 
            all_docs, 
            max_results=3
        )
        index["cross_references"][rel_path] = [doc['path'] for doc in related_docs if doc['path'] != rel_path]
        
        # Document metadata
        headers = _extract_headers(content)
        readability = doc_intel.analyze_readability(content)
        
        index["metadata"][rel_path] = {
            "word_count": len(content.split()),
            "sections": len(headers),
            "readability_score": readability.get('flesch_score', 0),
            "main_topics": [c['concept'] for c in concepts[:5]]
        }
    
    # Filter concepts that appear in multiple documents (more valuable for index)
    index["concepts"] = {
        concept: docs for concept, docs in all_concepts.items() 
        if len(docs) > 1 or any(d['frequency'] > 2 for d in docs)
    }
    
    # Create topic clusters
    topic_clusters = {}
    for concept, docs in index["concepts"].items():
        if len(docs) >= 2:  # Concept appears in multiple docs
            topic_clusters[concept] = [doc['document'] for doc in docs]
    
    index["topics"] = topic_clusters
    
    return {
        "index": index,
        "statistics": {
            "total_concepts": len(index["concepts"]),
            "total_topics": len(index["topics"]),
            "total_documents": len(all_docs),
            "avg_cross_references": sum(len(refs) for refs in index["cross_references"].values()) / len(index["cross_references"]) if index["cross_references"] else 0
        }
    }


@mcp.tool()
def get_ocr_status() -> Dict[str, Any]:
    """
    Get the current status of OCR (Optical Character Recognition) capabilities.
    
    Returns:
        Dictionary with OCR availability, supported formats, and setup information
    """
    try:
        if OCR_SUPPORT:
            from ocr_processor import get_ocr_status
            status = get_ocr_status()
            
            # Add document statistics
            all_docs = list(_iter_docs())
            image_docs = [doc for doc in all_docs if doc.suffix.lower() in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif"}]
            pdf_docs = [doc for doc in all_docs if doc.suffix.lower() == ".pdf"]
            
            status["document_stats"] = {
                "total_documents": len(all_docs),
                "pdf_documents": len(pdf_docs),
                "image_documents": len(image_docs),
                "text_documents": len(all_docs) - len(pdf_docs) - len(image_docs)
            }
            
            return status
        else:
            # OCR not available
            base_status = {
                "available": False,
                "error": "OCR libraries not available",
                "supported_formats": [],
                "installation_instructions": "Install OCR dependencies: pip install pytesseract pdf2image Pillow"
            }
            
            # Still provide document statistics
            all_docs = list(_iter_docs())
            pdf_docs = [doc for doc in all_docs if doc.suffix.lower() == ".pdf"]
            
            base_status["document_stats"] = {
                "total_documents": len(all_docs),
                "pdf_documents": len(pdf_docs),
                "image_documents": 0,  # Can't process without OCR
                "text_documents": len(all_docs) - len(pdf_docs)
            }
            
            if PDF_SUPPORT:
                base_status["note"] = "Basic PDF text extraction available, but OCR needed for image-based PDFs"
            
            return base_status
            
    except Exception as e:
        return {
            "available": False,
            "error": f"Error checking OCR status: {str(e)}",
            "supported_formats": []
        }


if __name__ == "__main__":
    # stdio transport keeps it compatible with the official client pattern
    mcp.run(transport="stdio")