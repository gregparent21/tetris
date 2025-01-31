class Piece:
    def __init__(self,pieceChar,row,col):
        self.pieceChar=pieceChar
        self.settled=False
        self.row=row
        self.col = col
        self.occupied = []
        self.color = ""
        self.rotationState = 0
        self.pivot = [row,col]

        if pieceChar == "O":
            self.occupied.append([row,col])
            self.occupied.append([row+1, col])
            self.occupied.append([row+1, col+1])
            self.occupied.append([row, col+1])
            self.color="yellow"
            self.pivot[0] =  row+1
            self.pivot[1] = col+1
        if pieceChar == "I":
            self.occupied.append([row,col-1])
            self.occupied.append([row, col+2])
            self.occupied.append([row, col+1])
            self.occupied.append([row, col])
            self.color="lightblue"
            self.pivot = [row+1,col+1]
        if pieceChar == "T":
            self.occupied.append([row,col])
            self.occupied.append([row+1, col-1])
            self.occupied.append([row+1, col])
            self.occupied.append([row+1, col+1])
            self.color="purple"
            self.pivot = [row+1.5,col+0.5]
        if pieceChar == "S":
            self.occupied.append([row,col])
            self.occupied.append([row, col+1])
            self.occupied.append([row+1, col])
            self.occupied.append([row+1, col-1])
            self.color="lightgreen"
            self.pivot=[row+1.5,col+.5]
        if pieceChar == "Z":
            self.occupied.append([row,col])
            self.occupied.append([row, col-1])
            self.occupied.append([row+1, col])
            self.occupied.append([row+1, col+1])
            self.color="red"
            self.pivot = [row+1.5,col+0.5]
        if pieceChar == "L":
            self.occupied.append([row+1,col-1])
            self.occupied.append([row+1, col+1])
            self.occupied.append([row+1, col])
            self.occupied.append([row, col+1])
            self.color="orange"
            self.pivot = [row+1.5,col+0.5]
        if pieceChar == "J":
            self.occupied.append([row+1,col])
            self.occupied.append([row+1, col+1])
            self.occupied.append([row+1, col-1])
            self.occupied.append([row, col-1])
            self.color="blue"
            self.pivot = [row+1.5,col+0.5]

    def settlePiece(self):
        self.settled=True