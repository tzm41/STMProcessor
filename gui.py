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

__author__ = 'Colin Tan'
__version__ = '1.3'


# message box displaying title and text with a close button
def msgWindow(title, text):
    top = tk.Toplevel()
    top.title(title)
    msg = tk.Message(top, text=text, width=300)
    msg.pack()
    button = tk.Button(top, text="Close", command=top.destroy)
    button.pack()


def clearCanvas(canvas):
    plt.cla()
    canvas.show()


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

        self.button_rmvoutlier = tk.Button(
            frame, text="Remove outliers",
            command=self.rmvOutlier)
        self.button_rmvoutlier.grid(row=5)

        self.button_avespec = tk.Button(
            frame, text="Calculate average spectra",
            command=self.displayAveFromRange)
        self.button_avespec.grid(row=6)

        self.button_avespecfrombox = tk.Button(
            frame, text="Display average spectra of specific boxcar width",
            command=self.displayAveFromBoxcar)
        self.button_avespecfrombox.grid(row=7)

        self.button_gapfromid = tk.Button(
            frame, text="Get gap size from spectrum", command=self.showGapSize)
        self.button_gapfromid.grid(row=8)

    def menu(self, master):
        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open...", command=self.openFile)
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

        def insertSpectrum(top):
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
                insert_var.set("Please provide CSV delimiter")
            elif stdev is "":
                insert_var.set("Please provide standard deviation multiple")
            elif gapmin is "":
                insert_var.set("Please provide minimum gap size")
            elif gapmax is "":
                insert_var.set("Please provide maximum gap size")
            elif self.sourcefile is None:
                insert_var.set("No file selected.")
            else:
                boxcar = int(boxcar)
                stdev = int(stdev)
                gapmin = float(gapmin)
                gapmax = float(gapmax)
                xs, yss = processor.readFile(self.sourcefile, delim)
                # TODO: add exclusion feature
                exclusions, excluded = processor.elimStdev(xs, yss, 2)
                count = 0
                for ys in yss:
                    count += 1
                    dbu.insertSpectrum(xs, ys, doping)
                msgWindow(
                    "Done", "Successfully inserted {} spectra".format(count))
                top.destroy()

        # internal testing
        def showsourcefilename():
            print(self.sourcefile)

        # plain old process function
        def POPF():
            doping = entry_doping.get()
            boxcar = entry_boxcar.get()
            delim = entry_delim.get()
            stdev = entry_stedv.get()
            gapmin = entry_gapmin.get()
            gapmax = entry_gapmax.get()
            xstep = entry_xstep.get()
            if doping is "":
                insert_var.set("Please provide doping")
            elif boxcar is "":
                insert_var.set("Please provide boxcar width")
            elif delim is "":
                insert_var.set("Please provide CSV delimiter")
            elif stdev is "":
                insert_var.set("Please provide standard deviation multiple")
            elif gapmin is "":
                insert_var.set("Please provide minimum gap size")
            elif gapmax is "":
                insert_var.set("Please provide maximum gap size")
            elif xstep is "":
                insert_var.set("Please provide x step size")
            elif self.sourcefile is None:
                insert_var.set("No file selected.")
            else:
                boxcar = int(boxcar)
                stdev = int(stdev)
                gapmin = float(gapmin)
                gapmax = float(gapmax)
                xstep = float(xstep)
                xs, yss = processor.readFile(self.sourcefile, delim)
                exclusions, excluded = processor.elimStdev(xs, yss, 2)
                boxcared = processor.boxcar(yss, boxcar, exclusions)
                gap_stat, average_box = processor.groupAverage(
                    xs, boxcared, gapmin, gapmax, xstep)
                top = tk.Toplevel()
                top.title("Choose output path")
                label_path = tk.Label(top, text="Select path")
                label_path.grid(row=0)
                processor.csv_writer

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

        label_xstep = tk.Label(frame_entry, text="x-step (V)")
        label_xstep.grid(row=4, column=2, sticky=tk.E)

        entry_xstep = tk.Entry(frame_entry)
        entry_xstep.insert(0, "0.025")
        entry_xstep.grid(row=4, column=3)

        button_openfile = tk.Button(
            top, text="Open...", command=askopenfilename)
        button_openfile.grid(row=2)

        filepath_var = tk.StringVar()
        filepath_var.set("Please select file.")
        label_file = tk.Label(
            top, textvariable=filepath_var, justify=tk.CENTER)
        label_file.grid(row=2, column=1)

        button_insertspec = tk.Button(
            top, text="Insert spectra", command=lambda: insertSpectrum(top))
        button_insertspec.grid(row=3)

        insert_var = tk.StringVar()
        label_insert = tk.Label(
            top, textvariable=insert_var, justify=tk.CENTER)
        label_insert.grid(row=3, column=1)

        # plain old process function
        button_POPF = tk.Button(
            top, text="Plain old process function", command=POPF)
        button_POPF.grid(row=4, columnspan=2)

        button_close = tk.Button(top, text="Close", command=top.destroy)
        button_close.grid(row=5, columnspan=2)

    def createdb(self):
        dbc.main
        msgWindow("Create database", "Finished creating the database")

    def displaySpectraNum(self):
        num = dba.displaySpectraNum()
        text = "Number of spectra in the database is {}.".format(str(num))
        msgWindow("Number of spectra", text)

    def showGapSize(self):
        def getGapSize(specID):
            gap = dba.getGap(int(specID))
            msgWindow(
                "Gap size: spec {}".format(specID),
                "Gap size is {}".format(gap))

        top = tk.Toplevel()

        label = tk.Label(top, text="Choose from available spectra ID")
        label.grid(row=0, columnspan=2)

        frame = tk.Frame(top)
        frame.grid(row=1, columnspan=2)

        idList = dba.specWithGap()

        idList_options = [str(row) for row in idList]
        id_var = tk.StringVar()
        id_var.set(idList_options[0])

        option = apply(tk.OptionMenu, (frame, id_var) + tuple(idList_options))
        option.grid(row=1, columnspan=2)

        button = tk.Button(
            frame, text="Show", command=lambda: getGapSize(id_var.get()))
        button.grid(row=2)

        button_close = tk.Button(frame, text="Close", command=top.destroy)
        button_close.grid(row=2, column=1)

    def displayAveFromBoxcar(self):
        class data():
            xseries = []
            boxcar = 0

        top = tk.Toplevel()
        top.title("Display averge spectra")
        label = tk.Label(top, text="Enter boxcar width")
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

        def display(fig, ax, canvas, toolbar):
            data.boxcar = entry.get()
            if data.boxcar is "":
                msgWindow("Error", "Please provide boxcar width")
            else:
                specData = dba.getAveFromBoxcarWidth(int(data.boxcar))
                if specData is None:
                    msgWindow(
                        "No spectrum found",
                        "Average spectrum of this boxcar width is not found")
                else:
                    data.xseries = dbapi.textToSeries(specData[0][4])
                    yseries = []
                    for i in range(len(specData)):
                        yseries.append(dbapi.textToSeries(specData[i][5]))

                    if len(data.xseries) is not len(yseries[0]):
                        msgWindow("Error", "x and y have different dimension")

                    # use '-o' for dots
                    for ys in yseries:
                        ax.plot(data.xseries, ys, '-')
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=Tkc.BOTTOM, fill=Tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=Tkc.TOP, fill=Tkc.BOTH, expand=1)

    def displaySpectrumFromID(self):
        class data():
            outdir = None  # output directory path
            xseries = yseries = None
            specid = 0

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
                    data.xseries, data.yseries, data.outdir, top))
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
        top.title("Display spectra")
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

        button_gap = tk.Button(
            frame_button, text="Gap",
            command=lambda: showGap(ax, canvas, toolbar, data.specid))
        button_gap.pack(side=tk.LEFT)

        button_export = tk.Button(
            frame_button, text="Export...", command=export)
        button_export.pack(side=tk.LEFT)

        button_close = tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=tk.LEFT)

        def exportSpec(xs, yss, path, top):
            if xs is None or yss is None or path is None:
                msgWindow("Error", "Something is missing")
            else:
                xs = mfn.transpose1d(xs)
                yss = mfn.transpose1d(yss)
                out = []
                for i in range(len(xs)):
                    out.append(xs[i] + yss[i])
                processor.csv_writer(out, path)
            msgWindow("Success", "Successfully exported")
            top.destroy()

        def display(fig, ax, canvas, toolbar):
            data.specid = entry.get()
            if data.specid is "":
                msgWindow("Error", "Please provde ID")
            else:
                specData = dba.getSpectrumFromID(int(data.specid))
                if specData is None:
                    msgWindow(
                        "No spectrum found",
                        "Spectrum of this ID is not found")
                else:
                    data.xseries = dbapi.textToSeries(specData[1])
                    data.yseries = dbapi.textToSeries(specData[2])

                    # use '-o' for dots
                    ax.plot(data.xseries, data.yseries, '-')
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=Tkc.BOTTOM, fill=Tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=Tkc.TOP, fill=Tkc.BOTH, expand=1)

        def showGap(ax, canvas, toolbar, id):
            top = tk.Toplevel()

            frame_entry = tk.Frame(top)
            frame_entry.grid(row=1, columnspan=2)

            label_gapmin = tk.Label(frame_entry, text="Min gap size (V)")
            label_gapmin.grid(row=1, sticky=tk.E)

            entry_gapmin = tk.Entry(frame_entry)
            entry_gapmin.insert(0, "0.025")
            entry_gapmin.grid(row=1, column=1)

            label_gapmax = tk.Label(frame_entry, text="Max gap size (V)")
            label_gapmax.grid(row=1, column=2, sticky=tk.E)

            entry_gapmax = tk.Entry(frame_entry)
            entry_gapmax.insert(0, "0.425")
            entry_gapmax.grid(row=1, column=3)

            label_boxcar = tk.Label(frame_entry, text="Boxcar width")
            label_boxcar.grid(row=1, column=4, sticky=tk.E)

            entry_boxcar = tk.Entry(frame_entry)
            entry_boxcar.insert(0, "10")
            entry_boxcar.grid(row=1, column=5)

            button_go = tk.Button(
                top, text="Calculate",
                command=lambda: getGap(data.xseries, data.yseries, top))
            button_go.grid(row=2)

            button_close = tk.Button(top, text="Close", command=top.destroy)
            button_close.grid(row=2, column=1)

            def getGap(xs, yss, top):
                gapmin = float(entry_gapmin.get())
                gapmax = float(entry_gapmax.get())
                boxcar = int(entry_boxcar.get())
                if gapmin is "":
                    msgWindow("Error", "Please provide minimum gap size")
                elif gapmax is "":
                    msgWindow("Error", "Please provide maximum gap size")
                elif boxcar is "":
                    msgWindow("Error", "Please provide boxcar width")
                else:
                    gapSize = mfn.poly_gap(
                        xs[0:20], yss[0:20], gapmin, gapmax).real
                    ax.axvline(gapSize)
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=Tkc.BOTTOM, fill=Tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=Tkc.TOP, fill=Tkc.BOTH, expand=1)
                dbu.insertGap(data.specid, gapSize, boxcar)
                msgWindow(
                    "Done",
                    "Gap size is {}, saved into database.".format(gapSize))

    def displayAveFromRange(self):
        class data():
            outdir = None  # output directory path
            xseries = []
            yave = []
            specidl = 0
            specidh = 0
            numAved = 0

        path_var = tk.StringVar()

        def export():
            top = tk.Toplevel()
            top.title("Export average spectrum")
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
                    data.xseries, data.yave, data.outdir, top))
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

        def dbInsert(xs, ys, numAve):
            if xs is None or ys is None:
                msgWindow("Error", "Spectrum does not exist")
            elif min is None or max is None:
                msgWindow("Error", "Gap range does not exist")
            else:
                aveID = dbu.insertAveSpectrum(xs, ys, 0, 0, numAve)
                for i in range(int(data.specidl), int(data.specidh) + 1):
                    dbu.insertSpecAvePair(i, aveID)
                msgWindow("Success", "Average spectra inserted into database")

        top = tk.Toplevel()
        top.title("Display averge spectra")
        label = tk.Label(top, text="Enter spectrum ID range")
        label.pack()
        entryl = tk.Entry(top)
        entryl.pack()
        entryh = tk.Entry(top)
        entryh.pack()

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

        button_gap = tk.Button(
            frame_button, text="Gap",
            command=lambda: showGap(ax, canvas, toolbar))
        button_gap.pack(side=tk.LEFT)

        button_export = tk.Button(
            frame_button, text="Export...", command=export)
        button_export.pack(side=tk.LEFT)

        button_db = tk.Button(
            frame_button, text="Add to DB",
            command=lambda: dbInsert(data.xseries, data.yave, data.numAved))
        button_db.pack(side=tk.LEFT)

        button_close = tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=tk.LEFT)

        def exportSpec(xs, yss, path, top):
            if xs is None or yss is None or path is None:
                msgWindow("Error", "Something is missing")
            else:
                xs = mfn.transpose1d(xs)
                yss = mfn.transpose1d(yss)
                out = []
                for i in range(len(xs)):
                    out.append(xs[i] + yss[i])
                processor.csv_writer(out, path)
            msgWindow("Success", "Successfully exported")
            top.destroy()

        def display(fig, ax, canvas, toolbar):
            data.specidl = entryl.get()
            data.specidh = entryh.get()
            if data.specidl is "":
                msgWindow("Error", "Please provide min ID")
            elif data.specidh is "":
                msgWindow("Error", "Please provide max ID")
            elif int(data.specidl) > int(data.specidh):
                msgWindow("Error", "Lower bound > upper bound")
            else:
                specData = dba.getSpectrumFromRange(
                    int(data.specidl), int(data.specidh))
                data.numAved = int(data.specidh) - int(data.specidl) + 1
                if specData is None:
                    msgWindow(
                        "No spectrum found",
                        "Spectrum of this ID is not found")
                else:
                    data.xseries = dbapi.textToSeries(specData[0][1])
                    yseries, data.yave = [], []
                    for i in range(len(specData)):
                        yseries.append(dbapi.textToSeries(specData[i][2]))
                    for x in range(len(data.xseries)):
                        data.yave.append(mfn.mean([col[x] for col in yseries]))

                    if len(data.xseries) is not len(data.yave):
                        msgWindow("Error", "x and y have different dimension")

                    # use '-o' for dots
                    ax.plot(data.xseries, data.yave, '-')
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=Tkc.BOTTOM, fill=Tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=Tkc.TOP, fill=Tkc.BOTH, expand=1)

        def showGap(ax, canvas, toolbar):
            top = tk.Toplevel()

            frame_entry = tk.Frame(top)
            frame_entry.grid(row=1, columnspan=2)

            label_gapmin = tk.Label(frame_entry, text="Min gap size (V)")
            label_gapmin.grid(row=1, sticky=tk.E)

            entry_gapmin = tk.Entry(frame_entry)
            entry_gapmin.insert(0, "0.025")
            entry_gapmin.grid(row=1, column=1)

            label_gapmax = tk.Label(frame_entry, text="Max gap size (V)")
            label_gapmax.grid(row=1, column=2, sticky=tk.E)

            entry_gapmax = tk.Entry(frame_entry)
            entry_gapmax.insert(0, "0.425")
            entry_gapmax.grid(row=1, column=3)

            label_boxcar = tk.Label(frame_entry, text="Boxcar width")
            label_boxcar.grid(row=1, column=4, sticky=tk.E)

            entry_boxcar = tk.Entry(frame_entry)
            entry_boxcar.insert(0, "10")
            entry_boxcar.grid(row=1, column=5)

            button_go = tk.Button(
                top, text="Calculate",
                command=lambda: getGap(data.xseries, data.yave, top))
            button_go.grid(row=2)

            button_close = tk.Button(top, text="Close", command=top.destroy)
            button_close.grid(row=2, column=1)

            def getGap(xs, yss, top):
                gapmin = float(entry_gapmin.get())
                gapmax = float(entry_gapmax.get())
                if gapmin is "":
                    msgWindow("Error", "Please provide minimum gap size")
                elif gapmax is "":
                    msgWindow("Error", "Please provide maximum gap size")
                else:
                    gapSize = mfn.poly_gap(
                        xs[0:20], yss[0:20], gapmin, gapmax).real
                    ax.axvline(gapSize)
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=Tkc.BOTTOM, fill=Tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=Tkc.TOP, fill=Tkc.BOTH, expand=1)
                msgWindow(
                    "Done",
                    "Gap size is {}".format(gapSize))

    def rmvOutlier(self):
        class data():
            outdir = None  # output directory path
            xseries = []
            yave = []
            specidl = 0
            specidh = 0
            numAved = 0

        def dbInsert(xs, ys, numAve):
            if xs is None or ys is None:
                msgWindow("Error", "Spectrum does not exist")
            elif min is None or max is None:
                msgWindow("Error", "Gap range does not exist")
            else:
                aveID = dbu.insertAveSpectrum(xs, ys, 0, 0, numAve)
                for i in range(int(data.specidl), int(data.specidh) + 1):
                    dbu.insertSpecAvePair(i, aveID)
                msgWindow("Success", "Average spectra inserted into database")

        top = tk.Toplevel()
        top.title("Display averge spectra")
        label = tk.Label(top, text="Enter spectrum ID range")
        label.pack()
        entryl = tk.Entry(top)
        entryl.pack()
        entryh = tk.Entry(top)
        entryh.pack()
        label_stdev = tk.Label(top, text="Enter standard deviation multiple")
        label_stdev.pack()
        entry = tk.Entry(top)
        entry.insert(0, "2")
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

        button_db = tk.Button(
            frame_button, text="Add to DB",
            command=lambda: dbInsert(data.xseries, data.yave, data.numAved))
        button_db.pack(side=tk.LEFT)

        button_close = tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=tk.LEFT)

        def display(fig, ax, canvas, toolbar):
            data.specidl = entryl.get()
            data.specidh = entryh.get()
            if data.specidl is "":
                msgWindow("Error", "Please provide min ID")
            elif data.specidh is "":
                msgWindow("Error", "Please provide max ID")
            elif int(data.specidl) > int(data.specidh):
                msgWindow("Error", "Lower bound > upper bound")
            else:
                specData = dba.getSpectrumFromRange(
                    int(data.specidl), int(data.specidh))
                data.numAved = int(data.specidh) - int(data.specidl) + 1
                if specData is None:
                    msgWindow(
                        "No spectrum found",
                        "Spectrum of this ID is not found")
                else:
                    data.xseries = dbapi.textToSeries(specData[0][1])
                    yseries, data.yave = [], []
                    for i in range(len(specData)):
                        yseries.append(dbapi.textToSeries(specData[i][2]))
                    for x in range(len(data.xseries)):
                        data.yave.append(mfn.mean([col[x] for col in yseries]))

                    if len(data.xseries) is not len(data.yave):
                        msgWindow("Error", "x and y have different dimension")

                    # use '-o' for dots
                    ax.plot(data.xseries, data.yave, '-')
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=Tkc.BOTTOM, fill=Tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=Tkc.TOP, fill=Tkc.BOTH, expand=1)


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
