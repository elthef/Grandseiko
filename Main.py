import csv
import re
import sys
import time
import tkinter as tk
import tkinter.filedialog
from tkinter.messagebox import askyesno
from PIL import ImageTk

import matplotlib.pyplot as plt
import customtkinter
import serial
import serial.tools.list_ports

# Calling value used in slider
cat = 0
def getfluff(value):
    global cat
    cat = int(value)
    slidercat(int(value))
    # return cat

# entry box
def sliderbetter(entry):
    global cat
    cat = (entry.get())
    if cat != "":
        cat = re.sub("[^0-9]", "", cat)
        anotherline = int(cat)
        if not 0 <= anotherline <= 200:
            if anotherline < 0:
                anotherline = 0
            if anotherline > 200:
                anotherline = 200

        entry.set(str(anotherline))
        horizontal.set(anotherline)
        cat = anotherline
    else:
        entry.set('')
        cat = 0

# Calling value used in entry box
def slidercat(yes):
    entry.set(str(int(yes)))

# connect function
def connect():
    global ser
    ser = serial.Serial(port)
    ser.baudrate = 9600
    ser.stopbits = 1
    ser.bytesize = 8
    # if button_measure.state == 'normal':
    ser.write(b'ID0 R\r\n')
    response = ser.readline()
    if response == b'Y\r\n':
        print("Device successfully identified")
    else:
        print("Error: Device not identified")
    # writing to serial com to get response
    ser.write(b'W\r\n')
    response1 = ser.readline()
    ser.write(b'S\r\n')
    time.sleep(0.1)
    ser.write(b'S\r\n')
    time.sleep(0.1)
    ser.write(b'S\r\n')
    if response1 == b'S\r\n':
        print("Respond1", response1)


# close function
def close():
    ser.close()
    sys.exit()


# popup to tell user to press switch
def popup():
    result = askyesno(title="Caution", message="Please press the switch in order to continue with measurements")
    print(result)
    if result:
        button_measure.configure(state="normal")
        button_close.configure(state="normal")
        connect()
    else:
        button_measure.configure(state="disabled")
        button_close.configure(state="disabled")

directory = 0
# directory function
def directoption():
    global directory
    directory = tk.filedialog.askopenfilename(title='Open a file', filetypes=[('csv files', '*.csv')])
    print(directory)
    directory_label(directory)

def directory_label(value):
    label.configure(text=value,font=("Calibri",12))

# measurement function
def measure():
    global cat
    datalist = []
    start_time = time.time()
    for _ in range(cat):
        ser.write(b'S\r\n')
        while True:
            if ser.inWaiting() > 0:
                # read the bytes and convert from binary array to ASCII
                data_str = ser.read(ser.inWaiting()).decode('ascii')
                # print the incoming string without putting a new-line
                # ('\n') automatically after every print()

                # time function
                subtract = time.time() - start_time
                print(data_str, end='')
                data = data_str.removesuffix("\r\n")
                result = [n.isspace() for n in data]
                if len(result) >= 12:
                    if result[1 & 3] == False:
                        data2 = data.replace('  ', ' ').split(' ')
                        data4 = [ele for ele in data2 if ele.strip()]
                        data3 = []
                        for i in data4:
                            # if i == '':
                            data3.append(i.strip())
                        # data2 = [i.strip() for i in data.split(" ")]
                        print(data3)
                        datalist.append([f"{subtract:.2f}"] + data3)
            break
        time.sleep(0.3)

    print(datalist)
    time.sleep(0.5)
    writefile(datalist)


# name and save into a file function



def writefile(measurements):

    ser.write(b'E\r\n')
    open_csv = tkinter.filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('csv files', '*.csv')])

    directory_label(open_csv)

    with open(open_csv, mode='w', newline='') as wam_file:
        file_writer = csv.writer(wam_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(["WAM5500", "DATA-000", "Measured data", "C"])
        for measurement in measurements:
            file_writer.writerow(measurement)
    if not open_csv:
        print("Nothing left to do")
    return open_csv


# graph function
def plot_file():
    global directory
    x = []
    y = []
    directoption()
    with open(directory, 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(row[0])
            y.append(row[2])
    plt.plot(x, y, color='g', linestyle='dashed', label="WAM Measurements")
    plt.xlabel('Time')
    plt.ylabel('Measured data')
    plt.title('WAM Measurement', fontsize=15)
    plt.grid()
    plt.legend()
    plt.show()
    return directory

def combobox_port_selection(event):
    global port
    port = event


app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.resizable(False, False)
app.geometry("600x240")
customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
# customtkinter.set_default_color_theme("blue")
app.wm_iconbitmap()
p1 = ImageTk.PhotoImage(file="essilor-logo-rgb-blue.png")
app.iconphoto(False, p1)

app.title("WAM Interface")

# COM port
port = 'COM10'
# ser = serial.Serial('COM10')
# ser.baudrate = 9600
# ser.stopbits = 1
# ser.bytesize = 8

#  Labels for entry box
label_counter = customtkinter.CTkLabel(master=app, text="Number of measurements:")
label_counter.place(relx=0.45, rely=0.6, anchor=tk.CENTER)
entry = customtkinter.StringVar(value="0")
entry_widget = customtkinter.CTkEntry(app, width=80, textvariable=entry)
entry_widget.place(relx=0.65, rely=0.6, anchor=tk.CENTER)

# slider
horizontal = customtkinter.CTkSlider(master=app, from_=0, to=200, number_of_steps=200,
                                     command=getfluff)
horizontal.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
horizontal.set(0)

entry.trace("w", lambda *args: sliderbetter(entry))


# label for directory for graph
label = customtkinter.CTkLabel(master=app, text="Choose a Directory")
label.place(relx=0.8, rely=0.3, anchor=tk.CENTER)

# connect button
button_CnS = customtkinter.CTkButton(master=app, text="Connect and Standby", command=popup)
button_CnS.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

# measurement button
button_measure = customtkinter.CTkButton(master=app, text="Measurements", command=measure, state='disabled')
button_measure.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

# close button
button_close = customtkinter.CTkButton(master=app, text="Close", command=close, state='disabled')
button_close.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

# directory button
button_dir = customtkinter.CTkButton(master=app, text="Directory", command=directoption)
button_dir.place(relx=0.8, rely=0.4, anchor=tk.CENTER)

# graph button
button4 = customtkinter.CTkButton(master=app, text="Graph", command=plot_file)
button4.place(relx=0.2, rely=0.4, anchor=tk.CENTER)

ports = serial.tools.list_ports.comports()
com_list = [com[0] for com in ports]
print(com_list)
combobox_serial = customtkinter.CTkComboBox(master=app, values=com_list,command=combobox_port_selection)
combobox_serial.set(port)
combobox_serial.place(relx=0.2, rely=0.1, anchor=tk.CENTER)

app.mainloop()
