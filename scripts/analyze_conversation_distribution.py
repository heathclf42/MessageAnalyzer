#!/usr/bin/env python3
"""
Analyze conversation distribution to estimate processing times.
"""

import json
from pathlib import Path

CONVERSATIONS_DIR = Path(__file__).parent / "data" / "output" / "all_conversations"
CHUNK_SIZE = 15
OVERLAP = 5
TIME_PER_CHUNK = 0.5  # seconds (4 model inferences)

# Find all conversation files
all_files = [
    f for f in CONVERSATIONS_DIR.glob("*.json")
    if not f.name.endswith("_analysis.json") and not f.name.endswith("_llm_analysis.json")
]

# Extract message counts
valid_files = []
for f in all_files:
    parts = f.name.split('_')
    if len(parts) >= 2:
        try:
            msg_count = int(parts[1])
            valid_files.append((msg_count, f))
        except ValueError:
            continue

# Sort by message count
valid_files.sort(key=lambda x: x[0])

print("=" * 80)
print("CONVERSATION DISTRIBUTION ANALYSIS")
print("=" * 80)
print(f"\nTotal conversations: {len(valid_files)}")
print(f"Chunk size: {CHUNK_SIZE} messages, Overlap: {OVERLAP}")
print(f"Time per chunk: {TIME_PER_CHUNK}s\n")

# Calculate deciles
total = len(valid_files)
decile_size = total // 10

print("DECILE BREAKDOWN:")
print("-" * 80)
print(f"{'Decile':<10} {'Range':<20} {'Msg Count':<15} {'Chunks':<10} {'Est Time':<15}")
print("-" * 80)

total_chunks = 0
cumulative_time = 0

for i in range(10):
    start_idx = i * decile_size
    end_idx = start_idx + decile_size if i < 9 else total

    decile_convs = valid_files[start_idx:end_idx]

    if not decile_convs:
        continue

    min_msgs = decile_convs[0][0]
    max_msgs = decile_convs[-1][0]

    # Calculate chunks for this decile
    decile_chunks = 0
    for msg_count, _ in decile_convs:
        chunks = max(1, msg_count // (CHUNK_SIZE - OVERLAP))
        decile_chunks += chunks

    decile_time = decile_chunks * TIME_PER_CHUNK
    total_chunks += decile_chunks
    cumulative_time += decile_time

    print(f"{i+1:<10} {min_msgs}-{max_msgs:<15} {len(decile_convs):<15} {decile_chunks:<10} {decile_time/60:.1f} min ({cumulative_time/60:.1f} total)")

print("-" * 80)
print(f"\nTOTAL ESTIMATES:")
print(f"  Total chunks: {total_chunks:,}")
print(f"  Total time: {cumulative_time/60:.1f} minutes ({cumulative_time/3600:.1f} hours)")

# Recommendations
print("\n" + "=" * 80)
print("RECOMMENDATIONS FOR QUICK RESULTS:")
print("=" * 80)

# Find conversations that would complete in < 1 minute
quick_convs = []
for msg_count, f in valid_files:
    chunks = max(1, msg_count // (CHUNK_SIZE - OVERLAP))
    time_estimate = chunks * TIME_PER_CHUNK
    if time_estimate < 60:  # Less than 1 minute
        quick_convs.append((msg_count, f, chunks, time_estimate))

print(f"\nConversations completable in < 1 minute: {len(quick_convs)}")
if quick_convs:
    print(f"  Smallest: {quick_convs[0][0]} messages ({quick_convs[0][2]} chunks, {quick_convs[0][3]:.1f}s)")
    print(f"  Largest in this group: {quick_convs[-1][0]} messages ({quick_convs[-1][2]} chunks, {quick_convs[-1][3]:.1f}s)")

# Find sweet spot: 1-5 minute conversations
medium_convs = []
for msg_count, f in valid_files:
    chunks = max(1, msg_count // (CHUNK_SIZE - OVERLAP))
    time_estimate = chunks * TIME_PER_CHUNK
    if 60 <= time_estimate < 300:  # 1-5 minutes
        medium_convs.append((msg_count, f, chunks, time_estimate))

print(f"\nConversations completable in 1-5 minutes: {len(medium_convs)}")
if medium_convs:
    print(f"  Range: {medium_convs[0][0]}-{medium_convs[-1][0]} messages")
    print(f"  Chunks: {medium_convs[0][2]}-{medium_convs[-1][2]}")

print("\n" + "=" * 80)
print("SUGGESTED PROCESSING ORDER:")
print("=" * 80)
print("1. Start with decile 1 (smallest conversations) for quick validation")
print("2. Then process deciles 2-3 (medium conversations) for broader coverage")
print("3. Finally process deciles 4-10 (large conversations) overnight")
print()
