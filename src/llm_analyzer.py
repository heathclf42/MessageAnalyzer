#!/usr/bin/env python3
"""
LLM-based psychological analysis for conversations.
Analyzes personality, toxicity, sarcasm, and sentiment using specialized transformer models.
"""

import os
# Disable tokenizer parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from transformers import pipeline, BertTokenizer, BertForSequenceClassification, AutoTokenizer, AutoModelForSeq2SeqLM

# Add src to path for imports if needed
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

from llm_monitor import get_monitor

class LLMAnalyzer:
    """Analyzes conversations using specialized LLM models."""

    def __init__(self, use_gpu: bool = True):
        """Initialize the LLM analyzer with all models.

        Args:
            use_gpu: Whether to use GPU acceleration (MPS for Mac, CUDA for Linux/Windows)
        """
        self.monitor = get_monitor()
        device = "mps" if use_gpu else -1  # -1 means CPU

        print("Loading LLM models...")

        try:
            # Personality classifiers (2 models for redundancy)
            print("  Loading personality model 1 (holistic-ai)...")
            self.personality_model = pipeline(
                "text-classification",
                model="holistic-ai/personality_classifier",
                device=device
            )

            print("  Loading personality model 2 (bert-base)...")
            self.bert_tokenizer = BertTokenizer.from_pretrained("Minej/bert-base-personality")
            self.bert_personality_model = BertForSequenceClassification.from_pretrained("Minej/bert-base-personality")
            if device == "mps":
                self.bert_personality_model = self.bert_personality_model.to("mps")

            # Toxicity detectors (2 models for redundancy)
            print("  Loading toxicity model 1 (martin-ha)...")
            self.toxicity_model = pipeline(
                "text-classification",
                model="martin-ha/toxic-comment-model",
                device=device
            )

            # Skip toxicchat - has compatibility issues with Python 3.13
            # print("  Loading toxicity model 2 (lmsys/toxicchat)...")
            # self.toxicchat_tokenizer = AutoTokenizer.from_pretrained("lmsys/toxicchat-t5-large-v1.0")
            # self.toxicchat_model = AutoModelForSeq2SeqLM.from_pretrained("lmsys/toxicchat-t5-large-v1.0")
            # if device == "mps":
            #     self.toxicchat_model = self.toxicchat_model.to("mps")

            # Sarcasm detector
            print("  Loading sarcasm model...")
            self.sarcasm_model = pipeline(
                "text-classification",
                model="jkhan447/sarcasm-detection-RoBerta-base",
                device=device
            )

            # Sentiment analyzer
            print("  Loading sentiment model...")
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="finiteautomata/bertweet-base-sentiment-analysis",
                device=device
            )

            print("✓ All models loaded successfully\n")

        except Exception as e:
            print(f"Warning: GPU acceleration failed, falling back to CPU: {e}")
            # Retry without GPU
            self.personality_model = pipeline("text-classification", model="holistic-ai/personality_classifier", device=-1)

            print("  Loading personality model 2 (bert-base) on CPU...")
            self.bert_tokenizer = BertTokenizer.from_pretrained("Minej/bert-base-personality")
            self.bert_personality_model = BertForSequenceClassification.from_pretrained("Minej/bert-base-personality")

            self.toxicity_model = pipeline("text-classification", model="martin-ha/toxic-comment-model", device=-1)

            # Skip toxicchat - has compatibility issues with Python 3.13
            # print("  Loading toxicity model 2 (lmsys/toxicchat) on CPU...")
            # self.toxicchat_tokenizer = AutoTokenizer.from_pretrained("lmsys/toxicchat-t5-large-v1.0")
            # self.toxicchat_model = AutoModelForSeq2SeqLM.from_pretrained("lmsys/toxicchat-t5-large-v1.0")

            self.sarcasm_model = pipeline("text-classification", model="jkhan447/sarcasm-detection-RoBerta-base", device=-1)
            self.sentiment_model = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis", device=-1)

            print("✓ All models loaded successfully on CPU\n")

    def analyze_personality(self, text: str) -> Dict[str, Any]:
        """Analyze personality traits in text using Big 5 model.

        Args:
            text: Text to analyze (truncated to ~512 tokens / 2000 chars)

        Returns:
            Dictionary with personality analysis results
        """
        with self.monitor.track_operation('holistic-ai/personality_classifier', 'inference', len(text)):
            result = self.personality_model(text[:2000])[0]  # 2000 chars ≈ 500 tokens

        return {
            'trait': result['label'],
            'confidence': result['score']
        }

    def analyze_personality_bert(self, text: str) -> Dict[str, Any]:
        """Analyze personality traits using bert-base model (returns all Big 5 scores).

        Args:
            text: Text to analyze (truncated to ~512 tokens / 2000 chars)

        Returns:
            Dictionary with all Big 5 personality scores
        """
        import torch

        with self.monitor.track_operation('Minej/bert-base-personality', 'inference', len(text)):
            inputs = self.bert_tokenizer(text[:2000], truncation=True, padding=True, return_tensors="pt")
            if hasattr(self.bert_personality_model, 'device') and str(self.bert_personality_model.device) == 'mps':
                inputs = {k: v.to('mps') for k, v in inputs.items()}

            outputs = self.bert_personality_model(**inputs)
            predictions = outputs.logits.squeeze().detach().cpu().numpy()

        label_names = ['Extroversion', 'Neuroticism', 'Agreeableness', 'Conscientiousness', 'Openness']
        return {label_names[i]: float(predictions[i]) for i in range(len(label_names))}

    def analyze_toxicity(self, text: str) -> Dict[str, Any]:
        """Detect toxic/harmful content in text.

        Args:
            text: Text to analyze (truncated to ~512 tokens / 2000 chars)

        Returns:
            Dictionary with toxicity analysis results
        """
        with self.monitor.track_operation('martin-ha/toxic-comment-model', 'inference', len(text)):
            result = self.toxicity_model(text[:2000])[0]

        return {
            'is_toxic': result['label'] == 'toxic',
            'confidence': result['score']
        }

    def analyze_toxicity_toxicchat(self, text: str) -> Dict[str, Any]:
        """Detect toxic content using lmsys/toxicchat model.

        Args:
            text: Text to analyze (truncated to ~512 tokens / 2000 chars)

        Returns:
            Dictionary with toxicity analysis results
        """
        import torch

        with self.monitor.track_operation('lmsys/toxicchat-t5-large-v1.0', 'inference', len(text)):
            prefix = "ToxicChat: "
            inputs = self.toxicchat_tokenizer.encode(prefix + text[:2000], return_tensors="pt", truncation=True, max_length=512)

            if hasattr(self.toxicchat_model, 'device') and str(self.toxicchat_model.device) == 'mps':
                inputs = inputs.to('mps')

            outputs = self.toxicchat_model.generate(inputs, max_new_tokens=10)
            result = self.toxicchat_tokenizer.decode(outputs[0], skip_special_tokens=True)

        # ToxicChat outputs: "positive" = toxic, "negative" = not toxic
        is_toxic = result.strip().lower() == "positive"

        return {
            'is_toxic': is_toxic,
            'raw_output': result.strip()
        }

    def analyze_sarcasm(self, text: str) -> Dict[str, Any]:
        """Detect sarcasm in text.

        Args:
            text: Text to analyze (truncated to ~512 tokens / 2000 chars)

        Returns:
            Dictionary with sarcasm analysis results
        """
        with self.monitor.track_operation('jkhan447/sarcasm-detection-RoBerta-base', 'inference', len(text)):
            result = self.sarcasm_model(text[:2000])[0]

        return {
            'is_sarcastic': result['label'].lower() == 'sarcasm',
            'confidence': result['score']
        }

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment (positive/negative/neutral) in text.

        Args:
            text: Text to analyze (truncated to ~512 tokens / 2000 chars)

        Returns:
            Dictionary with sentiment analysis results
        """
        with self.monitor.track_operation('finiteautomata/bertweet-base-sentiment-analysis', 'inference', len(text)):
            result = self.sentiment_model(text[:2000])[0]

        return {
            'sentiment': result['label'],
            'confidence': result['score']
        }

    def analyze_message(self, text: str) -> Dict[str, Any]:
        """Run all analyses on a single message.

        Args:
            text: Message text to analyze

        Returns:
            Dictionary with all analysis results
        """
        if not text or len(text.strip()) < 3:
            return None

        return {
            'personality': self.analyze_personality(text),
            'toxicity': self.analyze_toxicity(text),
            'sarcasm': self.analyze_sarcasm(text),
            'sentiment': self.analyze_sentiment(text)
        }

    def analyze_conversation(self, messages: List[Dict[str, Any]], chunk_size: int = 10, overlap: int = 3, batch_size: int = 16, return_per_message: bool = False) -> Dict[str, Any]:
        """Analyze a conversation using overlapping chunks with GPU batching for speed.

        Args:
            messages: List of message dictionaries with 'text' and 'is_from_me' fields (in chronological order)
            chunk_size: Number of messages per chunk
            overlap: Number of messages to overlap between chunks
            batch_size: Number of chunks to process simultaneously on GPU (default: 16)
            return_per_message: If True, also return per-message scores (for Stage 2)

        Returns:
            Dictionary with aggregated conversation analysis
        """
        print(f"  Analyzing conversation: {len(messages)} total messages")

        # Create overlapping chunks from the chronological conversation
        chunks = self._create_chunks(messages, chunk_size, overlap)

        print(f"  Created {len(chunks)} chunks (maintaining conversation flow)")
        print(f"  Using GPU batching (batch_size={batch_size})")

        # Prepare chunks as dialogues (preserving context) and track metadata
        chunk_data = []

        for i, chunk in enumerate(chunks):
            # Build dialogue format with timestamps: "[12:30 PM] You: text\n[12:31 PM] Them: text..."
            dialogue_parts = []
            your_msg_count = 0
            their_msg_count = 0

            for msg in chunk:
                if msg.get('text'):
                    label = "You" if msg.get('is_from_me') else "Them"

                    # Clean text artifacts (leading/trailing special chars and numbers from extraction)
                    import re
                    clean_text = msg['text']
                    # Remove leading special chars, numbers, or single letters followed by space/text
                    clean_text = re.sub(r'^[&*@,;+)\]\[0-9]+\s*', '', clean_text)
                    clean_text = re.sub(r'^[a-zA-Z]\s*(?=[A-Z])', '', clean_text)  # Single letter before capital
                    # Remove trailing special chars
                    clean_text = re.sub(r'\s*[;,]+$', '', clean_text)
                    clean_text = clean_text.strip()

                    # Get date and time from date_formatted (e.g., "2021-12-18 03:12:03 AM" -> "Dec 18 03:12 AM")
                    timestamp = ""
                    if msg.get('date_formatted'):
                        try:
                            parts = msg['date_formatted'].split(' ')
                            date_str = parts[0]  # "2021-12-18"
                            time_str = parts[1]  # "03:12:03"
                            ampm = parts[2]      # "AM"

                            # Convert date: "2021-12-18" -> "Dec 18"
                            from datetime import datetime
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            date_formatted = date_obj.strftime('%b %d')  # "Dec 18"

                            # Format time: "03:12:03" -> "03:12"
                            time_formatted = ':'.join(time_str.split(':')[:2]) + ' ' + ampm

                            timestamp = f"[{date_formatted} {time_formatted}] "
                        except:
                            timestamp = ""

                    dialogue_parts.append(f"{timestamp}{label}: {clean_text}")

                    if msg.get('is_from_me'):
                        your_msg_count += 1
                    else:
                        their_msg_count += 1

            if dialogue_parts:
                # Limit to ~300 tokens (~1200 chars) to stay safely under 512 token limit (with special tokens)
                dialogue_text = '\n'.join(dialogue_parts)[:1200]

                chunk_data.append({
                    'dialogue': dialogue_text,
                    'has_your_msgs': your_msg_count > 0,
                    'has_their_msgs': their_msg_count > 0,
                    'your_msg_count': your_msg_count,
                    'their_msg_count': their_msg_count
                })

        # Batch process with progress tracking
        import time
        start_time = time.time()

        print(f"  Processing {len(chunk_data)} conversation chunks...")

        # Analyze all chunks in batches
        all_results = self._batch_analyze_dialogues([c['dialogue'] for c in chunk_data], batch_size, start_time)

        # Separate results by speaker
        your_results = []
        their_results = []

        for i, result in enumerate(all_results):
            if chunk_data[i]['has_your_msgs']:
                your_results.append(result)
            if chunk_data[i]['has_their_msgs']:
                their_results.append(result)

        # Count messages by sender
        your_msg_count = sum(1 for m in messages if m.get('is_from_me'))
        their_msg_count = sum(1 for m in messages if not m.get('is_from_me'))

        # Aggregate results
        return {
            'your_analysis': self._aggregate_results(your_results),
            'their_analysis': self._aggregate_results(their_results),
            'metadata': {
                'total_messages': len(messages),
                'your_messages': your_msg_count,
                'their_messages': their_msg_count,
                'chunks_analyzed': len(chunks),
                'chunk_size': chunk_size,
                'overlap': overlap
            }
        }

    def _batch_analyze_dialogues(self, texts: List[str], batch_size: int, start_time: float) -> List[Dict[str, Any]]:
        """Analyze dialogue chunks in batches for GPU efficiency.

        Args:
            texts: List of dialogue text strings (formatted as "You: ...\nThem: ...")
            batch_size: Number of texts to process at once
            start_time: Start time for progress calculation

        Returns:
            List of analysis results for each dialogue chunk
        """
        if not texts:
            return []

        results = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        for batch_idx in range(0, len(texts), batch_size):
            batch_texts = texts[batch_idx:batch_idx + batch_size]
            batch_num = batch_idx // batch_size + 1

            # Process entire batch through each model (with truncation to stay under token limits)
            with self.monitor.track_operation('holistic-ai/personality_classifier', 'batch_inference', sum(len(t) for t in batch_texts)):
                personality_results = self.personality_model(batch_texts, truncation=True, max_length=512)

            # Bert-base personality (batch inference)
            with self.monitor.track_operation('Minej/bert-base-personality', 'batch_inference', sum(len(t) for t in batch_texts)):
                bert_personality_results = self._batch_bert_personality(batch_texts)

            with self.monitor.track_operation('martin-ha/toxic-comment-model', 'batch_inference', sum(len(t) for t in batch_texts)):
                toxicity_results = self.toxicity_model(batch_texts, truncation=True, max_length=512)

            # Skip ToxicChat - compatibility issues
            # with self.monitor.track_operation('lmsys/toxicchat-t5-large-v1.0', 'batch_inference', sum(len(t) for t in batch_texts)):
            #     toxicchat_results = self._batch_toxicchat(batch_texts)

            with self.monitor.track_operation('jkhan447/sarcasm-detection-RoBerta-base', 'batch_inference', sum(len(t) for t in batch_texts)):
                sarcasm_results = self.sarcasm_model(batch_texts, truncation=True, max_length=512)

            with self.monitor.track_operation('finiteautomata/bertweet-base-sentiment-analysis', 'batch_inference', sum(len(t) for t in batch_texts)):
                sentiment_results = self.sentiment_model(batch_texts, truncation=True, max_length=128)

            # Combine results
            for i in range(len(batch_texts)):
                result = {
                    'personality': {
                        'holistic_ai': {
                            'trait': personality_results[i]['label'],
                            'confidence': personality_results[i]['score']
                        },
                        'bert_base': bert_personality_results[i]
                    },
                    'toxicity': {
                        'martin_ha': {
                            'is_toxic': toxicity_results[i]['label'] == 'toxic',
                            'confidence': toxicity_results[i]['score']
                        }
                    },
                    'sarcasm': {
                        'is_sarcastic': sarcasm_results[i]['label'].lower() == 'sarcasm',
                        'confidence': sarcasm_results[i]['score']
                    },
                    'sentiment': {
                        'sentiment': sentiment_results[i]['label'],
                        'confidence': sentiment_results[i]['score']
                    }
                }
                results.append(result)

            # Progress update
            elapsed = time.time() - start_time
            rate = elapsed / (batch_idx + len(batch_texts))
            remaining = (len(texts) - (batch_idx + len(batch_texts))) * rate
            print(f"    Batch {batch_num}/{total_batches} | ~{remaining:.0f}s remaining")

        return results

    def _batch_bert_personality(self, texts: List[str]) -> List[Dict[str, float]]:
        """Batch process texts through bert-base-personality model.

        Args:
            texts: List of text strings to analyze

        Returns:
            List of Big 5 personality score dictionaries
        """
        import torch

        # Tokenize all texts
        inputs = self.bert_tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="pt")

        # Move to device if needed
        if hasattr(self.bert_personality_model, 'device') and str(self.bert_personality_model.device) == 'mps':
            inputs = {k: v.to('mps') for k, v in inputs.items()}

        # Get predictions
        with torch.no_grad():
            outputs = self.bert_personality_model(**inputs)
            predictions = outputs.logits.detach().cpu().numpy()

        # Convert to list of dicts
        label_names = ['Extroversion', 'Neuroticism', 'Agreeableness', 'Conscientiousness', 'Openness']
        results = []
        for pred in predictions:
            results.append({label_names[i]: float(pred[i]) for i in range(len(label_names))})

        return results

    def _batch_toxicchat(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Batch process texts through lmsys/toxicchat model.

        Args:
            texts: List of text strings to analyze

        Returns:
            List of toxicity analysis dictionaries
        """
        import torch

        results = []
        prefix = "ToxicChat: "

        for text in texts:
            inputs = self.toxicchat_tokenizer.encode(prefix + text[:2000], return_tensors="pt", truncation=True, max_length=512)

            if hasattr(self.toxicchat_model, 'device') and str(self.toxicchat_model.device) == 'mps':
                inputs = inputs.to('mps')

            with torch.no_grad():
                outputs = self.toxicchat_model.generate(inputs, max_new_tokens=10)
                result = self.toxicchat_tokenizer.decode(outputs[0], skip_special_tokens=True)

            # ToxicChat outputs: "positive" = toxic, "negative" = not toxic
            is_toxic = result.strip().lower() == "positive"
            results.append({
                'is_toxic': is_toxic,
                'raw_output': result.strip()
            })

        return results

    def _create_chunks(self, messages: List[Dict[str, Any]], chunk_size: int = 450, overlap: int = 45) -> List[List[Dict[str, Any]]]:
        """Create overlapping chunks from messages based on token count.

        Args:
            messages: List of message dictionaries
            chunk_size: Target token count per chunk (default: 450)
            overlap: Token overlap between chunks (default: 45, ~10%)

        Returns:
            List of message chunks
        """
        if not messages:
            return []

        chunks = []
        i = 0

        while i < len(messages):
            chunk = []
            token_count = 0

            # Build chunk up to token limit
            for j in range(i, len(messages)):
                msg = messages[j]
                if msg.get('text'):
                    # Estimate tokens: ~4 chars per token + timestamp overhead
                    msg_tokens = (len(msg['text']) + 20) // 4

                    if token_count + msg_tokens > chunk_size and len(chunk) > 0:
                        # Would exceed limit, stop here
                        break

                    chunk.append(msg)
                    token_count += msg_tokens
                else:
                    chunk.append(msg)

            if chunk:
                chunks.append(chunk)

                # Calculate overlap in messages (backtrack to get ~10% token overlap)
                overlap_tokens = 0
                overlap_msgs = 0
                for msg in reversed(chunk):
                    if msg.get('text'):
                        msg_tokens = (len(msg['text']) + 20) // 4
                        if overlap_tokens + msg_tokens > overlap:
                            break
                        overlap_tokens += msg_tokens
                        overlap_msgs += 1

                # Move forward by chunk size minus overlap messages
                i += max(1, len(chunk) - overlap_msgs)
            else:
                i += 1

        return chunks

    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate individual message analyses into summary statistics.

        Args:
            results: List of individual message analysis results

        Returns:
            Dictionary with aggregated statistics
        """
        if not results:
            return {}

        # Count personality traits from holistic-ai
        personality_counts = {}
        for r in results:
            trait = r['personality']['holistic_ai']['trait']
            personality_counts[trait] = personality_counts.get(trait, 0) + 1

        # Average bert-base Big 5 scores
        bert_big5_sums = {'Extroversion': 0, 'Neuroticism': 0, 'Agreeableness': 0, 'Conscientiousness': 0, 'Openness': 0}
        for r in results:
            for trait, score in r['personality']['bert_base'].items():
                bert_big5_sums[trait] += score
        bert_big5_avg = {trait: score / len(results) for trait, score in bert_big5_sums.items()} if results else {}

        # Calculate toxicity rates from both models
        martin_ha_toxic_count = sum(1 for r in results if r['toxicity']['martin_ha']['is_toxic'])
        toxicchat_toxic_count = sum(1 for r in results if r['toxicity']['toxicchat']['is_toxic'])

        martin_ha_toxicity_rate = martin_ha_toxic_count / len(results) if results else 0
        toxicchat_toxicity_rate = toxicchat_toxic_count / len(results) if results else 0

        # Average toxicity rate from both models
        avg_toxicity_rate = (martin_ha_toxicity_rate + toxicchat_toxicity_rate) / 2

        # Calculate sarcasm rate
        sarcasm_count = sum(1 for r in results if r['sarcasm']['is_sarcastic'])
        sarcasm_rate = sarcasm_count / len(results) if results else 0

        # Count sentiments
        sentiment_counts = {'POS': 0, 'NEG': 0, 'NEU': 0}
        for r in results:
            sentiment = r['sentiment']['sentiment']
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

        # Most common personality trait
        primary_trait = max(personality_counts.items(), key=lambda x: x[1])[0] if personality_counts else None

        return {
            'personality': {
                'holistic_ai': {
                    'primary_trait': primary_trait,
                    'trait_distribution': personality_counts
                },
                'bert_base': {
                    'big5_scores': bert_big5_avg
                }
            },
            'toxicity': {
                'martin_ha': {
                    'rate': martin_ha_toxicity_rate,
                    'toxic_messages': martin_ha_toxic_count
                },
                'toxicchat': {
                    'rate': toxicchat_toxicity_rate,
                    'toxic_messages': toxicchat_toxic_count
                },
                'average_rate': avg_toxicity_rate,
                'total_analyzed': len(results)
            },
            'sarcasm': {
                'rate': sarcasm_rate,
                'sarcastic_messages': sarcasm_count,
                'total_analyzed': len(results)
            },
            'sentiment': {
                'distribution': sentiment_counts,
                'positive_rate': sentiment_counts['POS'] / len(results) if results else 0,
                'negative_rate': sentiment_counts['NEG'] / len(results) if results else 0,
                'neutral_rate': sentiment_counts['NEU'] / len(results) if results else 0
            }
        }


def main():
    """Test the analyzer with sample texts."""
    analyzer = LLMAnalyzer()

    test_messages = [
        {'text': "I'm feeling really great about this project! So excited!", 'is_from_me': True},
        {'text': "Whatever. I don't even care anymore.", 'is_from_me': False},
        {'text': "I love helping people and making sure everyone feels valued.", 'is_from_me': True},
        {'text': "You're absolutely terrible at this. So incompetent.", 'is_from_me': False},
        {'text': "Oh great, another meeting. Just what I needed today.", 'is_from_me': True},
    ]

    results = analyzer.analyze_conversation(test_messages, sample_rate=1.0)

    import json
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
