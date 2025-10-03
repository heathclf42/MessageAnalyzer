#!/usr/bin/env python3
"""
Stage 2: Citation-Based LLM Analysis
Analyzes conversations with extensive citations and statistics.
"""

import json
import ollama
import time
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class CitationAnalyzer:
    """Performs citation-based analysis using local LLMs."""

    def __init__(self, model_name: str = "llama3.2"):
        """
        Initialize analyzer.

        Args:
            model_name: Ollama model to use (llama3.2, qwen2.5, etc.)
        """
        self.model_name = model_name

    def format_messages_for_prompt(self, messages: List[Dict]) -> str:
        """Format messages into readable text for LLM prompt."""
        formatted = []
        for msg in messages:
            if msg.get('text'):
                date = msg.get('date_formatted', 'Unknown date')
                sender = msg.get('sender', 'Unknown')
                text = msg['text']
                formatted.append(f"[{date}] {sender}: \"{text}\"")

        return '\n'.join(formatted)

    def build_analysis_prompt(self, messages: List[Dict], phone_number: str) -> str:
        """Build the full analysis prompt."""

        formatted_messages = self.format_messages_for_prompt(messages)
        message_count = len([m for m in messages if m.get('text')])

        # Get date range
        dates = [m.get('date_formatted', '') for m in messages if m.get('date_formatted')]
        date_range = f"{dates[0]} to {dates[-1]}" if dates else "Unknown"

        prompt = f"""Analyze the following text message conversation.

CONVERSATION DETAILS:
- Person A (YOU): Messages where sender = "YOU"
- Person B ({phone_number}): Messages where sender = "{phone_number}"
- Total messages in this sample: {message_count}
- Date range: {date_range}

MESSAGES:
{formatted_messages}

---

ANALYSIS TASKS:

1. RELATIONSHIP TYPE
Determine the nature of this relationship (friends, romantic, family, professional, etc.)
Provide a DEEP analysis with as many citations as possible. Every notable message that reveals relationship dynamics should be cited.

2. COMMUNICATION INITIATION
Calculate statistics:
- Total conversations initiated by YOU
- Total conversations initiated by {phone_number}
- Percentage breakdown
- Distribution histogram (morning/afternoon/evening/night)
Cite examples of each person initiating conversations across different times and contexts.

3. RESPONSE PATTERNS
Calculate statistics and create a response time histogram:
- Response time distribution (buckets: <1min, 1-5min, 5-30min, 30min-1hr, 1-6hr, 6-24hr, 1+ days)
- Count of messages in each bucket for YOU
- Count of messages in each bucket for {phone_number}
- Median response time for each person (more useful than average)
- Identify and EXCLUDE logistics exchanges (meeting up, calling) from average calculations
- Note exceptions: "Getting ready to call/meet" messages that get instant responses
Cite examples showing:
- Typical response patterns
- Fast responses (and their context)
- Slow responses (and their context)
- Logistics-related rapid exchanges (meeting up, coordinating calls)
- Response pattern changes over time

4. TONE AND SENTIMENT
What is the emotional tone of the conversation? Provide EXTENSIVE citations showing:
- Positive moments (cite all you can find)
- Negative moments (cite all you can find)
- Neutral exchanges (cite representative examples)
- Emotional shifts (cite before/after pairs)
- Humor or sarcasm (cite all instances)

5. KEY TOPICS
What do they primarily discuss? For EACH major topic, provide multiple citations:
- Topic 1: [Name] - cite all relevant messages
- Topic 2: [Name] - cite all relevant messages
- Topic 3: [Name] - cite all relevant messages
Continue for all major topics found.

6. CONFLICT INDICATORS
Are there signs of tension, disagreement, or conflict? Cite EVERY instance:
- Direct disagreements
- Passive aggressive language
- Ignored messages
- Short/cold responses
- Apologetic language
If none found, state "No conflict indicators detected in sample"

7. EMOTIONAL SUPPORT
Do they provide emotional support to each other? Cite ALL instances:
- Expressions of concern
- Offering help or advice
- Validation and encouragement
- Checking in on wellbeing
- Celebrating achievements
If none found, state "No emotional support instances in sample"

---

OUTPUT FORMAT:

For each analysis task, provide a RICH, DETAILED analysis:

**Assessment**: [Your conclusion - can be multiple paragraphs for complex findings]

**Evidence**: [Provide DOZENS of citations if available - use EVERY relevant message]
- [DATE TIME | SENDER: "exact message"] → [Detailed explanation of significance]
- [DATE TIME | SENDER: "exact message"] → [Detailed explanation]
- [DATE TIME | SENDER: "exact message"] → [Detailed explanation]
[Continue with all relevant citations - aim for completeness, not brevity]

**Statistics**: [For tasks 2 and 3, provide calculated metrics]
- Metric 1: X
- Metric 2: Y
- Metric 3: Z

**Confidence**: HIGH/MEDIUM/LOW

---

IMPORTANT:
- DO NOT summarize - cite everything that stands out
- For long conversations with 100+ messages, expect to cite 30-50+ messages across all tasks
- Use exact message text in every citation
- Include date and time in every citation
- More evidence is ALWAYS better than less
- Every interesting exchange deserves citation
- Look for patterns and cite multiple examples of the same pattern
- If you cannot find evidence for a task, explicitly state "Insufficient evidence in this sample"
"""

        return prompt

    def analyze_conversation(self, messages: List[Dict], phone_number: str) -> Dict[str, Any]:
        """
        Analyze a conversation using LLM with citation-based approach.

        Args:
            messages: List of message dictionaries
            phone_number: Phone number of the other participant

        Returns:
            Dictionary containing analysis results
        """
        print(f"\n{'='*80}")
        print(f"STAGE 2 CITATION ANALYSIS: {phone_number}")
        print(f"{'='*80}\n")

        print(f"Model: {self.model_name}")
        print(f"Messages: {len(messages)}")
        print(f"Building prompt...")

        # Build prompt
        prompt = self.build_analysis_prompt(messages, phone_number)

        print(f"Prompt length: {len(prompt)} characters")
        print(f"Sending to LLM...\n")

        # Track resource usage
        process = psutil.Process()
        start_time = time.time()
        start_cpu = process.cpu_percent(interval=0.1)
        start_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Call LLM
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    'role': 'system',
                    'content': '''You are a relationship dynamics analyst specializing in text message conversation analysis.

Your task is to analyze conversations and provide evidence-based assessments with precise citations.

CRITICAL RULES:
1. Every claim MUST be supported by exact message citations
2. Citation format: [DATE TIME | SENDER: "exact message text"]
   Example: [2018-12-21 10:37PM | YOU: "Yo"]
3. Use multiple citations to support claims: [citation1] [citation2]
4. Never make claims without direct evidence
5. State "Insufficient evidence" when you cannot support a claim
6. Include confidence levels: HIGH, MEDIUM, or LOW

Your analysis should be precise, factual, and verifiable.'''
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 0.3,  # Lower temperature for more factual analysis
                'num_predict': 8000  # Allow long responses
            }
        )

        # Calculate resource usage
        end_time = time.time()
        end_cpu = process.cpu_percent(interval=0.1)
        end_memory = process.memory_info().rss / 1024 / 1024  # MB

        elapsed_time = end_time - start_time
        memory_used = end_memory - start_memory

        analysis_text = response['message']['content']

        print("Analysis complete!")
        print(f"Response length: {len(analysis_text)} characters")
        print(f"Elapsed time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print(f"Memory used: {memory_used:.2f} MB")
        print(f"CPU usage: {end_cpu:.1f}%\n")

        return {
            'phone_number': phone_number,
            'model': self.model_name,
            'analysis_date': datetime.now().isoformat(),
            'messages_analyzed': len(messages),
            'analysis_text': analysis_text,
            'prompt_length': len(prompt),
            'response_length': len(analysis_text),
            'performance': {
                'elapsed_seconds': elapsed_time,
                'elapsed_minutes': elapsed_time / 60,
                'memory_mb': memory_used,
                'cpu_percent': end_cpu,
                'tokens_per_second': None  # Ollama doesn't expose this easily
            }
        }


def main(phone_number: str = "309-948-9979", model: str = "llama3.2"):
    """Run citation-based analysis on a conversation."""

    # Find conversation file
    conversations_dir = Path(__file__).parent.parent / "data" / "output" / "all_conversations"
    matches = list(conversations_dir.glob(f"*{phone_number}*.json"))
    matches = [f for f in matches if not f.name.endswith("_analysis.json")]

    if not matches:
        print(f"❌ No conversation found for {phone_number}")
        return

    # Use the file with more messages
    conv_file = max(matches, key=lambda f: int(f.name.split('_')[1]))

    print(f"Loading: {conv_file.name}")

    # Load conversation
    with open(conv_file, 'r') as f:
        data = json.load(f)

    messages = data.get('messages', [])

    # Initialize analyzer
    analyzer = CitationAnalyzer(model_name=model)

    # Run analysis
    results = analyzer.analyze_conversation(messages, phone_number)

    # Save results
    output_file = conv_file.parent / f"{conv_file.stem}_citation_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Analysis saved to: {output_file.name}\n")

    # Print analysis
    print(f"\n{'='*80}")
    print("ANALYSIS RESULTS")
    print(f"{'='*80}\n")
    print(results['analysis_text'])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Stage 2 citation-based analysis")
    parser.add_argument("--phone", type=str, default="309-948-9979", help="Phone number to analyze")
    parser.add_argument("--model", type=str, default="llama3.2", help="Ollama model to use")

    args = parser.parse_args()

    main(phone_number=args.phone, model=args.model)
