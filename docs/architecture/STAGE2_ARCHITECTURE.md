# Stage 2: Dual LLM Cumulative Analysis Architecture

## Overview

Stage 2 processes conversations using **two instruction-following LLMs** (Llama 3.2-8B + Qwen 2.5-7B) to provide sophisticated conversation-level psychological analysis with cumulative context management.

## Models

- **Llama 3.2-8B Instruct** (Q4_K_M quantization via Ollama)
- **Qwen 2.5-7B Instruct** (Q4_K_M quantization via Ollama)

Both models run in parallel on each chunk for comparison and ensemble potential.

## Input Data Flow

```
Stage 1 (Per-Message Analysis)
    ↓
┌─────────────────────────────────────────┐
│ Chunk 1                                 │
│ - Messages (450 tokens, 10% overlap)    │
│ - Specialized model scores per message  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Both LLMs Process Chunk 1               │
│                                         │
│ Input:                                  │
│ - Raw messages with timestamps          │
│ - Per-message specialized model scores  │
│                                         │
│ Output:                                 │
│ - Initial psychological assessment      │
│ - Evidence with citations               │
│ - Reasoning for each dimension          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Chunk 2                                 │
│ - New messages (450 tokens)             │
│ - Specialized model scores              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Both LLMs Process Chunk 2               │
│                                         │
│ Input:                                  │
│ - Summary from Chunk 1 (compressed)     │
│ - Raw messages from Chunk 2             │
│ - Per-message specialized model scores  │
│                                         │
│ Output:                                 │
│ - Updated psychological assessment      │
│ - Trend analysis (vs previous)          │
│ - New evidence                          │
└─────────────────────────────────────────┘
    ↓
    (Continue for all chunks...)
```

## Cumulative Summary Management

### Strategy: Hierarchical Compression

**Chunks 1-3**: Keep detailed summaries
- Full assessment for each dimension
- All evidence preserved
- Detailed reasoning

**Chunks 4-6**: Medium compression
- Key findings from chunks 1-3 summarized
- Major patterns noted
- Significant evidence retained

**Chunks 7+**: High compression
- Early conversation (chunks 1-3): High-level trait summary
- Middle conversation (chunks 4-6): Pattern summary
- Recent (current - 2): Detailed assessment
- Current chunk: Full analysis

### Example Compressed Summary

```
PREVIOUS ANALYSIS SUMMARY (Chunks 1-5):

You:
- Toxicity: Low throughout (avg 15/100), professional tone
- Sentiment: Started neutral (50), trending slightly negative (40)
- Personality: Introverted (35), conscientious (75)
- Key pattern: Defensive when criticized, accommodating overall

Them:
- Toxicity: Moderate and increasing (started 40, now 65/100)
- Sentiment: Consistently negative (30/100)
- Personality: Low agreeableness (25), high neuroticism (70)
- Key pattern: Passive-aggressive, indirect criticism escalating

Conversation dynamic: Asymmetric - You attempting de-escalation, Them escalating tension
```

## Prompt Structure

### System Prompt (Chain-of-Thought + Role-Playing)

```
You are an expert psychological analyst specializing in conversation dynamics and personality assessment.
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
- Cite specific evidence from messages
- Explain your reasoning using psychological principles

Output your analysis as valid JSON only, no additional text.
```

### User Prompt Template (Per Chunk)

```
PREVIOUS ANALYSIS:
{compressed_summary_of_previous_chunks}

CURRENT CONVERSATION CHUNK (Chunk {N}):
{formatted_messages_with_timestamps}

SPECIALIZED MODEL SCORES FOR THIS CHUNK:
{per_message_model_scores}

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
- current_assessment: Your score (0-100)
- trend: "stable", "increasing", "decreasing", or "insufficient_data"
- confidence: "low", "medium", "high" (based on amount of data)
- evidence: Array of message quotes with timestamps that support your assessment
- reasoning: 1-2 sentence psychological explanation

Also provide a brief cumulative_summary (2-3 sentences) describing each speaker's overall psychological profile
and the relationship dynamic.

Think through your analysis step by step, considering context, specialized model scores, and conversational
dynamics before providing scores.

Output format:
{json_output_schema}
```

