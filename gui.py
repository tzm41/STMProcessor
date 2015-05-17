#!/usr/bin/env python

import Tkinter as Tk
import tkFileDialog
import Tkconstants as Tkc
from Database import dbaccess as dba, dbcreate as dbc, dbupdate as dbu, dbapi
from Processor import processor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from Processor import mfn
from threading import Thread
import logging

__author__ = 'Colin Tan'
__version__ = '2.0'

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s')


# message box displaying title and text with a close button
def msg_window(title, text):
    top = Tk.Toplevel()
    top.title(title)
    msg = Tk.Message(top, text=text, width=300)
    msg.pack()
    button = Tk.Button(top, text="Close", command=top.destroy)
    button.pack()


def clear_canvas(canvas):
    plt.cla()
    canvas.show()


# main window
class MainApp:
    def __init__(self, master, title):
        self.sourcefile = None  # source data file path

        self.root = master
        self.root.title(title)

        frame = Tk.Frame(root)
        frame.grid(row=1, columnspan=2)

        self.quit_button = Tk.Button(
            frame, text="QUIT", fg="red", command=frame.quit)
        self.quit_button.grid(row=0, column=0)

        self.create_button = Tk.Button(
            frame, text="Create new/erase existing database",
            command=self.createdb)
        self.create_button.grid(row=1)

        self.num_button = Tk.Button(
            frame, text="Spectra in database", command=self.displaySpectraNum)
        self.num_button.grid(row=2)

        self.button_open = Tk.Button(
            frame, text="Open...", command=self.open_file)
        self.button_open.grid(row=3)

        self.button_display_spec = Tk.Button(
            frame, text="Display spectra", command=self.displaySpectrumFromID)
        self.button_display_spec.grid(row=4)

        self.button_rm_outlier = Tk.Button(
            frame, text="Remove outliers",
            command=self.rmvOutlier)
        self.button_rm_outlier.grid(row=5)

        self.button_ave_spec = Tk.Button(
            frame, text="Calculate average spectra",
            command=self.displayAveFromRange)
        self.button_ave_spec.grid(row=6)

        self.button_ave_spec_from_box = Tk.Button(
            frame, text="Display average spectra of specific boxcar width",
            command=self.displayAveFromBoxcar)
        self.button_ave_spec_from_box.grid(row=7)

        self.button_gap_from_id = Tk.Button(
            frame, text="Get gap size from spectrum", command=self.showGapSize)
        self.button_gap_from_id.grid(row=8)

    def menu(self, master):
        menu_bar = Tk.Menu(master)
        file_menu = Tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Quit", command=root.quit)
        file_menu.add_separator()
        menu_bar.add_cascade(label="STMPLab", menu=file_menu)
        master.config(menu=menu_bar)

    def open_file(self):
        # open file window
        def askopenfilename():
            """Return the selected file name(s)"""

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

        def insert_spectrum(top):
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
                msg_window(
                    "Done", "Successfully inserted {} spectra".format(count))
                top.destroy()

        # internal testing
        def showsourcefilename():
            print(self.sourcefile)

        # plain old process function
        def POPF():
            class Data():
                out_dir = None
                gap_stat, average_box = [], []

            path_var = Tk.StringVar()
            status_var.set("Processing... Please wait.")

            def askpath():
                """Return the selected directory name"""

                file_opt = options = {}
                options['initialdir'] = 'User\\'
                options['parent'] = root
                options['title'] = 'Choose directory'

                # get pathname
                pathname = tkFileDialog.askdirectory(**file_opt)

                if pathname:
                    Data.out_dir = pathname
                    path_var.set(pathname)

            def process():
                exclusions, excluded = processor.elimStdev(xs, yss, stdev)
                boxcared = processor.boxcar(yss, boxcar, exclusions)
                Data.gap_stat, Data.average_box = processor.groupAverage(
                    xs, boxcared, gapmin, gapmax, xstep)

            def output():
                processor.csv_writer(
                    Data.gap_stat, "{}/gap.csv".format(Data.out_dir))
                logging.debug("Gap output path" + "{}/gap.csv".format(Data.out_dir))
                processor.csv_writer(
                    Data.average_box, "{}/ave.csv".format(Data.out_dir))
                top_top.destroy()

            boxcar = entry_boxcar.get()
            delim = entry_delim.get()
            stdev = entry_stedv.get()
            gapmin = entry_gapmin.get()
            gapmax = entry_gapmax.get()
            xstep = entry_xstep.get()
            if boxcar is "":
                status_var.set("Please provide boxcar width")
            elif delim is "":
                status_var.set("Please provide CSV delimiter")
            elif stdev is "":
                status_var.set("Please provide standard deviation multiple")
            elif gapmin is "":
                status_var.set("Please provide minimum gap size")
            elif gapmax is "":
                status_var.set("Please provide maximum gap size")
            elif xstep is "":
                status_var.set("Please provide x step size")
            elif self.sourcefile is None:
                status_var.set("No file selected.")
            else:
                boxcar = int(boxcar)
                stdev = int(stdev)
                gapmin = float(gapmin)
                gapmax = float(gapmax)
                xstep = float(xstep)
                try:
                    xs, yss = processor.readFile(self.sourcefile, delim)
                except ValueError:
                    if delim is ",":
                        status_var.set("Error, wrong csv delimiter. Try semicolon.")
                    elif delim is ";":
                        status_var.set("Error, wrong csv delimiter. Try comma.")
                    else:
                        status_var.set("Error, wrong csv delimiter.")
                else:
                    thread = Thread(target=process)
                    thread.start()
                    thread.join()

                    logging.debug("Finished processing.")

                    status_var.set("Done.")

                    top_top = Tk.Toplevel()
                    top_top.title("Choose output path")

                    button_path = Tk.Button(top_top, text="Select path", command=askpath)
                    button_path.grid(row=1)

                    path_var = Tk.StringVar()
                    path_var.set("Please select output path.")

                    label_path = Tk.Label(
                        top_top, textvariable=path_var, justify=Tk.CENTER)
                    label_path.grid(row=1, column=1)

                    button_export = Tk.Button(
                        top_top, text="Export", command=output)
                    button_export.grid(row=2, columnspan=2)

        top = Tk.Toplevel()

        frame_entry = Tk.Frame(top)
        frame_entry.grid(row=1, columnspan=2)

        label_doping = Tk.Label(frame_entry, text="Doping")
        label_doping.grid(row=1, sticky=Tk.E)

        entry_doping = Tk.Entry(frame_entry)
        entry_doping.insert(0, "78K UD")
        entry_doping.grid(row=1, column=1)

        label_boxcar = Tk.Label(frame_entry, text="Boxcar width")
        label_boxcar.grid(row=1, column=2, sticky=Tk.E)

        entry_boxcar = Tk.Entry(frame_entry)
        entry_boxcar.insert(0, "10")
        entry_boxcar.grid(row=1, column=3)

        label_delim = Tk.Label(frame_entry, text="CSV delimiter")
        label_delim.grid(row=2, sticky=Tk.E)

        entry_delim = Tk.Entry(frame_entry)
        entry_delim.insert(0, ",")
        entry_delim.grid(row=2, column=1)

        label_stedv = Tk.Label(frame_entry, text="Stdev multiple")
        label_stedv.grid(row=2, column=2, sticky=Tk.E)

        entry_stedv = Tk.Entry(frame_entry)
        entry_stedv.insert(0, "2")
        entry_stedv.grid(row=2, column=3)

        label_gapmin = Tk.Label(frame_entry, text="Min gap size (V)")
        label_gapmin.grid(row=3, sticky=Tk.E)

        entry_gapmin = Tk.Entry(frame_entry)
        entry_gapmin.insert(0, "0.025")
        entry_gapmin.grid(row=3, column=1)

        label_gapmax = Tk.Label(frame_entry, text="Max gap size (V)")
        label_gapmax.grid(row=3, column=2, sticky=Tk.E)

        entry_gapmax = Tk.Entry(frame_entry)
        entry_gapmax.insert(0, "0.425")
        entry_gapmax.grid(row=3, column=3)

        label_xstep = Tk.Label(frame_entry, text="x-step (V)")
        label_xstep.grid(row=4, column=2, sticky=Tk.E)

        entry_xstep = Tk.Entry(frame_entry)
        entry_xstep.insert(0, "0.025")
        entry_xstep.grid(row=4, column=3)

        button_openfile = Tk.Button(
            top, text="Open...", command=askopenfilename)
        button_openfile.grid(row=2)

        filepath_var = Tk.StringVar()
        filepath_var.set("Please select file.")
        label_file = Tk.Label(
            top, textvariable=filepath_var, justify=Tk.CENTER)
        label_file.grid(row=2, column=1)

        button_insertspec = Tk.Button(
            top, text="Insert spectra", command=lambda: insert_spectrum(top))
        button_insertspec.grid(row=3)

        insert_var = Tk.StringVar()
        label_insert = Tk.Label(
            top, textvariable=insert_var, justify=Tk.CENTER)
        label_insert.grid(row=3, column=1)

        # plain old process function
        button_POPF = Tk.Button(
            top, text="Plain old process function", command=POPF)
        button_POPF.grid(row=4)

        status_var = Tk.StringVar()

        label_POPF = Tk.Label(top, textvariable=status_var, justify=Tk.CENTER)
        label_POPF.grid(row=4, column=1)

        button_close = Tk.Button(top, text="Close", command=top.destroy)
        button_close.grid(row=5, columnspan=2)

    def createdb(self):
        dbc.main
        logging.debug("Finished creating database")
        msg_window("Create database", "Finished creating the database")

    def displaySpectraNum(self):
        num = dba.displaySpectraNum()
        text = "Number of spectra in the database is {}.".format(str(num))
        msg_window("Number of spectra", text)

    def showGapSize(self):
        def getGapSize(specID):
            gap = dba.getGap(int(specID))
            msg_window(
                "Gap size: spec {}".format(specID),
                "Gap size is {}".format(gap))

        top = Tk.Toplevel()

        label = Tk.Label(top, text="Choose from available spectra ID")
        label.grid(row=0, columnspan=2)

        frame = Tk.Frame(top)
        frame.grid(row=1, columnspan=2)

        idList = dba.specWithGap()

        idList_options = [str(row) for row in idList]
        id_var = Tk.StringVar()
        id_var.set(idList_options[0])

        option = apply(Tk.OptionMenu, (frame, id_var) + tuple(idList_options))
        option.grid(row=1, columnspan=2)

        button = Tk.Button(
            frame, text="Show", command=lambda: getGapSize(id_var.get()))
        button.grid(row=2)

        button_close = Tk.Button(frame, text="Close", command=top.destroy)
        button_close.grid(row=2, column=1)

    def displayAveFromBoxcar(self):
        class Data():
            xseries = []
            boxcar = 0

        top = Tk.Toplevel()
        top.title("Display averge spectra")
        label = Tk.Label(top, text="Enter boxcar width")
        label.pack()
        entry = Tk.Entry(top)
        entry.pack()

        fig = plt.figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=top)
        toolbar = NavigationToolbar2TkAgg(canvas, top)

        frame_button = Tk.Frame(top)
        frame_button.pack()

        button_display = Tk.Button(
            frame_button, text="Display",
            command=lambda: display(fig, ax, canvas, toolbar))
        button_display.pack(side=Tk.LEFT)

        button_clear = Tk.Button(
            frame_button, text="Clear",
            command=lambda: clear_canvas(canvas))
        button_clear.pack(side=Tk.LEFT)

        button_close = Tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=Tk.LEFT)

        def display(fig, ax, canvas, toolbar):
            Data.boxcar = entry.get()
            if Data.boxcar is "":
                msg_window("Error", "Please provide boxcar width")
            else:
                specData = dba.getAveFromBoxcarWidth(int(Data.boxcar))
                if specData is None:
                    msg_window(
                        "No spectrum found",
                        "Average spectrum of this boxcar width is not found")
                else:
                    Data.xseries = dbapi.textToSeries(specData[0][4])
                    yseries = []
                    for i in range(len(specData)):
                        yseries.append(dbapi.textToSeries(specData[i][5]))

                    if len(Data.xseries) is not len(yseries[0]):
                        msg_window("Error", "x and y have different dimension")

                    # use '-o' for dots
                    for ys in yseries:
                        ax.plot(Data.xseries, ys, '-')
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

        path_var = Tk.StringVar()

        def export():
            top = Tk.Toplevel()
            top.title("Export spectrum")
            button_dir = Tk.Button(
                top, text="Choose path", command=askpath)
            button_dir.pack()
            path_var.set("Please select path")
            label_path = Tk.Label(
                top, textvariable=path_var, justify=Tk.CENTER)
            label_path.pack()
            button_exc = Tk.Button(
                top, text="Export",
                command=lambda: exportSpec(
                    data.xseries, data.yseries, data.outdir, top))
            button_exc.pack()
            button_close = Tk.Button(
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

        top = Tk.Toplevel()
        top.title("Display spectra")
        label = Tk.Label(top, text="Enter spectrum ID")
        label.pack()
        entry = Tk.Entry(top)
        entry.pack()

        fig = plt.figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=top)
        toolbar = NavigationToolbar2TkAgg(canvas, top)

        frame_button = Tk.Frame(top)
        frame_button.pack()

        button_display = Tk.Button(
            frame_button, text="Display",
            command=lambda: display(fig, ax, canvas, toolbar))
        button_display.pack(side=Tk.LEFT)

        button_clear = Tk.Button(
            frame_button, text="Clear",
            command=lambda: clear_canvas(canvas))
        button_clear.pack(side=Tk.LEFT)

        button_gap = Tk.Button(
            frame_button, text="Gap",
            command=lambda: showGap(ax, canvas, toolbar, data.specid))
        button_gap.pack(side=Tk.LEFT)

        button_export = Tk.Button(
            frame_button, text="Export...", command=export)
        button_export.pack(side=Tk.LEFT)

        button_close = Tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=Tk.LEFT)

        def exportSpec(xs, yss, path, top):
            if xs is None or yss is None or path is None:
                msg_window("Error", "Something is missing")
            else:
                xs = mfn.transpose1d(xs)
                yss = mfn.transpose1d(yss)
                out = []
                for i in range(len(xs)):
                    out.append(xs[i] + yss[i])
                processor.csv_writer(out, path)
            msg_window("Success", "Successfully exported")
            top.destroy()

        def display(fig, ax, canvas, toolbar):
            data.specid = entry.get()
            if data.specid is "":
                msg_window("Error", "Please provde ID")
            else:
                specData = dba.getSpectrumFromID(int(data.specid))
                if specData is None:
                    msg_window(
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
            top = Tk.Toplevel()

            frame_entry = Tk.Frame(top)
            frame_entry.grid(row=1, columnspan=2)

            label_gapmin = Tk.Label(frame_entry, text="Min gap size (V)")
            label_gapmin.grid(row=1, sticky=Tk.E)

            entry_gapmin = Tk.Entry(frame_entry)
            entry_gapmin.insert(0, "0.025")
            entry_gapmin.grid(row=1, column=1)

            label_gapmax = Tk.Label(frame_entry, text="Max gap size (V)")
            label_gapmax.grid(row=1, column=2, sticky=Tk.E)

            entry_gapmax = Tk.Entry(frame_entry)
            entry_gapmax.insert(0, "0.425")
            entry_gapmax.grid(row=1, column=3)

            label_boxcar = Tk.Label(frame_entry, text="Boxcar width")
            label_boxcar.grid(row=1, column=4, sticky=Tk.E)

            entry_boxcar = Tk.Entry(frame_entry)
            entry_boxcar.insert(0, "10")
            entry_boxcar.grid(row=1, column=5)

            button_go = Tk.Button(
                top, text="Calculate",
                command=lambda: getGap(data.xseries, data.yseries, top))
            button_go.grid(row=2)

            button_close = Tk.Button(top, text="Close", command=top.destroy)
            button_close.grid(row=2, column=1)

            def getGap(xs, yss, top):
                gapmin = float(entry_gapmin.get())
                gapmax = float(entry_gapmax.get())
                boxcar = int(entry_boxcar.get())
                if gapmin is "":
                    msg_window("Error", "Please provide minimum gap size")
                elif gapmax is "":
                    msg_window("Error", "Please provide maximum gap size")
                elif boxcar is "":
                    msg_window("Error", "Please provide boxcar width")
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
                msg_window(
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

        path_var = Tk.StringVar()

        def export():
            top = Tk.Toplevel()
            top.title("Export average spectrum")
            button_dir = Tk.Button(
                top, text="Choose path", command=askpath)
            button_dir.pack()
            path_var.set("Please select path")
            label_path = Tk.Label(
                top, textvariable=path_var, justify=Tk.CENTER)
            label_path.pack()
            button_exc = Tk.Button(
                top, text="Export",
                command=lambda: exportSpec(
                    data.xseries, data.yave, data.outdir, top))
            button_exc.pack()
            button_close = Tk.Button(
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
                msg_window("Error", "Spectrum does not exist")
            elif min is None or max is None:
                msg_window("Error", "Gap range does not exist")
            else:
                aveID = dbu.insertAveSpectrum(xs, ys, 0, 0, numAve)
                for i in range(int(data.specidl), int(data.specidh) + 1):
                    dbu.insertSpecAvePair(i, aveID)
                msg_window("Success", "Average spectra inserted into database")

        top = Tk.Toplevel()
        top.title("Display averge spectra")
        label = Tk.Label(top, text="Enter spectrum ID range")
        label.pack()
        entryl = Tk.Entry(top)
        entryl.pack()
        entryh = Tk.Entry(top)
        entryh.pack()

        fig = plt.figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=top)
        toolbar = NavigationToolbar2TkAgg(canvas, top)

        frame_button = Tk.Frame(top)
        frame_button.pack()

        button_display = Tk.Button(
            frame_button, text="Display",
            command=lambda: display(fig, ax, canvas, toolbar))
        button_display.pack(side=Tk.LEFT)

        button_clear = Tk.Button(
            frame_button, text="Clear",
            command=lambda: clear_canvas(canvas))
        button_clear.pack(side=Tk.LEFT)

        button_gap = Tk.Button(
            frame_button, text="Gap",
            command=lambda: showGap(ax, canvas, toolbar))
        button_gap.pack(side=Tk.LEFT)

        button_export = Tk.Button(
            frame_button, text="Export...", command=export)
        button_export.pack(side=Tk.LEFT)

        button_db = Tk.Button(
            frame_button, text="Add to DB",
            command=lambda: dbInsert(data.xseries, data.yave, data.numAved))
        button_db.pack(side=Tk.LEFT)

        button_close = Tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=Tk.LEFT)

        def exportSpec(xs, yss, path, top):
            if xs is None or yss is None or path is None:
                msg_window("Error", "Something is missing")
            else:
                xs = mfn.transpose1d(xs)
                yss = mfn.transpose1d(yss)
                out = []
                for i in range(len(xs)):
                    out.append(xs[i] + yss[i])
                processor.csv_writer(out, path)
            msg_window("Success", "Successfully exported")
            top.destroy()

        def display(fig, ax, canvas, toolbar):
            data.specidl = entryl.get()
            data.specidh = entryh.get()
            if data.specidl is "":
                msg_window("Error", "Please provide min ID")
            elif data.specidh is "":
                msg_window("Error", "Please provide max ID")
            elif int(data.specidl) > int(data.specidh):
                msg_window("Error", "Lower bound > upper bound")
            else:
                specData = dba.getSpectrumFromRange(
                    int(data.specidl), int(data.specidh))
                data.numAved = int(data.specidh) - int(data.specidl) + 1
                if specData is None:
                    msg_window(
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
                        msg_window("Error", "x and y have different dimension")

                    # use '-o' for dots
                    ax.plot(data.xseries, data.yave, '-')
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=Tkc.BOTTOM, fill=Tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=Tkc.TOP, fill=Tkc.BOTH, expand=1)

        def showGap(ax, canvas, toolbar):
            top = Tk.Toplevel()

            frame_entry = Tk.Frame(top)
            frame_entry.grid(row=1, columnspan=2)

            label_gapmin = Tk.Label(frame_entry, text="Min gap size (V)")
            label_gapmin.grid(row=1, sticky=Tk.E)

            entry_gapmin = Tk.Entry(frame_entry)
            entry_gapmin.insert(0, "0.025")
            entry_gapmin.grid(row=1, column=1)

            label_gapmax = Tk.Label(frame_entry, text="Max gap size (V)")
            label_gapmax.grid(row=1, column=2, sticky=Tk.E)

            entry_gapmax = Tk.Entry(frame_entry)
            entry_gapmax.insert(0, "0.425")
            entry_gapmax.grid(row=1, column=3)

            label_boxcar = Tk.Label(frame_entry, text="Boxcar width")
            label_boxcar.grid(row=1, column=4, sticky=Tk.E)

            entry_boxcar = Tk.Entry(frame_entry)
            entry_boxcar.insert(0, "10")
            entry_boxcar.grid(row=1, column=5)

            button_go = Tk.Button(
                top, text="Calculate",
                command=lambda: getGap(data.xseries, data.yave, top))
            button_go.grid(row=2)

            button_close = Tk.Button(top, text="Close", command=top.destroy)
            button_close.grid(row=2, column=1)

            def getGap(xs, yss, top):
                gapmin = float(entry_gapmin.get())
                gapmax = float(entry_gapmax.get())
                if gapmin is "":
                    msg_window("Error", "Please provide minimum gap size")
                elif gapmax is "":
                    msg_window("Error", "Please provide maximum gap size")
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
                msg_window(
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
                msg_window("Error", "Spectrum does not exist")
            elif min is None or max is None:
                msg_window("Error", "Gap range does not exist")
            else:
                aveID = dbu.insertAveSpectrum(xs, ys, 0, 0, numAve)
                for i in range(int(data.specidl), int(data.specidh) + 1):
                    dbu.insertSpecAvePair(i, aveID)
                msg_window("Success", "Average spectra inserted into database")

        top = Tk.Toplevel()
        top.title("Display averge spectra")
        label = Tk.Label(top, text="Enter spectrum ID range")
        label.pack()
        entryl = Tk.Entry(top)
        entryl.pack()
        entryh = Tk.Entry(top)
        entryh.pack()
        label_stdev = Tk.Label(top, text="Enter standard deviation multiple")
        label_stdev.pack()
        entry = Tk.Entry(top)
        entry.insert(0, "2")
        entry.pack()

        fig = plt.figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=top)
        toolbar = NavigationToolbar2TkAgg(canvas, top)

        frame_button = Tk.Frame(top)
        frame_button.pack()

        button_display = Tk.Button(
            frame_button, text="Display",
            command=lambda: display(fig, ax, canvas, toolbar))
        button_display.pack(side=Tk.LEFT)

        button_clear = Tk.Button(
            frame_button, text="Clear",
            command=lambda: clear_canvas(canvas))
        button_clear.pack(side=Tk.LEFT)

        button_db = Tk.Button(
            frame_button, text="Add to DB",
            command=lambda: dbInsert(data.xseries, data.yave, data.numAved))
        button_db.pack(side=Tk.LEFT)

        button_close = Tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=Tk.LEFT)

        def display(fig, ax, canvas, toolbar):
            data.specidl = entryl.get()
            data.specidh = entryh.get()
            if data.specidl is "":
                msg_window("Error", "Please provide min ID")
            elif data.specidh is "":
                msg_window("Error", "Please provide max ID")
            elif int(data.specidl) > int(data.specidh):
                msg_window("Error", "Lower bound > upper bound")
            else:
                specData = dba.getSpectrumFromRange(
                    int(data.specidl), int(data.specidh))
                data.numAved = int(data.specidh) - int(data.specidl) + 1
                if specData is None:
                    msg_window(
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
                        msg_window("Error", "x and y have different dimension")

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
    welcome = Tk.Label(root, text="Welcome to STMPLab")
    welcome.grid(row=0, columnspan=2)

    mainApp = MainApp(root, 'STMPLab')
    mainApp.menu(root)

if __name__ == "__main__":
    root = Tk.Tk()
    main()
    root.mainloop()
