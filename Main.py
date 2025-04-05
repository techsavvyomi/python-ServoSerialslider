import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import os
import sys
import json

arduino = None
warning_shown = False
servo_sliders = []
angle_label_var = []

def resource_path(relative_path):
    try:
        # PyInstaller will unpack to this location
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def safe_exit():
    global arduino
    if arduino:
        for i in range(9):
            min_val = servo_limits[i][0]
            send_servo_command(i, min_val)
        arduino.flush()
        arduino.close()
        arduino = None
    root.destroy()

# Load config
def load_servo_limits():
    config_path = resource_path("servo_limits.json")
    try:
        with open(config_path, "r") as f:
            data = json.load(f)
            return data.get("servo_limits", [(0, 180)] * 9)
    except Exception as e:
        print(f"[Warning] Could not load config: {e}")
        return [(0, 180)] * 9

servo_limits = load_servo_limits()

# Send command
def send_servo_command(servo_num, angle):
    global arduino, warning_shown
    if not arduino:
        if not warning_shown:
            messagebox.showerror("Error", "Arduino not connected.")
            warning_shown = True
        return
    try:
        angle = int(float(angle))
        command = f"{servo_num} {angle}\n"
        arduino.write(command.encode())
        print(f"[Sent] {command.strip()}")
    except Exception as e:
        if not warning_shown:
            messagebox.showerror("Error", f"Lost connection: {e}")
            warning_shown = True

# Update label
def update_servo_labels():
    for i in range(9):
        angle_label_var[i].set(f"{int(float(servo_sliders[i].get()))}°")

# Clear and reset servos
def clear_all_sliders():
    for i in range(9):
        min_val = servo_limits[i][0]
        servo_sliders[i].set(min_val)
        send_servo_command(i, min_val)
    update_servo_labels()

# Connect / Disconnect
def toggle_connection():
    global arduino, warning_shown
    if arduino:
        for i in range(9):
            min_val = servo_limits[i][0]
            send_servo_command(i, min_val)
        arduino.flush()
        arduino.close()
        arduino = None
        toggle_button.config(text="Connect")
        update_status_circle("red")
        messagebox.showinfo("Disconnected", "Disconnected from Arduino.")
    else:
        port = serial_port_var.get()
        baud = baud_rate_var.get()
        try:
            arduino = serial.Serial(port, baud)
            warning_shown = False
            clear_all_sliders()
            toggle_button.config(text="Disconnect")
            update_servo_labels()
            update_status_circle("green")
            messagebox.showinfo("Connected", f"Connected to {port} at {baud} baud.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")
            update_status_circle("red")


# Status circle
def update_status_circle(color):
    status_canvas.itemconfig(status_circle, fill=color)

# Refresh port list
def refresh_ports():
    ports = [p.device for p in serial.tools.list_ports.comports()]
    serial_port_dropdown["values"] = ports
    if ports:
        serial_port_var.set(ports[0])
    else:
        serial_port_var.set("")

# GUI setup
root = tk.Tk()
root.title("P-Arm Servo Controller")

# Serial settings
serial_frame = ttk.Frame(root)
serial_frame.pack(padx=20, pady=10)

ttk.Label(serial_frame, text="Serial Port:").grid(row=0, column=0, padx=5, pady=5)
serial_port_var = tk.StringVar()
serial_port_dropdown = ttk.Combobox(serial_frame, textvariable=serial_port_var)
serial_port_dropdown.grid(row=0, column=1, padx=5, pady=5)

refresh_button = ttk.Button(serial_frame, text="Refresh", command=refresh_ports)
refresh_button.grid(row=0, column=2, padx=5, pady=5)

ttk.Label(serial_frame, text="Baud Rate:").grid(row=1, column=0, padx=5, pady=5)
baud_rate_var = tk.StringVar(value="9600")
baud_rate_entry = ttk.Entry(serial_frame, textvariable=baud_rate_var)
baud_rate_entry.grid(row=1, column=1, padx=5, pady=5)

toggle_button = ttk.Button(serial_frame, text="Connect", command=toggle_connection)
toggle_button.grid(row=1, column=2, padx=5, pady=5)

# Connection status
status_frame = ttk.Frame(root)
status_frame.pack(pady=5)
ttk.Label(status_frame, text="Status:").pack(side="left", padx=5)
status_canvas = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
status_circle = status_canvas.create_oval(2, 2, 18, 18, fill="red")
status_canvas.pack(side="left")

# Sliders
slider_frame = ttk.Frame(root)
slider_frame.pack(padx=20, pady=10)

for i in range(9):
    min_val, max_val = servo_limits[i]
    ttk.Label(slider_frame, text=f"Servo {i}").grid(row=i, column=0, padx=5, pady=2)

    slider = ttk.Scale(slider_frame, from_=min_val, to=max_val, orient="horizontal")
    slider.grid(row=i, column=1, padx=5, pady=2, sticky="we")
    slider.configure(command=lambda val, idx=i: (send_servo_command(idx, val), update_servo_labels()))
    servo_sliders.append(slider)

    angle_var = tk.StringVar()
    angle_label = ttk.Label(slider_frame, textvariable=angle_var)
    angle_label.grid(row=i, column=2, padx=5)
    angle_label_var.append(angle_var)

# Control buttons
clear_button = ttk.Button(root, text="Clear All", command=clear_all_sliders)
clear_button.pack(pady=5)

exit_button = ttk.Button(root, text="Exit", command=safe_exit)
exit_button.pack(pady=5)

refresh_ports()
root.mainloop()
