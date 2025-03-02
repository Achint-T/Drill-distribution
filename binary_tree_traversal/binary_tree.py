import numpy as np
from scipy.ndimage import zoom
from copy import copy
from collections import deque
import multiprocessing

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
    
    value = (np.random.random()*0.3)+0.2

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
            return [(new_drill_grid, new_drills, last_value+increase, count),(drill_grid, drills, last_value, count )]
        else:
            return [(drill_grid, drills, last_value, count)]
    else:
        return [(drill_grid, drills, last_value, count)]
    
def worker_loop(task_queue, mylock, current_best_value, best_layout):
    while True:
        try:
            input_argument = task_queue.get(timeout=5)
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
        else:
            results = binary_search(placeables, ore_grid, *input_argument, dimentions)
            for result in results:
                task_queue.put(result)

dimentions = 10,10
ore_grid = np.array(random_ore_generator(*dimentions))

placeables = []

for position in range((dimentions[0]-1)*(dimentions[1]-1)):
    y, x = int(position/(dimentions[1]-1)), position%(dimentions[1]-1)
    if ore_grid[y][x] or ore_grid[y][x+1] or ore_grid[y+1][x] or ore_grid[y+1][x+1]:
        placeables.append(position)

with open('binary_tree_traversal/binary_tree_output.txt', 'w') as file:
    file.write(printify(ore_grid) + '\n' + str(len(placeables)) + '\n\n')

drill_grid = np.full(dimentions, None)

manager = multiprocessing.Manager()
branches_to_explore = manager.Queue()
branches_to_explore.put((drill_grid, [], 0, 0)) # drill_grid, drills, last_value, count

locking = multiprocessing.Lock()

current_best_value = multiprocessing.Value('f',0)
best_layout = multiprocessing.Array('i',[-1]*len(placeables))

num_workers = 8
processes = [multiprocessing.Process(target=worker_loop, args=(branches_to_explore,locking, current_best_value, best_layout)) for _ in range(num_workers)]

for p in processes:
    p.start()

for p in processes:
    p.join()

with open('binary_tree_traversal/binary_tree_output.txt', 'a') as file:
    file.write(str([(int(number/(dimentions[1]-1)),number%(dimentions[1]-1)) for number in best_layout if number != -1]))