#!/usr/bin/env python3
"""
Preview what chunks will be sent to the LLM models.
"""

import sys
import json
from pathlib import Path

# Configuration
CONVERSATIONS_DIR = Path(__file__).parent / "data" / "output" / "all_conversations"
CHUNK_SIZE = 450  # Target tokens per chunk
OVERLAP = 45  # Token overlap (~10%)

def create_chunks(messages, chunk_size=450, overlap=45):
    """Create overlapping chunks from messages based on token count."""
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
                    break

                chunk.append(msg)
                token_count += msg_tokens
            else:
                chunk.append(msg)

        if chunk:
            chunks.append(chunk)

            # Calculate overlap in messages
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

def preview_chunks(phone):
    """Preview chunks for a conversation."""

    # Find conversation file
    phone_digits = ''.join(c for c in phone if c.isdigit())
    conv_file = None

    for f in CONVERSATIONS_DIR.glob("*.json"):
        if f.name.endswith("_analysis.json") or f.name.endswith("_llm_analysis.json"):
            continue
        filename_digits = ''.join(c for c in f.name if c.isdigit())
        if phone_digits in filename_digits:
            conv_file = f
            break

    if not conv_file:
        print(f"❌ Conversation not found for {phone}")
        return

    # Load conversation
    with open(conv_file, 'r') as f:
        data = json.load(f)

    messages = data.get('messages', [])

    print("=" * 80)
    print(f"CHUNK PREVIEW FOR: {data.get('conversation_name')}")
    print(f"Total messages: {len(messages)}")
    print("=" * 80)

    # Create chunks
    chunks = create_chunks(messages, CHUNK_SIZE, OVERLAP)

    print(f"\nTotal chunks: {len(chunks)}")
    print(f"Target: 450 tokens/chunk with 45 token (~10%) overlap\n")

    # Preview first 2 chunks
    for chunk_idx in range(min(2, len(chunks))):
        chunk = chunks[chunk_idx]

        print("=" * 80)
        print(f"CHUNK {chunk_idx + 1}")
        print("=" * 80)

        # Build dialogue format
        dialogue_parts = []
        your_count = 0
        their_count = 0

        for msg in chunk:
            if msg.get('text'):
                label = "You" if msg.get('is_from_me') else "Them"

                # Clean text artifacts
                import re
                clean_text = msg['text']
                clean_text = re.sub(r'^[&*@,;+)\]\[0-9]+\s*', '', clean_text)
                clean_text = re.sub(r'^[a-zA-Z]\s*(?=[A-Z])', '', clean_text)
                clean_text = re.sub(r'\s*[;,]+$', '', clean_text)
                clean_text = clean_text.strip()

                # Get date and time
                timestamp = ""
                if msg.get('date_formatted'):
                    try:
                        from datetime import datetime
                        parts = msg['date_formatted'].split(' ')
                        date_str = parts[0]
                        time_str = parts[1]
                        ampm = parts[2]

                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_formatted = date_obj.strftime('%b %d')

                        time_formatted = ':'.join(time_str.split(':')[:2]) + ' ' + ampm

                        timestamp = f"[{date_formatted} {time_formatted}] "
                    except:
                        timestamp = ""

                dialogue_parts.append(f"{timestamp}{label}: {clean_text}")

                if msg.get('is_from_me'):
                    your_count += 1
                else:
                    their_count += 1

        dialogue_text = '\n'.join(dialogue_parts)

        # Show what will be sent (truncated to 1600 chars)
        truncated_text = dialogue_text[:1600]

        print(f"\nMessages in chunk: {len(chunk)} ({your_count} from you, {their_count} from them)")
        print(f"Character count: {len(dialogue_text)}")
        print(f"After truncation: {len(truncated_text)} chars (~{len(truncated_text)//4} tokens)")
        print(f"\nText sent to models:")
        print("-" * 80)
        print(truncated_text)
        print("-" * 80)

        if len(dialogue_text) > 1600:
            print(f"\n⚠️  TRUNCATED: {len(dialogue_text) - 1600} characters removed")
            print(f"   Original: {len(dialogue_text)} chars")
            print(f"   Truncated: 1600 chars")

        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preview_chunks.py <phone_number>")
        print("Example: python preview_chunks.py 817-709-1307")
        sys.exit(1)

    preview_chunks(sys.argv[1])
