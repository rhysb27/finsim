# finsim - Personal Financial Simulator

[![CircleCI](https://circleci.com/gh/rhysb27/finsim/tree/master.svg?style=shield)](https://circleci.com/gh/rhysb27/finsim/tree/master)
[![codecov](https://codecov.io/gh/rhysb27/finsim/branch/master/graph/badge.svg)](https://codecov.io/gh/rhysb27/finsim)

## Project Overview

Finsim is a configurable simulation which can help individuals or groups of people estimate how long it will take them to reach a given Savings target. Simulation data is provided via a `data.json` file in the project's root directory, allowing the simulation to be executed with just a couple of lines of code. The simulation will initially and periodically prompt the user to enter a "financial strategy" for each person included in the simulation, to allow fine-grained control over monthly savings deposits and debt repayments.

## The Data File

The simulation relies on a JSON file to be supplied, which declares all data to be used by the program. It includes salaries, expenses, debts, saving accounts etc. Read the "[Building Your Data File](https://github.com/rhysb27/finsim/blob/master/building-your-data-file.md)" guide for full details on how to prepare your file.

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