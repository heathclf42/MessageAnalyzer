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

    def extract_date_range(self, response_text: str) -> Dict[str, str]:
        """Extract date range from citations in response."""
        import re

        # Find all dates in citations
        date_pattern = r'\[(\d{4}-\d{2}-\d{2})'
        dates = re.findall(date_pattern, response_text)

        if dates:
            dates.sort()
            return {
                'start_date': dates[0],
                'end_date': dates[-1],
                'date_range': f"{dates[0]} to {dates[-1]}"
            }

        return {'start_date': None, 'end_date': None, 'date_range': 'Unknown'}

    def validate_metrics(self, response_text: str) -> Dict[str, Any]:
        """Validate that all required metrics are present and parseable."""
        import re

        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Check for required sections
        required_sections = [
            'SENTIMENT SCORES',
            'PERSONALITY TRAITS',
            'PSYCHOLOGICAL TRAITS',
            'EMOTIONAL STATES',
            'ARCHETYPE DISTRIBUTION',
            'COMMUNICATION METRICS',
            'RELATIONSHIP EVOLUTION'
        ]

        for section in required_sections:
            if section not in response_text:
                validation['errors'].append(f"Missing required section: {section}")
                validation['is_valid'] = False

        # Validate sentiment scores are present and parseable
        you_sentiment = re.search(r'(?:\*\*)?YOU(?:\*\*)?:.*?Positive:\s*(\d+)/100', response_text, re.DOTALL)
        them_sentiment = re.search(r'(?:\*\*)?THEM(?:\*\*)?:.*?Positive:\s*(\d+)/100', response_text, re.DOTALL)

        if not you_sentiment:
            validation['errors'].append("Could not parse YOU sentiment scores")
            validation['is_valid'] = False

        if not them_sentiment:
            validation['errors'].append("Could not parse THEM sentiment scores")
            validation['is_valid'] = False

        # Check for citation format
        citations = re.findall(r'\[\d{4}-\d{2}-\d{2}', response_text)
        if len(citations) < 3:
            validation['warnings'].append(f"Only {len(citations)} citations found, expected at least 3")

        # Check for academic references (should be forbidden)
        if re.search(r'References:|et al\.|Ekman|Russell|Frijda', response_text):
            validation['warnings'].append("Found possible academic references (should be citations only)")

        # Check for metric/narrative discrepancies (CRITICAL - triggers retry)
        if you_sentiment and them_sentiment:
            you_pos = int(you_sentiment.group(1))
            them_pos = int(them_sentiment.group(1))

            # Extract overall tone statements (capture multiple words for "VERY POSITIVE" etc.)
            you_tone = re.search(r'Overall Tone:\s*([\w\s]+?)(?:\n|$)', response_text)
            them_tone_match = re.search(r'THEM.*?Overall Tone:\s*([\w\s]+?)(?:\n|$)', response_text, re.DOTALL)

            if you_tone:
                tone = you_tone.group(1).strip().upper()
                # Check if numerical scores match narrative tone - ERRORS trigger retry
                if you_pos >= 70 and tone not in ['POSITIVE', 'VERY POSITIVE']:
                    validation['errors'].append(f"YOU sentiment score ({you_pos}) suggests POSITIVE but tone is '{tone}'")
                    validation['is_valid'] = False
                elif you_pos <= 40 and tone not in ['NEGATIVE', 'VERY NEGATIVE']:
                    validation['errors'].append(f"YOU sentiment score ({you_pos}) suggests NEGATIVE but tone is '{tone}'")
                    validation['is_valid'] = False

            if them_tone_match:
                tone = them_tone_match.group(1).strip().upper()
                if them_pos >= 70 and tone not in ['POSITIVE', 'VERY POSITIVE']:
                    validation['errors'].append(f"THEM sentiment score ({them_pos}) suggests POSITIVE but tone is '{tone}'")
                    validation['is_valid'] = False
                elif them_pos <= 40 and tone not in ['NEGATIVE', 'VERY NEGATIVE']:
                    validation['errors'].append(f"THEM sentiment score ({them_pos}) suggests NEGATIVE but tone is '{tone}'")
                    validation['is_valid'] = False

        return validation

    def refine_prompt_with_llm(self, original_prompt: str, failed_output: str, validation_errors: List[str]) -> str:
        """Use LLM to refine the prompt based on validation failures."""

        meta_prompt = f"""You are a prompt engineering expert. Analyze why the LLM failed to produce the correct output format.

ORIGINAL PROMPT:
{original_prompt[:1000]}...

FAILED OUTPUT:
{failed_output[:1000]}...

VALIDATION ERRORS:
{chr(10).join(f"- {error}" for error in validation_errors)}

TASK:
The LLM must produce output with these sections in THIS EXACT FORMAT:

### SENTIMENT SCORES (0-100 scale)

**YOU:**
* Positive: X/100
* Neutral: X/100
* Negative: X/100
* Overall Tone: POSITIVE/NEUTRAL/NEGATIVE

**THEM:**
* Positive: X/100
...

Generate a BRIEF additional instruction (2-3 sentences) to add to the system prompt that will ensure the LLM follows the exact format. Focus on the specific errors that occurred.

RESPOND WITH ONLY THE ADDITIONAL INSTRUCTION, NOTHING ELSE."""

        try:
            meta_response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': meta_prompt}],
                options={'temperature': 0.1, 'num_predict': 200}
            )

            additional_instruction = meta_response['message']['content'].strip()
            print(f"  🧠 Meta-LLM suggests: {additional_instruction[:100]}...")
            return additional_instruction

        except Exception as e:
            print(f"  ⚠️  Meta-LLM refinement failed: {e}")
            return "Follow the exact format shown in the template. Use precise section headers and score formats."

    def parse_weekly_response(self, response_text: str, week_number: int) -> Dict[str, Any]:
        """Parse LLM response into structured metrics with validation."""

        # Extract date range
        date_info = self.extract_date_range(response_text)

        # Validate metrics
        validation = self.validate_metrics(response_text)

        result = {
            'week_number': week_number,
            'raw_analysis': response_text,
            'date_range': date_info['date_range'],
            'start_date': date_info['start_date'],
            'end_date': date_info['end_date'],
            'validation': validation
        }

        # Log validation issues
        if not validation['is_valid']:
            print(f"  ⚠️  Validation errors in Week {week_number + 1}:")
            for error in validation['errors']:
                print(f"     - {error}")

        if validation['warnings']:
            print(f"  ⚠️  Warnings in Week {week_number + 1}:")
            for warning in validation['warnings']:
                print(f"     - {warning}")

        return result

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
        max_context_weeks: int = 4,
        incremental_save_path: Path = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze conversation week-by-week with cumulative context.

        Args:
            messages: All conversation messages
            phone_number: Other participant's phone number
            max_context_weeks: After this many weeks, start compressing history
            incremental_save_path: If provided, save progress after each week

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

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Analyzing Week {week_num + 1} ({len(week_messages)} messages)...", flush=True)

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

            # Call LLM with retry logic
            max_retries = 5
            retry_count = 0
            analysis = None
            prompt_versions = []  # Track all prompt variations tried
            meta_llm_refinement = None

            while retry_count <= max_retries:
                system_prompt = '''You are a relationship psychiatrist analyzing text message conversations. Provide both structured metrics AND thoughtful narrative insights.

CRITICAL RULES:
1. Archetype names: ONLY use these exact 12: Innocent, Sage, Explorer, Outlaw, Magician, Hero, Lover, Jester, Everyperson, Caregiver, Ruler, Creator
2. Citations: ONLY cite actual messages from THIS conversation - NO academic papers, NO research citations
3. Citation format: [DATE TIME | SENDER: "exact message"]
4. Scores: Exact numbers (e.g., "75/100") never ranges
5. Be thoughtful: Provide narrative insights, observations, and professional analysis alongside the metrics
6. Be honest: Include observations, caveats, and nuanced interpretations where appropriate

CRITICAL TONE CONSISTENCY RULES:
- If Positive score ≥70/100, Overall Tone MUST be "POSITIVE" or "VERY POSITIVE"
- If Positive score ≤40/100, Overall Tone MUST be "NEGATIVE" or "VERY NEGATIVE"
- If Positive score 41-69/100, Overall Tone should be "NEUTRAL" or "MIXED"
- Ensure numerical scores and tone labels are internally consistent'''

                # Add refinements on retry
                if retry_count > 0:
                    if retry_count == 1:
                        # First retry: add generic strict instructions
                        system_prompt += f'''

⚠️ RETRY ATTEMPT 1/{max_retries}
Your previous response had validation errors. You MUST:
- Include ALL required sections: SENTIMENT SCORES, PERSONALITY TRAITS, PSYCHOLOGICAL TRAITS, EMOTIONAL STATES, ARCHETYPE DISTRIBUTION, COMMUNICATION METRICS, RELATIONSHIP EVOLUTION
- Use EXACT format "YOU:" and "THEM:" with "Positive: X/100" scores
- Include at least 3 message citations in format [YYYY-MM-DD HH:MM:SS AM/PM | SENDER: "message"]
- Match numerical scores with Overall Tone (70+ = POSITIVE, 40- = NEGATIVE)
- NO academic references or external sources'''
                    else:
                        # Second retry: use meta-LLM to refine prompt
                        if analysis and not analysis['validation']['is_valid']:
                            meta_llm_refinement = self.refine_prompt_with_llm(
                                prompt,
                                analysis['raw_analysis'],
                                analysis['validation']['errors']
                            )
                            system_prompt += f'''

⚠️ RETRY ATTEMPT 2/{max_retries} - META-LLM REFINED INSTRUCTIONS:
{meta_llm_refinement}'''

                # Track this prompt version (store full prompts for debugging)
                prompt_versions.append({
                    'attempt': retry_count + 1,
                    'system_prompt': system_prompt,
                    'system_prompt_length': len(system_prompt),
                    'has_meta_refinement': meta_llm_refinement is not None,
                    'meta_refinement': meta_llm_refinement,
                    'temperature': 0.3 if retry_count == 0 else 0.2
                })

                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {
                            'role': 'system',
                            'content': system_prompt
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    options={
                        'temperature': 0.3 if retry_count == 0 else 0.2,  # Lower temperature on retry
                        'num_predict': 4000
                    }
                )

                # Calculate performance metrics
                end_time = time.time()
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                elapsed = end_time - start_time
                memory_used = end_memory - start_memory

                analysis = self.parse_weekly_response(response['message']['content'], week_num)

                # Add validation result to this prompt version
                prompt_versions[-1]['validation_passed'] = analysis['validation']['is_valid']
                prompt_versions[-1]['validation_errors'] = analysis['validation']['errors']
                prompt_versions[-1]['validation_warnings'] = analysis['validation']['warnings']

                # Check if validation passed
                if analysis['validation']['is_valid']:
                    break  # Success!

                # If critical errors and retries remain, try again
                if retry_count < max_retries:
                    print(f"  🔄 Retrying due to validation errors (attempt {retry_count + 2}/{max_retries + 1})...")
                    retry_count += 1
                    start_time = time.time()  # Reset timer for retry
                else:
                    print(f"  ❌ Max retries reached. Saving analysis with validation errors.")
                    break

            # Add performance data
            analysis['performance'] = {
                'elapsed_seconds': elapsed,
                'elapsed_minutes': elapsed / 60,
                'memory_mb': memory_used,
                'prompt_length': len(prompt),
                'response_length': len(response['message']['content']),
                'cpu_percent': process.cpu_percent(),
                'retry_count': retry_count,
                'prompt_versions': prompt_versions,
                'final_prompt_worked': analysis['validation']['is_valid']
            }

            all_analyses.append(analysis)

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] ✓ Week {week_num + 1} complete ({elapsed:.1f}s, {len(response['message']['content'])} chars)\n", flush=True)

            # Save incremental progress
            if incremental_save_path:
                total_time = sum(w.get('performance', {}).get('elapsed_seconds', 0) for w in all_analyses)
                total_chars = sum(w.get('performance', {}).get('response_length', 0) for w in all_analyses)

                incremental_data = {
                    'phone_number': phone_number,
                    'model': self.model_name,
                    'analysis_date': datetime.now().isoformat(),
                    'total_weeks': len(all_analyses),
                    'total_weeks_planned': len(weeks),
                    'progress_percent': (len(all_analyses) / len(weeks) * 100),
                    'performance_summary': {
                        'total_time_seconds': total_time,
                        'total_time_minutes': total_time / 60,
                        'average_time_per_week': total_time / len(all_analyses),
                        'total_response_characters': total_chars,
                        'average_chars_per_week': total_chars / len(all_analyses)
                    },
                    'weekly_analyses': all_analyses
                }

                with open(incremental_save_path, 'w') as f:
                    json.dump(incremental_data, f, indent=2)

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

    # Set up incremental save path
    suffix = "_test" if test_mode else ""
    incremental_file = conversations_dir / f"{phone_number}_weekly_metrics{suffix}_PROGRESS.json"

    # Run weekly analysis
    weekly_analyses = analyzer.analyze_conversation_weekly(
        messages,
        phone_number,
        incremental_save_path=incremental_file
    )

    # Calculate aggregate stats
    total_time = sum(w.get('performance', {}).get('elapsed_seconds', 0) for w in weekly_analyses)
    total_chars = sum(w.get('performance', {}).get('response_length', 0) for w in weekly_analyses)
    avg_time_per_week = total_time / len(weekly_analyses) if weekly_analyses else 0

    # Save results
    suffix = "_test" if test_mode else ""
    output_file = conversations_dir / f"{phone_number}_weekly_metrics{suffix}.json"

    output_data = {
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
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Clean up progress file
    if incremental_file.exists():
        incremental_file.unlink()

    # Save debug prompt log (tracks what prompts worked)
    debug_file = conversations_dir / f"{phone_number}_prompt_debug{suffix}.json"
    prompt_effectiveness = []

    for week in weekly_analyses:
        week_num = week['week_number']
        prompt_versions = week['performance'].get('prompt_versions', [])

        # Only track if retries occurred
        if len(prompt_versions) > 1:
            prompt_effectiveness.append({
                'week_number': week_num + 1,
                'date_range': week.get('date_range', 'Unknown'),
                'attempts': len(prompt_versions),
                'final_success': week['validation']['is_valid'],
                'prompt_versions': prompt_versions,
                'validation_errors': week['validation'].get('errors', []),
                'validation_warnings': week['validation'].get('warnings', [])
            })

    if prompt_effectiveness:
        with open(debug_file, 'w') as f:
            json.dump({
                'phone_number': phone_number,
                'model': model,
                'analysis_date': datetime.now().isoformat(),
                'total_weeks_with_retries': len(prompt_effectiveness),
                'prompt_effectiveness_log': prompt_effectiveness
            }, f, indent=2)

        print(f"\n📝 Prompt debug log saved: {debug_file.name}")
        print(f"   {len(prompt_effectiveness)} week(s) required retries")

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
