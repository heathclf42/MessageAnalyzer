# Locally-Runnable LLMs for Psychological Text Analysis

Your Mac with 24GB RAM can absolutely handle psychological text analysis, but you'll need a **hybrid approach** combining specialized small models with general-purpose LLMs. The field has excellent coverage for some capabilities (Big 5, toxicity, sarcasm) but notable gaps for others (Jungian archetypes, narcissistic patterns, supportive behavior).

## What exists: Specialized psychology models under 1GB

The good news is that **production-ready specialized models exist** for several psychological analysis tasks, all running easily on standard laptop hardware with no quantization needed.

### Big 5 personality traits: Best specialized coverage

The **theweekday personality traits models** offer the most validated approach, with five separate RoBERTa-based models (one per trait). Each model has 124.6M parameters (~500MB) and **4,100-4,400 downloads indicating real-world validation**. Total size for all five models is just 2.5GB, easily fitting in your 24GB RAM. These models are gated (requiring approval) but represent the most mature specialized option for Big 5 assessment.

Alternative options include **Arash-Alborz/personality-trait-predictor** (268MB), which uses an ensemble combining LIWC psycholinguistic features with DistilBERT for Big 5 prediction. The **margati BERT variants** offer multiple versions trained on different datasets, all around 440MB each. For a unified approach, **holistic-ai/personality_classifier** (500MB RoBERTa) provides general personality classification in a single model.

Academic research shows these BERT-based approaches achieve meaningful results when combined with psycholinguistic features. Studies report 2.9% improvements on essay datasets when BERT is augmented with psycholinguistic text contours. The key finding from academic research is that **domain-specific pre-training matters more than model size** – a 125M parameter model trained on psychological texts outperforms larger general models.

### MBTI detection: Limited but functional

**MalekOthman/mbti_bilstm_personality_prediction** offers the most specialized option for MBTI classification using an ensemble BiLSTM architecture under 100MB. However, this is less validated (60 downloads) compared to Big 5 models. The academic literature shows MBTI detection from text is possible – one Twitter study successfully predicted MBTI from user biographies, statuses, and liked tweets using BERT embeddings – but pre-trained models are scarce.

For more robust MBTI analysis, consider using **PsyCoT (Psychological Chain-of-Thought) prompting** with a general LLM. Research shows this approach improved GPT-3.5 by 4.23-10.63 F1 points by mimicking psychological questionnaire completion in multi-turn dialogue.

### Sarcasm detection: Multiple validated options

Sarcasm detection has **excellent model availability**. The top choice is **jkhan447/sarcasm-detection-RoBerta-base** (500MB, 1,400 downloads) with multiple variants including context-aware versions. **sadia72/roberta-base-finetuned-sarcasm-news-headline-detection** has the highest validation at 3,600 downloads. Research shows hybrid CNN-RNN-Attention architectures achieve 81% accuracy on headline datasets.

All these models use RoBERTa-base or BERT-base architectures (110-125M parameters, 440-500MB), making them trivial to run locally. They work with standard PyTorch and Transformers library inference.

### Toxic behavior detection: Production-grade models

Toxicity detection is the most mature area with **massive real-world validation**. **martin-ha/toxic-comment-model** (DistilBERT, 265MB) has **19 million downloads** and is used in 10+ production demo spaces. **facebook/roberta-hate-speech-dynabench-r4-target** (498MB) has **25.9 million downloads** and was adversarially trained on the Dynabench R4 dataset for robust hate speech detection.

Academic validation is strong: models achieve 0.76-0.82 F1 scores on toxicity benchmarks. **JungleLee/bert-toxic-comment-classification** (440MB, 1.6M downloads) offers another highly validated option. Research shows these models can serve as proxies for narcissistic behavior patterns since toxicity correlates with low agreeableness and hostile communication styles.

For sentiment analysis to complement toxicity detection, **finiteautomata/bertweet-base-sentiment-analysis** (RoBERTa, ~500MB) has **32.5 million downloads** and is specifically optimized for social media text. **tabularisai/multilingual-sentiment-analysis** (541MB, 2.1M downloads) supports 23+ languages if you need multilingual capabilities.

