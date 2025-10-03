# Ensemble Model Architecture

## Stage 1: Specialized Models (5 models)

### Personality Detection (2 models - REDUNDANT, will average)
1. **holistic-ai/personality_classifier**
   - Output: `{'label': 'extraversion', 'score': 0.991}`
   - Returns: Single dominant trait with confidence

2. **Minej/bert-base-personality**
   - Output: `{'Extroversion': -0.030, 'Neuroticism': -0.150, 'Agreeableness': 0.317, 'Conscientiousness': 0.314, 'Openness': 0.033}`
   - Returns: All Big 5 scores (raw logits, range: -0.86 to 0.32)

**Ensemble Strategy:**
- Store both outputs individually
- For top-level reporting: Average the two models' Big 5 scores
- Normalize holistic-ai output (convert dominant trait to Big 5 scores)

### Toxicity Detection (1 model)
3. **martin-ha/toxic-comment-model**
   - Output: `{'label': 'non-toxic', 'score': 0.999}`
   - Returns: Binary toxic/non-toxic with confidence

**Note:** Skipping lmsys/toxicchat (requires tiktoken, dependency issue)

### Sarcasm Detection (1 model)
4. **jkhan447/sarcasm-detection-RoBerta-base**
   - Output: `{'label': 'LABEL_0', 'score': 0.9999}`
   - Returns: Binary (LABEL_0=not sarcasm, LABEL_1=sarcasm) with confidence

### Sentiment Analysis (1 model)
5. **finiteautomata/bertweet-base-sentiment-analysis**
   - Output: `{'label': 'POS', 'score': 0.993}`
   - Returns: POS/NEG/NEU with confidence

## Stage 2: Qwen Synthesis

### Input to Qwen:
```
DIALOGUE:
[Dec 18 02:46 AM] You: Hey
[Dec 18 03:12 AM] Them: Hello! Made it home
...

MODEL ANALYSIS (Raw Outputs):

PERSONALITY:
- Model 1 (holistic-ai): extraversion (confidence: 0.991)
- Model 2 (bert-base): Extroversion=-0.030, Neuroticism=-0.150, Agreeableness=0.317, Conscientiousness=0.314, Openness=0.033

TOXICITY:
- Model 1 (toxic-comment): non-toxic (confidence: 0.999)

SARCASM:
- Model 1 (sarcasm-detection): not sarcastic (confidence: 0.9999)

SENTIMENT:
- Model 1 (bertweet): POS (confidence: 0.993)
```

### Qwen Prompt:
```
You are a psychological analysis expert. Analyze the conversation above and synthesize the model outputs to provide speaker-specific assessments.

IMPORTANT:
- The dialogue contains TWO speakers: "You" and "Them"
- Analyze EACH speaker separately based on their messages
- Use the model outputs as supporting evidence, but apply them to the correct speaker

Provide analysis in this EXACT JSON format:

{
  "You": {
    "personality": {
      "openness": <0-100>,
      "conscientiousness": <0-100>,
      "extraversion": <0-100>,
      "agreeableness": <0-100>,
      "neuroticism": <0-100>,
      "raw_scores": {
        "holistic_ai": {"dominant_trait": "...", "confidence": 0.0},
        "bert_base": {"Extroversion": 0.0, "Neuroticism": 0.0, ...}
      }
    },
    "toxicity": {
      "score": <0-100>,
      "raw_scores": {
        "toxic_comment_model": {"is_toxic": false, "confidence": 0.0}
      }
    },
    "sarcasm": {
      "score": <0-100>,
      "raw_scores": {
        "sarcasm_detection": {"is_sarcastic": false, "confidence": 0.0}
      }
    },
    "sentiment": {
      "positive": <0-100>,
      "negative": <0-100>,
      "neutral": <0-100>,
      "raw_scores": {
        "bertweet": {"label": "POS", "confidence": 0.0}
      }
    }
  },
  "Them": {
    // Same structure
  }
}

Output ONLY valid JSON. No markdown, no explanations.
```

### Output Structure:

```json
{
  "You": {
    "personality": {
      "openness": 65,
      "conscientiousness": 72,
      "extraversion": 88,
      "agreeableness": 75,
      "neuroticism": 35,
      "raw_scores": {
        "holistic_ai": {"dominant_trait": "extraversion", "confidence": 0.991},
        "bert_base": {"Extroversion": -0.030, "Neuroticism": -0.150, "Agreeableness": 0.317, "Conscientiousness": 0.314, "Openness": 0.033}
      }
    },
    "toxicity": {
      "score": 2,
      "raw_scores": {
        "toxic_comment_model": {"is_toxic": false, "confidence": 0.999}
      }
    },
    "sarcasm": {
      "score": 0,
      "raw_scores": {
        "sarcasm_detection": {"is_sarcastic": false, "confidence": 0.9999}
      }
    },
    "sentiment": {
      "positive": 85,
      "negative": 10,
      "neutral": 5,
      "raw_scores": {
        "bertweet": {"label": "POS", "confidence": 0.993}
      }
    }
  },
  "Them": {
    // Same structure with their scores
  }
}
```

## Aggregation Strategy

### For Personality (2 redundant models):

**Observed Ranges** (from test_bert_range.py):
- bert-base: **-0.86 to 0.32** (raw logits, mean ~-0.15)
- holistic-ai: **0.0 to 1.0** (confidence scores)

**Normalization Strategy**:
1. **bert-base**: Min-max normalize from [-0.86, 0.32] to [0, 100]
   - Formula: `score_normalized = (score - (-0.86)) / (0.32 - (-0.86)) * 100`
   - Example: -0.86 → 0, -0.15 → 60, 0.32 → 100
2. **holistic-ai**: Convert dominant trait to Big 5 scores
   - Dominant trait: 90-100 (weighted by confidence)
   - Other traits: 40-60 (baseline)
3. **Average** the two normalized sets for top-level reporting
4. **Store raw scores** for debugging/validation

### For Other Metrics (1 model each):
- Direct conversion: confidence → 0-100 score
- Store raw output for reference

## Benefits

✅ **No information loss**: All raw model outputs stored
✅ **Redundancy handled**: Personality models averaged for consensus
✅ **Speaker-aware**: Qwen separates You vs Them
✅ **Comparable metrics**: Everything normalized to 0-100
✅ **Debuggable**: Raw scores available for validation
✅ **Flexible**: Can add/remove models without changing structure
