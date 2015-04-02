from Tkinter import *

__author__ = 'Colin Tan'
__version__ = '0.6'


class App:
    def __init__(self, master, title):

        self.root = master
        self.root.title(title)

        frame = Frame(master)
        frame.pack()

        self.quit_button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.quit_button.pack(side=LEFT)

        self.import_button = Button(frame, text="Import", command=frame.quit)
        self.import_button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

    def menu(self, master):
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Hello!", command=self.say_hi)
        filemenu.add_command(label="Quit!", command=root.quit)
        filemenu.add_separator()
        menubar.add_cascade(label="STMPLab", menu=filemenu)
        master.config(menu=menubar)

    def say_hi(self):
        print "Hi! This is a draft GUI!"

root = Tk()
app = App(root, 'STMPLab')
menu = app.menu(root)

root.mainloop()
root.destroy()
