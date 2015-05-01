from Tkinter import *
import tkFileDialog
import Tkconstants as Tkc
from Database import dbaccess as dba
from Database import dbcreate as dbc
from Database import dbapi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
# matplotlib.use('TkAgg')

__author__ = 'Colin Tan'
__version__ = '0.6'


# message box displaying title and text with a close button
def msgWindow(title, text):
    top = Toplevel()
    top.title(title)
    msg = Message(top, text=text, width=300)
    msg.pack()
    button = Button(top, text="Close", command=top.destroy)
    button.pack()


class MainApp:
    def __init__(self, master, title):
        self.sourcefile = None

        self.root = master
        self.root.title(title)

        frame = Frame(root)
        frame.grid(row=1, columnspan=2)

        self.quit_button = Button(
            frame, text="QUIT", fg="red", command=frame.quit)
        self.quit_button.grid(row=0, column=0)

        self.create_button = Button(
            frame, text="Create new/erase existing database",
            command=self.createdb)
        self.create_button.grid(row=1)

        self.num_button = Button(
            frame, text="Spectra in database", command=self.displaySpectraNum)
        self.num_button.grid(row=2)

        self.button_open = Button(
            frame, text="Open...", command=self.openFile)
        self.button_open.grid(row=3)

        self.button_displayspec = Button(
            frame, text="Display spectra", command=self.displaySpectrumFromID)
        self.button_displayspec.grid(row=4)

    def menu(self, master):
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        # filemenu.add_command(label="Open...", command=self.askopenfilename)
        filemenu.add_command(label="Quit", command=root.quit)
        filemenu.add_separator()
        menubar.add_cascade(label="STMPLab", menu=filemenu)
        master.config(menu=menubar)

    def openFile(self):
        def askopenfilename():
            """Returns an opened file in read mode.
            This time the dialog just returns a filename and the file
            is opened by your own code.
            """

            file_opt = options = {}
            options['defaultextension'] = '.*'
            # options['filetypes'] = [('csv files', '.csv')]
            options['initialdir'] = 'User\\'
            options['initialfile'] = ''
            options['parent'] = root
            options['title'] = 'Open file'
            options['multiple'] = 0

            # get filename
            filename = tkFileDialog.askopenfilename(**file_opt)

            if filename:
                self.sourcefile = filename
                filepath_var.set(filename)

        def insertSpectrum():
            doping = entry_doping.get()
            boxcar = entry_boxcar.get()
            if doping is "":
                insert_var.set("Please provide doping.")
            elif boxcar is "":
                insert_var.set("Please provide boxcar width.")
            elif self.sourcefile is None:
                insert_var.set("No file selected.")
            else:
                boxcar = int(boxcar)
                print "x"

        def showsourcefilename():
            print(self.sourcefile)

        top = Toplevel()

        frame_entry = Frame(top)
        frame_entry.grid(row=1, columnspan=2)

        label_doping = Label(frame_entry, text="Doping")
        label_doping.grid(row=1, sticky=E)

        entry_doping = Entry(frame_entry)
        entry_doping.insert(0, "78K UD")
        entry_doping.grid(row=1, column=1)

        label_boxcar = Label(frame_entry, text="Boxcar width")
        label_boxcar.grid(row=2, sticky=E)

        entry_boxcar = Entry(frame_entry)
        entry_boxcar.insert(0, "10")
        entry_boxcar.grid(row=2, column=1)

        label_delim = Label(frame_entry, text="CSV delimiter")
        label_delim.grid(row=3, sticky=E)

        entry_delim = Entry(frame_entry)
        entry_delim.insert(0, ",")
        entry_delim.grid(row=3, column=1)

        button_openfile = Button(
            top, text="Open...", command=askopenfilename)
        button_openfile.grid(row=4)

        filepath_var = StringVar()
        filepath_var.set("Please select file.")
        label_file = Label(
            top, textvariable=filepath_var, justify=CENTER)
        label_file.grid(row=4, column=1)

        button_insertspec = Button(
            top, text="Insert spectra", command=insertSpectrum)
        button_insertspec.grid(row=5)

        insert_var = StringVar()
        label_insert = Label(
            top, textvariable=insert_var, justify=CENTER)
        label_insert.grid(row=5, column=1)

        button_close = Button(top, text="Close", command=top.destroy)
        button_close.grid(row=6, columnspan=2)

    def createdb(self):
        result = dbc.main
        msgWindow("Create database", result)

    def displaySpectraNum(self):
        num = dba.displaySpectraNum()
        text = "Number of spectra in the database is {}.".format(str(num))
        msgWindow("Number of spectra", text)

    def displaySpectrumFromID(self):
        top = Toplevel()
        top.title("Display spectrum")
        label = Label(top, text="Enter spectrum ID")
        label.pack()
        entry = Entry(top)
        entry.pack()

        fig = plt.figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=top)
        toolbar = NavigationToolbar2TkAgg(canvas, top)

        frame_button = Frame(top)
        frame_button.pack()

        button_display = Button(
            frame_button, text="Display",
            command=lambda: display(fig, ax, canvas, toolbar))
        button_display.pack(side=LEFT)

        button_clear = Button(
            frame_button, text="Clear",
            command=lambda: clearCanvas(canvas))
        button_clear.pack(side=LEFT)

        button_close = Button(frame_button, text="Close", command=top.destroy)
        button_close.pack(side=LEFT)

        def display(fig, ax, canvas, toolbar):
            id = entry.get()
            specData = dba.getSpectrumFromID(int(id))
            if specData is None:
                msgWindow(
                    "No spectrum found", "Spectra of this ID is not found")
            else:
                xseries = dbapi.textToSeries(specData[1])
                yseries = dbapi.textToSeries(specData[2])

                ax.plot(xseries, yseries, '-o')
                canvas.show()
                canvas.get_tk_widget().pack(
                    side=Tkc.BOTTOM, fill=Tkc.BOTH, expand=1)

                toolbar.update()
                canvas._tkcanvas.pack(side=Tkc.TOP, fill=Tkc.BOTH, expand=1)

        def clearCanvas(canvas):
            plt.cla()


class FileDialog(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)

        # button options
        button_opt = {'fill': Tkc.BOTH, 'padx': 5, 'pady': 5}

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
