#!/usr/bin/env python3
"""
LLM Performance Monitoring System
Tracks CPU, memory, GPU usage, and timing for all LLM model operations.
"""

import time
import psutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import threading

class LLMMonitor:
    """Monitors performance metrics for LLM model operations."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize the monitor.

        Args:
            log_dir: Directory to save performance logs. Defaults to data/output/llm_metrics/
        """
        if log_dir is None:
            log_dir = Path(__file__).parent.parent / "data" / "output" / "llm_metrics"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.metrics: List[Dict[str, Any]] = []
        self.process = psutil.Process()

    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource usage."""
        # CPU usage (percentage)
        cpu_percent = self.process.cpu_percent(interval=0.1)

        # Memory usage
        mem_info = self.process.memory_info()
        memory_mb = mem_info.rss / 1024 / 1024  # Convert to MB
        memory_percent = self.process.memory_percent()

        # System-wide metrics
        system_cpu = psutil.cpu_percent(interval=0.1)
        system_memory = psutil.virtual_memory()

        metrics = {
            'process_cpu_percent': cpu_percent,
            'process_memory_mb': memory_mb,
            'process_memory_percent': memory_percent,
            'system_cpu_percent': system_cpu,
            'system_memory_percent': system_memory.percent,
            'system_memory_available_gb': system_memory.available / 1024 / 1024 / 1024,
        }

        # Try to get GPU metrics if available (Apple Silicon)
        try:
            import subprocess
            result = subprocess.run(
                ['powermetrics', '-n', '1', '-i', '100', '--samplers', 'gpu_power'],
                capture_output=True,
                text=True,
                timeout=2
            )
            # This is a simplified check - powermetrics requires sudo
            # In practice, you'd parse the output or use a library
            metrics['gpu_available'] = True
        except Exception:
            metrics['gpu_available'] = False

        return metrics

    @contextmanager
    def track_operation(
        self,
        model_name: str,
        operation: str,
        text_length: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Context manager to track a single model operation.

        Args:
            model_name: Name of the model (e.g., 'holistic-ai/personality_classifier')
            operation: Type of operation (e.g., 'inference', 'load')
            text_length: Length of input text in characters
            metadata: Additional metadata to log

        Usage:
            with monitor.track_operation('qwen2.5:7b', 'inference', len(text)):
                result = model(text)
        """
        start_time = time.time()
        start_metrics = self._get_system_metrics()

        try:
            yield
        finally:
            end_time = time.time()
            end_metrics = self._get_system_metrics()

            duration = end_time - start_time

            # Calculate deltas
            cpu_delta = end_metrics['process_cpu_percent'] - start_metrics['process_cpu_percent']
            memory_delta = end_metrics['process_memory_mb'] - start_metrics['process_memory_mb']

            metric_entry = {
                'timestamp': datetime.now().isoformat(),
                'model_name': model_name,
                'operation': operation,
                'text_length': text_length,
                'duration_seconds': duration,
                'throughput_chars_per_sec': text_length / duration if duration > 0 else 0,
                'cpu_delta_percent': cpu_delta,
                'memory_delta_mb': memory_delta,
                'peak_memory_mb': end_metrics['process_memory_mb'],
                'peak_cpu_percent': end_metrics['process_cpu_percent'],
                'system_cpu_percent': end_metrics['system_cpu_percent'],
                'system_memory_percent': end_metrics['system_memory_percent'],
                'gpu_available': end_metrics['gpu_available'],
            }

            if metadata:
                metric_entry['metadata'] = metadata

            self.metrics.append(metric_entry)

    def get_summary_stats(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get summary statistics for a model or all models.

        Args:
            model_name: Filter by specific model. If None, returns stats for all models.

        Returns:
            Dictionary with summary statistics
        """
        filtered_metrics = self.metrics
        if model_name:
            filtered_metrics = [m for m in self.metrics if m['model_name'] == model_name]

        if not filtered_metrics:
            return {}

        durations = [m['duration_seconds'] for m in filtered_metrics]
        memory_peaks = [m['peak_memory_mb'] for m in filtered_metrics]
        cpu_peaks = [m['peak_cpu_percent'] for m in filtered_metrics]
        throughputs = [m['throughput_chars_per_sec'] for m in filtered_metrics]

        return {
            'model_name': model_name or 'all',
            'total_operations': len(filtered_metrics),
            'avg_duration_seconds': sum(durations) / len(durations),
            'min_duration_seconds': min(durations),
            'max_duration_seconds': max(durations),
            'avg_memory_mb': sum(memory_peaks) / len(memory_peaks),
            'max_memory_mb': max(memory_peaks),
            'avg_cpu_percent': sum(cpu_peaks) / len(cpu_peaks),
            'max_cpu_percent': max(cpu_peaks),
            'avg_throughput_chars_per_sec': sum(throughputs) / len(throughputs),
            'operations_per_minute': len(filtered_metrics) / (sum(durations) / 60) if sum(durations) > 0 else 0,
        }

    def get_model_comparison(self) -> Dict[str, Dict[str, Any]]:
        """Get comparison statistics across all models."""
        models = set(m['model_name'] for m in self.metrics)
        return {
            model: self.get_summary_stats(model)
            for model in models
        }

    def save_metrics(self, filename: Optional[str] = None):
        """Save all metrics to JSON file.

        Args:
            filename: Output filename. If None, uses timestamp.
        """
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        output_path = self.log_dir / filename

        data = {
            'timestamp': datetime.now().isoformat(),
            'total_operations': len(self.metrics),
            'metrics': self.metrics,
            'summary': self.get_model_comparison(),
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        return output_path

    def print_summary(self):
        """Print a formatted summary of all metrics."""
        comparison = self.get_model_comparison()

        print("\n" + "=" * 80)
        print("LLM PERFORMANCE SUMMARY")
        print("=" * 80)

        for model, stats in comparison.items():
            print(f"\n📊 {model}")
            print(f"   Operations:      {stats['total_operations']}")
            print(f"   Avg Duration:    {stats['avg_duration_seconds']:.3f}s")
            print(f"   Avg Memory:      {stats['avg_memory_mb']:.1f} MB")
            print(f"   Peak Memory:     {stats['max_memory_mb']:.1f} MB")
            print(f"   Avg CPU:         {stats['avg_cpu_percent']:.1f}%")
            print(f"   Peak CPU:        {stats['max_cpu_percent']:.1f}%")
            print(f"   Throughput:      {stats['avg_throughput_chars_per_sec']:.0f} chars/sec")
            print(f"   Ops/Minute:      {stats['operations_per_minute']:.1f}")

        print("\n" + "=" * 80)
        print(f"Total operations tracked: {len(self.metrics)}")
        print("=" * 80 + "\n")


class ModelBenchmark:
    """Benchmark suite for comparing model performance."""

    def __init__(self, monitor: LLMMonitor):
        self.monitor = monitor

    def benchmark_model(
        self,
        model_name: str,
        model_callable,
        test_texts: List[str],
        warmup_runs: int = 2
    ) -> Dict[str, Any]:
        """Benchmark a model with multiple test texts.

        Args:
            model_name: Name of the model
            model_callable: Function that takes text and returns result
            test_texts: List of test texts to process
            warmup_runs: Number of warmup runs before benchmarking

        Returns:
            Benchmark results dictionary
        """
        # Warmup
        print(f"Warming up {model_name}...")
        for _ in range(warmup_runs):
            model_callable(test_texts[0])

        # Benchmark
        print(f"Benchmarking {model_name} on {len(test_texts)} texts...")
        for text in test_texts:
            with self.monitor.track_operation(model_name, 'benchmark', len(text)):
                result = model_callable(text)

        return self.monitor.get_summary_stats(model_name)


# Singleton instance for easy import
_monitor_instance = None

def get_monitor() -> LLMMonitor:
    """Get or create the global monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = LLMMonitor()
    return _monitor_instance
