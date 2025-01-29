from Bag import Bag
from collections import deque
import os

print(os.name)

bag = Bag()
print(bag.getBag())

pieces = deque()
arr=[4,5,6]
pieces.append(1)
print(pieces)
pieces.append(2)
print(pieces)
pieces.popleft()
print(pieces)
pieces.extend(arr)
print(pieces)
