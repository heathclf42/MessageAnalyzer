# Stage 2: Daily Metrics with Citations

## New Approach: Per-Day Analysis

Instead of conversation-level summaries, output **daily metrics** with citations. This allows charts to show WHY patterns exist.

---

## System Prompt

```
You are a relationship dynamics analyst specializing in text message conversation analysis.

Your task is to analyze conversations DAY BY DAY and provide metrics with evidence for each day.

CRITICAL RULES:
1. Analyze each day individually
2. Every metric MUST have supporting citations from that day
3. Citation format: [DATE TIME | SENDER: "exact message text"]
4. Output structured data that can be mapped to charts
5. State "No data" for days with insufficient evidence

Your analysis will be used to create interactive visualizations with citation tooltips.
```

---

## Analysis Prompt Template

```
Analyze the following text message conversation DAY BY DAY.

CONVERSATION DETAILS:
- Person A (YOU): Messages where sender = "YOU"
- Person B ({phone_number}): Messages where sender = "{phone_number}"
- Total messages: {message_count}
- Date range: {date_range}

MESSAGES:
{formatted_messages}

---

TASK: Analyze EACH DAY individually and output the following metrics:

For EACH DAY in the conversation, provide:

## DAY: [DATE]

### Message Activity
- Total messages: [number]
- YOU messages: [number]
- THEM messages: [number]
- Key citations:
  * [TIME | SENDER: "message"] → [context]
  * [TIME | SENDER: "message"] → [context]

### Sentiment Scores (0-100)
- Positive: [score] / 100
- Neutral: [score] / 100
- Negative: [score] / 100
- Overall tone: [positive/neutral/negative/mixed]
- Key citations:
  * [TIME | SENDER: "message"] → [why this is positive/negative/neutral]
  * [TIME | SENDER: "message"] → [why this matters]

### Topics Discussed
- Primary topic: [topic name]
- Secondary topics: [topic1, topic2, ...]
- Key citations:
  * [TIME | SENDER: "message"] → [topic: explanation]
  * [TIME | SENDER: "message"] → [topic: explanation]

### Emotional Indicators
- Support given: YES/NO
- Conflict present: YES/NO
- Humor/playfulness: YES/NO
- If YES to any, provide citations:
  * [TIME | SENDER: "message"] → [what this shows]

### Response Patterns
- Average response time: [X minutes]
- Notable exchanges:
  * [TIME | SENDER: "message"] → [TIME | SENDER: "response"] (response time: X)

---

## OUTPUT FORMAT

Structure your response as:

```
=== 2018-12-21 ===

ACTIVITY: 7 messages (YOU: 4, THEM: 3)
Citations:
- [2018-12-21 10:37:05 PM | YOU: "Yo"] → Initiated contact
- [2018-12-21 10:37:42 PM | THEM: "Hey dude!"] → Quick response (37 sec)
- [2018-12-21 10:38:08 PM | YOU: ",I'm home for several days. We should hang."] → Proposing meetup

SENTIMENT: Positive 85/100, Neutral 15/100, Negative 0/100
Overall: POSITIVE
Citations:
- [2018-12-21 10:37:42 PM | THEM: "Hey dude!"] → Friendly enthusiastic greeting
- [2018-12-21 10:39:59 PM | THEM: "Awesome. Are you home now?"] → Excitement about meeting up
- [2018-12-21 10:40:47 PM | THEM: "=Cool; no doubt a crazy busy couple days..."] → Acknowledgment with empathy

TOPICS:
Primary: Planning/Logistics (meetup coordination)
Secondary: Personal updates, Social plans
Citations:
- [2018-12-21 10:38:08 PM | YOU: ",I'm home for several days. We should hang."] → Topic: Meetup planning
- [2018-12-21 10:40:47 PM | THEM: "when do you return?"] → Topic: Travel timeline
- [2018-12-21 10:41:02 PM | YOU: "I leave the 26th"] → Topic: Schedule coordination

EMOTIONAL INDICATORS:
- Support: YES (acknowledging busy schedule)
- Conflict: NO
- Humor: NO
Citations:
- [2018-12-21 10:40:47 PM | THEM: "no doubt a crazy busy couple days..."] → Shows understanding/support

RESPONSE PATTERNS:
Average response time: 1.2 minutes
Notable exchanges:
- [10:37:05 PM | YOU] → [10:37:42 PM | THEM] = 37 seconds (very engaged)
- [10:38:08 PM | YOU] → [10:39:59 PM | THEM] = 1m 51s (enthusiastic reply)
- [10:40:47 PM | THEM] → [10:41:02 PM | YOU] = 15 seconds (quick logistics response)

=== 2018-12-24 ===

[Continue for each day...]
```

---

## Benefits of Daily Metrics

1. **Chart Annotations**: Each point on a timeline chart can show specific citations
2. **Interactive Tooltips**: Hover over a spike → see the actual messages
3. **Evidence-Based Patterns**: Every trend has direct message evidence
4. **Granular Analysis**: Track sentiment changes day-by-day, not just overall

---

## Implementation

The daily metrics will be parsed and mapped to:
- **Message Activity Chart**: Daily totals with key message tooltips
- **Emotional Arc Chart**: Daily sentiment scores with citation tooltips
- **Topic Timeline**: Show which topics dominated each day
- **Response Time Chart**: Daily average with notable exchange examples

---

## JSON Output Format (for parsing)

```json
{
  "daily_metrics": [
    {
      "date": "2018-12-21",
      "activity": {
        "total_messages":