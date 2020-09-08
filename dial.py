# Stolen from: http://svn.cgl.ucsf.edu/svn/chimera/trunk/libs/CGLtk/Dial.py
# -----------------------------------------------------------------------------
# Dial widget that shows a turnable knob for setting an angle.
#
import math
import tkinter


# -----------------------------------------------------------------------------
# Radius is in any Tk-acceptable format.
# Command callback takes an angle argument (degrees).
#
class Dial:

    def __init__(self, parent, radius='.5i', command=None, initAngle=0.0,
                 zeroAxis='x', rotDir='counterclockwise', grabAngle=20.0,
                 maxRot=None, fill=None, outline='black', line='black'):

        self.command = command
        self.radius = parent.winfo_pixels(radius)
        self.bump_size = .2 * self.radius
        rpb = self.radius + self.bump_size
        self.center_xy = (rpb, rpb)
        self.rotations = 0
        self.max_rotations = maxRot

        self.grabbed = False
        self.grabAngle = grabAngle

        self.last_angle = 0.0
        self.current_angle = 0.0

        s = int(2 * (self.radius + self.bump_size))
        c = tkinter.Canvas(parent, width=s, height=s)
        c.bind('<ButtonPress-1>', self.button_press_cb)
        c.bind('<Button1-Motion>', self.pointer_drag_cb)
        c.bind('<ButtonRelease-1>', self.button_release_cb)
        cx, cy = self.center_xy
        r = self.radius
        kw = {}
        if fill is not None:
            kw['fill'] = fill
        if outline is not None:
            kw['outline'] = outline
        c.create_oval(cx - r, cy - r, cx + r, cy + r, **kw)
        bs = self.bump_size
        kw = {'width': bs}
        if line is not None:
            kw['fill'] = line
        id = c.create_line(cx, cy, cx + r + bs, cy, **kw)
        self.line_id = id
        self.canvas = c
        self.widget = c
        self.rotDir = rotDir
        self.zeroAxis = zeroAxis
        self.setAngle(initAngle, doCallback=0)

    # ---------------------------------------------------------------------------
    #
    def button_press_cb(self, event):
        try:
            drag_from_angle = self.event_angle(event)
            diff = abs(drag_from_angle - self.last_angle)
            if diff < self.grabAngle or abs(diff - 360) < self.grabAngle:
                self.grabbed = True
            else:
                pass
        except ValueError:
            pass

    # ---------------------------------------------------------------------------
    #
    def pointer_drag_cb(self, event):

        if not self.grabbed:
            return

        try:
            a = self.event_angle(event)
        except ValueError:
            pass
        else:
            self.last_angle = self.current_angle
            self.current_angle = a
            if self.last_angle < 0 and self.current_angle >= 0 and self.current_angle > 90:
                self.rotations -= 1
            elif self.last_angle >=0 and self.current_angle < 0 and self.last_angle > 90:
                self.rotations += 1
            elif self.max_rotations is not None and self.rotations == self.max_rotations and (self.current_angle > 0 or self.last_angle >= 0):
                if self.last_angle >= 0 and self.current_angle <= 0 and self.current_angle > -self.grabAngle:
                    pass
                else:
                    self.current_angle = 0
            elif self.max_rotations is not None and self.rotations == -self.max_rotations and (self.current_angle < 0 or self.last_angle <= 0):
                if self.last_angle <= 0 and self.current_angle >= 0 and self.current_angle < self.grabAngle:
                    pass
                else:
                    self.current_angle = 0

            self.set_angle(self.current_angle)

    # ---------------------------------------------------------------------------
    #
    def button_release_cb(self, event):
        if not self.grabbed:
            return

        try:
            a = self.event_angle(event)
        except ValueError:
            pass
        else:
            self.last_angle = self.current_angle
            self.current_angle = a
            if self.last_angle < 0 and self.current_angle >= 0 and self.current_angle > 90:
                self.rotations -= 1
            elif self.last_angle >=0 and self.current_angle < 0 and self.last_angle > 90:
                self.rotations += 1
            elif self.max_rotations is not None and self.rotations == self.max_rotations and (self.current_angle > 0 or self.last_angle >= 0):
                if self.last_angle >= 0 and self.current_angle <= 0 and self.current_angle > -self.grabAngle:
                    pass
                else:
                    self.current_angle = 0
            elif self.max_rotations is not None and self.rotations == -self.max_rotations and (self.current_angle < 0 or self.last_angle <= 0):
                if self.last_angle <= 0 and self.current_angle >= 0 and self.current_angle < self.grabAngle:
                    pass
                else:
                    self.current_angle = 0
            self.grabbed = False
            self.set_angle(self.current_angle)

    # ---------------------------------------------------------------------------
    #
    def event_angle(self, event):
        # math.atan2 may raise ValueError if dx and dy are zero.
        (x, y) = canvas_coordinates(self.canvas, event)
        (dx, dy) = (x - self.center_xy[0], self.center_xy[1] - y)
        rad = math.atan2(dy, dx)
        deg = 180 * rad / math.pi
        if self.zeroAxis == 'y':
            deg = deg + 270
        elif self.zeroAxis == '-x':
            deg = deg + 180
        elif self.zeroAxis == '-y':
            deg = deg + 90

        if self.rotDir == 'clockwise':
            deg = 360 - deg

        while deg > 180.0:
            deg = deg - 360
        while deg <= -180.0:
            deg = deg + 360
        return deg

    # ---------------------------------------------------------------------------
    #
    def set_angle(self, a, doCallback=1):

        #
        # Move dial pointer
        #
        cx, cy = self.center_xy
        d = self.radius + self.bump_size
        cartesian = a
        if self.rotDir == 'clockwise':
            cartesian = 360 - cartesian
        if self.zeroAxis == 'y':
            cartesian = cartesian + 90
        elif self.zeroAxis == '-x':
            cartesian = cartesian + 180
        elif self.zeroAxis == '-y':
            cartesian = cartesian + 270
        while cartesian > 180.0:
            cartesian = cartesian - 360
        while cartesian <= -180.0:
            cartesian = cartesian + 360
        rad = math.pi * cartesian / 180.0
        ox = d * math.cos(rad)
        oy = d * math.sin(rad)
        self.canvas.coords(self.line_id, cx, cy, cx + ox, cy - oy)

        #
        # Call callback
        #
        if doCallback:
            self.command(a + self.rotations * 360)

    setAngle = set_angle

    def reset(self):
        self.rotations = 0
        self.set_angle(0.0)
        self.current_angle = 0.0
        self.last_angle = 0.0

    

