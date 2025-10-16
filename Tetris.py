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

    # do not append a sentinel row; keep states as a numRows x numColumns grid


        # default tick speed (will be set on start screen)
        self.tick_speed = 500
        self.current_tick_speed = 500
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

        # self.drawButton = tk.Button(self.root, text="Create",
        #                             command=lambda: self.create_piece(Piece(pieceChar=self.queue.popleft(),
        #                                                                     row=0, col=3), canvas=self.canvas))
        # self.drawButton.grid(row=3, column=0)

        self.holdCanvas = tk.Canvas(self.root,width=140,height = 140,highlightbackground="black",highlightthickness=3,
                                    bg="grey")

        self.holdCanvas.grid(row=2,column=0)

        self.currentPieceChar = self.queue[0]

        self.heldPiece=""
        self.can_hold = True
        self.firstHold = True

        self.pivotX = None
        self.pivotY = None

        # show start menu to choose speed and then begin game loop
        self.show_start_menu()
        self.root.mainloop()

    def show_start_menu(self):
        # modal start window
        start_win = tk.Toplevel(self.root)
        start_win.title("Start Tetris")
        start_win.transient(self.root)
        start_win.grab_set()

        tk.Label(start_win, text="Choose start speed (1 slow - 10 fast):").grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        speed_var = tk.IntVar(value=5)
        speed_scale = tk.Scale(start_win, from_=1, to=10, orient=tk.HORIZONTAL, variable=speed_var)
        speed_scale.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        def on_start():
            s = speed_var.get()
            # map 1 -> 1000, 10 -> 100 linearly
            mapped = int(round(1000 - (s - 1) * 100))
            self.tick_speed = mapped
            self.current_tick_speed = mapped
            start_win.grab_release()
            start_win.destroy()
            # start the update loop
            self.update_game()

        start_btn = tk.Button(start_win, text="Start", command=on_start)
        start_btn.grid(row=2, column=0, padx=10, pady=10)
        quit_btn = tk.Button(start_win, text="Quit", command=self.root.destroy)
        quit_btn.grid(row=2, column=1, padx=10, pady=10)



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
            # self.draw_pivot(pivotX=self.pivotX,pivotY=self.pivotY)
        else:
            self.move_live_down()
            self.pivotY+=1
            # self.draw_pivot(pivotX=self.pivotX,pivotY=self.pivotY)
        self.draw_queue()
        self.check_clear()
        # print(self.pivotY,self.pivotX)

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

    '''
    Debug helper method which draws the pivot point of the current piece
    '''
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
        if event.keysym == "space":
            self.hard_drop()
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
        live_tiles = [(x, y) for x in range(self.numRows) for y in range(self.numColumns) if self.states[x][y] == "L"]

        if not live_tiles:
            return
        # pivot returned as [pivot_row, pivot_col]
        pivot_row, pivot_col = self.find_pivot_point(live_tiles)

        # keep a set of current live tiles so rotation can overlap old positions
        live_set = set((r, c) for r, c in live_tiles)

        # compute candidate rotated positions (rounded to nearest int)
        new_positions = []
        for r, c in live_tiles:
            if angle == 90:
                new_r = pivot_row + (c - pivot_col)
                new_c = pivot_col - (r - pivot_row)
            elif angle == 180:
                new_r = pivot_row - (r - pivot_row)
                new_c = pivot_col - (c - pivot_col)
            elif angle == 270:
                new_r = pivot_row - (c - pivot_col)
                new_c = pivot_col + (r - pivot_row)
            else:
                return
            # round to nearest integer cell
            new_positions.append((int(round(new_r)), int(round(new_c))))

        # quick validity check: if rotation fits without kicks, apply it
        def positions_valid(positions, dr=0, dc=0):
            for rr, cc in positions:
                nr, nc = rr + dr, cc + dc
                if not (0 <= nr < self.numRows and 0 <= nc < self.numColumns):
                    return False
                # treat settled tiles as collisions. It's ok to overlap current live tiles
                if self.states[nr][nc] == "S" and (nr, nc) not in live_set:
                    return False
            return True

        if positions_valid(new_positions, dr=0, dc=0):
            chosen_offset = (0, 0)
        else:
            # try simple kicks: left, right, up, down (one cell)
            kicks = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            chosen_offset = None
            for dr, dc in kicks:
                if positions_valid(new_positions, dr=dr, dc=dc):
                    chosen_offset = (dr, dc)
                    break
            if chosen_offset is None:
                # no valid kick found -> cancel rotation
                return

        # clear old live tiles
        for r, c in live_tiles:
            self.states[r][c] = "E"
            self.draw_square(row=r, col=c, color="grey", canvas=self.canvas)

        # apply rotated (and kicked) positions
        dr, dc = chosen_offset
        for nr, nc in new_positions:
            rr, cc = nr + dr, nc + dc
            self.states[rr][cc] = "L"
            self.draw_square(row=rr, col=cc, color=self.currentColor, canvas=self.canvas)

        # update stored pivot to reflect any kick displacement
        # pivot stored as [row, col] in Tetris as self.pivotY, self.pivotX
        self.pivotY = pivot_row + dr
        self.pivotX = pivot_col + dc

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
        # collect live tiles
        for r in range(self.numRows):
            for c in range(self.numColumns):
                if self.states[r][c] == "L":
                    liveTiles.append((r, c))

        if not liveTiles:
            return

        translation = -1 if direction == "L" else 1

        # check collision for all tiles (allow overlap with current live tiles)
        live_set = set(liveTiles)
        for r, c in liveTiles:
            nc = c + translation
            if not (0 <= nc < self.numColumns):
                return
            if self.states[r][nc] == "S" and (r, nc) not in live_set:
                return

        # perform move in safe order: when moving left, iterate increasing cols; when right, decreasing cols
        if translation == -1:
            ordered = sorted(liveTiles, key=lambda t: (t[1], t[0]))
        else:
            ordered = sorted(liveTiles, key=lambda t: (t[1], t[0]), reverse=True)

        for r, c in ordered:
            nc = c + translation
            # set new cell to live
            self.states[r][nc] = "L"
            self.draw_square(r, nc, color=self.currentColor, canvas=self.canvas)
            # clear old cell
            self.states[r][c] = "E"
            self.draw_square(r, c, color="grey", canvas=self.canvas)

        # update pivot column
        if self.pivotX is not None:
            self.pivotX = self.pivotX + translation

    '''
    The gravity system that moves each live tile down during each frame
    '''
    def move_live_down(self):
        # collect all live tiles (including those on the bottom row)
        live_tiles = [(r, c) for r in range(self.numRows) for c in range(self.numColumns) if self.states[r][c] == "L"]
        if not live_tiles:
            return

        live_set = set(live_tiles)

        # if any live tile would fall out of bounds or land on an S tile (not part of live set), settle whole piece
        for r, c in live_tiles:
            below_r = r + 1
            if below_r >= self.numRows or (self.states[below_r][c] == "S" and (below_r, c) not in live_set):
                # settle
                for i, j in live_tiles:
                    self.states[i][j] = "S"
                    self.colors[i][j] = self.currentColor
                    self.draw_square(row=i, col=j, color=self.currentColor, canvas=self.canvas)
                return

        # otherwise, move live tiles down by 1 safely (do descending order)
        for r, c in sorted(live_tiles, key=lambda t: t[0], reverse=True):
            self.states[r][c] = "E"
            self.draw_square(row=r, col=c, color="grey", canvas=self.canvas)
            self.states[r+1][c] = "L"
            self.draw_square(row=r+1, col=c, color=self.currentColor, canvas=self.canvas)

        # update pivot row if present
        if self.pivotY is not None:
            self.pivotY += 1

    def hard_drop(self):
        """Drop the current live piece straight down until it would land on settled tiles, then settle it immediately."""
        # collect live tiles
        live_tiles = [(r, c) for r in range(self.numRows) for c in range(self.numColumns) if self.states[r][c] == "L"]
        if not live_tiles:
            return

        # compute how many rows we can move down without collision
        max_drop = None
        live_set = set(live_tiles)
        for r, c in live_tiles:
            # look down from r+1 until collision or bottom
            drop = 0
            rr = r
            while True:
                rr += 1
                if not (0 <= rr < self.numRows):
                    break
                if self.states[rr][c] == "S" and (rr, c) not in live_set:
                    break
                drop += 1
            # drop is number of empty/overlap cells below this tile
            if max_drop is None or drop < max_drop:
                max_drop = drop

        if max_drop is None or max_drop == 0:
            for r, c in live_tiles:
                if r + 1 < self.numRows and self.states[r+1][c] == "S":
                    for i, j in live_tiles:
                        self.states[i][j] = "S"
                        self.colors[i][j] = self.currentColor
                    return
            return

        for r, c in live_tiles:
            self.states[r][c] = "E"
            self.draw_square(row=r, col=c, color="grey", canvas=self.canvas)

        new_tiles = []
        for r, c in live_tiles:
            nr = r + max_drop
            self.states[nr][c] = "L"
            self.draw_square(row=nr, col=c, color=self.currentColor, canvas=self.canvas)
            new_tiles.append((nr, c))

        # settling the tiles
        for r, c in new_tiles:
            self.states[r][c] = "S"
            self.colors[r][c] = self.currentColor

        # after settling, clear any remaining live markers (should be none)
        for i in range(self.numRows):
            for j in range(self.numColumns):
                if self.states[i][j] == "L":
                    self.states[i][j] = "S"
                    self.colors[i][j] = self.currentColor


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
