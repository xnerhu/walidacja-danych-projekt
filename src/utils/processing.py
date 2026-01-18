import os


def get_worker_cpu() -> int:
    return max(1, (os.cpu_count() or 2) - 1)
