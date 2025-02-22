import pprint
from reward_functions import create_drills_grid, depth_first_flood_fill, sum_drills

dimentions = (10, 10)

ore_grid = [
    [0,0,0,0,0,0,0,0,0,0],
    [0,1,1,0,1,1,1,1,0,0],
    [0,1,1,0,1,1,1,1,0,0],
    [0,0,0,0,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,1,0,0],
    [0,1,1,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0]
]

drills = [[1,1],[1,4],[1,6],[3,0],[3,2],[3,6],[4,4],[5,1],[5,7],[7,1],[7,3],[7,5],[7,7]]

grid = create_drills_grid(dimentions, drills)
depth_first_flood_fill((10, 10), grid, False)
sum_drills(dimentions, drills, grid, ore_grid)