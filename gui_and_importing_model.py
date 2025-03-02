import tkinter as tk
from keras import models
import numpy as np

def center_grid(grid, rows, columns):
    add_rows = int((17-rows)/2)
    add_columns = int((17-columns)/2)
    grid = [[0]*columns]*(add_rows+1-(rows%2)) + grid + [[0]*columns]*add_rows

    return [[0]*(add_columns+1-(rows%2))+index+[0]*add_columns for index in grid]

def check_status(number):
    return max(5,min(number, 15))

def get_max_index(data):
    max = 0
    index = 0
    for x in range(len(data)):
        if data[x] > max:
            max = data[x]
            index = x
    return index

class GridApp:
    def __init__(self, root):
        self.root = root
        self.rows = 15
        self.cols = 15
        self.grid_state = []
        self.buttons = []
        
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack()

        tk.Button(self.controls_frame, text="Submit", command=self.submit_data).pack(side=tk.LEFT)
        
        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack()
        self.create_grid()

    def toggle_tile(self, row, col):
        self.grid_state[row][col] = 1 - self.grid_state[row][col] 
        color = "black" if self.grid_state[row][col] else "white"
        self.buttons[row][col].config(bg=color)

    def create_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        self.grid_state = [[0] * self.cols for _ in range(self.rows)]
        self.buttons = []
        
        for r in range(self.rows):
            row_buttons = []
            for c in range(self.cols):
                btn = tk.Button(self.grid_frame, width=1, height=1, bg="white", 
                                command=lambda r=r, c=c: self.toggle_tile(r, c))
                btn.grid(row=r, column=c)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
    
    def submit_data(self):
        global ore_grid
        ore_grid = center_grid(self.grid_state, self.rows, self.cols)

drill_grid = [[0]*17 for _ in range(17)]
action_list = []

root = tk.Tk()
root.title("Grid Toggle GUI")
app = GridApp(root)
root.mainloop()

RL_trained = models.load_model('RL_approach/models/500.keras')

for x in range(10):
    result = RL_trained.predict(np.expand_dims(np.stack((np.array(ore_grid), np.array(drill_grid)), axis=-1), axis=0))
    data = np.ndarray.tolist(result)[0]

    action = int(np.argmax(data))

    y = int(action/16)
    x = action%16

    print(y,x)

    action_list.append([y,x])

    if action==256:
        break
    
    drill_grid[y][x] = 1
    drill_grid[y][x+1] = .75
    drill_grid[y+1][x] = .5
    drill_grid[y+1][x+1] = .25


