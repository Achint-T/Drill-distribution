import numpy as np
from scipy.ndimage import zoom
from copy import copy
from collections import deque
import multiprocessing

def trim_grid(grid):
    column_sum = np.sum(grid, axis=0)
    row_sum = np.sum(grid, axis=1)

    if not column_sum.any():
        return [100]

    while not column_sum[1]:
        grid = np.delete(grid, 0, 1)
        column_sum = column_sum[1:]

    while not row_sum[1]:
        grid = np.delete(grid, 0, 0)
        row_sum = row_sum[1:]

    while not column_sum[-2]:
        grid = np.delete(grid, -1, 1)
        column_sum = column_sum[:-1]

    while not row_sum[-2]:
        grid = np.delete(grid, -1, 0)
        row_sum = row_sum[:-1]
    
    return grid

def printify(nested_arrays):

    string = ''
    
    for array in nested_arrays:
        for item in array:
            string += str(item)
        string += '\n'

    return string

def random_ore_generator(height, width, resolution):
    arr = np.random.uniform(size=(int(height/resolution)+1, int(width/resolution)+1))

    arr = [np.ndarray.tolist(zoom(arr, resolution))[x][:width] for x in range(height)]
    
    value = (np.random.random()*0.3)+0.4

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

def can_be_placed(drill_grid, y, x):
    return not (drill_grid[y][x]==0 or drill_grid[y+1][x]==0 or drill_grid[y][x+1]==0 or drill_grid[y+1][x+1]==0)

def check_each_drill(fgrid, drills, dimentions):
    height, width = dimentions
    for drill in drills:
        y, x = int(drill/(dimentions[1]-1)), drill%(dimentions[1]-1)
        if y > 1 and x > 1 and y < height-3 and x < width-3:
            if not (fgrid[y-1][x] or fgrid[y-1][x+1] or fgrid[y][x+2] or fgrid[y+1][x+2] or fgrid[y+2][x+1] or fgrid[y+2][x] or fgrid[y+1][x-1] or fgrid[y][x-1]):
                return False
    return True

def binary_search(placeables, ore_grid, drill_grid, drills, last_value, count, dimentions):

    position = placeables[count]

    y, x = int(position/(dimentions[1]-1)), position%(dimentions[1]-1)
    
    count += 1

    if can_be_placed(drill_grid, y, x):
        new_drill_grid = drill_grid.copy()
        new_drill_grid[y][x] = 0
        new_drill_grid[y+1][x] = 0
        new_drill_grid[y][x+1] = 0
        new_drill_grid[y+1][x+1] = 0
        
        flooded_grid = new_drill_grid.copy()
        flood_fill(flooded_grid, dimentions)

        new_drills = copy(drills)
        new_drills.append(position)

        if check_each_drill(flooded_grid, new_drills, dimentions):
            increase = ore_grid[y][x] + ore_grid[y+1][x] + ore_grid[y][x+1] + ore_grid[y+1][x+1] - 0.5
            return [(new_drill_grid, new_drills, last_value+increase, count),(drill_grid, drills, last_value, count)]
        else:
            return [(drill_grid, drills, last_value, count)]
    else:
        return [(drill_grid, drills, last_value, count)]
    
def worker_loop(task_queue, mylock, current_best_value, best_layout):
    while True:
        try:
            input_argument = task_queue.get(timeout=1.5) # drill_grid, drills, last_value, count
        except:
            break
        
        print(input_argument[3])

        if input_argument[3] >= len(placeables):
            with mylock:
                if input_argument[2] > current_best_value.value:
                    current_best_value.value = input_argument[2]
                    for i in range(len(input_argument[1])):
                        best_layout[i] = input_argument[1][i]
                    for i in range(len(input_argument[1]),len(placeables)):
                        best_layout[i] = -1
        elif (len(placeables)-input_argument[3])*3.5+input_argument[2] > current_best_value.value:
            results = binary_search(placeables, ore_grid, *input_argument, dimentions)
            for result in results:
                task_queue.put(result)

#start here
ore_grid = [50]

while np.sum(ore_grid) > 25:
    ore_grid = trim_grid(np.array(random_ore_generator(15,15, resolution=5)))

dimentions = len(ore_grid),len(ore_grid[0])
placeables = []

#find the coordinates where its possible to place a drill
for position in range((dimentions[0]-1)*(dimentions[1]-1)):
    y, x = int(position/(dimentions[1]-1)), position%(dimentions[1]-1)
    if ore_grid[y][x] or ore_grid[y][x+1] or ore_grid[y+1][x] or ore_grid[y+1][x+1]:
        placeables.append(position)

#output the start parameters to the monitoring file incase the placeable count is too high
with open('binary_tree_traversal/binary_tree_output.txt', 'w') as file:
    file.write(printify(ore_grid) + '\n' + str(len(placeables)) + '\n\n')

drill_grid = np.full(dimentions, None)

manager = multiprocessing.Manager()
branches_to_explore = manager.Queue()
branches_to_explore.put((drill_grid, [], 0, 0)) # drill_grid, drills, last_value, count

locking = multiprocessing.Lock()

current_best_value = multiprocessing.Value('f',0)
best_layout = multiprocessing.Array('i',[-1]*len(placeables))

num_workers = 16
processes = [multiprocessing.Process(target=worker_loop, args=(branches_to_explore,locking, current_best_value, best_layout)) for _ in range(num_workers)]

for p in processes:
    p.start()

for p in processes:
    p.join()

with open('binary_tree_traversal/binary_tree_output.txt', 'a') as file:
    file.write(str([(int(number/(dimentions[1]-1)),number%(dimentions[1]-1)) for number in best_layout if number != -1]))