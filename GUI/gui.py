from Tkinter import *

__author__ = 'Colin Tan'
__version__ = 0.5


class MainMenu:
    "Menu of the program"
    def __init__(self, master):
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Hello!", command=App.say_hi)
        filemenu.add_command(label="Quit!", command=root.quit)
        filemenu.add_separator()
        menubar.add_cascade(label="File", menu=filemenu)
        master.config(menu=menubar)


class App:

    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

    def say_hi(self):
        print "Hi! This is a draft GUI!"

root = Tk()

app = App(root)
menu = MainMenu(root)

root.mainloop()
root.destroy()
