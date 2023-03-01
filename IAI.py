'''
IAI from IAI_test20221124
'''

import csv
import tkinter
import tkinter as tk
from tkinter import messagebox
import time
from tkinter import filedialog as fd
import threading
from serial import Serial
from serial.threaded import ReaderThread, Protocol, LineReader
import customtkinter
import IAI_MODBUS as IAI
import pandas as pd
import openpyxl
from PIL import ImageTk
from datetime import datetime

HOME = ":0105040BFF00EC\r\n"
SERVO_ON = ":01050403FF00F4\r\n"
MOVE_LOC0 = ":01069800000061\r\n"
MOVE_LOC1 = ":01069800000160\r\n"
MOVE_LOC2 = ":0106980000025F\r\n"
MOVE_LOC3 = ":0106980000035E\r\n"
MOVE_LOC4 = ":0106980000045D\r\n"
MOVE_LOC5 = ":0106980000055C\r\n"
CurrentPos = ":0103900000026A\r\n"
FiftymmPos = ":0110990000020400001388B5\r\n"

# constant parameters
speed_combValues = ['2.5 mm/s', '4 mm/s', '5.2 mm/s','10 mm/s','100 mm/s']
max_distance = 200
tgt_pos_band = '000A'  # Position band 0.01 mm pg 377
tgt_pos_vel  = '2710'  # Velocity 0.01 mm/s
tgt_pos_acc  = '001E'  # Acceleration 0.01 G

def startCallBack():
    # Initiate serial port
    # messagebox.showinfo( "Hello Python", "Hello World")
    # data = SERVO_ON
    # for i in data:
    #     serial_port.write(bytearray(i, 'ascii'))
    IAI.servo_On()

def MovePos():
    global t
    num = 1
    test = f"{num:04}"
    IAI.move_loc(test.upper())
    t = IAI.InfiniteTimer(0.01, readPostCallBack)
    t.start()


def MoveCallBack(pos):
    global t1
    global MF_tgt_pos

    select_file()
    MF_tgt_pos = (pos)
    #print("position",pos)
    if MF_tgt_pos > 0 and MF_tgt_pos <= max_distance:
        dist = MF_tgt_pos * 100
        tgt_pos = str(f'{int(dist):0>4x}')
        IAI.move2PoswifSpeed(tgt_pos,tgt_pos_band,tgt_pos_vel, tgt_pos_acc)
        time.sleep(0.01)
        #t1 = threading.Thread(target=IAI.move2PoswifSpeed,args=(tgt_pos,tgt_pos_band, tgt_pos_vel, tgt_pos_acc,))
        # Start the threads
        #t1.start()
        #print("Inside loop",pos)
        #readPostCallBack()
        t1 = IAI.InfiniteTimer(0.02, readPostCallBack)
        t1.start()
    else:
        messagebox.showerror("Error",f'The Position value entered {MF_tgt_pos} mm \n must be between 0 and 200' )

def ResetCallBack():
    IAI.ALRS()

def readPostCallBack():
    #pass
    #print("1")
    IAI.PNOW()
    # data = CurrentPos
    # for i in data:
    #      serial_port.write(bytearray(i, 'ascii'))

def select_file():
        global filename
        filetypes = (
            ('text files', '*.txt'),
            ('csv', '*.csv')
        )

        filename = fd.asksaveasfilename(
            defaultextension="",
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)

        # tk.messagebox.showinfo(
        #     title='Selected File',
        #     message=filename
        # )
        # MoveCallBack(pos,filename)

