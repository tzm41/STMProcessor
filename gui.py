from Tkinter import *
import tkFileDialog
from Database import dbaccess as dba
from Database import dbcreate as dbc

__author__ = 'Colin Tan'
__version__ = '0.6'


class AccessApp:
    def __init__(self, master, title):

        self.root = master
        self.root.title(title)

        frame = Frame(root)
        frame.grid(row=3, columnspan=2)

        self.quit_button = Button(
            frame, text="QUIT", fg="red", command=frame.quit)
        self.quit_button.grid(row=0, column=0)

        self.create_button = Button(
            frame, text="Create new database", command=self.createdb)
        self.create_button.grid(row=0, column=1)

        self.num_button = Button(
            frame, text="Spectra in database", command=self.displaySpectraNum)
        self.num_button.grid(row=0, column=2)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.grid(row=0, column=3)

    def menu(self, master):
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Hello!", command=self.say_hi)
        filemenu.add_command(label="Quit!", command=root.quit)
        filemenu.add_separator()
        menubar.add_cascade(label="STMPLab", menu=filemenu)
        master.config(menu=menubar)

    def createdb(self):
        print(dbc.main)

    def say_hi(self):
        print("Hi! This is a draft GUI!")

    def displaySpectraNum(self):
        num = dba.displaySpectraNum()
        text = "Number of spectra in the database is {}.".format(str(num))
        top = Toplevel()
        top.title("Number of spectra")
        msg = Message(top, text=text, width=300)
        msg.pack()
        button = Button(top, text="Close", comman=top.destroy)
        button.pack()


def main():
    root = Tk()

    welcome = Label(root, text="Welcome to STMPLab")
    welcome.grid(row=0, columnspan=2)

    label_doping = Label(root, text="Doping")
    label_doping.grid(row=1, sticky=E)
    entry_doping = Entry(root)
    entry_doping.grid(row=1, column=1)
    label_current = Label(root, text="Current")
    label_current.grid(row=2, sticky=E)
    entry_current = Entry(root)
    entry_current.grid(row=2, column=1)

    accessApp = AccessApp(root, 'STMPLab')
    menu = accessApp.menu(root)

    root.mainloop()
    root.destroy()

if __name__ == "__main__":
    main()
