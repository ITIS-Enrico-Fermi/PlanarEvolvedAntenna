# Path Evolved Antenna
2-dimensional patch antenna optimized with genetic algorithms.

## Objectives
The main goal of this project is simulating the evolution of a patch antenna subject to space and shape constraints, in order to maximize isotropic gain and minimize backlobes propagation. The simulation is carried out through a genetic algorithm framed as described in the following paragraphs.

## Problem representation

### Encoding
A planar antenna can be represented as a path with both cartesian and polar coordinates. The latter is our case. Each segment of the polygonal chain is a polar coordinate (angle, distance) whose origin is the end-point of the previous segment. 

### Constraints
Trhoughout the simulation (at any given time of it), every path must be contained inside a circle of diameter _outer\_diameter_ - specified in _config.yaml_ file - and must avoid an inner circle of diameter _inner\_diameter_, namely the hole for the onboard camera.

### Fitness (objective function)

### Crossover and mutation
A single cut-point crossover is done a the moment. Crossover recombines genes from the previous generation to reach _population\_size_ individuals.

Mutation is a draw without replacement of _mutation\_rate_ * _population\_size_ individuals to which a random mutation (for both angles and lengths) is applied.

## Usage
Dependencies installation:
```bash
python3 -m pip install -r requirements.txt
```

Proof-of-concept:
```bash
cd src
python3 poc.py [-p]
```

Where `-p` is the short option for `--plot`.

## Credits
 - Enlightening _Advanced antenna design for a NASA satellite mission_ paper ([https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=1426&context=smallsat](https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=1426&context=smallsat))
 - _Learning and evolution of artificial systems_ lectures (UniMoRe)