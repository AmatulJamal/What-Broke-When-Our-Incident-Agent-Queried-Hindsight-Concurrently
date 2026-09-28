import asyncio
from benchmark import run_benchmark

if __name__ == "__main__":
    result = asyncio.run(run_benchmark())
    print("\nIncident Agent Benchmark")
    print("-----------------------")
    for key, value in result.items():
        print(f"{key}: {value}")