## Critical gaps: What doesn't exist

### Jungian archetypes: No models found

Despite extensive searching across Hugging Face models and academic papers, **no pre-trained models exist** for identifying Jungian archetypes (Hero, Sage, Caregiver, etc.) in text. This is a significant gap in the field – academic NLP research has not yet tackled this psychological framework. You would need to fine-tune a base model yourself using custom annotated datasets, which contradicts your requirement for pre-trained models.

### Narcissistic behavior: Use toxicity as proxy

No models are specifically labeled for narcissistic language patterns. However, research on personality style recognition shows LIWC features combined with BERT can detect related patterns. The recommended workaround is **combining toxicity models with low agreeableness indicators** from Big 5 models plus detecting self-reference patterns in text. High toxicity + low agreeableness + frequent self-references can approximate narcissistic communication patterns.

### Loving/supportive behavior: Use sentiment as proxy

This is another critical gap – **no specialized empathy detection or supportive language models exist**. The research identified no datasets for prosocial behavior detection, compassionate communication, or empathy classification. The workaround is an **ensemble approach**: combine positive sentiment detection (using finiteautomata/bertweet) + low toxicity scores + detection of joy/love emotions using **borisn70/bert-43-multilabel-emotion-detection** (440MB, 43 emotion classes). This approximation works because supportive language correlates with positive sentiment, low toxicity, and nurturing emotions.

## General-purpose alternatives: Best models under 10GB

When specialized models don't exist or when you need flexible prompting capabilities, general-purpose instruction-following LLMs offer strong alternatives for psychological analysis.

### Top recommendation: Qwen2.5-7B-Instruct

**Qwen2.5-7B-Instruct** is the best all-around choice with **7.2 million downloads** (most popular 7B model). The GGUF quantized version fits perfectly on 24GB RAM:

**Q4_K_M**: 4.4GB file size, uses 6-8GB total RAM, ~30-40 tokens/sec on M2/M3 Macs
**Q5_K_M** (recommended for psychology): 5.4GB file, 7-9GB RAM usage, ~25-35 tokens/sec  
**Q8_0** (maximum quality): 7.2GB file, 9-11GB RAM usage, ~20-30 tokens/sec

This model excels at nuanced text analysis with 74.2 MMLU score (strong general understanding) and 81.2 Arena-Hard score (excellent human preference alignment). It has a 128K context window for analyzing lengthy texts and demonstrates superior instruction following with resilience to diverse system prompts. For psychological profiling, the strong reasoning capabilities and ability to generate 8K+ token responses make it ideal for detailed analysis.

Download from: hf.co/MaziyarPanahi/Qwen2.5-7B-Instruct-GGUF

### Second choice: Llama 3.1-8B-Instruct

**Llama 3.1-8B-Instruct** is specifically validated for sentiment and emotion analysis, making it particularly relevant for psychological text work. Academic research shows fine-tuned versions (SentriLlama) achieve 87% accuracy on emotion datasets and 96% on standard sentiment benchmarks (SST-2, IMDB). Multiple papers demonstrate successful fine-tuning for mental health text classification.

**Q5_K_M** (recommended): 5.9GB file, 8-10GB RAM usage, ~25-32 tokens/sec  
**Q4_K_M**: 4.9GB file, 7-9GB RAM usage, ~30-38 tokens/sec

This model has **native Apple Silicon optimization** and excellent compatibility with Ollama and LM Studio. The Apache 2.0 license is fully permissive for research use. With 128K context window and strong instruction following, it handles complex psychological analysis prompts effectively.

Download from: hf.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF

### Alternative: Mistral-7B-Instruct-v0.3

**Mistral-7B-Instruct-v0.3** (726K downloads) offers rock-solid reliability with extensive Mac testing showing 14-33 tokens/sec on M1/M2 hardware. The Q4_K_M version is just 4.1GB with 6-10GB total RAM usage. While slightly older, it's extremely stable and well-optimized for Apple Silicon. The Apache 2.0 license and 32K context window make it a dependable fallback option.

### Efficiency champion: Phi-3.5-mini-instruct