# -----------------------------------------------------------------------------
#
def canvas_coordinates(canvas, event):
    return (canvas.canvasx(event.x), canvas.canvasy(event.y))

class DiscreteDial(Dial):
    def __init__(self, parent, angles, radius='.5i', command=None,
                 initAngleIndex=0, zeroAxis='x', rotDir='counterclockwise',
                 grabAngle=10.0, fill=None, outline='black', line='black'):
        self.discrete_angles = angles # sorted list
        self.region_borders = [-180] + [0.5 * (angles[i] + angles[i + 1]) for i in range(len(angles) - 1)] + [180]
        self.initial_index = initAngleIndex
        self.current_index = initAngleIndex
        self.num_indices = len(self.discrete_angles)
        super().__init__(parent, radius, command, angles[initAngleIndex], zeroAxis, rotDir, grabAngle, None, fill, outline, line)

    def pointer_drag_cb(self, event):

        if not self.grabbed:
            return

        try:
            a = self.event_angle(event)
        except ValueError:
            pass
        else:
            for idx in [self.current_index - 1, self.current_index, self.current_index + 1]:
                if self.in_region(idx, a):
                    self.current_index = idx
                    break

            self.set_angle(self.discrete_angles[self.current_index])

    def button_release_cb(self, event):
        self.pointer_drag_cb(event)

    def set_angle(self, a, doCallback=1):

        #
        # Move dial pointer
        #
        cx, cy = self.center_xy
        d = self.radius + self.bump_size
        cartesian = a
        if self.rotDir == 'clockwise':
            cartesian = 360 - cartesian
        if self.zeroAxis == 'y':
            cartesian = cartesian + 90
        elif self.zeroAxis == '-x':
            cartesian = cartesian + 180
        elif self.zeroAxis == '-y':
            cartesian = cartesian + 270
        while cartesian > 180.0:
            cartesian = cartesian - 360
        while cartesian <= -180.0:
            cartesian = cartesian + 360
        rad = math.pi * cartesian / 180.0
        ox = d * math.cos(rad)
        oy = d * math.sin(rad)
        self.canvas.coords(self.line_id, cx, cy, cx + ox, cy - oy)

        #
        # Call callback
        #
        if doCallback:
            self.command(self.current_index)

    def in_region(self, index, a):
        if index < 0 or index >= self.num_indices: return False
        return a > self.region_borders[index] and a <= self.region_borders[index + 1]

    def reset(self):
        self.current_index = self.initial_index
        self.set_angle(self.discrete_angles[self.initial_index])

if __name__ == '__main__':
    window = tkinter.Tk()

    def command(deg):
        # print(deg)
        pass

    # dial = Dial(window, command=command, maxRot=2, zeroAxis='y', rotDir='clockwise')
    dial = DiscreteDial(window, [-135, -90, -45, -0, 45, 90, 135], initAngleIndex=3, command=command, zeroAxis='y', rotDir='clockwise')
    dial.widget.pack()

    window.mainloop()
