import pulp as pl
import numpy as np
from scipy.ndimage import zoom

def random_ore_generator(height, width):
    arr = np.random.uniform(size=(int(height/4)+1, int(width/4)+1))

    arr = [np.ndarray.tolist(zoom(arr, 4))[x][:width] for x in range(height)]
    
    value = (np.random.random()*0.3)+0.25

    for y in range(height):
        for x in range(width):
            if x == 0 or y == 0 or x == width-1 or y == height-1:
                arr[y][x] = 0
            elif x == 1 or y == 1 or x == width-2 or y == height-2:
                arr[y][x] = int(arr[y][x]*.6 > value)
            elif x == 2 or y == 2 or x == width-3 or y == height-3:
                arr[y][x] = int(arr[y][x]*.75 > value)
            elif x == 3 or y == 3 or x == width-4 or y == height-4:
                arr[y][x] = int(arr[y][x]*.85 > value)
            else:
                arr[y][x] = int(arr[y][x] > value)
    
    return arr

def printify(nested_arrays):

    string = ''
    
    for array in nested_arrays:
        for item in array:
            string += str(item)
        string += '\n'

    return string

height, width = 15,15

# Creates the random grid
ore_grid = random_ore_generator(height, width)

# Sets up the problem
prob = pl.LpProblem('drill_distribution', pl.LpMaximize)

# Creates a set variable for every possible tile placement and a set to track which tiles are accessible
drills = pl.LpVariable.dicts('drills', [(y,x) for x in range(width-1) for y in range(height-1)], cat='Binary')
accessible = pl.LpVariable.dicts('accessible', [(y,x) for x in range(width) for y in range(height)], cat='Binary')

# Sets up the objective
prob += pl.lpSum([drills[y,x] * (ore_grid[y][x] + ore_grid[y+1][x] + ore_grid[y][x+1] + ore_grid[y+1][x+1] - 0.5) 
                 for x in range(width-1) for y in range(height-1)])

# Constraint: No overlapping drills
for y in range(height-2):
    for x in range(width-2):
        prob += drills[y,x] + drills[y+1,x] + drills[y,x+1] + drills[y+1,x+1] <= 1

# Constraint: Drills can't be placed without ore under them
for y in range(height-1):
    for x in range(width-1):
        if ore_grid[y][x] + ore_grid[y+1][x] + ore_grid[y][x+1] + ore_grid[y+1][x+1] == 0:
            prob += drills[y,x] == 0

# Constraint: Areas under drills aren't accessible
for y in range(1,height-1):
    for x in range(1,width-1):
            prob += accessible[y,x] <= 1 - (drills[y,x] + drills[y-1,x] + drills[y,x-1] + drills[y-1,x-1])

# Constraint: Corners aren't accessible
for num in range(1,height-1):
    prob += accessible[0,0] == 0
    prob += accessible[height-1,0] == 0
    prob += accessible[0,width-1] == 0
    prob += accessible[height-1,width-1] == 0

# Constraint: External sides (first and last, rows and columns) are always accessible unless covered
for num in range(1,height-1):
    prob += accessible[num,0] == (1 - (drills[num,0] + drills[num-1,0]))
    prob += accessible[num,width-1] == (1 - (drills[num,width-2] + drills[num-1,width-2]))
    prob += accessible[0,num] == (1 - (drills[0,num] + drills[0,num-1]))
    prob += accessible[height-1,num] == (1 - (drills[height-2,num] + drills[height-2,num-1]))

# Constraint: Recursive fill
for y in range(1,height-1):
    for x in range(1,width-1):
        prob += accessible[y,x] <= accessible[y+1, x] + accessible[y-1, x] + accessible[y, x+1] + accessible[y, x-1]

# Constraint: Drill can only be placed when accessible
for y in range(2,height-3):
    for x in range(2,width-3):
        prob += drills[y,x] <= accessible[y-1,x] + accessible[y-1,x+1] + accessible[y,x+2] + accessible[y+1,x+2] + accessible[y+2,x+1] + accessible[y+2,x] + accessible[y+1,x-1] + accessible[y,x-1]

prob.solve()

with open('ILP_approach/ilp_training_data.txt', 'w') as file:
    file.write(printify(ore_grid)+'\n')
    for y in range(height-1):
        for x in range(width-1):
            if drills[y,x].varValue == 1:
                file.write(f"Drill placed at ({y},{x})\n")
    
    