## Output Schema

```json
{
  "chunk_id": 5,
  "model": "llama3.2:8b-instruct",
  "timestamp": "2025-03-15T18:30:00Z",

  "You": {
    "toxicity": {
      "current_assessment": 25,
      "trend": "stable",
      "confidence": "high",
      "evidence": [
        {
          "message": "I mean, I sent it yesterday. That's not really last minute.",
          "timestamp": "Mar 15 02:36 PM",
          "context": "Defending timeline after criticism"
        }
      ],
      "reasoning": "Shows mild defensiveness but remains professional. Specialized models scored 0.15/1.0 for toxicity."
    },

    "sentiment": {
      "current_assessment": 45,
      "trend": "decreasing",
      "confidence": "high",
      "evidence": [...],
      "reasoning": "..."
    },

    "sarcasm": {
      "current_assessment": 10,
      "trend": "stable",
      "confidence": "medium",
      "evidence": [...],
      "reasoning": "..."
    },

    "personality": {
      "openness": {
        "current_assessment": 55,
        "trend": "insufficient_data",
        "confidence": "low",
        "evidence": [],
        "reasoning": "Limited evidence about intellectual curiosity or creativity in work-focused conversation"
      },
      "conscientiousness": {
        "current_assessment": 70,
        "trend": "stable",
        "confidence": "high",
        "evidence": [...],
        "reasoning": "..."
      },
      "extraversion": {
        "current_assessment": 35,
        "trend": "stable",
        "confidence": "medium",
        "evidence": [...],
        "reasoning": "..."
      },
      "agreeableness": {
        "current_assessment": 60,
        "trend": "stable",
        "confidence": "high",
        "evidence": [...],
        "reasoning": "..."
      },
      "neuroticism": {
        "current_assessment": 45,
        "trend": "increasing",
        "confidence": "medium",
        "evidence": [...],
        "reasoning": "..."
      }
    }
  },

  "Them": {
    "toxicity": {...},
    "sentiment": {...},
    "sarcasm": {...},
    "personality": {...}
  },

  "cumulative_summary": "You: Professional and accommodating despite defensiveness when criticized. Them: Increasingly passive-aggressive with indirect criticism pattern. Relationship shows asymmetric tension - one party attempting de-escalation while other escalates.",

  "conversation_dynamic": {
    "power_balance": "uneven - Them more dominant",
    "communication_style": "Them: critical, You: conciliatory",
    "conflict_trajectory": "escalating"
  }
}
```

## Processing Strategy

### Parallel Processing
- Run both models simultaneously on each chunk
- Each model maintains its own cumulative summary
- Store both outputs separately
- Can compare/ensemble later

### Error Handling
- If JSON parsing fails, retry with stricter prompt
- If model refuses/errors, mark chunk as failed, continue with next
- Log all failures for manual review

### Performance Optimization
- Process chunks sequentially (can't parallelize due to cumulative context)
- But run both models in parallel within each chunk
- Estimated time: 5-10 seconds per chunk per model

## Storage Format

```
data/output/all_conversations/
  0020_01338_msgs_817-709-1307_stage2_llama.json
  0020_01338_msgs_817-709-1307_stage2_qwen.json
```

Each file contains array of chunk analyses with full cumulative context.

## Benefits

✅ **Conversation-aware**: Models understand speaker dynamics
✅ **Cumulative context**: Maintains conversation history efficiently
✅ **Evidence-based**: Every score has supporting quotes
✅ **Explainable**: Reasoning provided for each assessment
✅ **Trend detection**: Tracks psychological evolution over time
✅ **Dual models**: Compare outputs, ensemble for robustness
✅ **Structured output**: Consistent JSON for programmatic use

## Next Steps

1. Implement cumulative summary manager
2. Create prompt templates
3. Build JSON parser with validation
4. Implement dual-model processor
5. Test on single conversation
6. Refine prompts based on output quality
