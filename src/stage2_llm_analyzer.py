#!/usr/bin/env python3
"""
Stage 2: Dual LLM Cumulative Analysis

Uses Llama 3.2-8B and Qwen 2.5-7B to perform conversation-level psychological
analysis with cumulative context management, evidence citation, and trend tracking.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import ollama


class CumulativeSummaryManager:
    """Manages compression and formatting of cumulative conversation summaries."""

    def __init__(self):
        self.chunk_summaries = []

    def add_chunk_summary(self, chunk_id: int, summary: Dict[str, Any]):
        """Add a chunk's analysis summary to the cumulative history."""
        self.chunk_summaries.append({
            'chunk_id': chunk_id,
            'summary': summary
        })

    def get_compressed_summary(self, current_chunk_id: int) -> str:
        """
        Generate compressed summary of all previous chunks.

        Strategy:
        - Chunks 1-3: Keep detailed summaries
        - Chunks 4-6: Medium compression
        - Chunks 7+: High compression (early chunks summarized broadly)
        """
        if current_chunk_id <= 1:
            return "This is the first chunk of the conversation. No previous analysis available."

        # Get all previous summaries
        previous = [s for s in self.chunk_summaries if s['chunk_id'] < current_chunk_id]

        if not previous:
            return "This is the first chunk of the conversation. No previous analysis available."

        # Different compression based on chunk count
        if current_chunk_id <= 3:
            # Early conversation - keep detailed
            return self._detailed_summary(previous)
        elif current_chunk_id <= 6:
            # Medium conversation - moderate compression
            return self._medium_compression_summary(previous)
        else:
            # Long conversation - high compression for old chunks
            return self._hierarchical_compression_summary(previous, current_chunk_id)

    def _detailed_summary(self, summaries: List[Dict]) -> str:
        """Keep full detail for early chunks."""
        parts = ["PREVIOUS ANALYSIS:\n"]

        for s in summaries:
            chunk_id = s['chunk_id']
            summary = s['summary']

            parts.append(f"\n--- Chunk {chunk_id} ---")
            if 'cumulative_summary' in summary:
                parts.append(summary['cumulative_summary'])

        return '\n'.join(parts)

    def _medium_compression_summary(self, summaries: List[Dict]) -> str:
        """Moderate compression - keep key findings."""
        parts = ["PREVIOUS ANALYSIS SUMMARY:\n"]

        # Get latest summary (has most up-to-date cumulative view)
        if summaries:
            latest = summaries[-1]['summary']
            if 'cumulative_summary' in latest:
                parts.append(f"Overall assessment (through Chunk {summaries[-1]['chunk_id']}):")
                parts.append(latest['cumulative_summary'])

            # Add any notable trends
            if 'You' in latest:
                you_data = latest['You']
                parts.append(f"\nYou - Key patterns:")
                for dimension in ['toxicity', 'sentiment', 'sarcasm']:
                    if dimension in you_data and 'trend' in you_data[dimension]:
                        trend = you_data[dimension]['trend']
                        if trend != 'stable':
                            parts.append(f"  - {dimension.capitalize()}: {trend}")

        return '\n'.join(parts)

    def _hierarchical_compression_summary(self, summaries: List[Dict], current_chunk: int) -> str:
        """High compression for long conversations."""
        parts = ["PREVIOUS ANALYSIS SUMMARY:\n"]

        # Divide into sections
        early = [s for s in summaries if s['chunk_id'] <= 3]
        middle = [s for s in summaries if 3 < s['chunk_id'] <= current_chunk - 3]
        recent = [s for s in summaries if s['chunk_id'] > current_chunk - 3]

        # Early conversation (high-level only)
        if early:
            parts.append(f"\nEarly conversation (Chunks 1-{len(early)}):")
            if early[-1]['summary'].get('cumulative_summary'):
                # Just take the cumulative summary from last early chunk
                parts.append(f"  {early[-1]['summary']['cumulative_summary'][:200]}...")

        # Middle conversation (pattern summary)
        if middle:
            parts.append(f"\nMiddle conversation (Chunks {early[-1]['chunk_id']+1 if early else 4}-{middle[-1]['chunk_id']}):")
            # Extract key trends
            if middle[-1]['summary'].get('You'):
                you_trends = []
                for dim in ['toxicity', 'sentiment']:
                    if dim in middle[-1]['summary']['You']:
                        trend = middle[-1]['summary']['You'][dim].get('trend', 'stable')
                        if trend != 'stable':
                            you_trends.append(f"{dim}: {trend}")
                if you_trends:
                    parts.append(f"  You: {', '.join(you_trends)}")

        # Recent conversation (detailed)
        if recent:
            parts.append(f"\nRecent analysis (Chunks {recent[0]['chunk_id']}-{recent[-1]['chunk_id']}):")
            if recent[-1]['summary'].get('cumulative_summary'):
                parts.append(recent[-1]['summary']['cumulative_summary'])

        return '\n'.join(parts)


