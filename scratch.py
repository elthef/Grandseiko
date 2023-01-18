import tkinter as tk
import serial

root = tk.Tk()

root.geometry("400x500")
root.title("WAM Interface")

textbox = tk.Text(root, font=('Arial', 16))
textbox.pack()
ser = serial.Serial('COM9')
ser.baudrate = 9600
ser.stopbits = 1
ser.bytesize = 8


def click():
    print(ser.name)
    ser.write(b'Y\n\r')
    ser.write(b'W\n\r')

def close():
    ser.close()

button = tk.Button(root, text="Connect", font=('Arial', 18))
button1 = tk.Button(root, text="Close", font=('Arial', 18))
button.config(command=click)
button1.config(command=close)
button.pack(padx=10, pady=10)
button1.pack(padx=10, pady=10)
root.mainloop()
