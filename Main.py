import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports

# Initialize the Arduino variable globally
arduino = None
warning_shown = False  # To avoid multiple popups when Arduino is not connected

# Hardcoded servo limits
servo_limits = [
    (0, 180),  # Servo 0
    (0, 180),  # Servo 1
    (0, 180),  # Servo 2
    (0, 180),  # Servo 3
    (0, 180),  # Servo 4
    (0, 180),  # Servo 5
    (0, 180),  # Servo 6
    (0, 180),  # Servo 7
    (0, 180)   # Servo 8
]

# Send servo control command
def send_servo_command(servo_num, angle):
    global arduino, warning_shown
    if not arduino:
        if not warning_shown:
            messagebox.showerror("Error", "Arduino not connected.")
            warning_shown = True
        return
    angle = int(float(angle))
    command = f"{servo_num} {angle}\n"
    try:
        arduino.write(command.encode())
        print(command)
    except:
        if not warning_shown:
            messagebox.showerror("Error", "Lost connection to Arduino.")
            warning_shown = True

# Update angle label
def update_servo_labels():
    if not arduino:
        return
    for i in range(9):
        angle_label_var[i].set(f"{int(float(servo_sliders[i].get()))}°")

# Toggle connection
def toggle_connection():
    global arduino, warning_shown
    if arduino:
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
            warning_shown = False  # Reset warning status
            clear_all_sliders()
            toggle_button.config(text="Disconnect")
            update_servo_labels()
            update_status_circle("green")
            messagebox.showinfo("Connected", f"Connected to {port} at {baud} baud.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
            update_status_circle("red")

# Update status indicator circle
def update_status_circle(color):
    status_canvas.itemconfig(status_circle, fill=color)

# Clear all sliders
def clear_all_sliders():
    for i in range(9):
        servo_sliders[i].set(servo_limits[i][0])
        update_servo_labels()
        send_servo_command(i, servo_limits[i][0])

# GUI Setup
root = tk.Tk()
root.title("P-arm Control")

# Serial setup frame
serial_frame = ttk.Frame(root)
serial_frame.pack(padx=20, pady=10)

available_ports = [port.device for port in serial.tools.list_ports.comports()]

ttk.Label(serial_frame, text="Serial Port:").grid(row=0, column=0, padx=10, pady=5)
serial_port_var = tk.StringVar()
serial_port_dropdown = ttk.Combobox(serial_frame, textvariable=serial_port_var, values=available_ports)
serial_port_dropdown.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(serial_frame, text="Baud Rate:").grid(row=1, column=0, padx=10, pady=5)
baud_rate_var = tk.StringVar(value="9600")
baud_rate_entry = ttk.Entry(serial_frame, textvariable=baud_rate_var)
baud_rate_entry.grid(row=1, column=1, padx=10, pady=5)

# Toggle button
toggle_button = ttk.Button(serial_frame, text="Connect", command=toggle_connection)
toggle_button.grid(row=2, column=0, columnspan=2, pady=5)

# Connection status indicator
status_frame = ttk.Frame(root)
status_frame.pack(pady=5)

ttk.Label(status_frame, text="Status:").pack(side="left", padx=5)
status_canvas = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
status_circle = status_canvas.create_oval(2, 2, 18, 18, fill="red")
status_canvas.pack(side="left")

# Servo sliders frame
slider_frame = ttk.Frame(root)
slider_frame.pack(padx=20, pady=10)

servo_sliders = []
angle_label_var = []

for i in range(9):
    ttk.Label(slider_frame, text=f"Servo {i}").grid(row=i, column=0, padx=5)

    min_val, max_val = servo_limits[i]

    slider = ttk.Scale(slider_frame, from_=min_val, to=max_val, orient="horizontal")
    slider.grid(row=i, column=1, padx=5, pady=2, sticky="we")
    slider.configure(command=lambda val, idx=i: (send_servo_command(idx, val), update_servo_labels()))
    servo_sliders.append(slider)

    angle_var = tk.StringVar()
    angle_label = ttk.Label(slider_frame, textvariable=angle_var)
    angle_label.grid(row=i, column=2, padx=5)
    angle_label_var.append(angle_var)

# Clear button
clear_button = ttk.Button(root, text="Clear All", command=clear_all_sliders)
clear_button.pack(pady=10)

# Exit button
exit_button = ttk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=10)

root.mainloop()
