# MeMOC project
Lab exercises for the MeMOC course (Methods and Models for Combinatorial Optimization).

The goal was to implement the classic algorithmic problem Travel Salesman Problem (TSP) with two different approaches in order to compare them later.
The project is therefore composed of two sections:
* Implement the TSP problem using CPLEX APIs and find the maximum dimension size solvable within a certain time frame (1s, 10s, etc.)
* desing and develop ad-hoc optimization algorithm using a meta-heuristic, Genetic Algorithm (GA).

## Getting Started
### Prerequisites
LaTeX, Python, g++, CPLEX

### Compile
First run a terminal and move into the folder that contains the code:
```
cd code/
```
Then compile:
```
make
```
Generate the instances:
```
make gen-instances
```

### Run
Run main program on a sample instance by typing:
```
bin/main "samples/dcc1911_n025.tsp"
```
If you want to run over all instances:
```
make run-cplex
make run-ga
```

## License
The source code is distributed under GNU GPL-3.0-only License.  
Other material (including but not limited to pdf documents, figures, etc) is licensed under CC BY-NC-ND 4.0.  

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)