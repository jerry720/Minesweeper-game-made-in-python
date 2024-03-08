from tkinter import Tk
from game_control import Game


try:
    if __name__ == '__main__':
        root = Tk()
        root.configure(bg='dark green')
        my_game = Game(root, 20, 90)
        root.mainloop()
except Exception as e:
    print(e)
