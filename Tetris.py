import tkinter as tk
from Piece import Piece
from collections import deque
from Bag import Bag


'''
Tetris game with both front and back end
'''
class Tetris:

    '''
    Constructor that initializes the game canvas as well as instance variables
    '''
    def __init__ (self):
        self.root = tk.Tk()
        self.root.geometry("1000x700")
        self.root.title("Tetris")
        self.currentColor=""
        #state of E for empty
        self.states = [["E" for _ in range(10)] for _ in range(20)]
        self.colors = [["" for _ in range(10)] for _ in range(20)]
        self.pieceDispX = {"I":1.35,"O":1.4}
        self.pieceDispY = {"I":1.8}

        self.states.append(["S" for _ in range(10)])


        self.tick_speed=1000
        self.current_tick_speed = 1000
        self.cellSize=30
        self.queue = deque()
        self.build_piece_queue()
        self.score = 0
        self.lines_cleared = 0
        self.numColumns=10
        self.numRows=20

        self.root.bind("<KeyPress>", self.key_pressed)
        self.root.bind("<KeyRelease>", self.key_released)


        self.label=tk.Label(self.root, text=self.get_header(), font=('Arial', 18))
        self.quitButton = tk.Button(self.root,text="Quit",command=quit)
        self.label.grid(row=1,column=1,pady=10)
        self.quitButton.grid(row=1,column=0,padx=100)

        self.canvas=tk.Canvas(self.root,
                              width=self.numColumns*self.cellSize,
                              height=self.numRows*self.cellSize,
                              bg="grey",
                              highlightbackground="black",
                              highlightthickness=3)
        self.canvas.grid(row=2,column=1)
        self.draw_grid()


        self.queueCanvas=tk.Canvas(self.root,width = 140,height=500,highlightbackground="black",
                              highlightthickness=3, bg="grey")
        self.queueCanvas.grid(row=2,column =2,padx=50)

        self.drawButton = tk.Button(self.root, text="Create",
                                    command=lambda: self.create_piece(Piece(pieceChar=self.queue.popleft(),
                                                                            row=0, col=3), canvas=self.canvas))
        self.drawButton.grid(row=3, column=0)

        self.holdCanvas = tk.Canvas(self.root,width=140,height = 140,highlightbackground="black",highlightthickness=3,
                                    bg="grey")

        self.holdCanvas.grid(row=2,column=0)

        self.currentPieceChar = self.queue[0]

        self.heldPiece=""
        self.can_hold = True
        self.firstHold = True

        self.pivotX = None
        self.pivotY = None

        self.update_game()
        self.root.mainloop()


    '''
    Update method called every tick speed. Checks for game updates such as score and cleared lines as well as updates 
    the piece queue if there are less than two piece bags in the queue
    '''
    def update_game(self):
        self.label.config(text=self.get_header())
        self.build_piece_queue()
        if not any("L" in subarray for subarray in self.states):
            self.currentPieceChar = self.queue.popleft()
            temp_piece = Piece(self.currentPieceChar, row=0, col=4)
            self.create_piece(temp_piece, canvas=self.canvas)
            self.can_hold=True
            self.pivotX = temp_piece.pivot[1]
            self.pivotY = temp_piece.pivot[0]
            self.draw_pivot(pivotX=self.pivotX,pivotY=self.pivotY)
        else:
            self.move_live_down()
            self.pivotY+=1
            self.draw_pivot(pivotX=self.pivotX,pivotY=self.pivotY)
        self.draw_queue()
        self.check_clear()
        print(self.pivotY,self.pivotX)

        if not self.check_game_over():
            self.root.after(self.current_tick_speed, lambda: self.update_game())
            # self.root.after(2000, lambda: self.update_game())

        else:
            string = "Game Over! Score: " + str(self.score)
            game_over_label = tk.Label(self.root, text=string, font=('Arial', 30))
            game_over_label.grid(row = 3,column=1)

    '''
    Returns True if the game is over. Game is over if there is a settled tile in the first row
    '''
    def check_game_over(self):
        if any("S" in value for value in self.states[0]):
            return True
        return False

    def draw_pivot(self,pivotX,pivotY):
        self.canvas.create_oval(pivotX*self.cellSize,pivotY*self.cellSize,
                                pivotX*self.cellSize+4,pivotY*self.cellSize+4,
                                outline="Black",fill="Red")
    '''
    Checks for key pressed events such as moving left and right and updating tick speed
    '''
    def key_pressed(self,event):
        if event.keysym=="Left":
            self.horizontal_translation("L")
        if event.keysym =="Right":
            self.horizontal_translation("R")
        if event.keysym == "Down":
            self.current_tick_speed = 75
        if event.keysym == "c" and self.can_hold:
            self.hold_piece()
        if event.keysym == "Up":
            self.rotate_piece(angle=90)
        if event.keysym == "z":
            self.rotate_piece(angle = 270)
        if event.keysym == "r":
            self.root.destroy()
            Tetris()
        if event.keysym == "Shift_L":
            self.rotate_piece(angle =180)
        if event.keysym == "q":
            self.root.destroy()


    '''
    Swaps the current piece with the piece held in the hold canvas 
    '''
    def hold_piece(self):
        self.can_hold = False
        self.holdCanvas.delete("all")
        self.create_piece(piece=Piece(self.currentPieceChar, row=self.pieceDispY.get(self.currentPieceChar, 1.3),
                                      col=self.pieceDispX.get(self.currentPieceChar, 1.8)), canvas=self.holdCanvas)
        for i in range(20):
            for j in range(10):
                if self.states[i][j] == "L":
                    self.states[i][j] = "E"
                    self.draw_square(row=i, col=j, color="grey", canvas=self.canvas)
        if self.heldPiece != "":
            self.create_piece(piece=Piece(self.heldPiece, row=0, col=4), canvas=self.canvas)
            temp = self.currentPieceChar
            self.currentPieceChar = self.heldPiece
            self.heldPiece = temp
        else:
            self.heldPiece = self.currentPieceChar

    '''
    Given an angle of either 90, 270, or 180 degrees, rotates the current piece accordingly. If rotated piece would fall
    into settled tiles or out of bounds, calls the find_kick() method to translate piece to empty tiles. Determines the 
    pivot point of the tile in which it will be rotated by calling the find_pivot_point() method.
    '''
    def rotate_piece(self,angle):
        live_tiles = [(x, y) for x in range(len(self.states)) for y in range(len(self.states[0])) if self.states[x][y] == "L"]

        if not live_tiles:
            return
        pivot_x , pivot_y = self.find_pivot_point(live_tiles)

        new_positions = []
        for x, y in live_tiles:
            if angle == 90:
                new_x = pivot_x + (y - pivot_y)
                new_y = pivot_y - (x - pivot_x)
            elif angle == 180:
                new_x = pivot_x - (x - pivot_x)
                new_y = pivot_y - (y - pivot_y)
            elif angle == 270:
                new_x = pivot_x - (y - pivot_y)
                new_y = pivot_y + (x - pivot_x)
            else:
                return
            print(new_x,new_y)
            new_positions.append((int(new_x), int(new_y)))

        for new_x, new_y in new_positions:
            if (not (0 <= new_x < len(self.states) and 0 <= new_y < len(self.states[0])) or
                    self.states[int(new_x)][int(new_y)] == "S"):
                self.find_kick()
                return

        for x, y in live_tiles:
            self.states[x][y] = "E"
            self.draw_square(row=x, col=y, color="grey", canvas=self.canvas)

        for new_x, new_y in new_positions:
            self.states[new_x][new_y] = "L"
            self.draw_square(row=new_x, col=new_y, color=self.currentColor, canvas=self.canvas)

    '''
    Given a list of the live tiles, return the x and y coord of the pivot point
    '''
    def find_pivot_point(self,live_tiles):
        return [self.pivotY,self.pivotX]
        # return live_tiles[1]
    '''
    Returns a set of new tiles in which the rotated piece can fall if there are potential collisions
    '''
    def find_kick(self):
        return

    '''
    Checks for key released events such as re-updating tick speed
    '''
    def key_released(self,event):
        if event.keysym== "Down":
            self.current_tick_speed=self.tick_speed

    '''
    Checks the game canvas for a cleared row. If there is a cleared row, calls moveDown
    '''
    def check_clear(self):
        for i in range(20):
            rowsum = 0
            for j in range(10):
                if self.states[i][j] == "S":
                    rowsum+=1
            if rowsum == 10:
                self.score+=100
                self.lines_cleared+=1
                for j in range(10):
                    self.states[i][j]="E"
                    self.colors[i][j]=""
                    self.draw_square(row=i, col=j, color="grey", canvas=self.canvas)
                    self.move_down(cleared_row=i, row_one=True)
                if self.lines_cleared  % 10 == 0 and self.current_tick_speed>100:
                    self.tick_speed -= 100
                    self.current_tick_speed -=100

    '''
    Moves all the rows down from the clearedRow and up. Is called as a result of clearing a row
    TODO fix. Doesn't work correctly with holes. Potentially remove recursion to fix. it shouldn't move Settled states
    to fill empty states unless it was the initial cleared row. Otherwise leave holes. 
    '''
    def move_down(self,cleared_row,row_one):
        if cleared_row == 0:
            return
        for j in range(10):
            if self.states[cleared_row][j] != "S" and self.states[cleared_row - 1][j] == "S" and row_one:
                self.states[cleared_row][j] = "S"
                self.states[cleared_row - 1][j]= "E"

                self.colors[cleared_row][j]=self.colors[cleared_row - 1][j]
                self.colors[cleared_row - 1][j]= ""

                self.draw_square(row=cleared_row, col=j, color=self.colors[cleared_row][j], canvas=self.canvas)
                self.draw_square(row=cleared_row - 1, col=j, color="grey", canvas=self.canvas)
        self.move_down(cleared_row - 1, row_one=True)

    '''
    Moves the live tiles either left or right depending on key press
    '''
    def horizontal_translation(self,direction):
        liveTiles = []
        translation = -1 if direction == "L" else 1
        for col in range(len(self.states[0])):
                for row in range(len(self.states)):
                    if self.states[row][col]=="L":
                        liveTiles.append([row,col])
        for tile in liveTiles if translation == -1 else reversed(liveTiles):
            if direction == "L" :
                if tile[1]-1<0 or self.states[tile[0]][tile[1]-1] == "S":
                    return
            if direction == "R":
                if tile[1]+1>9 or self.states[tile[0]][tile[1]+1] == "S":
                    return
            self.states[tile[0]][tile[1]] = self.states[tile[0]][tile[1]-translation] if tile[1]-translation<9 else "E"
            self.states[tile[0]][tile[1]+translation] = "L"
            self.draw_square(tile[0], tile[1] + translation, color=self.currentColor, canvas=self.canvas)
            self.draw_square(tile[0], tile[1], color="grey", canvas=self.canvas)
        if direction == "L":
            self.pivotX-=1
        if direction == "R":
            self.pivotX+=1

    '''
    The gravity system that moves each live tile down during each frame
    '''
    def move_live_down(self):
        live_tiles=[]
        for i in range(len(self.states)-1):
            for j in range(len(self.states[i])):
                if self.states[i][j] == "L":
                    live_tiles.append([i, j])
        for tile in reversed(live_tiles):
            if  self.states[tile[0]+1][tile[1]] == "S":
                for i in range(20):
                    for j in range(10):
                        if self.states[i][j]=="L":
                            self.states[i][j]="S"
                            self.colors[i][j]=self.currentColor
                break
        else:
            for tile in reversed(live_tiles):
                self.states[tile[0]][tile[1]]=self.states[tile[0]-1][tile[1]] if tile[0]-1 >= 0 else "E"
                self.states[tile[0]+1][tile[1]] = "L"
                self.draw_square(tile[0] + 1, tile[1], color=self.currentColor, canvas=self.canvas)
                self.draw_square(tile[0], tile[1], color="grey", canvas=self.canvas)

    '''
    Draws the grid in the game canvas
    '''
    def draw_grid(self):
        for row in range(self.numRows):
            for col in range(self.numColumns):
                x1= col*self.cellSize
                x2 = x1 + self.cellSize
                y1 = row * self.cellSize
                y2 = y1 + self.cellSize
                self.canvas.create_rectangle(x1+3,y1+3,x2+3,y2+3,outline="black")

    '''
    Fills a tile in the game canvas which either a shape color or deletes a shape by filling the tile grey 
    '''
    def draw_square(self,row,col,color,canvas):
        x1 = col * self.cellSize
        x2 = x1 + self.cellSize
        y1 = row * self.cellSize
        y2 = y1 + self.cellSize
        canvas.create_rectangle(x1 + 3, y1 + 3, x2 + 3, y2 + 3, outline="black",fill=color)

    '''
    Generates a piece at the top of the game canvas. The piece is popped from the piece queue
    '''
    def create_piece(self,piece,canvas):
        for tile in piece.occupied:
            self.draw_square(row=tile[0], col=tile[1], color=piece.color, canvas=canvas)
            if canvas == self.canvas:
                self.states[tile[0]][tile[1]]="L"
        # self.printStates()
        self.currentColor = piece.color

    '''
    Draws the piece queue canvas to show which pieces come next
    '''
    def draw_queue(self):
        self.queueCanvas.delete("all")
        for i in range(0,4):
            # piece = Piece(self.queue[i],row=3.5*i+2,col=1.5)
            piece = Piece(self.queue[i],row=3.5*i+2,col=self.pieceDispX.get(self.queue[i],1.8))
            for tile in piece.occupied:
                self.draw_square(row=tile[0], col=tile[1], color=piece.color, canvas=self.queueCanvas)

    '''
    Updates the pieceQueue to ensure there is at least two piece bags present at all times
    '''
    def build_piece_queue(self):
        while len(self.queue)<14:
            self.queue.extend(Bag().getBag())

    '''
    Returns a formated string of the score
    '''
    def get_header(self):
        return ("Score: "+ str(self.score) + "\n Lines Cleared: " + str(self.lines_cleared)
                + " Speed: " + str(self.current_tick_speed))

    '''
    Prints the 2d array of tile states to the terminal
    '''
    def print_states(self):
        for i in range(len(self.states)):
            print(self.states[i])
        print("–" * 50)

    '''
    Debug helped method which prints the 2d array of colors to the terminal 
    '''
    def print_colors(self):
        for i in range(len(self.colors)):
            print(self.colors[i])
        print()
game = Tetris()
