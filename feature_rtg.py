import time

from rtg.ga.main_ga import genetic_algorithm

if __name__ == "__main__":
    start = time.time()
    print("Starting generating programs!")
    genetic_algorithm()
    end = time.time()
    print(f"Finished in {end - start:.2f} seconds.")
