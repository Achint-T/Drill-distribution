# Drill-distribution
A proof of concept for a number of different approaching to an algorithmn to find the most efficient distribution of drills on ores in a 2d enviroment.

## Breakdown of the problem:
This project was one I started when I faced this problem playing a game called ['Mindustry'](https://mindustrygame.github.io/). Specifically, I wanted to be able to place drills to cover an area of ore in such a way that every drill had a conveyor next to it. The main problem I faced was when it came to large areas (which meant that there were a large number of different possible drills) and when working around walls (which posed added complexity since the drills were no longer acessible from all directions).

My first step was to break down the problem into a number of constraints my algorithmn would have to satisfy in order of importance.

- There can never be any overlap between each 4x4 drill
- Each drill must be accessible by a conveyor (This doesnt mean just having an open square next to the drill since that open area may be a closed off 'pocket')
- As many ore tiles must be covered as possible
- The fewest number of drills used
- No drills can be placed in areas with no ores (This last rule is largely not relevant since if the fewest number of drills are used then there can't be any 'wasted' drills)

## Approached I implemented: