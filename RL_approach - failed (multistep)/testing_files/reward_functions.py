# pseudocode:
    
    # inputs:
    # input1 - a grid in the form of a list of lists, with values for if each tile is empty or ore
    # input2 - a list of coordinates of where every drill is placed, to be used to calculate the total value

    # step 1 - find what tiles can be accessed by a conveyor
        # create a new grid of the same dimentions full of no values yet
        # set every tile covered by a drill to 0
        # then use a flooding algorithmn to find the tiles that can be accessed by a conveyor

    # step 2 - use the flooded grid and the list of drills to check whether each of those drills can be accessed
    # step 3 - of the drills that can be accessed find a sum of all the ore that they cover

def check_location(dimentions, y,x):
    return x < 0 or y < 0 or x >= dimentions[1] or y >= dimentions[0]

def place_drill(location, grid):
    grid[location[0]][location[1]] = 0
    grid[location[0]+1][location[1]] = 0
    grid[location[0]][location[1]+1] = 0
    grid[location[0]+1][location[1]+1] = 0

def create_drills_grid(dimentions, drills=[]):
    grid = [[None for x in range(dimentions[1])] for y in range(dimentions[0])]
    for drill in drills:
        place_drill(drill, grid)
    return grid

def depth_first_flood_fill(dimentions, grid, use_routers, y=0,x=0):
    if check_location(dimentions, y,x) or grid[y][x] != None:
        return
    else:
        grid[y][x] = 1

    depth_first_flood_fill(dimentions, grid,use_routers,y+1,x)
    depth_first_flood_fill(dimentions, grid,use_routers,y-1,x)
    depth_first_flood_fill(dimentions, grid,use_routers,y,x+1)
    depth_first_flood_fill(dimentions, grid,use_routers,y,x-1)

    # if use_routers:
    #     depth_first_flood_fill(dimentions, grid,use_routers,y+3,x)
    #     depth_first_flood_fill(dimentions, grid,use_routers,y-3,x)
    #     depth_first_flood_fill(dimentions, grid,use_routers,y,x+3)
    #     depth_first_flood_fill(dimentions, grid,use_routers,y,x-3)

def check_drill_access(dimentions, drill, flooded_grid):
    list_to_check = [
            [drill[0]-1, drill[1]],
            [drill[0]-1, drill[1]+1],
            [drill[0], drill[1]+1],
            [drill[0]+1, drill[1]+2],
            [drill[0]+2, drill[1]+1],
            [drill[0]+2, drill[1]],
            [drill[0]+1, drill[1]-1],
            [drill[0], drill[1]-1]
            ]
    
    for coordinates in list_to_check:
        if check_location(dimentions, *coordinates) or flooded_grid[coordinates[0]][coordinates[1]]:
            return True
    
    return False

def sum_drills(dimentions, drills, flooded_grid, ores):
    sum = 0
    for drill in drills:
        if check_drill_access(dimentions, drill, flooded_grid):
            sum += ores[drill[0]][drill[1]] + ores[drill[0]+1][drill[1]] + ores[drill[0]][drill[1]+1] + ores[drill[0]+1][drill[1]+1]
    return sum