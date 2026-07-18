# Graduation Thesis - Random Test Generator RV32IMV

## Introduction 
This is my graduation thesis repository. Feel free to explore, use, or fork it for your own research.

## Installation
1. **Install [pyenv](https://github.com/pyenv/pyenv)**

- After a successful installation, install Python 3.14.3t: `pyenv install 3.14.3t`.

2. **Install [riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain)**
- Install the 32-bit version. 
- Verify the installation: `riscv32-linux-gcc --version`.

3. **Install [spike](https://github.com/riscv-software-src/riscv-isa-sim)**
- Verify the installation: `spike --help`. 

4. **Clone this repository**
- `git clone <repository-url>`. 

5. Prepare the execution environment
```shell
pyenv local 3.14.3t
python -m venv .venv
source .venv/bin/active
pip install -r requirements.txt
```

## User Guide
Execute the following commands in order to generate and analyze test cases:

| Command                              | Description                                |
| ------------------------------------ | ------------------------------------------ |
| `python feature_rtg.py`              | Generate test cases                        |
| `python feature_bare_metal.py`       | Add bare-metal mode instructions for Spike |
| `python feature_compile_execute.py`  | Compile and execute tests using Spike      |
| `python feature_analyze.py`          | Analyze test coverage                      |
| `streamlit run feature_visualize.py` | Visualize results and metrics              |
