#!/usr/bin/env python3
"""
Preview the exact inputs that will be sent to each Stage 1 model.
Shows first 5 chunks without actually running inference.
"""

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def main(phone_number: str = "817-709-1307"):
    """Preview Stage 1 inputs for a conversation."""

    conversations_dir = Path(__file__).parent / "data" / "output" / "all_conversations"

    # Find conversation file
    matches = list(conversations_dir.glob(f"*{phone_number}*.json"))
    matches = [f for f in matches if not f.name.endswith("_analysis.json") and not f.name.endswith("_llm_analysis.json")]

    if not matches:
        print(f"❌ No conversation found for {phone_number}")
        return

    conv_file = matches[0]

    print("=" * 80)
    print(f"STAGE 1 INPUT PREVIEW: {conv_file.name}")
    print("=" * 80)
    print()

    # Load conversation
    with open(conv_file, 'r') as f:
        data = json.load(f)

    messages = data.get('messages', [])

    print(f"Total messages: {len(messages)}")
    print(f"Chunk size: 15 messages, Overlap: 5 messages\n")

    # Create chunks (replicate the logic from llm_analyzer.py)
    chunks = create_chunks(messages, chunk_size=15, overlap=5)

    print(f"Total chunks: {len(chunks)}")
    print(f"Showing first 5 chunks...\n")

    # Process first 5 chunks
    for chunk_idx in range(min(5, len(chunks))):
        chunk = chunks[chunk_idx]

        print("=" * 80)
        print(f"CHUNK {chunk_idx + 1}")
        print("=" * 80)
        print()

        # Build dialogue (same logic as llm_analyzer.py)
        dialogue_parts = []

        for msg in chunk:
            if msg.get('text'):
                label = "You" if msg.get('is_from_me') else "Them"

                # Clean text
                import re
                clean_text = msg['text']
                clean_text = re.sub(r'^[&*@,;+)\]\[0-9]+\s*', '', clean_text)
                clean_text = re.sub(r'^[a-zA-Z]\s*(?=[A-Z])', '', clean_text)
                clean_text = re.sub(r'\s*[;,]+$', '', clean_text)
                clean_text = clean_text.strip()

                # Format timestamp
                timestamp = ""
                if msg.get('date_formatted'):
                    try:
                        parts = msg['date_formatted'].split(' ')
                        date_str = parts[0]
                        time_str = parts[1]
                        ampm = parts[2]

                        from datetime import datetime
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_formatted = date_obj.strftime('%b %d')
                        time_formatted = ':'.join(time_str.split(':')[:2]) + ' ' + ampm

                        timestamp = f"[{date_formatted} {time_formatted}] "
                    except:
                        timestamp = ""

                dialogue_parts.append(f"{timestamp}{label}: {clean_text}")

        # Create dialogue text (truncated to 1200 chars like in the actual code)
        dialogue_text = '\n'.join(dialogue_parts)[:1200]

        # Show EXACTLY what gets sent to each model - the literal string
        print("┌" + "─" * 78 + "┐")
        print("│ MODEL 1: holistic-ai/personality_classifier                              │")
        print("│ Input: batch_texts[0] = <string below>                                   │")
        print("└" + "─" * 78 + "┘")
        print(repr(dialogue_text))
        print()
        print()

        print("┌" + "─" * 78 + "┐")
        print("│ MODEL 2: Minej/bert-base-personality                                     │")
        print("│ Input: batch_texts[0] = <string below>                                   │")
        print("└" + "─" * 78 + "┘")
        print(repr(dialogue_text))
        print()
        print()

        print("┌" + "─" * 78 + "┐")
        print("│ MODEL 3: martin-ha/toxic-comment-model                                   │")
        print("│ Input: batch_texts[0] = <string below>                                   │")
        print("└" + "─" * 78 + "┘")
        print(repr(dialogue_text))
        print()
        print()

        print("┌" + "─" * 78 + "┐")
        print("│ MODEL 4: jkhan447/sarcasm-detection-RoBerta-base                         │")
        print("│ Input: batch_texts[0] = <string below>                                   │")
        print("└" + "─" * 78 + "┘")
        print(repr(dialogue_text))
        print()
        print()

        print("┌" + "─" * 78 + "┐")
        print("│ MODEL 5: finiteautomata/bertweet-base-sentiment-analysis                │")
        print("│ Input: batch_texts[0] = <string below>                                   │")
        print("│ Note: Model will auto-truncate to 128 tokens internally                  │")
        print("└" + "─" * 78 + "┘")
        print(repr(dialogue_text))
        print()
        print()

        print("=" * 80)
        print()


def create_chunks(messages, chunk_size=15, overlap=5):
    """Create overlapping chunks (same logic as llm_analyzer.py)."""
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
                if token_count + msg_tokens > chunk_size * 100 and len(chunk) > 0:  # Rough estimate
                    break
                chunk.append(msg)
                token_count += msg_tokens
            else:
                chunk.append(msg)

        if chunk:
            chunks.append(chunk)

            # Calculate overlap
            overlap_msgs = min(overlap, len(chunk))
            i += max(1, len(chunk) - overlap_msgs)
        else:
            i += 1

    return chunks


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Preview Stage 1 model inputs")
    parser.add_argument("--phone", type=str, default="817-709-1307", help="Phone number to analyze")

    args = parser.parse_args()

    main(phone_number=args.phone)
