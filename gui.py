#!/usr/bin/env python3

import tkinter as tk
import tkinter.constants as tkc
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
    top = tk.Toplevel()
    top.title(title)
    msg = tk.Message(top, text=text, width=300)
    msg.pack()
    button = tk.Button(top, text="Close", command=top.destroy)
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

        frame = tk.Frame(root)
        frame.grid(row=1, columnspan=2)

        self.quit_button = tk.Button(
            frame, text="QUIT", fg="red", command=frame.quit)
        self.quit_button.grid(row=0, column=0)

        self.create_button = tk.Button(
            frame, text="Create new/erase existing database",
            command=self.create_db)
        self.create_button.grid(row=1)

        self.num_button = tk.Button(
            frame, text="Spectra in database", command=self.display_spectra_num)
        self.num_button.grid(row=2)

        self.button_open = tk.Button(
            frame, text="Open...", command=self.open_file)
        self.button_open.grid(row=3)

        self.button_display_spec = tk.Button(
            frame, text="Display spectra", command=self.display_spectrum_from_id)
        self.button_display_spec.grid(row=4)

        self.button_rm_outlier = tk.Button(
            frame, text="Remove outliers",
            command=self.rmv_outlier)
        self.button_rm_outlier.grid(row=5)

        self.button_ave_spec = tk.Button(
            frame, text="Calculate average spectra",
            command=self.display_ave_from_range)
        self.button_ave_spec.grid(row=6)

        self.button_ave_spec_from_box = tk.Button(
            frame, text="Display average spectra of specific boxcar width",
            command=self.display_ave_from_boxcar)
        self.button_ave_spec_from_box.grid(row=7)

        self.button_gap_from_id = tk.Button(
            frame, text="Get gap size from spectrum", command=self.show_gap_size)
        self.button_gap_from_id.grid(row=8)

    def menu(self, master):
        menu_bar = tk.Menu(master)
        file_menu = tk.Menu(menu_bar, tearoff=0)
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
            options['initialdir'] = 'User\\'
            options['initialfile'] = ''
            options['parent'] = root
            options['title'] = 'choose file'
            options['multiple'] = 1

            # get filename
            filename = tk.filedialog.askopenfilename(**file_opt)

            if filename:
                self.sourcefile = filename
                if len(filename) is 1:
                    file_path_var.set(filename)
                else:
                    file_path_var.set(
                        "Multiple files, including {}".format(filename[0]))

        def insert_spectrum(top_arg):
            doping = entry_doping.get()
            boxcar = entry_boxcar.get()
            delimiter = entry_delimiter.get()
            std_dev = entry_std_dev.get()
            gap_min = entry_gap_min.get()
            gap_max = entry_gap_max.get()
            if doping is "":
                insert_var.set("Please provide doping")
            elif boxcar is "":
                insert_var.set("Please provide boxcar width")
            elif delimiter is "":
                insert_var.set("Please provide CSV delimiter")
            elif std_dev is "":
                insert_var.set("Please provide standard deviation multiple")
            elif gap_min is "":
                insert_var.set("Please provide minimum gap size")
            elif gap_max is "":
                insert_var.set("Please provide maximum gap size")
            elif self.sourcefile is None:
                insert_var.set("No file selected.")
            else:
                boxcar = int(boxcar)
                std_dev = int(std_dev)
                gap_min = float(gap_min)
                gap_max = float(gap_max)
                xs, yss = processor.readFile(self.sourcefile, delimiter)
                # TODO: add exclusion feature
                exclusions, excluded = processor.elimStdev(xs, yss, 2)
                count = 0
                for ys in yss:
                    count += 1
                    dbu.insertSpectrum(xs, ys, doping)
                msg_window(
                    "Done", "Successfully inserted {} spectra".format(count))
                top_arg.destroy()

        # plain old process function
        def process():
            class Data:
                out_dir = None
                gap_stat, average_box = [], []

            path_var = tk.StringVar()
            status_var.set("Processing... Please wait.")

            def ask_path():
                """Return the selected directory name"""

                file_opt = options = {}
                options['initialdir'] = 'User\\'
                options['parent'] = root
                options['title'] = 'Choose directory'

                # get pathname
                pathname = tk.filedialog.askdirectory(**file_opt)

                if pathname:
                    Data.out_dir = pathname
                    path_var.set(pathname)

            def processing():
                exclusions, excluded = processor.elimStdev(xs, yss, std_dev)
                boxcar_result = processor.boxcar(yss, boxcar, exclusions)
                Data.gap_stat, Data.average_box = processor.groupAverage(
                    xs, boxcar_result, gap_min, gap_max, x_step)

            def output():
                processor.csv_writer(
                    Data.gap_stat, "{}/gap.csv".format(Data.out_dir))
                logging.debug(
                    "Gap output path" + "{}/gap.csv".format(Data.out_dir))
                processor.csv_writer(
                    Data.average_box, "{}/ave.csv".format(Data.out_dir))
                top_top.destroy()

            boxcar = entry_boxcar.get()
            delimiter = entry_delimiter.get()
            std_dev = entry_std_dev.get()
            gap_min = entry_gap_min.get()
            gap_max = entry_gap_max.get()
            x_step = entry_x_step.get()
            if boxcar is "":
                status_var.set("Please provide boxcar width")
            elif delimiter is "":
                status_var.set("Please provide CSV delimiter")
            elif std_dev is "":
                status_var.set("Please provide standard deviation multiple")
            elif gap_min is "":
                status_var.set("Please provide minimum gap size")
            elif gap_max is "":
                status_var.set("Please provide maximum gap size")
            elif x_step is "":
                status_var.set("Please provide x step size")
            elif self.sourcefile is None:
                status_var.set("No file selected.")
            else:
                boxcar = int(boxcar)
                std_dev = int(std_dev)
                gap_min = float(gap_min)
                gap_max = float(gap_max)
                x_step = float(x_step)
                try:
                    xs, yss = processor.readFile(self.sourcefile, delimiter)
                except ValueError:
                    if delimiter is ",":
                        status_var.set(
                            "Error, wrong csv delimiter. Try semicolon.")
                    elif delimiter is ";":
                        status_var.set(
                            "Error, wrong csv delimiter. Try comma.")
                    else:
                        status_var.set("Error, wrong csv delimiter.")
                else:
                    thread = Thread(target=processing)
                    thread.start()
                    thread.join()

                    logging.debug("Finished processing.")

                    status_var.set("Done.")

                    top_top = tk.Toplevel()
                    top_top.title("Choose output path")

                    button_path = tk.Button(
                        top_top, text="Select path", command=ask_path)
                    button_path.grid(row=1)

                    path_var = tk.StringVar()
                    path_var.set("Please select output path.")

                    label_path = tk.Label(
                        top_top, textvariable=path_var, justify=tk.CENTER)
                    label_path.grid(row=1, column=1)

                    button_export = tk.Button(
                        top_top, text="Export", command=output)
                    button_export.grid(row=2, columnspan=2)

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

        label_delimiter = tk.Label(frame_entry, text="CSV delimiter")
        label_delimiter.grid(row=2, sticky=tk.E)

        entry_delimiter = tk.Entry(frame_entry)
        entry_delimiter.insert(0, ",")
        entry_delimiter.grid(row=2, column=1)

        label_std_dev = tk.Label(frame_entry, text="Stddev multiple")
        label_std_dev.grid(row=2, column=2, sticky=tk.E)

        entry_std_dev = tk.Entry(frame_entry)
        entry_std_dev.insert(0, "2")
        entry_std_dev.grid(row=2, column=3)

        label_gap_min = tk.Label(frame_entry, text="Min gap size (V)")
        label_gap_min.grid(row=3, sticky=tk.E)

        entry_gap_min = tk.Entry(frame_entry)
        entry_gap_min.insert(0, "0.025")
        entry_gap_min.grid(row=3, column=1)

        label_gap_max = tk.Label(frame_entry, text="Max gap size (V)")
        label_gap_max.grid(row=3, column=2, sticky=tk.E)

        entry_gap_max = tk.Entry(frame_entry)
        entry_gap_max.insert(0, "0.425")
        entry_gap_max.grid(row=3, column=3)

        label_x_step = tk.Label(frame_entry, text="x-step (V)")
        label_x_step.grid(row=4, column=2, sticky=tk.E)

        entry_x_step = tk.Entry(frame_entry)
        entry_x_step.insert(0, "0.025")
        entry_x_step.grid(row=4, column=3)

        button_openfile = tk.Button(
            top, text="Open...", command=askopenfilename)
        button_openfile.grid(row=2)

        file_path_var = tk.StringVar()
        file_path_var.set("Please select file.")
        label_file = tk.Label(
            top, textvariable=file_path_var, justify=tk.CENTER)
        label_file.grid(row=2, column=1)

        button_insert_spec = tk.Button(
            top, text="Insert spectra", command=lambda: insert_spectrum(top))
        button_insert_spec.grid(row=3)

        insert_var = tk.StringVar()
        label_insert = tk.Label(
            top, textvariable=insert_var, justify=tk.CENTER)
        label_insert.grid(row=3, column=1)

        # plain old process function
        button_process = tk.Button(
            top, text="Plain old process function", command=process)
        button_process.grid(row=4)

        status_var = tk.StringVar()

        label_process = tk.Label(top, textvariable=status_var, justify=tk.CENTER)
        label_process.grid(row=4, column=1)

        button_close = tk.Button(top, text="Close", command=top.destroy)
        button_close.grid(row=5, columnspan=2)

    @staticmethod
    def create_db():
        dbc.main()
        logging.debug("Finished creating database")
        msg_window("Create database", "Finished creating the database")

    @staticmethod
    def display_spectra_num():
        num = dba.displaySpectraNum()
        text = "Number of spectra in the database is {}.".format(str(num))
        msg_window("Number of spectra", text)

    @staticmethod
    def show_gap_size():
        def get_gap_size(spec_id):
            gap = dba.getGap(int(spec_id))
            msg_window(
                "Gap size: spec {}".format(spec_id),
                "Gap size is {}".format(gap))

        top = tk.Toplevel()

        label = tk.Label(top, text="Choose from available spectra ID")
        label.grid(row=0, columnspan=2)

        frame = tk.Frame(top)
        frame.grid(row=1, columnspan=2)

        id_list = dba.specWithGap()

        id_list_options = [str(row) for row in id_list]
        id_var = tk.StringVar()
        id_var.set(id_list_options[0])

        option = tk.OptionMenu(*(frame, id_var) + tuple(id_list_options))
        option.grid(row=1, columnspan=2)

        button = tk.Button(
            frame, text="Show", command=lambda: get_gap_size(id_var.get()))
        button.grid(row=2)

        button_close = tk.Button(frame, text="Close", command=top.destroy)
        button_close.grid(row=2, column=1)

    @staticmethod
    def display_ave_from_boxcar():
        class Data:
            x_series = []
            boxcar = 0

        def display():
            Data.boxcar = entry.get()
            if Data.boxcar is "":
                msg_window("Error", "Please provide boxcar width")
            else:
                spec_data = dba.getAveFromBoxcarWidth(int(Data.boxcar))
                if spec_data is None:
                    msg_window(
                        "No spectrum found",
                        "Average spectrum of this boxcar width is not found")
                else:
                    Data.x_series = dbapi.textToSeries(spec_data[0][4])
                    y_series = []
                    for i in range(len(spec_data)):
                        y_series.append(dbapi.textToSeries(spec_data[i][5]))

                    if len(Data.x_series) is not len(y_series[0]):
                        msg_window("Error", "x and y have different dimension")

                    # use '-o' for dots
                    for ys in y_series:
                        ax.plot(Data.x_series, ys, '-')
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=tkc.BOTTOM, fill=tkc.BOTH, expand=1)

                    toolbar.update()

                    canvas._tkcanvas.pack(
                        side=tkc.TOP, fill=tkc.BOTH, expand=1)

        top = tk.Toplevel()
        top.title("Display average spectra")
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

        button_display = tk.Button(frame_button, text="Display", command=display)
        button_display.pack(side=tk.LEFT)

        button_clear = tk.Button(
            frame_button, text="Clear",
            command=lambda: clear_canvas(canvas))
        button_clear.pack(side=tk.LEFT)

        button_close = tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=tk.LEFT)

    @staticmethod
    def display_spectrum_from_id():
        class Data:
            out_dir = None  # output directory path
            x_series = y_series = None
            spec_id = 0

        path_var = tk.StringVar()

        def export():
            top_top = tk.Toplevel()
            top_top.title("Export spectrum")
            button_dir = tk.Button(
                top_top, text="Choose path", command=ask_path)
            button_dir.pack()
            path_var.set("Please select path")
            label_path = tk.Label(
                top_top, textvariable=path_var, justify=tk.CENTER)
            label_path.pack()
            button_exc = tk.Button(
                top_top, text="Export",
                command=lambda: export_spec(
                    Data.x_series, Data.y_series, Data.out_dir, top_top))
            button_exc.pack()

            button_close_top = tk.Button(
                top_top, text="Close", command=top_top.destroy)
            button_close_top.pack()

        # open directory window
        def ask_path():
            """Return the selected directory name"""

            file_opt = options = {}
            options['initialdir'] = 'User\\'
            options['parent'] = root
            options['title'] = 'Choose directory'

            # get path name
            pathname = tk.filedialog.asksaveasfilename(**file_opt)

            if pathname:
                Data.out_dir = pathname
                path_var.set(pathname)

        def display():
            Data.spec_id = entry.get()
            if Data.spec_id is "":
                msg_window("Error", "Please provde ID")
            else:
                spec_data = dba.getSpectrumFromID(int(Data.spec_id))
                if spec_data is None:
                    msg_window(
                        "No spectrum found",
                        "Spectrum of this ID is not found")
                else:
                    Data.x_series = dbapi.textToSeries(spec_data[1])
                    Data.y_series = dbapi.textToSeries(spec_data[2])

                    # use '-o' for dots
                    ax.plot(Data.x_series, Data.y_series, '-')
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=tkc.BOTTOM, fill=tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=tkc.TOP, fill=tkc.BOTH, expand=1)

        def show_gap():
            top_top = tk.Toplevel()

            frame_entry = tk.Frame(top_top)
            frame_entry.grid(row=1, columnspan=2)

            label_gap_min = tk.Label(frame_entry, text="Min gap size (V)")
            label_gap_min.grid(row=1, sticky=tk.E)

            entry_gap_min = tk.Entry(frame_entry)
            entry_gap_min.insert(0, "0.025")
            entry_gap_min.grid(row=1, column=1)

            label_gap_max = tk.Label(frame_entry, text="Max gap size (V)")
            label_gap_max.grid(row=1, column=2, sticky=tk.E)

            entry_gap_max = tk.Entry(frame_entry)
            entry_gap_max.insert(0, "0.425")
            entry_gap_max.grid(row=1, column=3)

            label_boxcar = tk.Label(frame_entry, text="Boxcar width")
            label_boxcar.grid(row=1, column=4, sticky=tk.E)

            entry_boxcar = tk.Entry(frame_entry)
            entry_boxcar.insert(0, "10")
            entry_boxcar.grid(row=1, column=5)

            button_go = tk.Button(
                top_top, text="Calculate",
                command=lambda: get_gap(Data.x_series, Data.y_series))
            button_go.grid(row=2)

            button_close_top = tk.Button(top_top, text="Close", command=top_top.destroy)
            button_close_top.grid(row=2, column=1)

            def get_gap(xs, yss):
                gap_min = float(entry_gap_min.get())
                gap_max = float(entry_gap_max.get())
                boxcar = int(entry_boxcar.get())
                if gap_min is "":
                    msg_window("Error", "Please provide minimum gap size")
                elif gap_max is "":
                    msg_window("Error", "Please provide maximum gap size")
                elif boxcar is "":
                    msg_window("Error", "Please provide boxcar width")
                else:
                    gap_size = mfn.poly_gap(
                        xs[0:20], yss[0:20], gap_min, gap_max).real
                    ax.axvline(gap_size)
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=tkc.BOTTOM, fill=tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=tkc.TOP, fill=tkc.BOTH, expand=1)
                dbu.insertGap(Data.spec_id, gap_size, boxcar)
                msg_window(
                    "Done",
                    "Gap size is {}, saved into database.".format(gap_size))

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
            frame_button, text="Display", command=display)
        button_display.pack(side=tk.LEFT)

        button_clear = tk.Button(
            frame_button, text="Clear",
            command=lambda: clear_canvas(canvas))
        button_clear.pack(side=tk.LEFT)

        button_gap = tk.Button(
            frame_button, text="Gap", command=show_gap)
        button_gap.pack(side=tk.LEFT)

        button_export = tk.Button(
            frame_button, text="Export...", command=export)
        button_export.pack(side=tk.LEFT)

        button_close = tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=tk.LEFT)

        def export_spec(xs, yss, path, current_top):
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
            current_top.destroy()

    @staticmethod
    def display_ave_from_range():
        class Data:
            out_dir = None  # output directory path
            x_series = []
            y_ave = []
            spec_id_l = 0
            spec_id_h = 0
            num_ave = 0

        path_var = tk.StringVar()

        def export():
            top_top = tk.Toplevel()
            top_top.title("Export average spectrum")
            button_dir = tk.Button(
                top_top, text="Choose path", command=ask_path)
            button_dir.pack()
            path_var.set("Please select path")
            label_path = tk.Label(
                top_top, textvariable=path_var, justify=tk.CENTER)
            label_path.pack()
            button_exc = tk.Button(
                top_top, text="Export",
                command=lambda: export_spec(
                    Data.x_series, Data.y_ave, Data.out_dir, top_top))
            button_exc.pack()

            button_close_top = tk.Button(
                top_top, text="Close", command=top_top.destroy)
            button_close_top.pack()

        # open directory window
        def ask_path():
            """Return the selected directory name"""

            file_opt = options = {}
            options['initialdir'] = 'User\\'
            options['parent'] = root
            options['title'] = 'Choose directory'

            # get path name
            pathname = tk.filedialog.asksaveasfilename(**file_opt)

            if pathname:
                Data.out_dir = pathname
                path_var.set(pathname)

        def db_insert(xs, ys, num_ave):
            if xs is None or ys is None:
                msg_window("Error", "Spectrum does not exist")
            elif min is None or max is None:
                msg_window("Error", "Gap range does not exist")
            else:
                ave_id = dbu.insertAveSpectrum(xs, ys, 0, 0, num_ave)
                for i in range(int(Data.spec_id_l), int(Data.spec_id_h) + 1):
                    dbu.insertSpecAvePair(i, ave_id)
                msg_window("Success", "Average spectra inserted into database")

        def show_gap():
            top_top = tk.Toplevel()

            frame_entry = tk.Frame(top_top)
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
                top_top, text="Calculate",
                command=lambda: get_gap(Data.x_series, Data.y_ave))
            button_go.grid(row=2)

            button_close_top = tk.Button(top_top, text="Close", command=top_top.destroy)
            button_close_top.grid(row=2, column=1)

            def get_gap(xs, yss):
                gap_min = float(entry_gapmin.get())
                gap_max = float(entry_gapmax.get())
                if gap_min is "":
                    msg_window("Error", "Please provide minimum gap size")
                elif gap_max is "":
                    msg_window("Error", "Please provide maximum gap size")
                else:
                    gap_size = mfn.poly_gap(
                        xs[0:20], yss[0:20], gap_min, gap_max).real
                    ax.axvline(gap_size)
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=tkc.BOTTOM, fill=tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=tkc.TOP, fill=tkc.BOTH, expand=1)
                msg_window(
                    "Done",
                    "Gap size is {}".format(gap_size))

        def display():
            Data.spec_id_l = entry_l.get()
            Data.spec_id_h = entry_h.get()
            if Data.spec_id_l is "":
                msg_window("Error", "Please provide min ID")
            elif Data.spec_id_h is "":
                msg_window("Error", "Please provide max ID")
            elif int(Data.spec_id_l) > int(Data.spec_id_h):
                msg_window("Error", "Lower bound > upper bound")
            else:
                spec_data = dba.getSpectrumFromRange(
                    int(Data.spec_id_l), int(Data.spec_id_h))
                Data.num_ave = int(Data.spec_id_h) - int(Data.spec_id_l) + 1
                if spec_data is None:
                    msg_window(
                        "No spectrum found",
                        "Spectrum of this ID is not found")
                else:
                    Data.x_series = dbapi.textToSeries(spec_data[0][1])
                    y_series, Data.y_ave = [], []
                    for i in range(len(spec_data)):
                        y_series.append(dbapi.textToSeries(spec_data[i][2]))
                    for x in range(len(Data.x_series)):
                        Data.y_ave.append(mfn.mean([col[x] for col in y_series]))

                    if len(Data.x_series) is not len(Data.y_ave):
                        msg_window("Error", "x and y have different dimension")

                    # use '-o' for dots
                    ax.plot(Data.x_series, Data.y_ave, '-')
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=tkc.BOTTOM, fill=tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=tkc.TOP, fill=tkc.BOTH, expand=1)

        top = tk.Toplevel()
        top.title("Display average spectra")
        label = tk.Label(top, text="Enter spectrum ID range")
        label.pack()

        entry_l = tk.Entry(top)
        entry_l.pack()

        entry_h = tk.Entry(top)
        entry_h.pack()

        fig = plt.figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=top)
        toolbar = NavigationToolbar2TkAgg(canvas, top)

        frame_button = tk.Frame(top)
        frame_button.pack()

        button_display = tk.Button(frame_button, text="Display", command=display)
        button_display.pack(side=tk.LEFT)

        button_clear = tk.Button(
            frame_button, text="Clear",
            command=lambda: clear_canvas(canvas))
        button_clear.pack(side=tk.LEFT)

        button_gap = tk.Button(frame_button, text="Gap", command=show_gap)
        button_gap.pack(side=tk.LEFT)

        button_export = tk.Button(
            frame_button, text="Export...", command=export)
        button_export.pack(side=tk.LEFT)

        button_db = tk.Button(
            frame_button, text="Add to DB",
            command=lambda: db_insert(Data.x_series, Data.y_ave, Data.num_ave))
        button_db.pack(side=tk.LEFT)

        button_close = tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=tk.LEFT)

        def export_spec(xs, yss, path, current_top):
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
            current_top.destroy()

    @staticmethod
    def rmv_outlier():
        class Data:
            out_dir = None  # output directory path
            x_series = []
            y_ave = []
            spec_id_l = 0
            spec_id_h = 0
            num_ave = 0

        def db_insert(xs, ys, num_ave):
            if xs is None or ys is None:
                msg_window("Error", "Spectrum does not exist")
            elif min is None or max is None:
                msg_window("Error", "Gap range does not exist")
            else:
                ave_id = dbu.insertAveSpectrum(xs, ys, 0, 0, num_ave)
                for i in range(int(Data.spec_id_l), int(Data.spec_id_h) + 1):
                    dbu.insertSpecAvePair(i, ave_id)
                msg_window("Success", "Average spectra inserted into database")

        # TODO: possibly make display universal module?
        def display():
            Data.spec_id_l = entry_l.get()
            Data.spec_id_h = entry_h.get()
            if Data.spec_id_l is "":
                msg_window("Error", "Please provide min ID")
            elif Data.spec_id_h is "":
                msg_window("Error", "Please provide max ID")
            elif int(Data.spec_id_l) > int(Data.spec_id_h):
                msg_window("Error", "Lower bound > upper bound")
            else:
                spec_data = dba.getSpectrumFromRange(
                    int(Data.spec_id_l), int(Data.spec_id_h))
                Data.num_ave = int(Data.spec_id_h) - int(Data.spec_id_l) + 1
                if spec_data is None:
                    msg_window(
                        "No spectrum found",
                        "Spectrum of this ID is not found")
                else:
                    Data.x_series = dbapi.textToSeries(spec_data[0][1])
                    yseries, Data.y_ave = [], []
                    for i in range(len(spec_data)):
                        yseries.append(dbapi.textToSeries(spec_data[i][2]))
                    for x in range(len(Data.x_series)):
                        Data.y_ave.append(mfn.mean([col[x] for col in yseries]))

                    if len(Data.x_series) is not len(Data.y_ave):
                        msg_window("Error", "x and y have different dimension")

                    # use '-o' for dots
                    ax.plot(Data.x_series, Data.y_ave, '-')
                    canvas.show()
                    canvas.get_tk_widget().pack(
                        side=tkc.BOTTOM, fill=tkc.BOTH, expand=1)

                    toolbar.update()
                    canvas._tkcanvas.pack(
                        side=tkc.TOP, fill=tkc.BOTH, expand=1)

        top = tk.Toplevel()
        top.title("Display average spectra")
        label = tk.Label(top, text="Enter spectrum ID range")
        label.pack()

        entry_l = tk.Entry(top)
        entry_l.pack()

        entry_h = tk.Entry(top)
        entry_h.pack()

        label_std_dev = tk.Label(top, text="Enter standard deviation multiple")
        label_std_dev.pack()

        entry = tk.Entry(top)
        entry.insert(0, "2")
        entry.pack()

        fig = plt.figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=top)
        toolbar = NavigationToolbar2TkAgg(canvas, top)

        frame_button = tk.Frame(top)
        frame_button.pack()

        button_display = tk.Button(frame_button, text="Display", command=display)
        button_display.pack(side=tk.LEFT)

        button_clear = tk.Button(
            frame_button, text="Clear",
            command=lambda: clear_canvas(canvas))
        button_clear.pack(side=tk.LEFT)

        button_db = tk.Button(
            frame_button, text="Add to DB",
            command=lambda: db_insert(Data.x_series, Data.y_ave, Data.num_ave))
        button_db.pack(side=tk.LEFT)

        button_close = tk.Button(
            frame_button, text="Close", command=top.destroy)
        button_close.pack(side=tk.LEFT)


# main entrance
def main():
    welcome = tk.Label(root, text="Welcome to STMPLab")
    welcome.grid(row=0, columnspan=2)

    main_app = MainApp(root, 'STMPLab')
    main_app.menu(root)

if __name__ == "__main__":
    root = tk.Tk()
    main()
    root.mainloop()
