#!/usr/bin/env python

import Tkinter as tk
import tkFileDialog
import Tkconstants as Tkc
from Database import dbaccess as dba, dbcreate as dbc, dbupdate as dbu, dbapi
from Processor import processor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from Processor import mfn
# from matplotlib.figure import Figure
# matplotlib.use('TkAgg')

__author__ = 'Colin Tan'
__version__ = '1.0'


# message box displaying title and text with a close button
def msgWindow(title, text):
    top = tk.Toplevel()
    top.title(title)
    msg = tk.Message(top, text=text, width=300)
    msg.pack()
    button = tk.Button(top, text="Close", command=top.destroy)
    button.pack()


# main window
class MainApp:
    def __init__(self, master, title):
        self.sourcefile = None  # source data file path

        self.root = master
        self.root.title(title)

        frame = tk.Frame(root)
        frame.grid(row=1, columnspan=2)

        self.quit_button = tk.Button(
            frame, text="QUIT", fg="red", command=frame.quit)
        self.quit_button.grid(row=0, column=0)

        self.create_button = tk.Button(
            frame, text="Create new/erase existing database",
            command=self.createdb)
        self.create_button.grid(row=1)

        self.num_button = tk.Button(
            frame, text="Spectra in database", command=self.displaySpectraNum)
        self.num_button.grid(row=2)

        self.button_open = tk.Button(
            frame, text="Open...", command=self.openFile)
        self.button_open.grid(row=3)

        self.button_displayspec = tk.Button(
            frame, text="Display spectra", command=self.displaySpectrumFromID)
        self.button_displayspec.grid(row=4)

    def menu(self, master):
        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        # filemenu.add_command(label="Open...", command=self.askopenfilename)
        filemenu.add_command(label="Quit", command=root.quit)
        filemenu.add_separator()
        menubar.add_cascade(label="STMPLab", menu=filemenu)
        master.config(menu=menubar)

    def openFile(self):
        # open file window
        def askopenfilename():
            "Return the selected fileanme(s)"

            file_opt = options = {}
            options['defaultextension'] = '.*'
            # options['filetypes'] = [('csv files', '.csv')]
            options['initialdir'] = 'User\\'
            options['initialfile'] = ''
            options['parent'] = root
            options['title'] = 'choose file'
            options['multiple'] = 1

            # get filename
            filename = tkFileDialog.askopenfilename(**file_opt)

            if filename:
                self.sourcefile = filename
                if len(filename) is 1:
                    filepath_var.set(filename)
                else:
                    filepath_var.set(
                        "Multiple files, including {}".format(filename[0]))

        def insertSpectrum():
            doping = entry_doping.get()
            boxcar = entry_boxcar.get()
            delim = entry_delim.get()
            stdev = entry_stedv.get()
            gapmin = entry_gapmin.get()
            gapmax = entry_gapmax.get()
            if doping is "":
                insert_var.set("Please provide doping")
            elif boxcar is "":
                insert_var.set("Please provide boxcar width")
            elif delim is "":
                insert_var.set("Please proide CSV delimiter")
            elif stdev is "":
                insert_var.set("Please proide standard deviation multiple")
            elif gapmin is "":
                insert_var.set("Please proide minimum gap size")
            elif gapmax is "":
                insert_var.set("Please proide maximum gap size")
            elif self.sourcefile is None:
                insert_var.set("No file selected.")
            else:
                boxcar = int(boxcar)
                stdev = int(stdev)
                gapmin = float(gapmin)
                gapmax = float(gapmax)
                xs, yss = processor.readFile(self.sourcefile, delim)
                for ys in yss:
                    dbu.insertSpectrum(xs, ys, doping)

        # internal testing
        def showsourcefilename():
            print(self.sourcefile)

        top = tk.Toplevel()

        frame_entry = tk.Frame(top)
        frame_entry.grid(row=1, columnspan=2)

        label_doping = tk.Label(frame_entry, text="Doping")
        label_doping.grid(row=1, sticky=tk.E)

        entry_doping = tk.Entry(frame_entry)
        entry_doping.insert(0, "78K UD")
        entry_doping.grid(row=1, column=1)

        label_boxcar = tk.Label(frame_entry, text="Boxcar width")
        label_boxcar.grid(row=1, column=2, sticky=tk.E)

        entry_boxcar = tk.Entry(frame_entry)
        entry_boxcar.insert(0, "10")
        entry_boxcar.grid(row=1, column=3)

        label_delim = tk.Label(frame_entry, text="CSV delimiter")
        label_delim.grid(row=2, sticky=tk.E)

        entry_delim = tk.Entry(frame_entry)
        entry_delim.insert(0, ",")
        entry_delim.grid(row=2, column=1)

        label_stedv = tk.Label(frame_entry, text="Stdev multiple")
        label_stedv.grid(row=2, column=2, sticky=tk.E)

        entry_stedv = tk.Entry(frame_entry)
        entry_stedv.insert(0, "2")
        entry_stedv.grid(row=2, column=3)

        label_gapmin = tk.Label(frame_entry, text="Min gap size (V)")
        label_gapmin.grid(row=3, sticky=tk.E)

        entry_gapmin = tk.Entry(frame_entry)
        entry_gapmin.insert(0, "0.025")
        entry_gapmin.grid(row=3, column=1)

        label_gapmax = tk.Label(frame_entry, text="Max gap size (V)")
        label_gapmax.grid(row=3, column=2, sticky=tk.E)

        entry_gapmax = tk.Entry(frame_entry)
        entry_gapmax.insert(0, "0.425")
        entry_gapmax.grid(row=3, column=3)

        button_openfile = tk.Button(
            top, text="Open...", command=askopenfilename)
        button_openfile.grid(row=2)

        filepath_var = tk.StringVar()
        filepath_var.set("Please select file.")
        label_file = tk.Label(
            top, textvariable=filepath_var, justify=tk.CENTER)
        label_file.grid(row=2, column=1)

        button_insertspec = tk.Button(
            top, text="Insert spectra", command=insertSpectrum)
        button_insertspec.grid(row=3)

        insert_var = tk.StringVar()
        label_insert = tk.Label(
            top, textvariable=insert_var, justify=tk.CENTER)
        label_insert.grid(row=5, column=1)

        button_close = tk.Button(top, text="Close", command=top.destroy)
        button_close.grid(row=6, columnspan=2)

    def createdb(self):
        result = dbc.main
        msgWindow("Create database", result)

    def displaySpectraNum(self):
        num = dba.displaySpectraNum()
        text = "Number of spectra in the database is {}.".format(str(num))
        msgWindow("Number of spectra", text)

    def displaySpectrumFromID(self):
        class data():
            outdir = None  # output directory path
            xseries = yseries = None

        path_var = tk.StringVar()

        def export():
            top = tk.Toplevel()
            top.title("Export spectrum")
            button_dir = tk.Button(
                top, text="Choose path", command=askpath)
            button_dir.pack()
            path_var.set("Please select path")
            label_path = tk.Label(
                top, textvariable=path_var, justify=tk.CENTER)
            label_path.pack()
            button_exc = tk.Button(
                top, text="Export",
                command=lambda: exportSpec(
                    data.xseries, data.yseries, data.outdir))
            button_exc.pack()
            button_close = tk.Button(
                top, text="Close", command=top.destroy)
            button_close.pack()

        # open directory window
        def askpath():
            "Return the selected directory name"

            file_opt = options = {}
            options['initialdir'] = 'User\\'
            options['parent'] = root
            options['title'] = 'Choose directory'

            # get pathname
            pathname = tkFileDialog.asksaveasfilename(**file_opt)

            if pathname:
                data.outdir = pathname
                path_var.set(pathname)

        top = tk.Toplevel()
        top.title("Display spectrum")
        label = tk.Label(top, text="Enter spectrum ID")
        label.pack()
        entry = tk.Entry(top)
        entry.pack()

        fig = plt.figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=top)
        toolbar = NavigationToolbar2TkAgg(canvas, top)

        frame_button = tk.Frame(top)
        frame_button.pack()

        button_display = tk.Button(
            frame_button, text="Display",
            command=lambda: display(fig, ax, canvas, toolbar))
        button_display.pack(side=tk.LEFT)

        button_clear = tk.Button(
            frame_button, text="Clear",
            command=lambda: clearCanvas(canvas))
        button_clear.pack(side=tk.LEFT)

        button_close = tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=tk.LEFT)

        button_export = tk.Button(
            frame_button, text="Export...", command=export)
        button_export.pack(side=tk.LEFT)

        def exportSpec(xs, yss, path):
            if xs is None or yss is None or path is None:
                msgWindow("Error", "Something is missing")
            else:
                xs = mfn.transpose1d(xs)
                yss = mfn.transpose1d(yss)
                out = []
                for i in range(len(xs)):
                    out.append(xs[i] + yss[i])
                processor.csv_writer(out, path)

        def display(fig, ax, canvas, toolbar):
            id = entry.get()
            specData = dba.getSpectrumFromID(int(id))
            if specData is None:
                msgWindow(
                    "No spectrum found", "Spectrum of this ID is not found")
            else:
                data.xseries = dbapi.textToSeries(specData[1])
                data.yseries = dbapi.textToSeries(specData[2])

                # use '-o' for dots
                ax.plot(data.xseries, data.yseries, '-')
                canvas.show()
                canvas.get_tk_widget().pack(
                    side=Tkc.BOTTOM, fill=Tkc.BOTH, expand=1)

                toolbar.update()
                canvas._tkcanvas.pack(side=Tkc.TOP, fill=Tkc.BOTH, expand=1)

        def clearCanvas(canvas):
            plt.cla()
            canvas.show()


# depricated
class FileDialog(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)

        # button options
        button_opt = {'fill': Tkc.BOTH, 'padx': 5, 'pady': 5}

        # define buttons
        # tk.Button(self, text='Open File',
        #        command=self.askopenfile).pack(**button_opt)
        tk.Button(self, text='Open Filename',
                  command=self.askopenfilename).pack(**button_opt)
        # tk.Button(self, text='asksaveasfile',
        #        command=self.asksaveasfile).pack(**button_opt)
        # tk.Button(self, text='asksaveasfilename',
        #        command=self.asksaveasfilename).pack(**button_opt)
        # tk.Button(self, text='askdirectory',
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


# depricated
def openFileDiag():
    top = tk.Toplevel()
    top.title("Open File")
    FileDialog(top).pack()


# main entrance
def main():
    welcome = tk.Label(root, text="Welcome to STMPLab")
    welcome.grid(row=0, columnspan=2)

    mainApp = MainApp(root, 'STMPLab')
    mainApp.menu(root)

if __name__ == "__main__":
    root = tk.Tk()
    main()
    root.mainloop()
    root.destroy()
