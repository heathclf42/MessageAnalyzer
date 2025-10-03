# LLM Performance Monitoring System

Comprehensive performance tracking and dashboarding for all LLM operations in MessageAnalyzer.

## Features

- **Real-time Performance Tracking**
  - CPU usage per operation
  - Memory consumption (MB)
  - Processing duration (seconds)
  - Throughput (characters/second)
  - Operations per minute

- **Interactive Dashboard**
  - Visual charts comparing model performance
  - Timeline view of operations
  - Detailed metrics table
  - Summary statistics

- **Automatic Logging**
  - All metrics saved to JSON
  - Historical tracking
  - Easy data export

## Quick Start

### Run Test Script with Monitoring

```bash
source venv/bin/activate
python test_llm_models.py
```

This will:
1. Download and test all specialized models
2. Track performance metrics for each operation
3. Generate an interactive HTML dashboard
4. Save detailed metrics to JSON

### View the Dashboard

The test script outputs a direct link to open the dashboard:
```
file:///path/to/MessageAnalyzer/data/output/llm_metrics/metrics_TIMESTAMP_dashboard.html
```

Simply click or copy the link to your browser.

## Using the Monitor in Your Code

### Basic Usage

```python
from src.llm_monitor import LLMMonitor

# Initialize monitor
monitor = LLMMonitor()

# Track an operation
with monitor.track_operation('model-name', 'inference', len(text)):
    result = model(text)

# Print summary
monitor.print_summary()

# Save metrics
metrics_file = monitor.save_metrics()
```

### Advanced Usage

```python
from src.llm_monitor import LLMMonitor, ModelBenchmark

monitor = LLMMonitor()

# Benchmark a model with warmup
benchmark = ModelBenchmark(monitor)
results = benchmark.benchmark_model(
    model_name='qwen2.5:7b',
    model_callable=lambda text: ollama.generate(model='qwen2.5:7b', prompt=text),
    test_texts=my_test_texts,
    warmup_runs=3
)

# Get comparison across models
comparison = monitor.get_model_comparison()
for model, stats in comparison.items():
    print(f"{model}: {stats['avg_duration_seconds']:.3f}s avg")
```

### Generate Dashboard from Existing Metrics

```python
from src.create_llm_dashboard import create_llm_performance_dashboard
from pathlib import Path

metrics_file = Path('data/output/llm_metrics/metrics_20250102_143022.json')
dashboard_file = create_llm_performance_dashboard(metrics_file)
print(f"Dashboard: {dashboard_file}")
```

## Dashboard Metrics Explained

### Charts

1. **Average Duration by Model**
   - How long each model takes on average
   - Lower is better

2. **Peak Memory Usage by Model**
   - Maximum memory consumed
   - Important for understanding resource requirements

3. **Average CPU Usage by Model**
   - CPU utilization percentage
   - Higher means more intensive processing

4. **Throughput by Model**
   - Characters processed per second
   - Higher is better for batch processing

5. **Performance Over Time**
   - Line chart showing duration across operations
   - Useful for spotting warm-up effects or degradation

### Summary Statistics

Each model shows:
- **Operations**: Total number of inferences tracked
- **Avg Duration**: Mean processing time
- **Avg Memory**: Mean memory usage
- **Peak Memory**: Maximum memory used
- **Avg CPU**: Mean CPU utilization
- **Peak CPU**: Maximum CPU used
- **Throughput**: Characters processed per second
- **Ops/Minute**: How many operations per minute

## Tracked Metrics

For each operation, the monitor captures:

```json
{
  "timestamp": "2025-01-02T14:30:22.123456",
  "model_name": "holistic-ai/personality_classifier",
  "operation": "inference",
  "text_length": 75,
  "duration_seconds": 0.245,
  "throughput_chars_per_sec": 306.12,
  "cpu_delta_percent": 12.5,
  "memory_delta_mb": 15.3,
  "peak_memory_mb": 1234.5,
  "peak_cpu_percent": 45.2,
  "system_cpu_percent": 25.1,
  "system_memory_percent": 62.3,
  "gpu_available": false
}
```

## Integration with MessageAnalyzer

### Adding Monitoring to Analysis Pipeline

```python
from src.llm_monitor import get_monitor

# Get global monitor instance
monitor = get_monitor()

def analyze_conversation_with_monitoring(messages):
    """Analyze conversation with performance tracking."""

    # Track personality analysis
    with monitor.track_operation('personality-model', 'analysis', len(messages)):
        personality = analyze_personality(messages)

    # Track sentiment analysis
    with monitor.track_operation('sentiment-model', 'analysis', len(messages)):
        sentiment = analyze_sentiment(messages)

    return {
        'personality': personality,
        'sentiment': sentiment
    }

# After processing all conversations
monitor.save_metrics('conversation_analysis_metrics.json')
```

### Viewing Historical Metrics

All metrics are saved to `data/output/llm_metrics/` with timestamps. You can:

1. **Compare runs**: Load different metric files to compare performance over time
2. **Track improvements**: See if optimizations reduce processing time
3. **Resource planning**: Understand memory/CPU needs for scaling

## Performance Optimization Tips

Based on dashboard metrics:

### If Memory is High
- Use lower quantization (Q4 instead of Q8)
- Process texts in smaller batches
- Clear model cache between operations

### If CPU is High
- Reduce batch size
- Use GPU/Metal acceleration if available
- Consider simpler models for preliminary filtering

### If Duration is High
- Enable GPU acceleration (`device="mps"` for Mac)
- Use batch processing
- Optimize text preprocessing
- Consider model quantization

### If Throughput is Low
- Increase batch size (if memory allows)
- Enable parallel processing
- Use faster quantization formats

## Files and Directories

```
MessageAnalyzer/
├── src/
│   ├── llm_monitor.py              # Core monitoring module
│   └── create_llm_dashboard.py     # Dashboard generator
├── data/output/llm_metrics/
│   ├── metrics_TIMESTAMP.json      # Raw metrics data
│   └── metrics_TIMESTAMP_dashboard.html  # Interactive dashboard
├── test_llm_models.py              # Test script with monitoring
└── docs/guides/
    └── LLM_MONITORING.md           # This file
```

## Troubleshooting

### "Module not found: llm_monitor"
Ensure you're running from the project root and using the venv:
```bash
cd /path/to/MessageAnalyzer
source venv/bin/activate
python test_llm_models.py
```

### Dashboard won't open
The path must start with `file://` and be absolute:
```
file:///Users/your-name/Documents/Python/Projects/MessageAnalyzer/data/output/llm_metrics/dashboard.html
```

### Missing psutil
Install dependencies:
```bash
source venv/bin/activate
pip install psutil
```

## Future Enhancements

Planned features:
- [ ] Live monitoring during long batch jobs
- [ ] Alerting for memory/CPU thresholds
- [ ] Comparison view between multiple runs
- [ ] Export to CSV for external analysis
- [ ] GPU metrics for Apple Silicon (requires sudo)
- [ ] Network I/O tracking for remote models