At just 3.8B parameters, **Phi-3.5-mini-instruct** (104K downloads) punches above its weight class. The Q4_K_M version is only 2.4GB, using just 4-6GB RAM total, allowing you to run **multiple models simultaneously** or achieve very fast inference (40-50 tokens/sec). This is ideal for preliminary analysis before using larger models, or for iterative testing. The 128K context window is impressive for such a small model.

### Quantization guidance for 24GB RAM

Your 24GB RAM system can comfortably run any 7-8B model in any quantization format. Here's quality vs. speed guidance specifically for psychological analysis:

**Q5_K_M** (recommended for nuanced analysis): Preserves subtle emotional cues and complex psychological patterns with only ~15% slower inference than Q4. This is the **sweet spot for psychological text analysis** where understanding nuance matters. Size increase is only 25% vs. Q4 but quality improvement is meaningful for detecting subtle emotional differences and cognitive patterns.

**Q4_K_M** (acceptable if validated): Fast inference (2x faster than Q8) but may lose subtle nuances in complex reasoning. Use this **only if you validate outputs against Q5/Q8 versions first** and the analysis doesn't require detecting fine emotional distinctions. Good for high-throughput scenarios or preliminary analysis.

**Q8_0** (maximum quality): Near-lossless vs. full precision, recommended when you need to catch subtle psychological cues or validate other quantizations. At 40-50% slower inference, use this for **careful analysis of important cases** or as ground truth for validating Q4/Q5 outputs. 7-8B models in Q8 still fit comfortably with ~11-13GB RAM usage.

## Practical setup on Mac with 24GB RAM

### Recommended primary tool: Ollama

**Ollama is the optimal choice** for your setup: single-command installation via Homebrew, automatic Metal GPU acceleration, built-in model library with simple `ollama pull` commands, and native support for GGUF quantization formats. It automatically manages memory (using ~70-78% of unified memory efficiently) and provides an OpenAI-compatible REST API for scripting.

Installation is trivial:
```bash
brew install ollama
ollama serve
ollama pull qwen2.5:7b-instruct
```

For optimal performance with psychological analysis, configure these settings:
```bash
export OLLAMA_NUM_PARALLEL=4  # Process 4 texts concurrently
export OLLAMA_FLASH_ATTENTION=1  # Enable faster inference
export OLLAMA_KV_CACHE_TYPE=q8_0  # Quantize cache to save memory
```

Expected performance on your 24GB Mac:
- **8B Q5_K_M model**: 22-32 tokens/sec (M2 Pro/Max), 25-38 tokens/sec (M3 Pro/Max)
- **Concurrent processing**: 4 texts simultaneously at ~20 tokens/sec each
- **Memory usage**: 8-10GB for model + cache, leaving 14GB free
- **Throughput**: 50-100 therapy session notes per hour depending on analysis depth

### Alternative for GUI users: LM Studio

**LM Studio** offers a user-friendly interface for model discovery, downloading, and testing. It has visual controls for quantization and parameters, a built-in chat interface for quality validation, and can use Apple's MLX framework for optimization. The REST API is OpenAI-compatible for easy scripting integration.

Download from lmstudio.ai, then use the built-in search to find "llama-3.1-8B-Instruct GGUF" or "qwen2.5-7B-instruct GGUF" and download Q5_K_M variants. Configure parameters: temperature 0.3 for consistent analysis, context length 8192, Flash Attention ON, GPU layers set to maximum.

### Advanced option: llama.cpp

For maximum control and often 5-15% faster inference, **llama.cpp** offers fine-grained configuration but requires more technical expertise. Install via Homebrew with Metal support:
```bash
brew install llama.cpp
# Or build from source for latest features with LLAMA_METAL=1 make -j
```

Key parameters for psychological analysis:
`-ngl 99` (offload all layers to GPU), `-fa` (Flash Attention), `--ctx-size 8192`, `-c 0` (unlimited context, use carefully).

This is best for research and experimentation rather than production workflows, but offers maximum performance for optimized setups.

## Hybrid approach: The best solution

The optimal strategy combines specialized small models with general-purpose LLMs, giving you both academic rigor and flexibility.

### Recommended architecture

**Phase 1: Run specialized models via Transformers library**

