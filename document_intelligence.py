"""
Document Intelligence Module for Advanced Text Analysis and Processing
"""
from pathlib import Path
from typing import List, Dict, Any
import re
import math
from collections import Counter


class DocumentIntelligence:
    """Advanced document intelligence for smart analysis and summarization."""
    
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        
    def generate_smart_summary(self, content: str, summary_type: str = "medium") -> str:
        """Generate an intelligent summary based on content analysis."""
        # Handle PDF page markers
        content = self._clean_pdf_content(content)
        
        sentences = self._split_into_sentences(content)
        
        if not sentences:
            return "No content available for summarization."
        
        # Score sentences based on multiple factors
        sentence_scores = {}
        
        # Factor 1: Word frequency
        words = self._extract_words(content)
        word_freq = Counter(words)
        
        # Factor 2: Position (early sentences often important)
        # Factor 3: Length (moderate length sentences preferred)
        # Factor 4: Keywords (technical terms, action words)
        
        for i, sentence in enumerate(sentences):
            score = 0
            sentence_words = self._extract_words(sentence)
            
            # Word frequency score
            for word in sentence_words:
                score += word_freq.get(word, 0)
            
            # Position score (first and last sentences get bonus)
            if i < 3:
                score += 5
            elif i >= len(sentences) - 2:
                score += 3
                
            # Length score (prefer moderate length)
            word_count = len(sentence_words)
            if 10 <= word_count <= 25:
                score += 3
            elif 5 <= word_count <= 35:
                score += 1
                
            # Keyword bonus
            keywords = ['important', 'key', 'main', 'primary', 'essential', 
                       'note', 'must', 'should', 'required', 'configure', 
                       'setup', 'install', 'create', 'build']
            for keyword in keywords:
                if keyword in sentence.lower():
                    score += 2
            
            sentence_scores[i] = score / max(len(sentence_words), 1)
        
        # Select top sentences based on summary type
        if summary_type == "short":
            top_count = min(3, len(sentences))
        elif summary_type == "long":
            top_count = min(10, len(sentences))
        else:  # medium
            top_count = min(6, len(sentences))
        
        # Get top scoring sentences, maintaining order
        top_sentence_indices = sorted(
            sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:top_count],
            key=lambda x: x[0]
        )
        
        summary_sentences = [sentences[i] for i, _ in top_sentence_indices]
        return ' '.join(summary_sentences)
    
    def extract_key_concepts(self, content: str, min_frequency: int = 2) -> List[Dict[str, Any]]:
        """Extract key concepts and terms from content."""
        # Clean PDF content for better concept extraction
        content = self._clean_pdf_content(content)
        
        concepts = []
        
        # Extract technical terms (words in backticks)
        tech_terms = re.findall(r'`([^`]+)`', content)
        tech_term_freq = Counter(tech_terms)
        
        for term, freq in tech_term_freq.items():
            if freq >= min_frequency:
                concepts.append({
                    'concept': term,
                    'frequency': freq,
                    'type': 'technical_term'
                })
        
        # Extract important phrases (words in bold)
        bold_terms = re.findall(r'\*\*([^*]+)\*\*', content)
        bold_term_freq = Counter(bold_terms)
        
        for term, freq in bold_term_freq.items():
            if freq >= min_frequency:
                concepts.append({
                    'concept': term,
                    'frequency': freq,
                    'type': 'emphasized_term'
                })
        
        # Extract capitalized words (potential proper nouns/concepts)
        words = re.findall(r'\b[A-Z][a-z]+\b', content)
        cap_word_freq = Counter(words)
        
        for word, freq in cap_word_freq.items():
            if freq >= min_frequency and len(word) > 3:
                concepts.append({
                    'concept': word,
                    'frequency': freq,
                    'type': 'proper_noun'
                })
        
        # Sort by frequency and return top concepts
        concepts.sort(key=lambda x: x['frequency'], reverse=True)
        return concepts[:20]
    
    def analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability using various metrics."""
        # Clean PDF content for better analysis
        content = self._clean_pdf_content(content)
        
        sentences = self._split_into_sentences(content)
        words = self._extract_words(content)
        
        if not sentences or not words:
            return {"flesch_score": 0, "grade_level": 0, "complexity": "unknown"}
        
        # Basic counts
        sentence_count = len(sentences)
        word_count = len(words)
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        # Average sentence length
        avg_sentence_length = word_count / sentence_count
        
        # Average syllables per word
        avg_syllables = syllable_count / word_count if word_count > 0 else 0
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        flesch_score = max(0, min(100, flesch_score))  # Clamp to 0-100
        
        # Grade level estimation
        grade_level = 0.39 * avg_sentence_length + 11.8 * avg_syllables - 15.59
        grade_level = max(1, grade_level)
        
        # Complexity assessment
        if flesch_score >= 70:
            complexity = "easy"
        elif flesch_score >= 50:
            complexity = "moderate"
        elif flesch_score >= 30:
            complexity = "difficult"
        else:
            complexity = "very difficult"
        
        return {
            "flesch_score": round(flesch_score, 1),
            "grade_level": round(grade_level, 1),
            "complexity": complexity,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_syllables_per_word": round(avg_syllables, 2),
            "total_sentences": sentence_count,
            "total_words": word_count
        }
    
    def extract_questions_and_answers(self, content: str) -> List[Dict[str, str]]:
        """Extract Q&A pairs from content."""
        qa_pairs = []
        
        # Look for FAQ sections
        sections = self._extract_sections(content)
        for section in sections:
            if any(keyword in section['title'].lower() for keyword in ['faq', 'question', 'q&a', 'troubleshoot']):
                pairs = self._extract_qa_from_section(section['content'])
                qa_pairs.extend(pairs)
        
        # Look for question patterns throughout the text
        question_patterns = [
            r'(?:Q:|Question:|Q\d+:)\s*([^?]+\?)\s*(?:A:|Answer:)?\s*([^Q\n]+)',
            r'(?:^|\n)([^.!?\n]*\?)\s*\n([^?\n]+)',
            r'How (?:do|to|can) ([^?]+\?)\s*([^?\n]+)'
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    question, answer = match
                    qa_pairs.append({
                        "question": question.strip(),
                        "answer": answer.strip()[:300],  # Limit answer length
                        "type": "extracted"
                    })
        
        return qa_pairs[:15]  # Return top 15 Q&A pairs
    
    def find_related_content(self, query: str, doc_paths: List[Path], max_results: int = 5) -> List[Dict[str, Any]]:
        """Find documents related to a query using TF-IDF-like scoring."""
        query_words = set(self._extract_words(query.lower()))
        results = []
        
        for path in doc_paths:
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')
                content_words = self._extract_words(content.lower())
                
                if not content_words:
                    continue
                
                # Calculate similarity score
                word_freq = Counter(content_words)
                score = 0
                
                for query_word in query_words:
                    if query_word in word_freq:
                        # TF-IDF like scoring
                        tf = word_freq[query_word] / len(content_words)
                        score += tf * len(query_word)  # Longer words get more weight
                
                if score > 0:
                    # Normalize by document length
                    normalized_score = score / math.log(len(content_words) + 1)
                    
                    # Get context snippet
                    snippet = self._extract_snippet(content, query_words)
                    
                    results.append({
                        'path': str(path.relative_to(self.docs_root)),
                        'relevance_score': normalized_score,
                        'snippet': snippet,
                        'word_count': len(content_words)
                    })
                    
            except Exception:
                continue
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:max_results]
    
    def _split_into_sentences(self, content: str) -> List[str]:
        """Split content into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', content)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their'}
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower()
        if len(word) <= 3:
            return 1
        
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract sections from markdown content."""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.strip().startswith('#'):
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip()
                    })
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })
        
        return sections
    
    def _extract_qa_from_section(self, section_content: str) -> List[Dict[str, str]]:
        """Extract Q&A pairs from a section."""
        qa_pairs = []
        lines = section_content.split('\n')
        current_question = None
        current_answer = []
        
        for line in lines:
            line = line.strip()
            if line.endswith('?') and not current_question:
                current_question = line
            elif current_question and line and not line.endswith('?'):
                current_answer.append(line)
            elif current_question and (line.endswith('?') or not line):
                if current_answer:
                    qa_pairs.append({
                        "question": current_question,
                        "answer": ' '.join(current_answer),
                        "type": "faq"
                    })
                current_question = line if line.endswith('?') else None
                current_answer = []
        
        # Don't forget the last Q&A pair
        if current_question and current_answer:
            qa_pairs.append({
                "question": current_question,
                "answer": ' '.join(current_answer),
                "type": "faq"
            })
        
        return qa_pairs
    
    def _extract_snippet(self, content: str, query_words: set, snippet_length: int = 150) -> str:
        """Extract a relevant snippet containing query words."""
        content_lower = content.lower()
        
        # Find the first occurrence of any query word
        first_pos = len(content)
        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1:
                first_pos = min(first_pos, pos)
        
        if first_pos == len(content):
            # No query words found, return beginning
            return content[:snippet_length] + "..." if len(content) > snippet_length else content
        
        # Extract snippet around the found position
        start = max(0, first_pos - snippet_length // 2)
        end = min(len(content), start + snippet_length)
        snippet = content[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet.replace('\n', ' ')
    
    def _clean_pdf_content(self, content: str) -> str:
        """Clean PDF content by removing page markers and fixing formatting."""
        import re
        
        # Remove page markers like "--- Page 1 ---"
        content = re.sub(r'\n--- Page \d+ ---\n', '\n\n', content)
        content = re.sub(r'\n--- Page \d+ \(Error reading:.*?\) ---\n', '\n\n', content)
        
        # Fix common PDF extraction issues
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Fix broken words (common in PDF extraction)
        content = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', content)
        
        # Fix spacing issues
        content = re.sub(r'([a-z])([A-Z])', r'\1 \2', content)
        
        # Remove extra spaces
        content = re.sub(r' +', ' ', content)
        
        return content.strip()