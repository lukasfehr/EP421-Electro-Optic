import argparse
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style
import matplotlib.animation as mani
from PIL import ImageTk, Image

from dial import Dial, DiscreteDial

import tkinter as tk

parser = argparse.ArgumentParser(description='Run EP421 electro-optic experiment')
parser.add_argument('--offline', action='store_true')
offline = parser.parse_args().offline

style.use("ggplot")

FONT = ("Arial", 8)

distance_1 = 100
distance_2 = 30

jones_polaroid_vertical = np.array([[[1., 0.], [0., 0.]]])
jones_polaroid_horizontal = np.array([[[0., 0.], [0., 1.]]])


if offline:
    border = 4
    dial_height = 43
else:
    border = 6
    dial_height = 45


def jones_polaroid(angle):
    rad = np.deg2rad(angle)
    cos = np.cos(rad)
    sin = np.sin(rad)
    M = np.zeros((2, 2), dtype=np.complex)
    M[0, 0] = cos * cos
    M[0, 1] = M[1, 0] = sin * cos
    M[1, 1] = sin * sin
    return M

def jones_qwp(angle):
    rad = np.deg2rad(angle)
    cos = np.cos(rad)
    sin = np.sin(rad)
    M = np.zeros((2, 2), dtype=np.complex)
    M[0, 0] = cos * cos + 1j * sin * sin
    M[0, 1] = M[1, 0] = (1 - 1j) * sin * cos
    M[1, 1] = sin * sin + 1j * cos * cos
    M *= np.exp(-0.25j * np.pi)
    return M

def jones_crystal(phase):
    # angle locked at 45 for now
    phase = phase.reshape(1, 1, -1)
    M = np.zeros((phase.shape[2], 2, 2), dtype=np.complex)
    M[:, 0, 0] = M[:, 1, 1] = np.cos(0.5 * phase)
    M[:, 0, 1] = M[:, 1, 0] = -1j * np.sin(0.5 * phase)
    return M

class ImageCanvas:
    def __init__(self, master, image_path, column, row, columnspan=1, rowspan=1, width=distance_1, height=distance_1, bg='black', **kwargs):
        img = Image.open(image_path)
        blank = Image.open('imgs/blank.jpg')
        if width is not None and height is not None:
            img = img.resize((width-border, height-border), Image.ANTIALIAS)
            blank = blank.resize((width-border, height-border), Image.ANTIALIAS)
        else:
            width = img.width + 10
            height = img.height + 10
            blank = blank.resize((img.width, img.height), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.blank = ImageTk.PhotoImage(blank)
        self.canvas = tk.Canvas(master, width=width, height=height, bg=bg, **kwargs)
        self.canvas.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
        self.canvas_image = self.canvas.create_image(4, 4, anchor=tk.NW, image=self.img)
        self.visible = True

    def swap(self):
      if self.visible:
          self.canvas.itemconfig(self.canvas_image, image=self.blank)
          self.visible = False
      else:
          self.canvas.itemconfig(self.canvas_image, image=self.img)
          self.visible = True


class CenteredLabel:
    def __init__(self, master, label, column, row, columnspan=1, rowspan=1):
        self.label = tk.Label(master, text=label, font=FONT)
        self.label.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan, sticky='NESW')

class VerticalLabel:
    def __init__(self, master, label, height, width, column, row, columnspan=1, rowspan=1):
        self.canvas = tk.Canvas(master, height=height, width=width)
        self.canvas.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
        self.canvas.create_text(1, height//2, text=label, anchor=tk.N, angle=90, font=FONT)

class CanvasArrow:
    def __init__(self, master, column, row, columnspan=1, rowspan=1, width=distance_1, height=distance_1, direction='right'):
        self.canvas = tk.Canvas(master, width=width, height=height)
        self.canvas.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)

        if direction == 'left':
            x1, y1 = width - 1, height // 2
            x2, y2 = 1, height // 2
        elif direction == 'down':
            x1, y1 = width // 2, 1
            x2, y2 = width // 2, height - 1
        elif direction == 'up':
            x1, y1 = width // 2, height - 1
            x2, y2 = width // 2, 1
        else:
            x1, y1 = 1, height // 2
            x2, y2 = width - 1, height // 2

        self.canvas.create_line(x1, y1, x2, y2, fill='black', arrow='last', width=5)