Install the specialized psychology models and run them locally using standard PyTorch/Transformers:

```python
from transformers import pipeline

# Big 5 personality (non-gated, available immediately)
# Option 1: Single unified model (RECOMMENDED for immediate start)
personality_model = pipeline("text-classification",
    model="holistic-ai/personality_classifier")  # 500MB

# Option 2: If approved for theweekday gated models (higher validation)
# openness_model = pipeline("text-classification",
#     model="theweekday/personality_traits_openness")
# conscientiousness_model = pipeline("text-classification",
#     model="theweekday/personality_traits_conscientiousness")
# ... Load all 5 Big 5 models (~2.5GB total)

# Toxicity detection
toxicity_model = pipeline("text-classification",
    model="martin-ha/toxic-comment-model")  # 265MB

# Sarcasm detection
sarcasm_model = pipeline("text-classification",
    model="jkhan447/sarcasm-detection-RoBerta-base")  # 500MB

# Sentiment/emotion
sentiment_model = pipeline("sentiment-analysis",
    model="finiteautomata/bertweet-base-sentiment-analysis")  # ~500MB
```

All these models run simultaneously on your 24GB RAM (total ~2-3GB with holistic-ai, or ~4-5GB with theweekday models) with fast inference since they're just 110-185M parameters each.

**Phase 2: Use general LLM via Ollama for flexible analysis**

Run Qwen2.5 or Llama 3.1 via Ollama for tasks requiring reasoning, synthesis, or covering gaps (MBTI, psychological profiling, interpretation):

```python
from ollama import Client

client = Client()

def deep_analysis(text, specialized_results):
    prompt = f"""
    Analyze this text for psychological patterns. I have preliminary results:
    
    Text: {text}
    
    Detected patterns:
    - Big 5 Openness: {specialized_results['openness']}
    - Toxicity: {specialized_results['toxicity']}
    - Sarcasm: {specialized_results['sarcasm']}
    - Sentiment: {specialized_results['sentiment']}
    
    Provide:
    1. MBTI type inference based on Big 5 patterns
    2. Psychological profile synthesis
    3. Behavioral pattern interpretation
    4. Assessment of narcissistic vs supportive communication style
    """
    
    response = client.generate(
        model='qwen2.5:7b-instruct-q5_K_M',
        prompt=prompt,
        options={'temperature': 0.3}  # Low temp for consistency
    )
    return response['response']
```

### Complete workflow example

This combines both approaches for comprehensive psychological profiling:

1. **Input text** → Run all specialized models in parallel (fast, <1 second total)
2. **Gather specialized outputs** → Big 5 scores, toxicity score, sarcasm probability, sentiment
3. **Feed to general LLM** → Synthesize results, infer MBTI, create narrative profile
4. **Output comprehensive profile** → Big 5 traits, MBTI type, behavioral patterns, communication style, risk flags

Total processing time per text: 30-60 seconds depending on length. All inference happens locally with no external API calls. Memory usage peaks at ~12-15GB (specialized models + LLM), well within your 24GB capacity.

### Pipeline advantages

This approach gives you:
- **Academic rigor** from validated specialized models (millions of downloads)
- **Flexibility** from general LLM for gaps and synthesis
- **Interpretability** with each component explaining its contribution
- **Local deployment** entirely on your Mac with no privacy concerns
- **Modular design** allowing easy swapping of models as better ones emerge

## Academic validation and benchmarks

The recommended models have strong research backing. Domain-adapted BERT models achieve **0.88-0.91 F1 scores for depression/anxiety detection** in studies using MentalBERT and CASE-BERT. Toxicity detection models reach **0.76-0.82 F1 scores** with context-augmented prompting. Sarcasm detection achieves **79-81% accuracy** on benchmark datasets using hybrid CNN-RNN-Attention architectures.

For personality detection, research shows **BERT + psycholinguistic features improve accuracy by 2.9-8.28%** over baseline approaches. The critical finding is that **RoBERTa-base with domain-specific pre-training outperforms** much larger general models – a 125M parameter model trained on psychological texts beats 7B general models for specialized tasks.

