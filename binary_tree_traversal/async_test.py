import multiprocessing
import random
from time import sleep

def randomisor(number):
    sleep(0.15)
    if random.randint(0,5):
        return [number+1]
    else:
        return [number+1]*2

def worker_loop(task_queue, best, locking):
    while True:
        try:
            input_argument = task_queue.get(timeout=1)
        except:
            break

        if input_argument < 20:
            results = randomisor(input_argument)
            print(results)
            for result in results:
                task_queue.put(result)
        else:
            myoutput = random.randint(0,100)
            with locking:
                if myoutput > best.value:
                    print(best.value)
                    best.value = myoutput

manager = multiprocessing.Manager()
task_queue = manager.Queue()
task_queue.put(0)

locking = multiprocessing.Lock()
curr_best = multiprocessing.Value('i',0)

num_workers = 10
processes = [multiprocessing.Process(target=worker_loop, args=(task_queue,curr_best,locking)) for _ in range(num_workers)]

for p in processes:
    p.start()

for p in processes:
    p.join()