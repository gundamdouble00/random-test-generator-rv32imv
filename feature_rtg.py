import time

from rtg.ga.main_ga import genetic_algorithm


def main():
    start = time.time()
    print("Starting generating programs!")
    genetic_algorithm()
    end = time.time()
    print(f"Finished in {end - start:.2f} seconds.")


if __name__ == "__main__":
    main()
