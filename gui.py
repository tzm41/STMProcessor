from Tkinter import *
import tkFileDialog
import Tkconstants
from Database import dbaccess as dba
from Database import dbcreate as dbc

__author__ = 'Colin Tan'
__version__ = '0.6'


class MainApp:
    def __init__(self, master, title):

        self.sourcefile = None

        self.root = master
        self.root.title(title)

        frame = Frame(root)
        frame.grid(row=3, columnspan=2)

        label_doping = Label(root, text="Doping")
        label_doping.grid(row=1, sticky=E)
        self.entry_doping = Entry(root)
        self.entry_doping.insert(0, "78K UD")
        self.entry_doping.grid(row=1, column=1)
        # label_current = Label(root, text="Current")
        # label_current.grid(row=2, sticky=E)
        # entry_current = Entry(root)
        # entry_current.grid(row=2, column=1)

        self.quit_button = Button(
            frame, text="QUIT", fg="red", command=frame.quit)
        self.quit_button.grid(row=3, column=0)

        self.create_button = Button(
            frame, text="Create new database", command=self.createdb)
        self.create_button.grid(row=3, column=1)

        self.num_button = Button(
            frame, text="Spectra in database", command=self.displaySpectraNum)
        self.num_button.grid(row=3, column=2)

        self.button_openfile = Button(
            root, text="Open...", command=self.askopenfilename)
        self.button_openfile.grid(row=4, columnspan=2)

        self.button_insertspec = Button(
            root, text="Insert spectra", command=self.insertSpectrum)
        self.button_insertspec.grid(row=5, columnspan=2)

    def menu(self, master):
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open...", command=self.askopenfilename)
        filemenu.add_command(label="Quit", command=root.quit)
        filemenu.add_separator()
        menubar.add_cascade(label="STMPLab", menu=filemenu)
        master.config(menu=menubar)

    def createdb(self):
        print(dbc.main)

    def askopenfilename(self):
        """Returns an opened file in read mode.
        This time the dialog just returns a filename and the file
        is opened by your own code.
        """

        file_opt = options = {}
        options['defaultextension'] = '.*'
        # options['filetypes'] = [('all files', '.*'), ('csv files', '.csv')]
        options['initialdir'] = 'User\\'
        options['initialfile'] = ''
        options['parent'] = root
        options['title'] = 'Open file'
        options['multiple'] = 0

        # get filename
        filename = tkFileDialog.askopenfilename(**file_opt)

        # open file on your own
        if filename:
            self.sourcefile = filename

    def showsourcefilename(self):
        print(self.sourcefile)

    def displaySpectraNum(self):
        num = dba.displaySpectraNum()
        text = "Number of spectra in the database is {}.".format(str(num))
        top = Toplevel()
        top.title("Number of spectra")
        msg = Message(top, text=text, width=300)
        msg.pack()
        button = Button(top, text="Close", comman=top.destroy)
        button.pack()

    def insertSpectrum(self):
        doping = self.entry_doping.get()
        print doping


class FileDialog(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)

        # button options
        button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

        # define buttons
        # Button(self, text='Open File',
        #        command=self.askopenfile).pack(**button_opt)
        Button(self, text='Open Filename',
               command=self.askopenfilename).pack(**button_opt)
        # Button(self, text='asksaveasfile',
        #        command=self.asksaveasfile).pack(**button_opt)
        # Button(self, text='asksaveasfilename',
        #        command=self.asksaveasfilename).pack(**button_opt)
        # Button(self, text='askdirectory',
        #        command=self.askdirectory).pack(**button_opt)

        # define options for opening or saving a file
        self.file_opt = options = {}
        options['defaultextension'] = '.*'
        # options['filetypes'] = [('all files', '.*'), ('csv files', '.csv')]
        options['initialdir'] = 'User\\'
        options['initialfile'] = ''
        options['parent'] = root
        options['title'] = 'Open file'
        options['multiple'] = 0

    def askopenfile(self):
        "Returns an opened file in read mode."
        return tkFileDialog.askopenfile(mode='r', **self.file_opt)

    def askopenfilename(self):
        """Returns an opened file in read mode.
        This time the dialog just returns a filename and the file
        is opened by your own code.
        """

        # get filename
        filename = tkFileDialog.askopenfilename(**self.file_opt)

        # open file on your own
        if filename:
            print filename
            # return open(filename, 'r')

    def asksaveasfile(self):
        "Returns an opened file in write mode."
        return tkFileDialog.asksaveasfile(mode='w', **self.file_opt)

    def asksaveasfilename(self):
        """Returns an opened file in write mode.
        This time the dialog just returns a filename and the file
        is opened by your own code.
        """

        # get filename
        filename = tkFileDialog.asksaveasfilename(**self.file_opt)

        # open file on your own
        if filename:
            return open(filename, 'w')

    def askdirectory(self):
        "Returns a selected directory name."
        return tkFileDialog.askdirectory(**self.dir_opt)


def openFileDiag():
    top = Toplevel()
    top.title("Open File")
    FileDialog(top).pack()


def main():
    welcome = Label(root, text="Welcome to STMPLab")
    welcome.grid(row=0, columnspan=2)

    mainApp = MainApp(root, 'STMPLab')
    mainApp.menu(root)

if __name__ == "__main__":
    root = Tk()
    main()
    root.mainloop()
    root.destroy()
