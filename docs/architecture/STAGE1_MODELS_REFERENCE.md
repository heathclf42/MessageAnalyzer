# Stage 1: Model Reference Guide

Complete reference for all 5 specialized models used in Stage 1 analysis.

---

## Model 1: Holistic AI Personality Classifier

**Model**: `holistic-ai/personality_classifier`
**Type**: Text Classification
**Task**: Big 5 Personality Classification

### Input
- **Format**: Raw text string
- **Max Length**: 512 tokens (~2000 characters)
- **Context Window**: 512 tokens
- **Preprocessing**: Truncation enabled

### Output
- **Format**: Single label classification
- **Labels**:
  - `extraversion`
  - `neuroticism`
  - `agreeableness`
  - `openness`
  - `conscientiousness`
- **Confidence Score**: Float (0.0 to 1.0)

### Example
```python
Input: "I love going to parties and meeting new people!"
Output: {
    'label': 'extraversion',
    'score': 0.89
}
```

---

## Model 2: BERT Base Personality (Big 5)

**Model**: `Minej/bert-base-personality`
**Type**: Sequence Classification (Multi-output)
**Task**: Big 5 Personality Regression

### Input
- **Format**: Raw text string
- **Max Length**: 512 tokens (~2000 characters)
- **Context Window**: 512 tokens (BERT base)
- **Preprocessing**: BERT tokenization

### Output
- **Format**: 5 continuous scores (regression values)
- **Dimensions**:
  1. `Extroversion`: Float (-1.0 to 1.0 typical range)
  2. `Neuroticism`: Float (-1.0 to 1.0 typical range)
  3. `Agreeableness`: Float (-1.0 to 1.0 typical range)
  4. `Conscientiousness`: Float (-1.0 to 1.0 typical range)
  5. `Openness`: Float (-1.0 to 1.0 typical range)

### Example
```python
Input: "I love going to parties and meeting new people! Social events are so exciting."
Output: {
    'Extroversion': 0.1314,
    'Neuroticism': 0.1816,
    'Agreeableness': -0.0754,
    'Conscientiousness': -0.5306,
    'Openness': -0.0290
}
```

**Note**: Higher positive values = stronger trait expression

---

## Model 3: Martin-HA Toxic Comment Model

**Model**: `martin-ha/toxic-comment-model`
**Type**: Text Classification (Binary)
**Task**: Toxicity Detection

### Input
- **Format**: Raw text string
- **Max Length**: 512 tokens (~2000 characters)
- **Context Window**: 512 tokens
- **Preprocessing**: Truncation enabled

### Output
- **Format**: Binary classification
- **Labels**:
  - `toxic`: Contains toxic/harmful content
  - `non-toxic`: Clean content
- **Confidence Score**: Float (0.0 to 1.0)

### Example
```python
Input: "You're an idiot and nobody likes you."
Output: {
    'label': 'toxic',
    'score': 0.95
}

Input: "Have a great day!"
Output: {
    'label': 'non-toxic',
    'score': 0.98
}
```

---

## Model 4: Sarcasm Detection RoBERTa

**Model**: `jkhan447/sarcasm-detection-RoBerta-base`
**Type**: Text Classification (Binary)
**Task**: Sarcasm Detection

### Input
- **Format**: Raw text string
- **Max Length**: 512 tokens (~2000 characters)
- **Context Window**: 512 tokens (RoBERTa base)
- **Preprocessing**: Truncation enabled

### Output
- **Format**: Binary classification
- **Labels**:
  - `sarcasm`: Sarcastic text
  - `not sarcasm`: Sincere/literal text
- **Confidence Score**: Float (0.0 to 1.0)

### Example
```python
Input: "Oh great, another meeting. Just what I needed."
Output: {
    'label': 'sarcasm',
    'score': 0.87
}

Input: "I'm excited about this opportunity!"
Output: {
    'label': 'not sarcasm',
    'score': 0.91
}
```

---

## Model 5: BERTweet Sentiment Analysis

**Model**: `finiteautomata/bertweet-base-sentiment-analysis`
**Type**: Text Classification (Multi-class)
**Task**: Sentiment Analysis

