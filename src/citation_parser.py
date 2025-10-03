#!/usr/bin/env python3
"""
Parse citation-based LLM analysis output into structured data.
"""

import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class CitationParser:
    """Parses LLM analysis text to extract citations and structured data."""

    def __init__(self):
        # Regex pattern for citations: [DATE TIME | SENDER: "message"]
        self.citation_pattern = r'\[([^\]]+?)\s*\|\s*([^:]+?):\s*"([^"]+)"\]'

    def extract_citations(self, text: str) -> List[Dict[str, str]]:
        """
        Extract all citations from analysis text.

        Returns:
            List of dicts with 'date', 'sender', 'text' keys
        """
        citations = []
        matches = re.finditer(self.citation_pattern, text)

        for match in matches:
            date_time = match.group(1).strip()
            sender = match.group(2).strip()
            message_text = match.group(3).strip()

            citations.append({
                'date_time': date_time,
                'sender': sender,
                'text': message_text,
                'full_citation': match.group(0)
            })

        return citations

    def extract_section(self, text: str, section_number: int, section_name: str) -> Optional[str]:
        """Extract a specific analysis section."""
        # Pattern: "1. RELATIONSHIP TYPE" or "**1. RELATIONSHIP TYPE**"
        pattern = rf'(?:\*\*)?{section_number}\.\s+{section_name}(?:\*\*)?(.*?)(?=(?:\*\*)?\d+\.\s+[A-Z]|\Z)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            return match.group(1).strip()
        return None

    def extract_statistics(self, section_text: str) -> Dict[str, Any]:
        """Extract statistics from a section."""
        stats = {}

        # Look for patterns like "- Metric: Value"
        stat_pattern = r'-\s*([^:]+):\s*([^\n]+)'
        matches = re.finditer(stat_pattern, section_text)

        for match in matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            stats[key] = value

        return stats

    def extract_confidence(self, section_text: str) -> Optional[str]:
        """Extract confidence level from section."""
        match = re.search(r'\*\*Confidence\*\*:\s*(HIGH|MEDIUM|LOW)', section_text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return None

    def parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse full analysis into structured format.

        Returns structured dict with:
        - sections: Dict of analysis sections
        - all_citations: List of all citations
        - citation_count: Total citation count
        """
        sections = {
            'relationship_type': self.extract_section(analysis_text, 1, 'RELATIONSHIP TYPE'),
            'communication_initiation': self.extract_section(analysis_text, 2, 'COMMUNICATION INITIATION'),
            'response_patterns': self.extract_section(analysis_text, 3, 'RESPONSE PATTERNS'),
            'tone_sentiment': self.extract_section(analysis_text, 4, 'TONE AND SENTIMENT'),
            'key_topics': self.extract_section(analysis_text, 5, 'KEY TOPICS'),
            'conflict_indicators': self.extract_section(analysis_text, 6, 'CONFLICT INDICATORS'),
            'emotional_support': self.extract_section(analysis_text, 7, 'EMOTIONAL SUPPORT')
        }

        # Extract citations from each section
        section_data = {}
        for section_name, section_text in sections.items():
            if section_text:
                section_data[section_name] = {
                    'text': section_text,
                    'citations': self.extract_citations(section_text),
                    'statistics': self.extract_statistics(section_text),
                    'confidence': self.extract_confidence(section_text)
                }

        # Get all citations
        all_citations = self.extract_citations(analysis_text)

        return {
            'sections': section_data,
            'all_citations': all_citations,
            'citation_count': len(all_citations),
            'sections_found': len([s for s in sections.values() if s is not None])
        }

    def load_and_parse(self, json_file: Path) -> Dict[str, Any]:
        """Load a citation analysis JSON file and parse it."""
        with open(json_file, 'r') as f:
            data = json.load(f)

        analysis_text = data.get('analysis_text', '')
        parsed = self.parse_analysis(analysis_text)

        return {
            'metadata': {
                'phone_number': data.get('phone_number'),
                'model': data.get('model'),
                'analysis_date': data.get('analysis_date'),
                'messages_analyzed': data.get('messages_analyzed'),
                'performance': data.get('performance')
            },
            'parsed_analysis': parsed,
            'raw_text': analysis_text
        }


def main():
    """Demo: Parse citation analysis files."""
    parser = CitationParser()

    # Find citation analysis files
    conversations_dir = Path(__file__).parent.parent / "data" / "output" / "all_conversations"
    citation_files = list(conversations_dir.glob("*_citation_*.json"))

    if not citation_files:
        print("No citation analysis files found.")
        return

    for file in citation_files:
        print(f"\n{'='*80}")
        print(f"Parsing: {file.name}")
        print(f"{'='*80}\n")

        result = parser.load_and_parse(file)

        print(f"Phone: {result['metadata']['phone_number']}")
        print(f"Model: {result['metadata']['model']}")
        print(f"Messages analyzed: {result['metadata']['messages_analyzed']}")
        if result['metadata'].get('performance'):
            print(f"Performance: {result['metadata']['performance']['elapsed_minutes']:.2f} min")
        print(f"\nTotal citations: {result['parsed_analysis']['citation_count']}")
        print(f"Sections found: {result['parsed_analysis']['sections_found']}/7")

        print(f"\nCitations by section:")
        for section_name, section_data in result['parsed_analysis']['sections'].items():
            citation_count = len(section_data['citations'])
            confidence = section_data.get('confidence', 'N/A')
            print(f"  {section_name}: {citation_count} citations (confidence: {confidence})")


if __name__ == "__main__":
    main()
