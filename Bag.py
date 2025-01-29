import random
class Bag:
    def __init__(self):
        pieces = ["S","Z","O","L","J","T","I"]
        self.bag = []
        while len(pieces)>0:
            self.bag.append(pieces.pop(random.randint(0,len(pieces)-1)))
    def getBag(self):
        return self.bag