class PromptTemplateManager:
    """Manages prompt templates for LLM analysis."""

    SYSTEM_PROMPT = """You are an expert psychological analyst specializing in conversation dynamics and personality assessment.
Your task is to analyze text message conversations between two speakers ("You" and "Them") across multiple
psychological dimensions.

You have access to:
1. Raw conversation messages with timestamps
2. Per-message scores from specialized AI models (toxicity, sentiment, sarcasm, personality)
3. Summary of your previous analysis from earlier parts of the conversation

Your analysis should:
- Consider the full conversational context
- Distinguish between the two speakers' psychological profiles
- Track how traits evolve over the conversation
- Cite specific evidence from messages (quote them directly with timestamps)
- Explain your reasoning using psychological principles
- Be objective and evidence-based

Output your analysis as valid JSON only, no additional text or markdown formatting."""

    @staticmethod
    def create_user_prompt(
        chunk_id: int,
        messages: List[Dict[str, Any]],
        model_scores: Dict[str, Any],
        previous_summary: str
    ) -> str:
        """Create the user prompt for analyzing a chunk."""

        # Format messages
        formatted_messages = PromptTemplateManager._format_messages(messages)

        # Format specialized model scores
        formatted_scores = PromptTemplateManager._format_model_scores(messages, model_scores)

        # Build prompt
        prompt = f"""{previous_summary}

CURRENT CONVERSATION CHUNK (Chunk {chunk_id}):
{formatted_messages}

SPECIALIZED MODEL SCORES FOR THIS CHUNK:
{formatted_scores}

Analyze this chunk and update your psychological assessment of both speakers. For each speaker ("You" and "Them"),
provide scores (0-100) for:

1. Toxicity (0=completely non-toxic, 100=highly toxic/harmful)
2. Sentiment (0=very negative, 50=neutral, 100=very positive)
3. Sarcasm (0=completely sincere, 100=highly sarcastic)
4. Personality (Big 5):
   - Openness (0=closed-minded, 100=very open)
   - Conscientiousness (0=disorganized, 100=very organized)
   - Extraversion (0=very introverted, 100=very extroverted)
   - Agreeableness (0=antagonistic, 100=very agreeable)
   - Neuroticism (0=emotionally stable, 100=very neurotic)

For each dimension, provide:
- current_assessment: Your score (0-100) as an integer
- trend: "stable", "increasing", "decreasing", or "insufficient_data"
- confidence: "low", "medium", or "high" (based on amount of data)
- evidence: Array of objects with "message" (exact quote), "timestamp", and "context" (brief explanation)
- reasoning: 1-2 sentence psychological explanation

Also provide:
- cumulative_summary: 2-3 sentences describing each speaker's overall psychological profile and relationship dynamic
- conversation_dynamic: Object with "power_balance", "communication_style", and "conflict_trajectory"

Think through your analysis step by step, considering context, specialized model scores, and conversational
dynamics before providing scores.

Output ONLY valid JSON in this exact format:
{{
  "chunk_id": {chunk_id},
  "You": {{
    "toxicity": {{
      "current_assessment": <0-100 integer>,
      "trend": "<stable|increasing|decreasing|insufficient_data>",
      "confidence": "<low|medium|high>",
      "evidence": [
        {{"message": "<exact quote>", "timestamp": "<timestamp>", "context": "<brief explanation>"}}
      ],
      "reasoning": "<1-2 sentences>"
    }},
    "sentiment": {{ ... }},
    "sarcasm": {{ ... }},
    "personality": {{
      "openness": {{ ... }},
      "conscientiousness": {{ ... }},
      "extraversion": {{ ... }},
      "agreeableness": {{ ... }},
      "neuroticism": {{ ... }}
    }}
  }},
  "Them": {{ ... same structure ... }},
  "cumulative_summary": "<2-3 sentences>",
  "conversation_dynamic": {{
    "power_balance": "<description>",
    "communication_style": "<description>",
    "conflict_trajectory": "<description>"
  }}
}}

Output ONLY the JSON, no additional text."""

        return prompt

    @staticmethod
    def _format_messages(messages: List[Dict[str, Any]]) -> str:
        """Format messages for prompt."""
        lines = []
        for msg in messages:
            if msg.get('text'):
                label = "You" if msg.get('is_from_me') else "Them"
                timestamp = msg.get('date_formatted', '')

                # Format timestamp nicely
                if timestamp:
                    try:
                        parts = timestamp.split(' ')
                        date_str = parts[0]
                        time_str = parts[1]
                        ampm = parts[2]

                        from datetime import datetime as dt
                        date_obj = dt.strptime(date_str, '%Y-%m-%d')
                        date_formatted = date_obj.strftime('%b %d')
                        time_formatted = ':'.join(time_str.split(':')[:2]) + ' ' + ampm

                        timestamp = f"[{date_formatted} {time_formatted}]"
                    except:
                        timestamp = ""

                lines.append(f"{timestamp} {label}: {msg['text']}")

        return '\n'.join(lines)

    @staticmethod
    def _format_model_scores(messages: List[Dict[str, Any]], model_scores: Dict[str, Any]) -> str:
        """
        Format specialized model scores for prompt.

        Args:
            messages: List of message dictionaries for this chunk
            model_scores: Stage 1 aggregated analysis results (conversation-level)

        Returns:
            Formatted string showing conversation-level specialized model scores
        """
        if not model_scores:
            return "(No specialized model scores available - Stage 1 analysis not yet run)"

        lines = []
        lines.append("CONVERSATION-LEVEL SCORES FROM SPECIALIZED MODELS:")
        lines.append("")

        # Format "You" analysis
        if 'your_analysis' in model_scores:
            your_data = model_scores['your_analysis']
            lines.append("You (conversation-level metrics):")

            if 'personality' in your_data:
                pers = your_data['personality']
                primary = pers.get('primary_trait', 'unknown')
                dist = pers.get('trait_distribution', {})
                lines.append(f"  - Personality: Primary={primary}, Distribution={dist}")

            if 'toxicity' in your_data:
                tox = your_data['toxicity']
                rate = tox.get('rate', 0) * 100
                lines.append(f"  - Toxicity: {rate:.1f}% of messages ({tox.get('toxic_messages', 0)}/{tox.get('total_analyzed', 0)})")

            if 'sarcasm' in your_data:
                sarc = your_data['sarcasm']
                rate = sarc.get('rate', 0) * 100
                lines.append(f"  - Sarcasm: {rate:.1f}% of messages ({sarc.get('sarcastic_messages', 0)}/{sarc.get('total_analyzed', 0)})")

            if 'sentiment' in your_data:
                sent = your_data['sentiment']
                dist = sent.get('distribution', {})
                lines.append(f"  - Sentiment: POS={sent.get('positive_rate', 0)*100:.1f}%, NEG={sent.get('negative_rate', 0)*100:.1f}%, NEU={sent.get('neutral_rate', 0)*100:.1f}%")

        # Format "Them" analysis
        if 'their_analysis' in model_scores:
            lines.append("")
            their_data = model_scores['their_analysis']
            lines.append("Them (conversation-level metrics):")

            if 'personality' in their_data:
                pers = their_data['personality']
                primary = pers.get('primary_trait', 'unknown')
                dist = pers.get('trait_distribution', {})
                lines.append(f"  - Personality: Primary={primary}, Distribution={dist}")

            if 'toxicity' in their_data:
                tox = their_data['toxicity']
                rate = tox.get('rate', 0) * 100
                lines.append(f"  - Toxicity: {rate:.1f}% of messages ({tox.get('toxic_messages', 0)}/{tox.get('total_analyzed', 0)})")

            if 'sarcasm' in their_data:
                sarc = their_data['sarcasm']
                rate = sarc.get('rate', 0) * 100
                lines.append(f"  - Sarcasm: {rate:.1f}% of messages ({sarc.get('sarcastic_messages', 0)}/{sarc.get('total_analyzed', 0)})")

            if 'sentiment' in their_data:
                sent = their_data['sentiment']
                dist = sent.get('distribution', {})
                lines.append(f"  - Sentiment: POS={sent.get('positive_rate', 0)*100:.1f}%, NEG={sent.get('negative_rate', 0)*100:.1f}%, NEU={sent.get('neutral_rate', 0)*100:.1f}%")

        lines.append("")
        lines.append("(These are aggregate statistics from specialized models analyzing the full conversation)")

        return '\n'.join(lines)


