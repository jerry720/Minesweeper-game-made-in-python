from tkinter import *


# creating a custom tkinter stopwatch widget
class Stopwatch(LabelFrame): # the Frame holds all the widgets of the stopwatch
    def __init__(self, master):
        super().__init__(master, relief=SUNKEN)
        self.root = master
        self.new_time = ''
        self.running = False
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.add_features()

    def add_features(self):
        # the self in the 1st argument of Label()
        # refers to the instance of the Stopwatch class
        # which inherits from LabelFrame
        # meaning that self can be used as a valid master
        self.stopwatch_label = Label(self, text='00:00:00', bg='black', fg='white', font=('arial', 24, 'bold'), bd=4)
        self.stopwatch_label.pack()
        '''
        s = Button(self, text='start', command=self.start)
        s.pack()
        r = Button(self, text='reset', command=self.reset)
        r.pack()
        '''

    def start(self): # starts the timer
        if not self.running:
            self.running = True
            self.after(1000)
            self.change()

    def pause(self):
        if self.running:
            self.running = False

    def reset(self):
        if self.running:
            self.running = False
        self.hours, self.minutes, self.seconds = 0, 0, 0
        self.stopwatch_label.configure(text='00:00:00')

    def change(self):
        # only increments time if running
        if self.running:
            self.seconds += 1
            if self.seconds == 59:
                self.minutes += 1
                self.seconds = 0
            if self.minutes == 59:
                self.hours += 1
                self.minutes = 0
            
            self.stopwatch_label.configure(text=f'{str(self.hours).zfill(2)}:{str(self.minutes).zfill(2)}:{str(self.seconds).zfill(2)}')
            self.new_time = self.stopwatch_label.after(1000, self.change)


##
##if __name__ == '__main__': # testing
##    root = Tk()
##    obj = Stopwatch(root)
##    obj.pack()
##    root.mainloop()