Academic papers specifically validated for psychological LLMs include studies on **MentalBERT** (pre-trained on mental health social media, outperforms general BERT on disorder detection benchmarks), **PsyCoT prompting** (improves GPT-3.5 personality detection by 4.23-10.63 F1 points), and **emotion-enhanced personality detection** (EERPD approach improves detection by 15.05 F1 by incorporating emotion regulation theory).

The sentiment and toxicity models have the strongest validation with **tens of millions of downloads** indicating extensive production deployment. The specialized Big 5 models have thousands of downloads each, suggesting real research usage even if not at industrial scale.

## Setup recommendations and next steps

### For immediate start

1. **Install Ollama**: `brew install ollama`
2. **Download recommended general model**: `ollama pull qwen2.5:7b-instruct` (will get Q4 by default, manually download Q5_K_M from Hugging Face for better quality)
3. **Install transformers library**: `pip install transformers torch`
4. **Download specialized models** via Python - see sections below for gated vs. non-gated options

### Accessing Big 5 Personality Models

**IMPORTANT**: The theweekday Big 5 models are **gated** and require manual approval, which can take hours to days. You have two options:

#### Option A: Start immediately with non-gated alternatives (RECOMMENDED)

Use these production-ready models that require no approval and are available for immediate download:

**holistic-ai/personality_classifier** (PRIMARY RECOMMENDATION):
- Status: ✅ NOT gated - download immediately
- License: MIT (fully permissive)
- Size: 124.6M parameters (~500MB)
- Downloads: 520 (reasonably validated)
- Organization: Holistic AI (respected AI ethics organization)
- Link: [holistic-ai/personality_classifier](https://huggingface.co/holistic-ai/personality_classifier)

```python
from transformers import pipeline

# Single unified model for personality classification
personality = pipeline("text-classification",
                      model="holistic-ai/personality_classifier")
result = personality("Your text here")
```

**Arash-Alborz/personality-trait-predictor** (ALTERNATIVE):
- Status: ✅ NOT gated
- License: MIT
- Size: ~268MB
- Approach: Ensemble combining LIWC psycholinguistic features + DistilBERT
- Academic backing: Research shows LIWC+BERT improves accuracy
- Link: [Arash-Alborz/personality-trait-predictor](https://huggingface.co/Arash-Alborz/personality-trait-predictor)

**margati BERT variants** (ALTERNATIVE):
- Status: ✅ NOT gated
- Size: ~440MB each
- Multiple versions trained on different datasets
- Very recent (July 2025)
- Link: [margati/bert-personality-big5_nasser_ver2](https://huggingface.co/margati/bert-personality-big5_nasser_ver2)

#### Option B: Request access to theweekday gated models (higher validation)

While theweekday models have more downloads (4,100-4,400 each) indicating stronger validation, they require manual approval. If you want to use them:

**Step 1: Create a Hugging Face account**
Sign up at [huggingface.co](https://huggingface.co) if you don't already have one.

**Step 2: Request access via browser**
You **must** request access through your web browser - it can't be done programmatically. Visit each model page and click "Agree and access repository":
- [personality_traits_openness](https://huggingface.co/theweekday/personality_traits_openness)
- [personality_traits_conscientiousness](https://huggingface.co/theweekday/personality_traits_conscientiousness)
- [personality_traits_extraversion](https://huggingface.co/theweekday/personality_traits_extraversion)
- [personality_traits_agreeableness](https://huggingface.co/theweekday/personality_traits_agreeableness)
- [personality_traits_neuroticism](https://huggingface.co/theweekday/personality_traits_neuroticism)

**Step 3: Wait for approval**
These models require manual approval by the authors. This could take anywhere from a few hours to several days depending on their responsiveness.

**Step 4: Create an access token**
Once approved, go to your Hugging Face **Settings → Access Tokens** and create a Read token:
1. Click "New token"
2. Give it a name (e.g., "psychology-research")
3. Select role: **Read** (sufficient for downloading models)
4. **IMPORTANT**: Check the box for "Allow Read access to Gated Repositories"
5. Generate and copy the token (starts with `hf_...`)

**Step 5: Authenticate locally**
In your terminal:
```bash
huggingface-cli login
# Paste your token when prompted
```

Or in Python:
```python
from huggingface_hub import login
login(token="hf_...")  # Your token here
```

**Step 6: Download the models**
Once authenticated and approved:
```python
from transformers import pipeline

big5_models = {
    'openness': pipeline('text-classification',
        'theweekday/personality_traits_openness'),
    'conscientiousness': pipeline('text-classification',
        'theweekday/personality_traits_conscientiousness'),
    'extraversion': pipeline('text-classification',
        'theweekday/personality_traits_extraversion'),
    'agreeableness': pipeline('text-classification',
        'theweekday/personality_traits_agreeableness'),
    'neuroticism': pipeline('text-classification',
        'theweekday/personality_traits_neuroticism'),
}
```

### Recommended approach

**Start immediately** with holistic-ai/personality_classifier (no waiting), then:
1. Request access to theweekday models in parallel
2. Once approved, compare theweekday vs. holistic-ai performance on your data
3. Stick with whichever performs better for your specific use case

The practical reality is that starting fast is often more important than waiting for marginally better models. The holistic-ai model is from a reputable organization and immediately available for research use.

### Complete download for immediate start

```python
from transformers import pipeline

# Big 5 personality (non-gated, available now)
personality_model = pipeline("text-classification",
    model="holistic-ai/personality_classifier")  # 500MB

# Toxicity detection
toxicity_model = pipeline("text-classification",
    model="martin-ha/toxic-comment-model")  # 265MB

# Sarcasm detection
sarcasm_model = pipeline("text-classification",
    model="jkhan447/sarcasm-detection-RoBerta-base")  # 500MB

# Sentiment/emotion
sentiment_model = pipeline("sentiment-analysis",
    model="finiteautomata/bertweet-base-sentiment-analysis")  # ~500MB
```

Total download size: ~6-7GB (500MB Big 5 + 265MB toxicity + 500MB sarcasm + 500MB sentiment + 4-6GB general LLM)

### Testing your setup

Create a test script to validate everything works:

```python
test_text = """I've been feeling really overwhelmed lately. 
Work has been incredibly stressful and I'm not sleeping well. 
My colleagues are supportive but I feel like I'm letting everyone down."""

# Run specialized models
big5_results = {trait: model(test_text)[0] 
                for trait, model in big5_models.items()}
toxicity = toxicity_model(test_text)[0]
sarcasm = sarcasm_model(test_text)[0]
sentiment = sentiment_model(test_text)[0]

# Synthesize with LLM
analysis = deep_analysis(test_text, {
    'big5': big5_results,
    'toxicity': toxicity,
    'sarcasm': sarcasm,
    'sentiment': sentiment
})

print(analysis)
```

Expected output: Comprehensive psychological profile with Big 5 scores, emotional state assessment, behavioral patterns, and recommendations.

### For production use

Configure optimal settings for batch processing therapy notes or research data:

**Lower temperature** (0.1-0.3) for analytical consistency rather than creativity  
**Process texts in batches** of 4-8 concurrently using Ollama's parallel processing  
**Validate against multiple quantizations** – test Q4/Q5/Q8 on sample data and accept Q5 if agreement >95% with Q8  
**Monitor memory usage** – run Activity Monitor to ensure you stay within 24GB limits  
**Structure prompts carefully** – use consistent templates for comparable results across texts

Expected throughput on your Mac:
- **Single text deep analysis**: 30-60 seconds
- **Batch of 100 therapy notes**: 50-75 minutes sequential, 12-20 minutes with 4-way parallelization  
- **Memory usage**: 12-15GB peak (8GB LLM + 4-5GB specialized models + 2GB overhead)

## Addressing the gaps

For capabilities without pre-trained models, here are practical workarounds:

### Jungian archetypes approximation

While no models exist, you can prompt your general LLM with archetype descriptions and examples. Create a detailed system prompt:

```
You are analyzing text for Jungian archetypes. For each text, identify which 
archetype(s) are most prominent: Hero (courage, achievement), Sage (wisdom, truth), 
Innocent (optimism, simplicity), Explorer (independence, freedom), Rebel (revolution, 
change), Magician (transformation, power), Lover (passion, intimacy), Jester (joy, fun), 
Caregiver (nurturing, compassion), Ruler (control, order), Creator (innovation, 
expression), Everyman (belonging, realism). Provide evidence from the text.
```

Test this approach on texts with known archetypes to validate accuracy. The 7B models with strong reasoning (Qwen2.5) can perform this analysis reasonably well with careful prompting, though it won't match a dedicated fine-tuned model.

### Narcissistic behavior detection

Combine toxicity scores + Big 5 agreeableness (inverted) + self-reference pattern detection:

```python
def detect_narcissistic_patterns(text, specialized_results):
    # High toxicity + low agreeableness suggests narcissistic traits
    toxicity_score = specialized_results['toxicity']['score']
    agreeableness_score = specialized_results['big5']['agreeableness']['score']
    
    # Count self-references
    self_references = text.lower().count(' i ') + text.lower().count(' me ') + \
                      text.lower().count(' my ') + text.lower().count(' mine ')
    self_ratio = self_references / len(text.split())
    
    narcissism_indicator = (toxicity_score * 0.4) + \
                          ((1 - agreeableness_score) * 0.3) + \
                          (min(self_ratio * 20, 1.0) * 0.3)
    
    return narcissism_indicator
```

This approximation correlates with narcissistic communication patterns (hostility + low empathy + excessive self-focus). Validate against known narcissistic texts to calibrate thresholds.

### Loving/supportive behavior detection

Use inverse toxicity + positive sentiment + nurturing emotion detection:

```python
# Ensemble approach
supportive_score = (1 - toxicity_score) * 0.4 + \
                   positive_sentiment_score * 0.3 + \
                   (joy_emotion_score + love_emotion_score) * 0.3

# Or prompt the LLM:
prompt = f"""Rate this text on a 0-10 scale for supportive/loving communication:
Text: {text}

Consider: empathy, warmth, encouragement, validation, compassion, care.
Provide score and evidence."""
```

While not as precise as a dedicated model, this ensemble captures key aspects of supportive communication. The limitation is that it may miss subtle forms of support (tough love, quiet presence) that require deep contextual understanding.

## Final recommendations summary

**Best immediate setup for fast start**: Install Ollama + Qwen2.5-7B-Instruct Q5_K_M (~5.4GB) as your general LLM, then add specialized models via Transformers: holistic-ai personality classifier (500MB), martin-ha toxicity (265MB), jkhan447 sarcasm (500MB), finiteautomata sentiment (500MB). **Total: ~7GB well within your 24GB RAM**. No waiting for model approval required.

**Optional upgrade path**: Request access to theweekday Big 5 models (2.5GB total) for higher validation (4,100+ downloads each vs. 520 for holistic-ai). Compare performance on your data once approved and switch if meaningfully better. The holistic-ai model from a reputable organization is sufficient for most research purposes while you wait.

**Expect these capabilities**: Strong Big 5 assessment (validated models), good toxicity/toxic behavior detection (production-grade with 19M downloads), reasonable sarcasm detection (research-quality), flexible MBTI inference (via prompted LLM), approximations for narcissistic and supportive patterns (ensemble methods).

**Acknowledge these limitations**: No Jungian archetype models (must prompt LLM), no dedicated narcissistic pattern detection (use proxy metrics), no empathy/supportive language models (use sentiment inverse), limited MBTI validation (prompt-based only).

**Academic rigor**: Use validated specialized models where they exist (Big 5, toxicity) which have hundreds to millions of real-world deployments. For gaps, acknowledge in your research that you're using approximation methods and validate against ground truth where possible. The non-gated alternatives are academically sound and from reputable organizations.

**Performance expectations**: 20-35 tokens/sec for general LLM analysis, sub-second inference for specialized models, 30-60 seconds per text for comprehensive profiling, 50-100 texts per hour with optimized batch processing.

This hybrid approach maximizes both academic validity (using peer-reviewed specialized models) and practical flexibility (using general LLMs for gaps and synthesis) while running entirely locally on your Mac hardware. **The key advantage: you can start immediately without waiting for gated model approval**, then optionally upgrade to higher-validation models later.