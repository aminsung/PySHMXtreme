# PySHMXtreme
Nice shared memory interface using numpy b/c I couldn't find one that works.

## Instructions
1. First, import pyshmx and create some memory blocks that should be created before running the program.
MemoryManager.py
```python
# import
import pyshmxtreme.SHMSegment as shmx

# create an entry point
TIME_STATE = shmx.SHMSegment(robot_name='ALPHRED', seg_name='TIME_STATE', init=False)
# create memory segment blocks as needed
TIME_STATE.add_blocks(name='time', data=np.zeros((1,1)))
```

2. 
Setting the memory
```
import MemoryManager

data = {}
while True:
    data['time'] = np.array([[0.4]])
    MemoryManager.TIME_STATE.set(data)
```

3.
Getting the memory
```
import MemoryManager

while True:
    data = MemoryManager.TIME_STATE.get()
    print("I got my data at: {}".format(data['time']))
```

* Always set data stored in a dictionary
