#!/usr/bin/env python3
"""
Weekly Metrics Analyzer with Cumulative Context (Option B)
Analyzes conversations week-by-week with expanding context window.
"""

import json
import ollama
import time
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict


class WeeklyMetricsAnalyzer:
    """Analyzes conversations week-by-week with cumulative context."""

    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

    def group_messages_by_week(self, messages: List[Dict]) -> Dict[int, List[Dict]]:
        """Group messages into weekly buckets."""
        if not messages:
            return {}

        # Parse first message date to establish week 0
        first_date = datetime.fromisoformat(messages[0]['date'].replace('Z', '+00:00'))

        weeks = defaultdict(list)
        for msg in messages:
            msg_date = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))
            week_number = (msg_date - first_date).days // 7
            weeks[week_number].append(msg)

        return dict(weeks)

    def format_messages_for_prompt(self, messages: List[Dict]) -> str:
        """Format messages for LLM prompt."""
        formatted = []
        for msg in messages:
            if msg.get('text'):
                date = msg.get('date_formatted', 'Unknown date')
                sender = msg.get('sender', 'Unknown')
                text = msg['text']
                formatted.append(f"[{date}] {sender}: \"{text}\"")
        return '\n'.join(formatted)

    def build_weekly_prompt(
        self,
        week_number: int,
        week_messages: List[Dict],
        historical_summary: str,
        phone_number: str
    ) -> str:
        """Build prompt for weekly analysis."""

        formatted_messages = self.format_messages_for_prompt(week_messages)

        # Get date range for this week
        dates = [m.get('date_formatted', '') for m in week_messages if m.get('date_formatted')]
        date_range = f"{dates[0]} to {dates[-1]}" if dates else "Unknown"

        prompt = f"""Analyze this week of conversation and provide detailed metrics with citations.

WEEK: {week_number + 1}
DATE RANGE: {date_range}
PARTICIPANTS: YOU vs {phone_number}

"""

        # Add historical context if available
        if historical_summary:
            prompt += f"""HISTORICAL CONTEXT (Previous Weeks):
{historical_summary}

---

"""

        prompt += f"""MESSAGES THIS WEEK:
{formatted_messages}

---

TASK: Analyze THIS WEEK and output ALL metrics with citations.

## OUTPUT FORMAT:

=== WEEK {week_number + 1} ANALYSIS ===

### SENTIMENT SCORES (0-100 scale)
YOU:
- Positive: [score]/100
- Neutral: [score]/100
- Negative: [score]/100
- Overall Tone: [POSITIVE/NEUTRAL/NEGATIVE/MIXED]

THEM:
- Positive: [score]/100
- Neutral: [score]/100
- Negative: [score]/100
- Overall Tone: [POSITIVE/NEUTRAL/NEGATIVE/MIXED]

Key Citations:
- [DATE TIME | SENDER: "message"] → [Why this is positive/negative]
- [DATE TIME | SENDER: "message"] → [Significance]

### PERSONALITY TRAITS (Big 5, 0-100 scale)
YOU:
- Extroversion: [score]/100
- Neuroticism: [score]/100
- Agreeableness: [score]/100
- Conscientiousness: [score]/100
- Openness: [score]/100

THEM:
- Extroversion: [score]/100
- Neuroticism: [score]/100
- Agreeableness: [score]/100
- Conscientiousness: [score]/100
- Openness: [score]/100

Key Citations:
- [DATE TIME | SENDER: "message"] → [Which trait this demonstrates]

### PSYCHOLOGICAL TRAITS (0-100 scale)
YOU:
- Narcissism: [score]/100
- Toxicity: [score]/100

THEM:
- Narcissism: [score]/100
- Toxicity: [score]/100

Key Citations:
- [DATE TIME | SENDER: "message"] → [Evidence of narcissism/toxicity if present]

### EMOTIONAL STATES (0-100 scale)
YOU:
- Joy: [score]/100
- Love: [score]/100
- Sadness: [score]/100
- Anger: [score]/100

THEM:
- Joy: [score]/100
- Love: [score]/100
- Sadness: [score]/100
- Anger: [score]/100

Key Citations:
- [DATE TIME | SENDER: "message"] → [Which emotion this expresses]

### ARCHETYPE DISTRIBUTION (% of total)
YOU Top 7 (USE EXACT NAMES: Innocent, Sage, Explorer, Outlaw, Magician, Hero, Lover, Jester, Everyperson, Caregiver, Ruler, Creator):
- Sage: X%
- Hero: X%
- Explorer: X%
- Lover: X%
- Creator: X%
- Jester: X%
- Caregiver: X%

THEM Top 7 (USE EXACT NAMES: Innocent, Sage, Explorer, Outlaw, Magician, Hero, Lover, Jester, Everyperson, Caregiver, Ruler, Creator):
- Hero: X%
- Sage: X%
- Explorer: X%
- Lover: X%
- Creator: X%
- Jester: X%
- Magician: X%

### COMMUNICATION METRICS
Message Activity:
- Total messages: [number]
- YOU messages: [number] ([percentage]%)
- THEM messages: [number] ([percentage]%)

Initiation:
- YOU initiated: [number] conversations
- THEM initiated: [number] conversations

Response Times:
- YOU median: [X] minutes
- THEM median: [X] minutes
- Fastest exchange: [TIME | conversation snippet]
- Slowest exchange: [TIME | conversation snippet]

### EMOTIONAL INDICATORS
Toxicity:
- YOU: [X]% (count: [N])
- THEM: [X]% (count: [N])

Sarcasm:
- YOU: [X]% (count: [N])
- THEM: [X]% (count: [N])

Support Exchanges: [count]
Citations:
- [DATE TIME | Example of support]

Conflict Instances: [count]
Citations:
- [DATE TIME | Example of conflict if any]

### TOPICS (with message counts)
1. Topic Name: [count] messages
   - [DATE TIME | Example citation]
2. Topic Name: [count] messages
   - [DATE TIME | Example citation]
[Continue for all major topics...]

### NOTABLE MOMENTS
List 3-5 most significant exchanges this week:
1. [DATE TIME | Description] - Citation: "message"
2. [DATE TIME | Description] - Citation: "message"
[Continue...]

### RELATIONSHIP EVOLUTION
How did the relationship change THIS WEEK compared to history?
- [Describe any shifts in tone, intimacy, topics, patterns]
- Key evidence: [Citations]

---

OUTPUT REQUIREMENTS:
1. **Structured Metrics**: Provide EXACT numerical scores (e.g., "75/100" not ranges)
2. **Citations**: Include 3-5 message citations per section: [DATE TIME | SENDER: "exact message"]
3. **Archetypes**: Use ONLY these 12: Innocent, Sage, Explorer, Outlaw, Magician, Hero, Lover, Jester, Everyperson, Caregiver, Ruler, Creator
4. **NO Academic References**: Do NOT cite research papers or external sources
5. **Narrative Insights**: Provide thoughtful observations alongside metrics - be a psychiatrist, not just a data collector
6. **Professional Tone**: Include interpretations, caveats, and nuanced analysis where appropriate
7. **Honest Assessment**: If data is limited, acknowledge it while providing your best clinical interpretation
"""

        return prompt

    def parse_weekly_response(self, response_text: str, week_number: int) -> Dict[str, Any]:
        """Parse LLM response into structured metrics."""
        # TODO: Implement robust parsing
        # For now, return raw text with metadata
        return {
            'week_number': week_number,
            'raw_analysis': response_text,
            # Will add structured parsing later
        }

    def compress_historical_weeks(self, week_analyses: List[Dict]) -> str:
        """Compress multiple weeks into summary for context."""
        # TODO: Extract scores and create compressed summary
        # For now, create basic summary

        summary = f"HISTORICAL SUMMARY (Weeks 1-{len(week_analyses)}):\n\n"
        summary += f"Total weeks analyzed: {len(week_analyses)}\n"
        summary += "Key patterns identified across all previous weeks.\n"
        summary += "(Full metric aggregation to be implemented)\n"

        return summary

    def analyze_conversation_weekly(
        self,
        messages: List[Dict],
        phone_number: str,
        max_context_weeks: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Analyze conversation week-by-week with cumulative context.

        Args:
            messages: All conversation messages
            phone_number: Other participant's phone number
            max_context_weeks: After this many weeks, start compressing history

        Returns:
            List of weekly analyses with full metrics
        """

        # Group messages by week
        weeks = self.group_messages_by_week(messages)

        print(f"\n{'='*80}")
        print(f"WEEKLY ANALYSIS: {phone_number}")
        print(f"{'='*80}\n")
        print(f"Total weeks: {len(weeks)}")
        print(f"Total messages: {len(messages)}\n")

        all_analyses = []
        historical_summary = ""

        for week_num in sorted(weeks.keys()):
            week_messages = weeks[week_num]

            print(f"Analyzing Week {week_num + 1} ({len(week_messages)} messages)...")

            # Build prompt with historical context
            prompt = self.build_weekly_prompt(
                week_num,
                week_messages,
                historical_summary,
                phone_number
            )

            # Track performance
            process = psutil.Process()
            start_time = time.time()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Call LLM
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': '''You are a relationship psychiatrist analyzing text message conversations. Provide both structured metrics AND thoughtful narrative insights.

CRITICAL RULES:
1. Archetype names: ONLY use these exact 12: Innocent, Sage, Explorer, Outlaw, Magician, Hero, Lover, Jester, Everyperson, Caregiver, Ruler, Creator
2. Citations: ONLY cite actual messages from THIS conversation - NO academic papers, NO research citations
3. Citation format: [DATE TIME | SENDER: "exact message"]
4. Scores: Exact numbers (e.g., "75/100") never ranges
5. Be thoughtful: Provide narrative insights, observations, and professional analysis alongside the metrics
6. Be honest: Include observations, caveats, and nuanced interpretations where appropriate'''
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.3,
                    'num_predict': 4000
                }
            )

            # Calculate performance metrics
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            elapsed = end_time - start_time
            memory_used = end_memory - start_memory

            analysis = self.parse_weekly_response(response['message']['content'], week_num)

            # Add performance data
            analysis['performance'] = {
                'elapsed_seconds': elapsed,
                'elapsed_minutes': elapsed / 60,
                'memory_mb': memory_used,
                'prompt_length': len(prompt),
                'response_length': len(response['message']['content']),
                'cpu_percent': process.cpu_percent()
            }

            all_analyses.append(analysis)

            print(f"✓ Week {week_num + 1} complete ({elapsed:.1f}s, {len(response['message']['content'])} chars)\n")

            # Update historical context
            if week_num + 1 >= max_context_weeks:
                # Compress old weeks
                historical_summary = self.compress_historical_weeks(all_analyses[:-1])
            else:
                # Keep expanding context
                historical_summary += f"\nWeek {week_num + 1} Summary:\n{analysis['raw_analysis'][:500]}...\n"

        return all_analyses


def main(phone_number: str = "309-948-9979", model: str = "llama3.2", test_mode: bool = False, max_messages: int = 100):
    """Run weekly analysis on a conversation."""

    conversations_dir = Path(__file__).parent.parent / "data" / "output" / "all_conversations"

    # Find conversation file
    matches = list(conversations_dir.glob(f"*{phone_number}*.json"))
    matches = [f for f in matches if not any(x in f.name for x in ["_analysis", "_citation", "_weekly", "_llm"])]

    if not matches:
        print(f"❌ No conversation found for {phone_number}")
        return

    conv_file = max(matches, key=lambda f: int(f.name.split('_')[1]))

    print(f"Loading: {conv_file.name}")

    with open(conv_file, 'r') as f:
        data = json.load(f)

    messages = data.get('messages', [])

    # TEST MODE: Use only first N messages for rapid iteration
    if test_mode:
        messages = messages[:max_messages]
        print(f"\n⚡ TEST MODE: Using first {len(messages)} messages only")
        print(f"This allows rapid prompt iteration (~30 sec vs 10+ min)\n")

    # Initialize analyzer
    analyzer = WeeklyMetricsAnalyzer(model_name=model)

    # Run weekly analysis
    weekly_analyses = analyzer.analyze_conversation_weekly(messages, phone_number)

    # Calculate aggregate stats
    total_time = sum(w.get('performance', {}).get('elapsed_seconds', 0) for w in weekly_analyses)
    total_chars = sum(w.get('performance', {}).get('response_length', 0) for w in weekly_analyses)
    avg_time_per_week = total_time / len(weekly_analyses) if weekly_analyses else 0

    # Save results
    suffix = "_test" if test_mode else ""
    output_file = conversations_dir / f"{phone_number}_weekly_metrics{suffix}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'phone_number': phone_number,
            'model': model,
            'analysis_date': datetime.now().isoformat(),
            'total_weeks': len(weekly_analyses),
            'performance_summary': {
                'total_time_seconds': total_time,
                'total_time_minutes': total_time / 60,
                'average_time_per_week': avg_time_per_week,
                'total_response_characters': total_chars,
                'average_chars_per_week': total_chars / len(weekly_analyses) if weekly_analyses else 0
            },
            'weekly_analyses': weekly_analyses
        }, f, indent=2)

    print(f"\n{'='*80}")
    print(f"✅ Weekly analysis complete: {output_file.name}")
    print(f"{'='*80}")
    print(f"Total time: {total_time/60:.2f} minutes")
    print(f"Average per week: {avg_time_per_week:.1f} seconds")
    print(f"Total output: {total_chars:,} characters")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run weekly metrics analysis")
    parser.add_argument("--phone", type=str, default="309-948-9979", help="Phone number")
    parser.add_argument("--model", type=str, default="llama3.2", help="Ollama model")
    parser.add_argument("--test", action="store_true", help="Test mode: use only first 100 messages for rapid iteration")
    parser.add_argument("--max-messages", type=int, default=100, help="Max messages in test mode (default: 100)")

    args = parser.parse_args()

    main(phone_number=args.phone, model=args.model, test_mode=args.test, max_messages=args.max_messages)
