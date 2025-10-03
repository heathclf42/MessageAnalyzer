# Conversation Analysis Methodology

## Overview
This analysis uses computational linguistics and psychological frameworks to quantify communication patterns and personality indicators in text conversations.

---

## 1. Jungian Archetype Analysis

**Framework:** Carl Jung's 12 Archetypes (Hero, Sage, Explorer, Innocent, Caregiver, Rebel, Magician, Lover, Jester, Everyperson, Ruler, Creator)

**Methodology:**
- Keyword matching against archetype-specific vocabularies
- Each archetype has 10-15 characteristic words/phrases
- Example keywords:
  - **Sage**: understand, learn, know, wisdom, truth, think, analyze, research
  - **Caregiver**: help, care, support, protect, nurture, love, give, comfort
  - **Hero**: brave, challenge, overcome, fight, strong, courage, victory, achieve

**Calculation:**
1. Combine all messages from person into single text corpus
2. Count keyword matches for each archetype
3. Calculate percentage distribution: `(matches_for_archetype / total_matches) * 100`
4. Primary archetype = highest percentage

**Limitations:**
- Surface-level language analysis; doesn't capture context or sarcasm
- Cultural and linguistic biases in keyword selection
- Some people exhibit multiple archetypes strongly

---

## 2. Enneagram Type Analysis

**Framework:** 9 Enneagram Personality Types

**Methodology:**
- Similar keyword matching approach as archetypes
- Keywords represent core fears, desires, and behavioral patterns
- Example keywords:
  - **Type 1 (Perfectionist)**: should, must, right, wrong, perfect, improve, correct, better
  - **Type 2 (Helper)**: help, need, care, support, for you, give, love
  - **Type 6 (Loyalist)**: worry, anxious, safe, trust, loyal, cautious, prepared

**Calculation:**
1. Count keyword occurrences across all 9 types
2. Highest count = likely type
3. Secondary types are also tracked

**Limitations:**
- Enneagram requires deep self-knowledge; text analysis provides surface indicators only
- Stress/growth patterns not captured
- Wing types not calculated

---

## 3. MBTI (Myers-Briggs Type Indicator)

**Framework:** 4 dichotomies (I/E, S/N, T/F, J/P)

**Methodology:**
- Separate keyword lists for each of 8 preferences
- Keywords indicate cognitive function preferences
- Examples:
  - **Extraversion**: energized by people, talk, social, outgoing, group
  - **Introversion**: quiet, alone, recharge, think before, inner, private
  - **Thinking**: logical, analyze, objective, fair, reason
  - **Feeling**: feel, empathy, harmony, values, care about

**Calculation:**
1. Count keywords for each preference
2. For each dichotomy, compare counts:
   - If Extraversion > Introversion → E
   - If Sensing > Intuition → S
   - If Thinking > Feeling → T
   - If Judging > Perceiving → J
3. Combine letters to form 4-letter type (e.g., ESTP, INFJ)

**Limitations:**
- MBTI has limited scientific validity
- Text-based assessment misses non-verbal communication
- Situational context affects language use

---

## 4. Attachment Style Analysis

**Framework:** Attachment Theory (Bowlby, Ainsworth) - 4 styles

**Methodology:**
- Keywords indicate relationship patterns and emotional regulation
- Attachment keywords:
  - **Secure**: comfortable, trust, close, independent, honest, communicate, balance
  - **Anxious**: worry, need reassurance, fear losing, clingy, overthink, insecure
  - **Avoidant**: space, independent, distance, uncomfortable with, pull away, avoid
  - **Disorganized**: confusing, mixed signals, push and pull, fear and want, chaotic

**Calculation:**
1. Count attachment-related keywords across all styles
2. Highest count indicates likely attachment style
3. Relationships are also assessed for attachment dynamics

**Limitations:**
- Attachment styles are best assessed through behavior, not just language
- Text conversations may not reveal vulnerability
- Secure attachment can appear neutral/invisible in text

---

## 5. Emotion Analysis

**Framework:** Basic emotions (Joy, Sadness, Anger, Fear, Love, Gratitude)

**Methodology:**
- Sentiment keyword matching
- Emotion keywords:
  - **Joy**: happy, excited, love, joy, wonderful, amazing, great
  - **Sadness**: sad, depressed, down, hurt, pain, cry, miss, lonely
  - **Anger**: angry, mad, furious, annoyed, frustrated, pissed
  - **Love**: love, adore, cherish, care, affection, heart, romance

**Calculation:**
1. Count emotional keywords across all messages
2. Calculate percentage for each emotion
3. Dominant emotion = highest percentage
4. Emotional diversity = number of emotions present above 10%

