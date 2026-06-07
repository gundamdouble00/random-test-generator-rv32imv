import time

from coverage_analyzer.analyzer import coverage

if __name__ == "__main__":
    start = time.time()
    print("Starting analyzing!")
    coverage.main()
    end = time.time()
    print(f"Finished in {end - start:.2f} seconds.")
