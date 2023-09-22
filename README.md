# Soft Body Simulation

#### This experimental simulation program developed by Ajaya Ramachandran shows a soft body simulation of a falling object. It is an example of a mass-spring type simulation of a soft body, and features complex interparticle interactions, simple rigid interactions with a complex editable environment, and many painful hours and sleepless nights of work.


## Step 1: The Origin - Elastics
I first stumbled upon elastic code many years ago, and have used it in many unrelated ways since. However, I had never used the code to create an accurate simulation of physics, until now. Luckily, the dynamics of an elastic object are easy to understand, as they are simply based on just two factors: the distance (between two objects or between an object and a fixed point), and the force of gravity. Gravity is a constant accelerating force, meaning it is easy to implement into the motion of an object. Converting the distance between two objects into the elastic force between them, is slightly more involved.

Due to what is knows as Hooke's law, the force of elasticity present between two objects is directly proportional to the amount it is stretched from its resting state. (https://en.wikipedia.org/wiki/Hooke%27s_law)

**In code, this is easy to implement. Let's use some pseudo-variables.**

`elasticCoefficient = (distance - restingDistance) * (1 / elasticity)`

At first glance, this seems complicated, but breaking it down it is simple. The `(distance - restingDistance)` is simply a linear function that returns `0` when the `distance` is equal to the `restingDistance`. This means that when the object is in a free state (no gravity), any position other than a position where the object is at the `restingDistance` will return some value for the `elasticCoefficient` that will drive the motion of the object to a place where it will be closer to the resting state, and make the `elasticCoefficient` approach `0`. This is an exmaple of a negative feedback loop.

The `(1 / elasticity)` is a useful tool as it allows you to have full control over how "snappy" the elastic is. A lower elasticity will cause the object to very quickly and rigidly return to its resting state, whereas a higher elasticity will cause the object to slowly wobble around toward that state.

The `elasticCoefficient`, which is just a value that represents the strength of the elastic force, now needs to be converted into a vector, so that it may be added to the gravity vector, and create the final motion vector of the point. This is relatively simple:

**To achieve an "elastic vector", we need two things - the strength of the force (already known to be the `elasticCoefficient`), and the direction of the force, which can be calculated by taking the `atan2` of the differences the point's `x` and `y` coordinates and those of the point it is connected to. Multiplying the `sin` of the `direction` by the `elasticCoefficient` gets us the `y` component, and multiplying the `cos` of the `direction` by the `elasticCoefficient` gets us the `x` component. (This last step is, in mathematical lingo, converting a polar vector into a rectangular vector.)**

## Step 2: Getting More Complex - More than Two Objects
The elastic demonstration is cool, but gets boring pretty quick. I wanted to use the elastic physics to simulate something greater, a structure similar to jell-o or sponge, both of which exhibit properties of what is known as a "soft body". Soft bodies come in two flavors, namely plastic and elastic soft bodies, the key difference between the two being that plastic soft bodies deform irreversibly when influenced, while elastic soft bodies return to their original shape. We can simulate the latter using an expansion on my elastic code.

In order to create the simulation, `100` points are created in a square lattice structure, and a very simple edge table is constructed based on distance (at the start of the program) in order to generate the elastic connections between the points. The distance between adjacent points in the lattice is `10`, so if the threshold distance for elastic-connector generation is greater than `10 * sqrt(2)`, then not only do rigid squares form, but so do cross-beams that greatly improve the structural integrity of the simulation.

**Mathematically, this can be proven because the diagonals of a square have `sqrt(2)` times the length of the sides. Therefore, if the side lengths are `10`, then the diagonals have a length of `sqrt(2) * 10`, which is approximately `14.14`, and thus a threshold distance of `15` would cover straights and diagonals.**

A slight nuance to keep note of here is that the `restingDistance` of the diagonal connections is different from the `restingDistance` of the perpendicular connections. If they were the same, the edges and diagonals would want to be the same length, and would cause immense stress on the entire object. Rather, the `restingDistance` of a connection is calculated from the initial distance in the generated lattice, so the natural tendency of the system is to return to the initial lattice shape, and tension/stress is greatly reduced.

Without those supporting diagonal bands, however, the simulation is susceptible to high instability. Regardless, the interaction between particles is interesting to look into.

Every particle is influenced by a few factors: its current velocity, the positions of its neighbors, and gravity. These forces (written in the form of mathematical `vectors` and notated in the code as `tuples`) are used to perform the "elastic vector" calculation from above. However, this process only gets us the "elastic vector" of one connection to the point in question, but many if not all the points have several connected friends. To find the "ultimate elastic vector", we can just do the same calculation for all the connections and add them together as vectors. Finally, we add the "ultimate elastic vector" to the `gravity` vector to get the final motion vector of the point - however, I realized soon that this creates a system that never loses energy. That means the jello-like waves and oscillations never calm down and reach a steady state like they do in real life. To fix this, I multiply the motion vector by a `damping` coefficient (around 0.99) that allows the system to converge to a steady state. Another nuance here is that the "ultimate elastic vector" is not added directly to the `gravity` vector - instead, it is multiplied by an `elasticStrength` (around 0.5) that dictates how much of the energy of a particle is influenced by the elastic forces (relative to all other forces).

After the next frame's position is calculated for all particles, the data of frames is simply cascaded, and the current frame is updated. A drawer (which uses the Pygame library) blits to screen white dots for all the particles and gray lines for the connecting lines. For experimentation purposes, I tried to map how stress is dissipated through the object by coloring the connecting lines according to their `elasticCoefficient`s. This is not enabled by default, but can be toggled within the code.

## Step 3: The Simulation Gets Unstable (and so do I) - Adding Complex Environments
The final stage is allowing this simulation to interact with its environment. From the beginning, I designed the environment to be modular and easily configurable - it is a set of lines in a `lineLibrary`, stored in the simplest form: a pair of points. Each point loops through every line (with optimizations such as Bounding Boxes) to figure out what rigid transformations need to be applied.

Since the environment is made of lines and has no internal volume, intersections must be calculated temporally, by checking which particles have crossed a line in between the current and last frame (using vector math, refer to function `side`). This temporal collision detection lends itself to subtle issues, such as the fact that a particle has to pass the membrane one frame, be corrected the next, and so on. Because passage and correction occur on alternating frames, an odd resonant pattern emerged, which at high refresh rates resembled two "ghosts" of the same simulation. It was clear that naive temporal collision detection was not enough.

Instead, the simulation "simulates" the next frame before actually rendering it, in order to see if a collision will happen. If so, the exact intersection of the particle and the surface is calculated by treating this frame's position and next frame's position as endpoints of a line segment, and using some more fun vector math (refer to function `getIntersectionPoint`) to calculate the intersection of that pseudo-line-segment with the surface line. The object is moved to that location. `position` has been taken care of.

With `velocity`, things get a bit more difficult. We need to preserve `momentum`, which means that the particle needs to be propelled tangent to the direction of the surface, with a magnitude that inherits whatever `velocity` the particle has before. I've referenced a few papers on this (https://en.wikipedia.org/wiki/Sliding_%28motion%29), but I'm not quite there. This is where both the simulation and yours truly became very unstable, and I will definitely update this README when I re-understand high-school level trigonometry. But for now, the simulation is kind of broken, and I know this because I don't think gravity in real life pulls you more to the right than left. But maybe that's just me. Anyway, I'll see you later then.

## Applications
---
