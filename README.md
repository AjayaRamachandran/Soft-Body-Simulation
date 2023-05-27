# Soft Body Simulation

#### This experimental simulation program developed by Ajaya Ramachandran shows a soft body simulation of a falling object. I want to add more things to this project, and will update the Readme when this is done. As of now, there is still a lot to explore in this project, so let's do that.


## The Origin: Elastics
I first stumbled upon elastic code many years ago, and have used it in many unrelated ways since. However, I had never used the code to create an accurate simulation of physics, until now. Luckily, the dynamics of an elastic object are easy to understand, as they are simply based on just two factors: the distance (between two objects or between an object and a fixed point), and the force of gravity. Gravity is a constant accelerating force, meaning it is easy to implement into the motion of an object. Converting the distance between two objects into the elastic force between them, I initially thought was much harder. Turns out it's super simple.

Due to what is knows as Hooke's law, the force of elasticity present between two objects is directly proportional to the amount it is stretched from its resting state. (https://en.wikipedia.org/wiki/Hooke%27s_law)

#### In code, this is easy to implement. Let's use some pseudo-variables.

`elasticCoefficient = (distance - restingDistance) * (1 / elasticity)`

At first glance, this seems complicated, but breaking it down it is simple. The `(distance - restingDistance)` is simply a linear function that returns `0` when the `distance` is equal to the `restingDistance`. This means that when the object is in a free state (no gravity), any position other than a position where the object is at the `restingDistance` will return some value for the `elasticCoefficient` that will drive the motion of the object to a place where it will be closer to the resting state, and make the `elasticCoefficient` approach `0`. This is called a negative feedback loop.

That last `(1 / elasticity)` which could also be written as dividing by `elasticity` is a useful tool as it allows you to have full control over how "snappy" the elastic is. A lower elasticity will cause the object to very quickly and rigidly return to its resting state, whereas a higher elasticity will cause the object to slowly wobble around toward that state.

The `elasticCoefficient`, which is just a value that represents the strength of the elastic force, now needs to be converted into a vector, so that it may be added to the gravity vector, and create the final motion vector of the point. This is relatively simple:

#### To achieve an "elastic vector", we need two things - the strength of the force (already known to be the `elasticCoefficient`), and the direction of the force, which can be calculated by taking the `atan2` of the differences the point's `x` and `y` coordinates and those of the point it is connected to. Multiplying the `sin` of the direction by the `elasticCoefficient` gets us the `y` vector, and multiplying the `cos` by the `elasticCoefficient` gets us the `x` vector.

## Getting More Complex: More than Two Objects
The elastic demonstration was cool, but got boring pretty quick. I wanted to use the elastic physics to simulate something greater, like perhaps cloth, (which i did get pretty close to doing), but playing around I was able to achieve a structure similar to a sponge or steel wool, both of which exhibit properties of what is known as a "soft body". Soft bodies come in two flavors, namely plastic and elastic soft bodies, the key difference between the two being that plastic soft bodies deform irreversibly when influenced, while elastic soft bodies return to their original shape. I figured I could somehow simulate the latter using a variation of my elastic code (and I was right, fortunately!).

In order for the simulation work, `100` such points (particles, points, nodes, whatever you want to call them) are created in a square lattice structure, and a very simple edge table is constructed based on distance, at the start of the code, in order to generate the elastic connections between the points. The distance between adjacent points in the lattice is `10`, so if the threshold distance for elastic-connector generation is greater than `10 * sqrt(2)`, then not only do rigid squares form, but so do cross-beams that greatly improve the structural integrity of the simulation.

#### Mathematically, this can be proven because the diagonals of a square have `sqrt(2)` times the length of the sides. Therefore, if the side lengths are `10`, then the diagonals have a length of `sqrt(2) * 10`, which is approximately `14.14`, and thus a threshold distance of `15` would capture those as well.

A slight nuance to keep note of here is that the `restingDistance` of the diagonal connections is different from the `restingDistance` of the perpendicular connections. If they were the same, the edges and diagonals would want to be the same length, and would cause immense stress on the entire object. Rather, the `restingDistance` of a connection is calculated from the initial distance in the generated lattice, so the natural tendency of the system is to return to the initial pure lattice shape, and tension/stress is greatly reduced.

Without those supporting diagonal bands, however, the simulation is susceptible to high instability - an issue I want to fix soon, but haven't gotten to yet. Regardless, the interactions between particles is interesting to look into.

Every particle is influenced by a few factors: its current velocity, the positions of its neighbors, and gravity. These forces (written in the form of mathematical `vectors` and notated in the code as `tuples`) are used to perform the "elastic vector" calculation from above. However, this process only gets us the "elastic vector" of one connection to the point in question, but many if not all the points have several connected friends. To find the "ultimate elastic vector", can just do the same calculation for all the connections and add them together as vectors. Finally, we add the "ultimate elastic vector" to the `gravity` vector to get the final motion vector of the point - however, I realized soon that this creates a system that never loses energy. That means the jello-like waves and oscillations never calm down and reach a steady state like they do in real life. To fix this, I multiply the motion vector by a `dampening` coefficient (around 0.98) that allows the system to converge to a steady state.

After the next frame's position is calculated for all particles, the data of frames is simply cascaded, and the current frame is updated. A drawer (which uses the Pygame library) blits to screen white dots for all the particles and gray lines for the connecting lines. For experimentation purposes, I tried to map how stress is dissipated through the object by coloring the connecting lines according to their `elasticCoefficient`s. This was cool - I'm not keeping it in, but there's a commented-out line of code in there if you want to see what that looks like.

My next step planned is to add complex environments (composed of line segments) that the soft body simulation can interact with realistically, because right now it can only deal with a flat floor (and that's kind of boring!). I will most likely update the readme when this is completed.

## Applications
I might plan on using this in a game? We'll see.