# finsim - Personal Financial Simulator

## Project Overview

Finsim is a configurable simulation which can help individuals or groups of people estimate how long it will take them to reach a given Savings target. Simulation data is provided via a `data.json` file in the project's root directory, allowing the simulation to be executed with just a couple of lines of code. The simulation will initially and periodically prompt the user to enter a "financial strategy" for each person included in the simulation, to allow fine-grained control over monthly savings deposits and debt repayments.

## The Data File

Coming soon ...

## The UI

Coming soon ...

---

## Usage

### Setup

Setting up `finsim` is extremely simple.

1. Clone this repository.
2. Ensure `python3` (>=3.6), `venv` and `pip`/`pip3` are installed.

3. Create and activate a virtual environment:

    `python3 -m venv venv`

    `source venv/bin/activate`

4. Install dependencies:

    `pip install -r requirements-dev.txt`


### Execution

To run the simulation simply navigate to the project's root directory and run:

    `python3 main.py`

### Testing

This project uses `pytest` and `pytest-cov` for unit testing. These packages will already be installed if the **setup** section has been followed.

#### Unit Tests

To run the full suite of unit tests with coverage reporting, navigate to the project's root directory and run:

​	`python3 -m pytest --cov-report term-missing --cov=finsim tests`