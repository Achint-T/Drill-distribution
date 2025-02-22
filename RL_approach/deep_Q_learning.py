from keras import Sequential, layers
import tensorflow as tf
import os
from collections import deque
from copy import deepcopy
import numpy as np
from scipy.ndimage import zoom
import random

MEMORY_SIZE = 10000
MIN_REPLAY_MEMORY_SIZE = 1000
MINIBATCH_SIZE = 64
DISCOUNT = 0.98

EPISODES = 7500
MAX_STEPS = 50

epsilon = 1
EPSILON_DECAY = 0.999
MIN_EPSILON = 0.001
UPDATE_TARGET_EVERY = 20

class DQNAgent:
    def __init__(self):

        self.model = self.get_model()

        self.target_model = self.get_model()
        self.target_model.set_weights(self.model.get_weights())
        
        self.experience = deque(maxlen=MEMORY_SIZE)

        self.target_update_counter = 0

    def get_model(self):
        model = Sequential()

        model.add(layers.Conv2D(32, (3,3), padding='same', activation='relu', input_shape = (17, 17, 2)))
        model.add(layers.MaxPool2D(pool_size=(2,2)))

        model.add(layers.Conv2D(64, (3,3), padding='same', activation='relu', input_shape = (17, 17, 2)))
        model.add(layers.MaxPool2D(pool_size=(2,2)))

        model.add(layers.Flatten())

        model.add(layers.Dense(256, activation='relu'))

        model.add(layers.Dense(257))
        model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
        
        return model
    
    def update_replay_memory(self, transition):
        self.experience.append(transition)

    def get_qs(self, state):
        return self.model.predict(state)
    
    def train(self, terminal_state):
        
        if len(self.experience) < MIN_REPLAY_MEMORY_SIZE:
            return

        minibatch = random.sample(self.experience, MINIBATCH_SIZE)

        current_states = np.squeeze(np.stack([transition[0] for transition in minibatch]))
        changed_states = np.squeeze(np.stack([transition[3] for transition in minibatch]))

        current_qs_list = self.model.predict(current_states, batch_size=MINIBATCH_SIZE)
        future_qs_list = self.target_model.predict(changed_states, batch_size=MINIBATCH_SIZE)

        x = []
        y = []

        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            x.append(current_state)
            y.append(current_qs)

        self.model.fit(np.squeeze(np.array(x)),np.squeeze(np.array(y)), batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False)

        if terminal_state:
            self.target_update_counter += 1

        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0

def random_ore_generator():
    arr = np.random.uniform(size=(5,5))
    arr = [np.ndarray.tolist(zoom(arr, 4))[x][:17] for x in range(17)]
    
    value = (random.random()*0.3)+0.45

    for x in range(17):
        for y in range(17):
            if x == 0 or y == 0 or x == 16 or y == 16:
                arr[x][y] = 0
            elif x == 1 or y == 1 or x == 15 or y == 15:
                arr[x][y] = int(arr[x][y]*.6 > value)
            elif x == 2 or y == 2 or x == 14 or y == 14:
                arr[x][y] = int(arr[x][y]*.75 > value)
            elif x == 3 or y == 3 or x == 13 or y == 13:
                arr[x][y] = int(arr[x][y]*.85 > value)
            else:
                arr[x][y] = int(arr[x][y] > value)
    
    return arr

class Enviroment:
    def reset(self):
        self.ore_grid = np.array(random_ore_generator())
        self.drill_grid = [[0]*17 for _ in range(17)]

        self.episode_step = 0
        self.last_value = 0

        self.max_value = 0
        self.moves = []

        for row in self.ore_grid:
            for tile in row:
                self.max_value += tile

        return np.expand_dims(np.stack((np.array(self.ore_grid), np.array(self.drill_grid)), axis=-1), axis=0)
    
    def step(self, action):

        if action == 256:
            return np.expand_dims(np.stack([self.ore_grid, self.drill_grid], axis=-1), axis=0), 0,  True

        y = int(action/16)
        x = action%16

        self.episode_step += 1

        if self.drill_grid[y][x] or self.drill_grid[y+1][x] or self.drill_grid[y][x+1] or self.drill_grid[y+1][x+1]:
            return np.expand_dims(np.stack([self.ore_grid, self.drill_grid], axis=-1), axis=0), -1,  False

        done = False
        current_value = 0
        
        self.drill_grid[y][x] = 1
        self.drill_grid[y][x+1] = .75
        self.drill_grid[y+1][x] = .5
        self.drill_grid[y+1][x+1] = .25

        self.moves.append([y,x])

        def depth_first_flood_fill(grid,y,x):
            if x < 0 or y < 0 or x > 16 or y > 16 or grid[y][x] != 0:
                return
            else:
                grid[y][x] = None

            depth_first_flood_fill(grid,y+1,x)
            depth_first_flood_fill(grid,y-1,x)
            depth_first_flood_fill(grid,y,x+1)
            depth_first_flood_fill(grid,y,x-1)
        
        flooded_grid = deepcopy(self.drill_grid)

        for number in range(17):
            depth_first_flood_fill(flooded_grid, 0, number)
            depth_first_flood_fill(flooded_grid, 16, number)
            depth_first_flood_fill(flooded_grid, number, 0)
            depth_first_flood_fill(flooded_grid, number, 16)

        def is_accessible(grid, y, x):
            if y<2 or y>13 or x<2 or x>13:
                return True
            testing = [[-1,0],[-1,1],[0,2],[1,2],[2,1],[2,0],[1,-1],[0,-1]]
            for coords in testing:
                if grid[y+coords[0]][x+coords[1]] == None:
                    return True
            return False

        for [y,x] in self.moves:
            if is_accessible(flooded_grid, y, x):
                current_value += self.ore_grid[y][x]
                current_value += self.ore_grid[y+1][x]
                current_value += self.ore_grid[y][x+1]
                current_value += self.ore_grid[y+1][x+1]

        reward = (current_value - self.last_value - 0.5)/4
        self.last_value = current_value

        if self.last_value == self.max_value or self.episode_step >= MAX_STEPS:
            done = True

        return np.expand_dims(np.stack((np.array(self.ore_grid), np.array(self.drill_grid)), axis=-1), axis=0), reward, done

if not os.path.isdir('models'):
    os.makedirs('models')

env = Enviroment()
agent = DQNAgent()

for episode in range(1, EPISODES+1):

    episode_reward = 0
    step = 1

    current_state = env.reset()

    done = False

    while not done:

        if np.random.random() > epsilon:
            data = np.ndarray.tolist(agent.get_qs(current_state))[0]
            action = int(np.argmax(data))
        else:
            action = np.random.randint(257)
        new_state, reward, done = env.step(action)

        episode_reward += reward

        agent.update_replay_memory((current_state, action, reward, new_state, done))
        agent.train(done)

        current_state = new_state
        step += 1

        if episode % 500 == 0:
            agent.model.save(f'RL_approach/models/{episode}.keras')

    with open('RL_approach/training_data.txt','a') as data_log:
        data_log.write(f'{episode}, {step}, {env.last_value}\{env.max_value}, {epsilon}\n')
    
    if epsilon > MIN_EPSILON:
        epsilon *= EPSILON_DECAY
        epsilon = max(MIN_EPSILON, epsilon)