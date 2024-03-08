from tkinter import Label

# a long winded way of adding extra attribute
# a customised label class with custom attributes
# overloads the existing Label class with extra attributes
class Tile(Label):
    def __init__(self, master, coordinates: tuple, *args, **kwargs):
        # calling the constructor of the superclass
        # to create a stereotypical label
        super().__init__(master, *args, **kwargs)
        # extra attributes
        self.flagged = False
        self.clicked = False
        self.coordinates = coordinates

    # uncovering a square, programatically
    def uncover(self, current_number, images, remaining):
        if not self.clicked and not self.flagged:
            if current_number == 0:
                self.configure(image=images[10])
            elif 0 < current_number < 9:
                self.configure(image=images[current_number])
            elif current_number == 9:
                self.configure(image=images[11])
            if not self.flagged:
                self.configure(relief='sunken')
                self.clicked = True
            return remaining-1
        else:
            return remaining