class ToggleButton:
    def __init__(self, master, text, column=None, row=None, image_path=None, columnspan=1, rowspan=1, light=True, command=None, height=dial_height, width=60):
        self.frame = tk.Frame(master)

        self.command = command

        self.center_frame = tk.Frame(self.frame, height=height, width=width)

        if image_path is not None:
            img = Image.open(image_path)
            img = img.resize((dial_height - border, dial_height - border), Image.ANTIALIAS)
            self.img = ImageTk.PhotoImage(img)
            self.image_canvas = tk.Canvas(self.frame, width=dial_height, height=dial_height, bg='black')
            self.image_canvas.create_image(4, 4, anchor=tk.NW, image=self.img)
        else:
            self.img = None
            self.image_canvas = None

        self.text = text
        self.on = False
        self.button = tk.Button(self.center_frame, text=text, font=FONT, command=self.toggle)
        if light:
            self.light_canvas = tk.Canvas(self.frame, height=dial_height, width=dial_height)
            self.light = self.light_canvas.create_oval(dial_height * 0.25 - 1, dial_height * 0.25 - 1, dial_height * 0.75 - 1, dial_height * 0.75 - 1, fill='grey')
        else:
            self.light_canvas = None
            self.light = None

        self.button.grid(row=1, column=1)

        if image_path is not None: self.image_canvas.pack(side=tk.LEFT)
        self.center_frame.pack(side=tk.LEFT)
        if light: self.light_canvas.pack(side=tk.LEFT)

        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_columnconfigure(2, weight=1)
        self.center_frame.grid_rowconfigure(2, weight=1)
        self.center_frame.grid_propagate(0)

        if row is None or column is None: self.frame.pack(side=tk.TOP, anchor=tk.NW)
        else: self.frame.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)

    def toggle(self):
        if self.on:
            self.on = False
            self.light_canvas.itemconfig(self.light, fill='grey')
        else:
            self.on = True
            self.light_canvas.itemconfig(self.light, fill='green')
        if self.command is not None:
            self.command(self.on)

    def reset(self):
        self.on = False
        self.light_canvas.itemconfig(self.light, fill='grey')


class StateButton:
    def __init__(self, master, num_states, column, row, columnspan=1, rowspan=1, btn_label=None, labels=None, initState=0, command=None):
        assert(initState >= 0)
        assert(initState < num_states)

        self.frame = tk.Frame(master)
        self.frame.grid(row=row, column=column, columnspan=1, rowspan=1)

        self.num_states = num_states
        self.initState = initState
        self.state = initState
        self.label = btn_label
        self.labels = labels

        self.button = tk.Button(self.frame, text=self.label, command=self.command)
        if self.labels is not None:
            self.entry = tk.Entry(self.frame, width=5, justify='left', state='readonly', font=FONT)
            self.insert_entry(self.labels[self.state])

        self.button.pack(side=tk.LEFT)
        if self.labels is not None: self.entry.pack(side=tk.LEFT)

        self.user_command = command if command is not None else lambda state: None

    def command(self):
        self.state += 1
        if self.state >= self.num_states:
            self.state = 0
        self.insert_entry(self.labels[self.state])
        self.user_command(self.state)

    def insert_entry(self, text):
        self.entry.configure(state='normal')
        self.entry.delete(0, tk.END)
        self.entry.insert(tk.END, text)
        self.entry.configure(state='readonly')


