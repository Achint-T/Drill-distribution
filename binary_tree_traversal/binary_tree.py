import numpy as np
from scipy.ndimage import zoom
from copy import copy
from collections import deque

def printify(nested_arrays):

    string = ''
    
    for array in nested_arrays:
        for item in array:
            string += str(item)
        string += '\n'

    return string

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

def flood_fill(flooded_grid, dimentions):

    to_flood = deque()

    for height in range(dimentions[0]):
        to_flood.extend([(height, 0),(height, dimentions[1]-1)])
        
    for width in range(dimentions[1]):
        to_flood.extend([(0, width),(dimentions[0]-1, width)])

    while to_flood:
        y, x = to_flood.popleft()
        if 0 <= y < dimentions[0] and 0 <= x < dimentions[1] and flooded_grid[y][x] is None:
            flooded_grid[y][x] = 1
            to_flood.extend([(y+1,x),(y-1,x),(y,x+1),(y,x-1)])

def can_be_placed(ore_grid, drill_grid, y, x):
    covers = drill_grid[y][x]==0 or drill_grid[y+1][x]==0 or drill_grid[y][x+1]==0 or drill_grid[y+1][x+1]==0
    theres_ore = ore_grid[y][x] or ore_grid[y+1][x] or ore_grid[y][x+1] or ore_grid[y+1][x+1]
    return theres_ore and not covers

def check_each_drill(fgrid, drills, dimentions):
    height, width = dimentions
    for y,x in drills:
        if y > 1 and x > 1 and y < height-3 and x < width-3:
            if not (fgrid[y-1][x] or fgrid[y-1][x+1] or fgrid[y][x+2] or fgrid[y+1][x+2] or fgrid[y+2][x+1] or fgrid[y+2][x] or fgrid[y+1][x-1] or fgrid[y][x-1]):
                return False
    return True

def binary_search(ore_grid, drill_grid, drills, last_value, position, dimentions):

    y, x = int(position/(dimentions[1]-1)), position%(dimentions[1]-1)
    position += 1

    if can_be_placed(ore_grid, drill_grid, y, x):
        new_drill_grid = drill_grid.copy()
        new_drill_grid[y][x] = 0
        new_drill_grid[y+1][x] = 0
        new_drill_grid[y][x+1] = 0
        new_drill_grid[y+1][x+1] = 0
        
        flooded_grid = new_drill_grid.copy()
        flood_fill(flooded_grid, dimentions)

        new_drills = copy(drills)
        new_drills.append((y,x))

        if check_each_drill(flooded_grid, new_drills, dimentions):
            increase = ore_grid[y][x] + ore_grid[y+1][x] + ore_grid[y][x+1] + ore_grid[y+1][x+1] - 0.5
            return [(new_drill_grid, new_drills, last_value+increase, position),(drill_grid, drills, last_value, position)]
        else:
            return [(drill_grid, drills, last_value, position)]
    else:
        return [(drill_grid, drills, last_value, position)]

dimentions = 8,8
ore_grid = np.array(random_ore_generator(*dimentions))
print(printify(ore_grid))

drill_grid = np.full(dimentions, None)

# drill_grid, drills, last_value, position
branches_to_explore = deque([(drill_grid, [], 0, 0)])

max_position = (dimentions[0]-1)*(dimentions[1]-1)

current_best_value = 0
best_layout = []

while branches_to_explore:
    next_test = branches_to_explore.popleft()
    if next_test[3] >= max_position:
        if next_test[2] > current_best_value:
            current_best_value = next_test[2]
            best_layout = next_test[1]
    else:
        branches_to_explore.extend(binary_search(ore_grid, *next_test, dimentions))

with open('binary_tree_traversal/binary_tree_output.txt', 'w') as file:
    file.write(printify(ore_grid))
    file.write(str(best_layout))