**Limitations:**
- Emoji and punctuation not yet analyzed
- Doesn't capture emotional intensity (e.g., "happy" vs "ecstatic")
- Cultural differences in emotional expression

---

## 6. Relationship Dynamics

### 6.1 Message Balance
**Calculation:**
- Ratio = `your_messages / their_messages`
- Balanced relationship: 0.7 ≤ ratio ≤ 1.3
- Imbalanced: ratio > 2 or < 0.5

### 6.2 Conversation Initiation
**Methodology:**
- Identifies conversation boundaries (gaps > 6 hours)
- First message after gap = conversation initiator
- Tracks who initiates more frequently

**Calculation:**
- Initiation rate = `your_initiations / total_conversations`

### 6.3 Responsiveness
**Methodology:**
- Quick response = reply within 10 minutes
- Counts rapid back-and-forth exchanges

**Calculation:**
- Quick response count for each person
- Response balance = `min(your_quick, their_quick) / max(your_quick, their_quick)`

---

## 7. Relationship Scoring

### 7.1 Closeness Score (0-100)

**Components:**
- **Message Balance** (20 points): Closer to 50/50 = higher score
  - Formula: `(1 - abs(1 - ratio)) * 20` where ratio is normalized to ≤1.0
- **Mutual Responsiveness** (15 points): Both respond quickly
  - Formula: `(min_responses / max_responses) * 15`
- **Secure Attachment** (30 points): 15 per person if secure
- **Positive Emotions** (20 points): 10 per person if dominant emotion is Joy
- **Message Volume** (15 points): More messages indicates closeness
  - Formula: `min(message_count / 100, 15)`

**Interpretation:**
- 80-100: Very close relationship
- 60-79: Close relationship
- 40-59: Moderate connection
- 20-39: Distant relationship
- 0-19: Minimal connection

### 7.2 Toxicity Score (0-100)

**Components:**
- **Negative Emotions** (50 points): 25 per person if dominant emotion is Anger/Sadness/Fear
- **Insecure Attachment** (30 points): 15 per person if Anxious/Avoidant/Disorganized
- **Severe Imbalance** (10 points): If ratio > 2 or < 0.5
- **Response Imbalance** (10 points): One person much less responsive
  - Formula: `(abs(your_resp - their_resp) / total_resp) * 10`

**Interpretation:**
- 0-20: Healthy relationship
- 21-40: Some concerns
- 41-60: Moderately toxic
- 61-80: Very toxic
- 81-100: Extremely toxic

### 7.3 Reliability Score (0-100)

**Components (all based on "them"):**
- **Responsiveness** (30 points): Their quick response count / 10
- **Secure Attachment** (25 points): Full points if secure
- **Supportive Archetype** (20 points): Caregiver, Sage, Hero, or Ruler
- **Balanced Participation** (15 points): Ratio between 0.7-1.3
- **Reliable Enneagram** (10 points): Type 1, 2, or 6

**Interpretation:**
- 80-100: Highly reliable
- 60-79: Generally reliable
- 40-59: Moderately reliable
- 20-39: Somewhat unreliable
- 0-19: Unreliable

---

## 8. Timeline Analysis

### 8.1 Message Activity Timeline
- Groups messages by day
- Visualizes communication frequency over time
- Identifies patterns: consistent, sporadic, declining, increasing

### 8.2 Sentiment Timeline
- Groups messages by month
- Calculates monthly emotional percentages
- Tracks emotional arc of relationship over time
- Keywords matched per month, converted to percentages

---

## Validation & Limitations

### Strengths:
- Large sample size (analyzes entire message history)
- Quantitative and reproducible
- Identifies patterns humans might miss
- Based on established psychological frameworks

### Limitations:
- **Context-free**: Doesn't understand sarcasm, jokes, or situational context
- **Language-dependent**: Optimized for English, limited emoji/multimedia analysis
- **Keyword-based**: Simple matching, not true NLP/sentiment analysis
- **Cultural bias**: Keywords reflect Western psychological frameworks
- **Self-report bias**: People may communicate differently than they actually feel
- **Temporal limitations**: Relationship dynamics change; analysis is snapshot of text history
- **Platform effects**: Texting behavior differs from in-person communication

### Best Practices:
- Use as conversation starter, not clinical diagnosis
- Combine with subjective self-reflection
- Consider analysis across multiple relationships for patterns
- Update periodically as relationships evolve

---

## Technical Implementation

**Language:** Python 3
**Libraries:**
- `json` - data handling
- `collections.Counter` - keyword frequency
- `Chart.js` - visualization
- `D3.js` - network graphs

**Performance:**
- Average analysis time: ~0.5 seconds per 1,000 messages
- Scalable to 100,000+ message conversations

**Data Privacy:**
- All analysis runs locally
- No data sent to external servers
- Export functions for personal backup