class LabelledDial:
    def __init__(self, master, image_path, label, width, column, row, values, continuous=True, columnspan=1, rowspan=1, interval=None, unit='', maxRot=5, precision=0, secondary=None):
        self.frame = tk.Frame(master)
        self.frame.pack(side=tk.TOP, anchor=tk.NW)

        self.center_frame = tk.Frame(self.frame, height=dial_height, width=60)
        self.bottom_frame = tk.Frame(self.center_frame)
        self.right_frame = tk.Frame(self.frame, height=dial_height, width=dial_height)

        img = Image.open(image_path)
        img = img.resize((dial_height - border, dial_height - border), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.canvas = tk.Canvas(self.frame, width=dial_height, height=dial_height, bg='black')
        self.canvas.create_image(4, 4, anchor=tk.NW, image=self.img)

        self.last_degree = 0
        self.rotations = 0
        self.degree = 0
        # self.entry = entry
        self.values = values
        self.continuous = continuous
        self.interval = interval

        self.precision = precision
        self.label = tk.Label(self.center_frame, text=label, font=FONT)
        self.entry = tk.Entry(self.bottom_frame, width=width, justify='right', state='readonly', font=FONT)
        self.unit = tk.Label(self.bottom_frame, text=unit, font=FONT)

        if continuous:
            assert(len(values) == 2)
            self.m = (self.values[1] - self.values[0]) / (720.0 * maxRot)
            self.b = 0.5 * (self.values[0] + self.values[1])
            self.dial = Dial(self.right_frame, radius=f'{dial_height * 0.004:.2f}i', maxRot=maxRot, command=self.command_continuous, zeroAxis='y', rotDir='clockwise')
            self.init = self.b
            self.state = self.b
        else:
            assert(len(values) > 0)
            angles = [-180. + 360. * i / (len(values) + 1) for i in range(1, len(values) + 1)]
            self.dial = DiscreteDial(self.right_frame, angles=angles, initAngleIndex=len(values)//2, radius=f'{dial_height * 0.004:.2f}i', command=self.command_discrete, zeroAxis='y', rotDir='clockwise')
            self.init = self.values[len(values)//2]
            self.state = self.values[len(values)//2]
        # self.dial.widget.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)
        self.insert_entry()

        self.entry.pack(side=tk.LEFT)
        self.unit.pack(side=tk.LEFT)

        self.label.pack(anchor=tk.NW)
        self.bottom_frame.pack(anchor=tk.NW)

        self.canvas.pack(side=tk.LEFT)
        self.center_frame.pack(side=tk.LEFT)
        self.right_frame.pack(side=tk.LEFT)

        self.dial.widget.grid(column=1, row=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(2, weight=1)

        self.center_frame.pack_propagate(0)
        self.right_frame.grid_propagate(0)

        self.secondary_function = secondary # function to calculate a secondary value whenever the dial moves
        self.secondary_value = None
        if self.secondary_function is None:
            self.secondary_value = None
        else:
            self.secondary_value = self.secondary_function(self.state)

    def command_continuous(self, deg):
        self.state = self.m * deg + self.b
        self.insert_entry()
        if self.secondary_function is not None:
            self.secondary_value = self.secondary_function(self.state)

    def command_discrete(self, index):
        assert(index < len(self.values))
        self.state = self.values[index]
        self.insert_entry()

    def insert_entry(self):
        self.entry.configure(state='normal')
        self.entry.delete(0, tk.END)
        if self.precision == 0:
            self.entry.insert(tk.END, f'{self.state:.0f}')
        elif self.precision == 1:
            self.entry.insert(tk.END, f'{self.state:.1f}')
        self.entry.configure(state='readonly')


class Oscilliscope:
    def __init__(self, master, column, row, columnspan=1, rowspan=1):
        dpi = 100
        width = 600 / dpi
        height = 280 / dpi
        self.f = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.f.add_subplot(111)
        self.f.subplots_adjust(left=0, right=1, bottom=0, top=1)

        self.tkfig = FigureCanvasTkAgg(self.f, master)
        self.tkfig.get_tk_widget().grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan)

window = tk.Tk()

# set title
window.title("Title")

# optical bench labels
label_row_1 = 1
laser_label = CenteredLabel(window, 'Laser', column=2, row=label_row_1)
polarizer_label = CenteredLabel(window, 'Polarizer', column=3, row=label_row_1)
modulator_label = CenteredLabel(window, 'Electro-Optic\nModulator', column=4, row=label_row_1)
qwp_label = CenteredLabel(window, 'Quarter Wave\nPlate', column=5, row=label_row_1)
analyzer_label = CenteredLabel(window, 'Analyzer', column=6, row=label_row_1)
detector_label = CenteredLabel(window, 'Photodetector', column=7, row=label_row_1)

# optical bench
optical_bench_row = 2
bench_label = VerticalLabel(window, 'Optical Bench', height=distance_1, width=15, column=1, row=optical_bench_row)
laser = ImageCanvas(window, image_path='imgs/laser.jpg', column=2, row=optical_bench_row)
polarizer = ImageCanvas(window, image_path='imgs/polaroid.jpg', column=3, row=optical_bench_row)
modulator = ImageCanvas(window, image_path='imgs/modulator.jpg', column=4, row=optical_bench_row)
qwp = ImageCanvas(window, image_path='imgs/qwp.jpg', column=5, row=optical_bench_row)
qwp.swap()
analyzer = ImageCanvas(window, image_path='imgs/polaroid.jpg', column=6, row=optical_bench_row)
detector = ImageCanvas(window, image_path='imgs/photodetector.jpg', column=7, row=optical_bench_row)

# arrows showing signal/power propagation
equipment_row = 5
optical_bench_settings_row = optical_bench_row + 1
signal_to_hva = CanvasArrow(window, column=3, row=equipment_row, width=distance_1, height=distance_1, direction='right')
hva_to_mod = CanvasArrow(window, column=4, row=optical_bench_settings_row, width=distance_1, height=distance_2, direction='up')
hva_to_osc = CanvasArrow(window, column=5, row=equipment_row, width=2*distance_1, height=distance_1, direction='right', columnspan=2)
det_to_osc = CanvasArrow(window, column=7, row=optical_bench_settings_row, width=distance_1, height=distance_2, direction='down')

# equipment
signal = ImageCanvas(window, image_path='imgs/signal-generator.jpg', column=2, row=equipment_row)
amplifier = ImageCanvas(window, image_path='imgs/amplifier.jpg', column=4, row=equipment_row)
oscilliscope = ImageCanvas(window, image_path='imgs/osc.jpg', column=7, row=equipment_row)

# equipment labels
label_row_2 = 6
laser_label = CenteredLabel(window, 'Signal Generator', column=2, row=label_row_2)
polarizer_label = CenteredLabel(window, 'Amplifier With\nDC Bias', column=4, row=label_row_2)
modulator_label = CenteredLabel(window, 'Oscilliscope', column=7, row=label_row_2)

# window.grid_rowconfigure(8, minsize=10)
osc = Oscilliscope(window, column=2, row=9, columnspan=6)

# equipment settings
dial_frame = tk.Frame(window)
dial_frame.grid(column=8, row=1, rowspan=9)

qwp_button = ToggleButton(dial_frame, image_path='imgs/qwp.jpg', text='QWP', command=lambda state: qwp.swap())
qwp_angle = LabelledDial(dial_frame, image_path='imgs/qwp.jpg', label='Angle', width=5, column=0, row=0, values=[0, 90], continuous=True, unit=u'\u00b0', maxRot=1, precision=1, secondary=jones_qwp)
signal_amplitude = LabelledDial(dial_frame, image_path='imgs/signal-generator.jpg', label='Amplitude', width=5, column=0, row=0, values=[0, 50], continuous=True, unit='V', maxRot=1, precision=1)
signal_frequency = LabelledDial(dial_frame, image_path='imgs/signal-generator.jpg', label='Frequency', width=5, column=0, row=1, values=[0.01, 50], continuous=True, unit='kHz', maxRot=1, precision=1)
amplifier_offset = LabelledDial(dial_frame, image_path='imgs/amplifier.jpg', label='DC Offset', width=5, column=0, row=2, values=[-200, 200], continuous=True, unit='V', maxRot=2, precision=1)
ch1_toggle = ToggleButton(dial_frame, image_path='imgs/osc.jpg', text='CH1')
ch1_interval_dial = LabelledDial(dial_frame, image_path='imgs/osc.jpg', label='Division', width=5, column=0, row=4, values=[10, 20, 50, 100, 200, 500, 1000, 2000, 5000], continuous=False, unit='mV')
ch1_center_dial = LabelledDial(dial_frame, image_path='imgs/osc.jpg', label='Center', width=5, column=0, row=5, values=[-25e3, 25e3], continuous=True, interval=ch1_interval_dial, unit='mV')
ch2_toggle = ToggleButton(dial_frame, image_path='imgs/osc.jpg', text='CH2')
ch2_interval_dial = LabelledDial(dial_frame, image_path='imgs/osc.jpg', label='Division', width=5, column=0, row=7, values=[10, 20, 50, 100, 200, 500, 1000, 2000, 5000], continuous=False, unit='mV')
ch2_center_dial = LabelledDial(dial_frame, image_path='imgs/osc.jpg', label='Center', width=5, column=0, row=8, values=[-25e3, 25e3], continuous=True, interval=ch2_interval_dial, unit='mV')
t_interval_dial = LabelledDial(dial_frame, image_path='imgs/osc.jpg', label='Time', width=5, column=0, row=9, values=[10, 20, 50, 100, 200], continuous=False, unit=u'\u03BCs')

window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(10, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(8, weight=1)

def animate(i):
    n = 1001
    omega = 2e3 * np.pi * signal_frequency.state
    vmod = signal_amplitude.state
    dcbias = amplifier_offset.state
    tint = t_interval_dial.state

    t_display = np.linspace(-1, 1, n)
    t_true = np.linspace(-1, 1, n) * 5e-6 * tint

    osc.ax.clear()

    ch1_ctr = ch1_center_dial.state
    ch1_int = ch1_interval_dial.state

    m1 = 250. / ch1_int
    b1 = -ch1_ctr / (4 * ch1_int)

    vin_true = dcbias + vmod * np.sin(omega * t_true)
    # vin_true += np.random.normal(0.0, 0.500, n)

    if ch1_toggle.on:
        vin_monitor = vin_true * 0.05
        vin_display = vin_monitor * m1 + b1
        osc.ax.plot(t_display, vin_display, 'y')

    if ch2_toggle.on:
        ch2_ctr = ch2_center_dial.state
        ch2_int = ch2_interval_dial.state

        m2 = 250.0 / ch2_int
        b2 = -ch2_ctr / (4 * ch2_int)

        vout_min = -210 / 1000 # voltage corresponding to 0 transmittance in volts
        vout_max = 460 / 1000 # voltage corresponding to 1 transmittance in volts
        vout_center = 0.5 * (vout_min + vout_max)
        vout_amplitude = (vout_max - vout_min) / 2
        halfwave = 223.6 # half wave voltage in volts
        offset = 170.3 # + max(0, qwp_button.state - 1) * halfwave / 2

        phase = np.pi * (vin_true + offset) / halfwave
        j_crystal = jones_crystal(phase)
        j_qwp = qwp_angle.secondary_value if qwp_button.on else np.eye(2, dtype=np.complex)
        j_total = j_qwp @ j_crystal
        transmittance = np.abs(j_total[:, 1, 0])**2
        vout_true = transmittance * vout_amplitude + vout_center

        vout_display = vout_true * m2 + b2

        osc.ax.plot(t_display, vout_display, 'b')

    osc.ax.set_xlim(-1, 1)
    osc.ax.set_ylim(-1, 1)

def reset_command():
    qwp_button.reset()
    qwp_angle.dial.reset()
    signal_amplitude.dial.reset()
    signal_frequency.dial.reset()
    amplifier_offset.dial.reset()
    ch1_toggle.reset()
    ch1_interval_dial.dial.reset()
    ch1_center_dial.dial.reset()
    ch2_toggle.reset()
    ch2_interval_dial.dial.reset()
    ch2_center_dial.dial.reset()
    t_interval_dial.dial.reset()

reset = tk.Button(dial_frame, text='RESET', width=5, height=1, command=reset_command)
reset.pack()

# start the main application loop
window.geometry('800x600') # pixels
window.resizable(0, 0)
ani = mani.FuncAnimation(osc.f, animate, interval=500)
window.mainloop()