class Stage2LLMAnalyzer:
    """
    Main analyzer for Stage 2 - dual LLM cumulative analysis.
    """

    def __init__(self, models: List[str] = None):
        """
        Initialize Stage 2 analyzer.

        Args:
            models: List of model names (default: ['llama3.2', 'qwen2.5:7b-instruct'])
        """
        self.models = models or ['llama3.2', 'qwen2.5:7b-instruct']
        self.summary_manager = CumulativeSummaryManager()
        self.prompt_manager = PromptTemplateManager()

    def analyze_conversation(
        self,
        messages: List[Dict[str, Any]],
        stage1_results: Optional[Dict[str, Any]] = None,
        chunk_size: int = 8000,
        overlap: int = 800
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze entire conversation using both LLMs with cumulative context.

        Args:
            messages: List of message dictionaries (chronological order)
            stage1_results: Results from Stage 1 analysis (per-message scores)
            chunk_size: Target tokens per chunk
            overlap: Token overlap between chunks

        Returns:
            Dictionary with results from each model:
            {
                'llama3.2': [chunk1_analysis, chunk2_analysis, ...],
                'qwen2.5:7b-instruct': [chunk1_analysis, chunk2_analysis, ...]
            }
        """
        print(f"\n{'='*80}")
        print("STAGE 2: DUAL LLM CUMULATIVE ANALYSIS")
        print(f"{'='*80}\n")
        print(f"Models: {', '.join(self.models)}")
        print(f"Total messages: {len(messages)}")

        # Create chunks (reuse from Stage 1)
        chunks = self._create_chunks(messages, chunk_size, overlap)
        print(f"Total chunks: {len(chunks)}")
        print(f"Chunk size: {chunk_size} tokens, Overlap: {overlap} tokens\n")

        # Results storage
        results = {model: [] for model in self.models}

        # Process each chunk
        for chunk_idx, chunk in enumerate(chunks):
            chunk_id = chunk_idx + 1
            print(f"\n{'='*80}")
            print(f"Processing Chunk {chunk_id}/{len(chunks)}")
            print(f"{'='*80}")

            # Get cumulative summary
            previous_summary = self.summary_manager.get_compressed_summary(chunk_id)

            # Create prompt
            user_prompt = self.prompt_manager.create_user_prompt(
                chunk_id=chunk_id,
                messages=chunk,
                model_scores=stage1_results or {},
                previous_summary=previous_summary
            )

            # Analyze with both models (in parallel would be ideal, but for now sequential)
            for model_name in self.models:
                print(f"\n  Analyzing with {model_name}...")
                start_time = time.time()

                try:
                    analysis = self._analyze_chunk_with_model(
                        model_name=model_name,
                        chunk_id=chunk_id,
                        user_prompt=user_prompt
                    )

                    if analysis:
                        results[model_name].append(analysis)

                        # Update summary manager with this model's output
                        if model_name == self.models[0]:  # Use first model for summaries
                            self.summary_manager.add_chunk_summary(chunk_id, analysis)

                        elapsed = time.time() - start_time
                        print(f"  ✓ Completed in {elapsed:.1f}s")
                    else:
                        print(f"  ✗ Failed to get valid analysis")

                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    continue

        print(f"\n{'='*80}")
        print("STAGE 2 ANALYSIS COMPLETE")
        print(f"{'='*80}\n")

        return results

    def _analyze_chunk_with_model(
        self,
        model_name: str,
        chunk_id: int,
        user_prompt: str,
        max_retries: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a chunk with a specific model.

        Args:
            model_name: Name of the Ollama model
            chunk_id: Chunk number
            user_prompt: The user prompt
            max_retries: Number of retries if JSON parsing fails

        Returns:
            Parsed JSON analysis or None if failed
        """
        for attempt in range(max_retries):
            try:
                # Call Ollama
                response = ollama.generate(
                    model=model_name,
                    prompt=user_prompt,
                    system=self.prompt_manager.SYSTEM_PROMPT,
                    options={
                        'temperature': 0.3,  # Lower for more consistent output
                        'top_p': 0.9,
                    }
                )

                # Extract response text
                response_text = response['response'].strip()

                # Try to parse JSON
                analysis = self._parse_json_response(response_text)

                if analysis:
                    # Add metadata
                    analysis['model'] = model_name
                    analysis['timestamp'] = datetime.now().isoformat()
                    analysis['chunk_id'] = chunk_id
                    return analysis
                else:
                    print(f"    Retry {attempt + 1}/{max_retries}: Invalid JSON")

            except Exception as e:
                print(f"    Retry {attempt + 1}/{max_retries}: {str(e)}")

        return None

    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON from LLM response, handling markdown code blocks.

        Args:
            response_text: Raw response from LLM

        Returns:
            Parsed JSON dict or None if invalid
        """
        # Remove markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]

        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"    JSON parse error: {e}")
            return None

    def _create_chunks(
        self,
        messages: List[Dict[str, Any]],
        chunk_size: int = 450,
        overlap: int = 45
    ) -> List[List[Dict[str, Any]]]:
        """Create overlapping chunks from messages based on token count."""
        if not messages:
            return []

        chunks = []
        i = 0

        while i < len(messages):
            chunk = []
            token_count = 0

            for j in range(i, len(messages)):
                msg = messages[j]
                if msg.get('text'):
                    msg_tokens = (len(msg['text']) + 20) // 4
                    if token_count + msg_tokens > chunk_size and len(chunk) > 0:
                        break
                    chunk.append(msg)
                    token_count += msg_tokens
                else:
                    chunk.append(msg)

            if chunk:
                chunks.append(chunk)

                # Calculate overlap
                overlap_tokens = 0
                overlap_msgs = 0
                for msg in reversed(chunk):
                    if msg.get('text'):
                        msg_tokens = (len(msg['text']) + 20) // 4
                        if overlap_tokens + msg_tokens > overlap:
                            break
                        overlap_tokens += msg_tokens
                        overlap_msgs += 1

                i += max(1, len(chunk) - overlap_msgs)
            else:
                i += 1

        return chunks


def main():
    """Test the Stage 2 analyzer."""
    print("Stage 2 LLM Analyzer initialized")
    print("Ready for conversation analysis")


if __name__ == "__main__":
    main()
