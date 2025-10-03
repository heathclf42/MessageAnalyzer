# Stage 2: Citation-Based Analysis - Prompt Engineering

## Overview

This document contains the actual prompts that will be sent to LLMs for citation-based analysis.

---

## System Prompt

```
You are a relationship dynamics analyst specializing in text message conversation analysis.

Your task is to analyze conversations and provide evidence-based assessments with precise citations.

CRITICAL RULES:
1. Every claim MUST be supported by exact message citations
2. Citation format: [DATE TIME | SENDER: "exact message text"]
   Example: [2018-12-21 10:37PM | YOU: "Yo"]
3. Use multiple citations to support claims: [citation1] [citation2]
4. Never make claims without direct evidence
5. State "Insufficient evidence" when you cannot support a claim
6. Include confidence levels: HIGH, MEDIUM, or LOW

Your analysis should be precise, factual, and verifiable.
```

---

## Analysis Prompt Template

```
Analyze the following text message conversation.

CONVERSATION DETAILS:
- Person A (YOU): Messages where is_from_me = true
- Person B ({phone_number}): Messages where is_from_me = false
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
```

---

## Example of Formatted Messages for Prompt

```
[2018-12-21 10:37:05 PM] YOU: "Yo"
[2018-12-21 10:37:42 PM] 309-339-1100: "Hey dude!"
[2018-12-21 10:38:08 PM] YOU: ",I'm home for several days. We should hang."
[2018-12-21 10:39:59 PM] 309-339-1100: "Awesome. Are you home now?"
[2018-12-21 10:40:06 PM] YOU: "Yes"
[2018-12-21 10:40:47 PM] 309-339-1100: "=Cool; no doubt a crazy busy couple days...when do you return?"
[2018-12-21 10:41:02 PM] YOU: "I leave the 26th"
```

---

## Expected LLM Response Format

```
1. RELATIONSHIP TYPE

**Assessment**: Close friendship, characterized by casual communication style and proactive effort to meet in person.

**Evidence**:
- [2018-12-21 10:37:05 PM | YOU: "Yo"] Casual, informal greeting typical of friends
- [2018-12-21 10:37:42 PM | 309-339-1100: "Hey dude!"] Reciprocal casual greeting with "dude" indicating friendly familiarity
- [2018-12-21 10:38:08 PM | YOU: ",I'm home for several days. We should hang."] Proactive invitation to spend time together suggests valued friendship

**Confidence**: HIGH

---

2. COMMUNICATION INITIATION

**Assessment**: In this sample, YOU initiated the conversation and proposed meeting up.

**Evidence**:
- [2018-12-21 10:37:05 PM | YOU: "Yo"] First message in this exchange
- [2018-12-21 10:38:08 PM | YOU: ",I'm home for several days. We should hang."] Proactive proposal to meet

**Confidence**: MEDIUM (sample is too small to establish overall pattern)

---

[Continue for remaining analysis tasks...]
```

---

## JSON Output Format (for parsing)

After the human-readable analysis, we can request JSON:

```
Now output your analysis in JSON format for machine parsing:

{
  "relationship_type": {
    "assessment": "Close friendship",
    "citations": [
      {
        "date": "2018-12-21 10:37:05 PM",
        "sender": "YOU",
        "text": "Yo",
        "reasoning": "Casual informal greeting"
      }
    ],
    "confidence": "HIGH"
  },
  "communication_initiation": { ... },
  "response_patterns": { ... },
  "tone_sentiment": { ... },
  "key_topics": { ... },
  "conflict_indicators": { ... },
  "emotional_support": { ... }
}
```

---

## Implementation Notes

1. **Message Formatting**: Convert JSON messages to readable format for LLM
2. **Chunking Strategy**: For long conversations, analyze in chunks (e.g., 100-200 messages)
3. **Citation Extraction**: Parse LLM response to extract citations and link back to message_ids
4. **Confidence Aggregation**: Track confidence levels across multiple chunks
5. **Evidence Validation**: Verify that cited messages actually exist in source data
