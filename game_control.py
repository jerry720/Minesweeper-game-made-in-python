from square_tile import Tile
from timer import Stopwatch
from tkinter import *
from PIL import ImageTk, Image
import random
from pprint import pprint # debugging



class Game:
    def __init__(self, master, dimention, mine_count):
        self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.root = master
        self.dimention = dimention
        self.mine_count = mine_count # real mine count
        self.flags = 0 # theoretical mine count
        self.remaining_squares = self.dimention ** 2 - self.mine_count
        self.first_turn = True
        self.widget_container = None
        # initializing the game
        self.open_images()
        self.setup_board()
        self.metadata, self.mine_locations = self.generate_array()
        pprint(self.metadata)

    def open_images(self):
        # global image_table
        self.image_table = {}
        identifier = 0
        images = ['images\\default.png', 'images\\tile_1.png', 'images\\tile_2.png', 
                'images\\tile_3.png', 'images\\tile_4.png', 'images\\tile_5.png',
                'images\\tile_6.png', 'images\\tile_7.png', 'images\\tile_8.png',
                'images\\flag.png', 'images\\tile_plain.png', 'images\\mine.png']
        for item in images:
            current = Image.open(item).resize((40, 40))
            self.image_table[identifier] = ImageTk.PhotoImage(current)
            identifier += 1

    # uncovering a square(s) - through I/O
    def left_click(self, event):
        # must not be flagged to left click
        if not event.widget.flagged:
            clicked_coord = event.widget.coordinates
            current_number = self.metadata[clicked_coord[0]][clicked_coord[1]]
            if current_number == 9: # square is a mine
                if self.first_turn: # first click is exempt from mines
                    self.move_mine(clicked_coord)
                else:
                    self.show_all_mines()
            elif 0 < current_number < 9:
                if not event.widget.clicked:
                    # event.widget.configure(image=self.image_table[current_number])
                    self.remaining_squares = event.widget.uncover(current_number, self.image_table, self.remaining_squares)
                    self.check_win()
                else: # user wants to uncover all surrounding squares
                    for dx, dy in self.directions:
                        if 0 <= clicked_coord[0]+dx < self.dimention and 0 <= clicked_coord[1]+dy < self.dimention:
                            square = self.game_grid[clicked_coord[0]+dx][clicked_coord[1]+dy]
                            if not square.clicked and not square.flagged:
                                self.center_click(event)
                                return
            else:
                event.widget.configure(image=self.image_table[10])
                event.widget.configure(relief='sunken')
                # uncovering neighbouring squares
                self.uncover_connected(self.metadata, clicked_coord)
            event.widget.configure(relief='sunken')
            event.widget.clicked = True
            self.first_turn = False

    def center_click(self, event):
        clicked_coord = event.widget.coordinates
        current_number = self.metadata[clicked_coord[0]][clicked_coord[1]]
        if event.widget.clicked: # button must be clicked
            # left clicking squares around chosen square
            for dx, dy in self.directions:
                coord_1, coord_2 = clicked_coord[0]+dx, clicked_coord[1]+dy
                if 0 <= coord_1 < self.dimention and 0 <= coord_2 < self.dimention:
                    if self.metadata[coord_1][coord_2] == 9 and not self.game_grid[coord_1][coord_2].flagged:
                        self.show_all_mines()
                    self.remaining_squares = self.game_grid[coord_1][coord_2].uncover(self.metadata[coord_1][coord_2], self.image_table, self.remaining_squares)
                    self.check_win()
                    self.uncover_connected(self.metadata, (coord_1, coord_2))

    def right_click(self, event):
        if not event.widget.clicked:
            if not event.widget.flagged:
                event.widget.configure(image=self.image_table[9])
                event.widget.flagged = True
                existing = int(self.flag_count.cget('text')[2:])
                self.flag_count.configure(text='= '+str(existing+1))
            else:
                event.widget.configure(image=self.image_table[0])
                event.widget.flagged = False
                existing = int(self.flag_count.cget('text')[2:])
                self.flag_count.configure(text='= '+str(existing-1))
            
    # creates the grid and instantiates timer widget (LabelFrame)
    def setup_board(self):
        self.first_turn = True
        self.field = LabelFrame(self.root, bg='dark green', padx=3)
        self.field.grid(row=1, column=0, columnspan=4)
        # only instantiating new objects first time
        if not self.widget_container:
            self.widget_container = LabelFrame(self.root, bg='dark green')
            self.widget_container.grid(row=0, column=0)
            self.stopwatch = Stopwatch(self.widget_container)
            self.stopwatch.grid(row=0, column=0, padx=6, pady=2)
            Label(self.widget_container, image=self.image_table[9], bg='dark green', fg='white', font=('Helvetica', 20, 'bold')).grid(row=0, column=2, padx=5)
            self.start_game = Button(self.widget_container, text='New Game', pady=3, bg='gray', fg='white', font=('arial', 15, 'bold'), bd=4, activebackground='papayawhip', command=self.reset_board)
            self.start_game.grid(row=0, column=1, padx=6, pady=3)
        self.flag_count = Label(self.widget_container, text='= 0', bg='dark green', fg='white', font=('Arial', 25, 'bold'))
        self.flag_count.grid(row=0, column=3)

        self.game_grid = [] # a 2D array to store the actual game widgets
        for i in range(self.dimention):
            row = []
            for j in range(self.dimention):
                button = Tile(self.field, coordinates=(i, j), width=35, height=31, bg='grey', relief='ridge', image=self.image_table[0])
                button.grid(row=i, column=j)
                button.bind('<Button-1>', self.left_click)
                button.bind('<Button-2>', self.center_click) # button 2 is scroll wheel
                button.bind('<Button-3>', self.right_click)
                row.append(button)
            self.game_grid.append(row)
        self.stopwatch.start()

    def reset_board(self):
        self.start_game.configure(state=DISABLED)
        self.field.destroy()
        self.flag_count.configure(text='0')
        self.stopwatch.reset()
        self.metadata, self.mine_locations = self.generate_array()
        self.setup_board()
        self.root.after(6000, self.cooldown)

    def cooldown(self):
        self.start_game.configure(state=NORMAL)

    # creating an array containing mine and number information
    def generate_array(self):
        count = 0
        mine_locations = set()
        while len(mine_locations) < self.mine_count:
            mine_locations.add((random.randint(0, self.dimention-1), random.randint(0, self.dimention-1)))
            count += 1
        metadata = []
        for i in range(self.dimention):
            row = []
            for j in range(self.dimention):
                if (i, j) in mine_locations:
                    row.append(9)
                else:
                    row.append(0)
            metadata.append(row)

        # looping over the array and adding the numbers
        queue = []
        for i in range(self.dimention):
            for j in range(self.dimention):
                queue.append((i, j))
        while queue:
            coord_row, coord_col = queue.pop(0)
            value = metadata[coord_row][coord_col]
            if value > 0 or value == 9:
                continue
            # counting adjacent mines
            adjacent = 0
            for dx, dy in self.directions:
                if 0 <= coord_row+dx < self.dimention and 0 <= coord_col+dy < self.dimention:
                    if metadata[coord_row+dx][coord_col+dy] == 9:
                        adjacent += 1
                        # no need to visit this square
                        # try-except clause to deal with removing an already popped item
                        try: queue.remove((coord_row+dx, coord_col+dy))
                        except Exception: pass               
            metadata[coord_row][coord_col] = adjacent
        return metadata, mine_locations
    
    # moves the mine to another non-mine square in the grid
    # amends the numbers surrounding that square
    def move_mine(self, coordinate):
        if not self.first_turn:
            return
        x, y = coordinate
        # checking the mines that surround the square
        count = 0
        for dx, dy in self.directions:
            if self.metadata[x+dx][y+dy] == 9:
                count += 1
        self.metadata[x][y] = count

        moved = False
        while not moved:
            new_coords = (random.randint(0, self.dimention), random.randint(0, self.dimention))
            if self.metadata[new_coords[0]][new_coords[1]] != 9:
                self.metadata[new_coords[0]][new_coords[1]] = 9
                moved = True
        print('New Coordinates', new_coords) # test
        self.mine_locations.add(new_coords)
        for dx, dy in self.directions: # changing the numbers around the square
            if 0 <= new_coords[0]+dx < self.dimention and 0 <= new_coords[1]+dy < self.dimention:
                if self.metadata[new_coords[0]+dx][new_coords[1]+dy] < 8:
                    self.metadata[new_coords[0]+dx][new_coords[1]+dy] += 1
            if 0 <= x+dx < self.dimention and 0 <= y+dy < self.dimention:
                if 9 > self.metadata[x+dx][y+dy] > 0:
                    self.metadata[x+dx][y+dy] -= 1

        self.remaining_squares = self.game_grid[x][y].uncover(count, self.image_table, self.remaining_squares)
        self.uncover_connected(self.metadata, coordinate)
        pprint(self.metadata)

    # displaying all the mines when the game is lost
    def show_all_mines(self):
        for location in self.mine_locations:
            self.remaining_squares = self.game_grid[location[0]][location[1]].uncover(self.metadata[location[0]][location[1]], self.image_table, self.remaining_squares)
        self.stopwatch.pause()
    
    # uncovering neighbouring squares up to the first layer of numbers
    def uncover_connected(self, arr, coord:tuple): # breadth-first algorithm
        if arr[coord[0]][coord[1]] == 9:
            return
        coord = (coord[0], coord[1], False)
        explored = set()
        queue = []
        queue.append(coord)
        explored.add(coord)
        while queue:
            # visiting a square - popping off a current coordinate
            current = queue.pop(0)
            self.remaining_squares = self.game_grid[current[0]][current[1]].uncover(self.metadata[current[0]][current[1]], self.image_table, self.remaining_squares)
            self.check_win()
            if current[2]:
                continue
            #adding more squares to todo list
            for dx, dy in self.directions:
                new = (current[0]+dx, current[1]+dy, False)# boolean flag to indicate number border has been reached
                if 0 <= new[0] < len(arr) and 0 <= new[1] < len(arr[0]) and not self.game_grid[new[0]][new[1]].flagged: # within boundaries
                    if arr[new[0]][new[1]] == 0 and (new[0], new[1]) not in explored:
                        queue.append(new)
                        explored.add((new[0], new[1]))
                    elif 0 < arr[new[0]][new[1]] < 9 and (new[0], new[1]) not in explored:
                        queue.append((new[0], new[1], True)) # for boundary square
                        explored.add((new[0], new[1]))

    def check_win(self):
        if self.remaining_squares < 1:
            pass


