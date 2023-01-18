import tkinter as tk
import serial
import sys
import time

root = tk.Tk()

root.geometry("100x200")
root.title("WAM Interface")

textbox = tk.Text(root, font=('Arial', 16))
textbox.pack()
ser = serial.Serial('COM9')
ser.baudrate = 9600
ser.stopbits = 1
ser.bytesize = 8


def click():
    ser.write(b'ID0 R\r\n')
    response = ser.readline()

    if response == b'Y\r\n':
        print("Device successfully identified")
    else:
        print("Error: Device not identified")

    ser.write(b'W\r\n')
    response1 = ser.readline()
    ser.write(b'S\r\n')
    time.sleep(0.1)
    ser.write(b'S\r\n')
    time.sleep(0.1)
    ser.write(b'S\r\n')
    # if response1 == b'S\r\n':
    print("Respond1", response1)


def close():
    ser.write(b'E\r\n')
    ser.close()
    sys.exit()


def measure():
    textfile = r'C:\Users\8051\Desktop\drfoo\eyeting.txt'
    textfile = open(textfile, 'w')
    ser.write(b'S\r\n')
    # ser.write(b'S\r\n')
    # ser.write(b'S\r\n')
    # ser.write(b'S\r\n')
    # ser.write(b'S\r\n')
    # ser.write(b'S\r\n')
    # ser.write(b'S\r\n')
    # ser.write(b'S\r\n')
    while True:
        if ser.inWaiting() > 0:
            # read the bytes and convert from binary array to ASCII
            data_str = ser.read(ser.inWaiting()).decode('ascii')
            # print the incoming string without putting a new-line
            # ('\n') automatically after every print()
            print(data_str, end='')
        else:
            break


def readfile():
    textfile = r'C:\Users\8051\Desktop\drfoo\eyeting.txt'

    textfile = open(textfile, 'r')
    textfile.read()
    textfile.close()


def write():
    ting = ser.write(b'S\r\n')
    textfile = r'C:\Users\8051\Desktop\drfoo\eyeting.txt'
    textfile = open(textfile, 'w')
    textfile.write(str(ting))
    textfile.close()
    print(ting)


but = tk.Button(root, text="read", font=('Arial', 18), command=readfile)
but.pack(pady=10)
butt = tk.Button(root, text="write", font=('Arial', 18), command=write)
butt.pack(pady=10)
button = tk.Button(root, text="Connect", font=('Arial', 18))
button1 = tk.Button(root, text="Close", font=('Arial', 18))
button2 = tk.Button(root, text="Measurements", font=('Arial', 18))
button.config(command=click)
button1.config(command=close)
button2.config(command=measure)
button.pack(padx=10, pady=10)
button1.pack(padx=10, pady=10)
button2.pack(padx=10, pady=10)
root.mainloop()
