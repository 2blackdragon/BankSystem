import random

# Master switches
ENABLE_CHAOS = True

ENABLE_LATENCY = True
ENABLE_FAILURES = True
ENABLE_CPU_STRESS = False
ENABLE_MEMORY_STRESS = False

# Probabilities
LATENCY_PROBABILITY = 0.15
FAILURE_PROBABILITY = 0.1
CPU_STRESS_PROBABILITY = 0.05
MEMORY_STRESS_PROBABILITY = 0.02

# Latency params
MIN_LATENCY = 0.3
MAX_LATENCY = 2.0


def random_event(probability: float) -> bool:
    return ENABLE_CHAOS and random.random() < probability
