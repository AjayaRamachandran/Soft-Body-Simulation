<p align="center">
  <img alt="Nodes" src="https://i.ibb.co/5cB2TZK/mesh2.png" width="140px" />
  <h1 align="center">Soft Body Simulation</h1>
</p>

**This experimental simulation program demonstrates a mass-spring simulation of a soft-body. The project has been under on-off development for over a year, with the first iteration successfully modeling the dynamics of a soft-body in a simple enviroment, while the second takes aspects of the first but goes further with the use of grouped simulation steps, Verlet integration, and high stiffness to mimic something far closer to a rigid body. This second program has potential use in engineering simulation, game physics, and much more.**

## Program 1: A General-Purpose Physically Semi-Accurate Exploration of Soft-Body Dynamics (Jelly Simulation)
#### Originally constructed in late 2023; no longer in development
This program can be located in `main.py`. Apart from visual examination, this program is not physically accurate thus I do not recommend using it. It will not be updated. For an updated model that is physically accurate, see `new.py` (more info below).

## Program 2: A General-Purpose Physics-Based Simulation of Soft- and Rigid-Body Dynamics (Bridge Simulation)
#### Constructed in mid-2024; in active development
This program can accurately demonstrate the dynamics of mass-springs in a variety of different structures, and will continue to be updated as more features get added to it. Currently it is written in Python and uses the Pygame library to render to the screen, but for higher simulation fidelity and more complex simulations this is not fast enough. A C++ rewrite could happen sometime in the future.

### Benefits of Verlet Integration
| Method of Integration | Simulation Steps / Frame (Soft) | Simulation Steps / Frame (Rigid) |
|-----------------------|---------------------------------|----------------------------------|
| Euler                 | >150                            | >3600                            |
| Verlet                | >40                             | >500                             |