### Input
- **Format**: Raw text string (optimized for social media/informal text)
- **Max Length**: 128 tokens (~512 characters)
- **Context Window**: 128 tokens
- **Preprocessing**: Truncation enabled, tweet-style tokenization

### Output
- **Format**: Three-class classification
- **Labels**:
  - `POS`: Positive sentiment
  - `NEU`: Neutral sentiment
  - `NEG`: Negative sentiment
- **Confidence Score**: Float (0.0 to 1.0)

### Example
```python
Input: "I love this! Everything is wonderful!"
Output: {
    'label': 'POS',
    'score': 0.96
}

Input: "This is terrible. I hate everything about this."
Output: {
    'label': 'NEG',
    'score': 0.94
}

Input: "The meeting is at 3pm."
Output: {
    'label': 'NEU',
    'score': 0.88
}
```

---

## Stage 1 Processing Flow

### Batch Processing
- **Batch Size**: 16 chunks (configurable)
- **Chunk Size**: 15 messages with 5-message overlap
- **GPU Support**: MPS (Mac), CUDA (Linux/Windows), CPU fallback
- **Processing Mode**: Parallel batch inference

### Context Preservation
Each chunk maintains conversational context:
```
Chunk Format:
[Dec 18 02:30 PM] You: Hey, how are you?
[Dec 18 02:31 PM] Them: I'm good, thanks!
[Dec 18 02:32 PM] You: That's great to hear.
```

### Output Aggregation
Results from all 5 models are aggregated per speaker:
- Personality: Primary trait + distribution
- Toxicity: Rate (%) + count
- Sarcasm: Rate (%) + count
- Sentiment: Distribution (POS/NEG/NEU %)

---

## Model Comparison Table

| Model | Task | Context | Output Type | Labels/Dims | Speed |
|-------|------|---------|-------------|-------------|-------|
| **holistic-ai** | Personality | 512 tok | Single label | 5 traits | Fast |
| **BERT Base** | Personality | 512 tok | 5 scores | Big 5 values | Medium |
| **martin-ha** | Toxicity | 512 tok | Binary | toxic/non-toxic | Fast |
| **RoBERTa** | Sarcasm | 512 tok | Binary | sarcasm/sincere | Medium |
| **BERTweet** | Sentiment | 128 tok | 3-class | POS/NEG/NEU | Fast |

---

## Notes

1. **Context Windows**: All models use transformer-based architectures with fixed context windows. Text exceeding the limit is truncated.

2. **BERT Base Personality**: Provides continuous scores rather than categorical labels, allowing for more nuanced personality analysis.

3. **BERTweet**: Shorter context window (128 tokens) because it's optimized for tweet-length content. Sufficient for individual message analysis.

4. **Batch Processing**: All models support batch inference for improved performance (16 messages processed simultaneously).

5. **ToxicChat Model**: Originally included but removed due to Python 3.13 compatibility issues with SentencePiece tokenizer.

---

## Usage in Stage 1

```python
from llm_analyzer import LLMAnalyzer

# Initialize analyzer
analyzer = LLMAnalyzer(use_gpu=True)

# Analyze conversation
results = analyzer.analyze_conversation(
    messages=messages,
    chunk_size=15,
    overlap=5,
    batch_size=16
)

# Results structure
{
    'your_analysis': {
        'personality': {
            'primary_trait': 'neuroticism',
            'trait_distribution': {'extraversion': 92, 'neuroticism': 481, ...}
        },
        'toxicity': {
            'rate': 0.012,  # 1.2% of messages
            'toxic_messages': 8,
            'total_analyzed': 623
        },
        'sarcasm': {
            'rate': 0.0,
            'sarcastic_messages': 0,
            'total_analyzed': 623
        },
        'sentiment': {
            'distribution': {'POS': 115, 'NEG': 80, 'NEU': 428},
            'positive_rate': 0.185,
            'negative_rate': 0.128,
            'neutral_rate': 0.687
        }
    },
    'their_analysis': { ... },
    'metadata': {
        'total_messages': 1338,
        'chunks_analyzed': 1268
    }
}
```