class MainFrame(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = customtkinter.CTkFrame(master=app, width=600, height=300, corner_radius=15)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        # combo box
        # Label
        self.speedlabel = customtkinter.CTkLabel(master=self.frame, text="Speed (mm/s)", justify=tk.LEFT)
        self.speedlabel.place(x=80.5, y=20.5, anchor=tk.CENTER)
        self.speedlabel.grid(row=2, column=0, columnspan=1, padx=10, pady=10, sticky="e")

        self.combobox_speedvar = customtkinter.StringVar(value='5 mm/s')  # set initial value
        self.combobox_speed = customtkinter.CTkComboBox(master=self.frame, values=speed_combValues,
                                                        command=self.combobox_speed_selection)
        self.combobox_speed.grid(row=2, column=1, columnspan=1, pady=5, padx=5, sticky="e")

        self.label = customtkinter.CTkLabel(master=self.frame, text="Position (mm)", justify=tk.LEFT)
        self.label.place(x=20.5, y=20.5, anchor=tk.CENTER)
        self.label.grid(row=3, column=0, columnspan=1, padx=5, pady=5, sticky="e")

        int_var = tk.IntVar()
        self.slider_dist = customtkinter.CTkSlider(master=self.frame, from_=0, to=200, height = 10, width=100,
                                                   orientation="horizontal",command = self.slider_event)
        #self.slider_dist.place(x=20.5, y=20.5, anchor=tk.CENTER)
        self.slider_dist.grid(row=3, column=1, columnspan=1, padx=20,pady=30, sticky="n")

        self.slider_value = self.slider_dist.get()
        self.slider_dist_label = customtkinter.CTkLabel(master=self.frame, text=str(self.slider_value), justify=tk.LEFT)
        self.slider_dist_label.place(x=230, y=60.5, anchor=tk.CENTER)
        #START button
        self.button = customtkinter.CTkButton(master=self.frame, text="Start", command=startCallBack)
        self.button.place(x=20.5, y=0.5, anchor=tk.CENTER)
        self.button.grid(row=5, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        #MOVE button
        self.buttonMove = customtkinter.CTkButton(master=self.frame, text="Move",
                                                  command=lambda: MoveCallBack(self.slider_dist.get()))
        # self.buttonMove = customtkinter.CTkButton(master=self.frame, text="Move",
        #                                           command=lambda:select_file(self.slider_dist.get()))

        self.buttonMove.grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        self.buttonReset = customtkinter.CTkButton(master=self.frame, text="Reset",
                                                  command=lambda: ResetCallBack())
        self.buttonReset.grid(row=7, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        self.connectionStatuslabel = customtkinter.CTkLabel(master=self.frame, text="Not Connected", justify=tk.LEFT)
        self.connectionStatuslabel.place(x=80.5, y=20.5, anchor=tk.CENTER)
        self.connectionStatuslabel.grid(row=8, column=0, columnspan=1, padx=10, pady=10, sticky="e")

        # ports = serial.tools.list_ports.comports()
        # com_list = [com[0] for com in ports]
        # print(com_list)
        # combobox_serial = customtkinter.CTkComboBox(master=app, values=com_list, command=combobox_port_selection)
        # combobox_serial.set(port)
        # combobox_serial.place(relx=0.2, rely=0.1, anchor=tk.CENTER)

    def on_data(self, data):
        global t
        global filename
        count = 0
        file_data =[[],[]]
        #print("Called from on_data ", data)
        # lock = threading.Lock()
        # lock.acquire()
        try:
            if data[3] == '3':
                pos_data = data[6:14]
                strings = [str(pos) for pos in pos_data]
                a_string = "".join(strings)
                an_integer = int(a_string, 16) * 0.01
                #print(an_integer)
                dt = datetime.now()
                ts = datetime.timestamp(dt) * 1000
                file_data[0].append(ts)
                file_data[0].append(round(an_integer, 2))
                with open(filename,'a') as file:
                    write = csv.writer(file,lineterminator='\n')
                    write.writerows(file_data)
                # print(count, file_data)
                # count = count + 1

                print(f"tgt position {round(MF_tgt_pos,3):.3f} measured position: {round(an_integer,3):.3f} mm {ts} ms")
                if round(an_integer,2) == round(MF_tgt_pos,2):
                    print("stop")
                    t1.cancel()

        except IndexError:
            pass
            #print("error",len(data))
        # except Exception as ex:
        #     template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        #     message = template.format(type(ex).__name__, ex.args)
        #     print(message)

        #lock.release()

    def combobox_speed_selection(self, event):
        global tgt_pos_vel
        # Three methods here all get the same value.
        #print("change")
        #print(event)
        #speed_combValues = ['2.5 mm/s', '4 mm/s', '5.2 mm/s', '10 mm/s']
        match event:
            case '2.5 mm/s':
                print('2.5 mm/s')
                temp = 2.5 * 100
            case '4 mm/s':
                temp = 4 * 100
                print('4 mm/s')
            case '5.2 mm/s':
                temp = 5.2 * 100
                print('5.2 mm/s')
            case '10 mm/s':
                temp = 10 * 100
                print('10 mm/s')
            case _:
                temp = 100 * 100
                print("default 100 mm/s")

        tgt_pos_vel = str(f'{int(temp):0>4x}')

    def slider_event(self,value):
        self.slider_dist_label.configure(text= str(f"{value:.2f}"))
        # print(value)



if __name__ == '__main__':
    customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    app = customtkinter.CTk(className="IAI Actuator Control")
    app.wm_iconbitmap()
    p1 = ImageTk.PhotoImage(file="essilor-logo-rgb-blue.png")
    app.iconphoto(False, p1)
    # set window size
    app.geometry("440x450")
    app.title("IAI control")
    #
    # app = tk.Tk(className='IAI Actuator Control')
    #
    # app.geometry("300x300")

    # # SerialReaderProtocolLine.tk_listener = main_frame
    # # Initiate serial port

    # Getting the current date and time
    dt = datetime.now()


    print("Date and time is:", dt.strftime(("%d %B, %Y, %H:%M:%S")))
    # timestamp in milliseconds
    # getting the timestamp
    ts = datetime.timestamp(dt) * 1000
    print(ts)

    main_frame = MainFrame()
    #Set listener to our reader
    while True:
        serial_port = IAI.connect(portname="COM4", baudrate=38400)
        if serial_port.isOpen():
            main_frame.connectionStatuslabel.configure(text="Connected")
            break
        else:
            main_frame.connectionStatuslabel.configure(text="Not Connected")
            main_frame.connectionStatuslabel.showerror("Error",f'Please Check Seria port' )

    IAI.SerialReaderProtocolRaw.tk_listener = main_frame
    reader = ReaderThread(serial_port, IAI.SerialReaderProtocolRaw)
    reader.start()
    IAI.SerialReaderProtocolLine.tk_listener = main_frame
    # Initiate serial port
    serial_port = IAI.connect(portname="COM4", baudrate=38400)


    # Initiate ReaderThread
    #reader = IAI_MODBUSascii_20221104.ReaderThread(serial_port,IAI_MODBUSascii_20221104.SerialReaderProtocolRaw)
    # Start reader
    #reader.start()

    app.mainloop()