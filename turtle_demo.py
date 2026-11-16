"""turtle_demo.py - the ORIGINAL eco drawings, written with Python's real `turtle` module.

Run it on your own computer (it opens a window, so it needs a desktop with Tk):

    python turtle_demo.py

Why two versions? Streamlit Cloud is a server with no screen, so the real `turtle`
window cannot open there. The web app therefore uses `turtle_art.py`, which has the
SAME commands (forward, left, right, penup, pendown, goto, circle, begin_fill, end_fill)
but records them and replays the drawing as an animation in the browser.
Docs: https://docs.python.org/3/library/turtle.html
"""
import math
import turtle


def make_pen(color="#3F6B4F", size=4, speed=3):
    """Create a turtle with a colour, pen size and drawing speed."""
    t = turtle.Turtle()
    t.hideturtle()
    t.speed(speed)
    t.pensize(size)
    t.color(color)
    return t


def jump(t, x, y, heading=0):
    """Move without drawing (penup -> goto -> pendown)."""
    t.penup()
    t.goto(x, y)
    t.setheading(heading)
    t.pendown()


def draw_leaf(t):
    """A leaf: two matching circle arcs make a pointed oval, then a centre vein and side veins."""
    t.color("#5E9C6B", "#BFE3C0")
    jump(t, -90, -100, 20)        # heading 20 so the leaf points up and to the right (chord at 50 degrees)
    t.begin_fill()
    t.circle(240, 60)             # first edge: an arc that turns left by 60 degrees
    t.left(120)                   # turn at the tip
    t.circle(240, 60)             # second edge brings us back to the start
    t.end_fill()
    t.color("#3F6B4F")
    jump(t, -90, -100, 50)
    t.forward(240)                # centre vein along the chord
    for dist in (70, 120, 170):   # side veins (loop)
        jump(t, -90, -100, 50)
        t.penup(); t.forward(dist); t.pendown()
        t.left(40); t.forward(45)
        t.backward(45); t.right(80); t.forward(45)


def draw_footprint(t):
    """A footprint: an oval sole and five toes."""
    def oval(cx, cy, rx, ry):
        t.penup()
        t.goto(cx + rx, cy)
        t.pendown()
        t.begin_fill()
        for angle in range(0, 361, 15):
            rad = math.radians(angle)
            t.goto(cx + rx * math.cos(rad), cy + ry * math.sin(rad))
        t.end_fill()

    t.color("#5E9C6B", "#BFE3C0")
    oval(0, -40, 52, 92)                                            # sole
    for cx, cy, r in ((-38, 52, 15), (-16, 72, 14), (8, 79, 13), (30, 74, 12), (48, 60, 11)):
        oval(cx, cy, r, r)                                          # toes


def draw_badge(t):
    """A medal: a circle with a five-point star inside."""
    t.color("#E3A857", "#F6E3B4")
    jump(t, 0, -75, 0)
    t.begin_fill()
    t.circle(75)
    t.end_fill()
    t.color("#3F6B4F", "#BFE3C0")
    jump(t, -36, 17, 0)
    t.begin_fill()
    for _ in range(5):            # a star is 5 lines with 144 degree turns
        t.forward(72)
        t.right(144)
    t.end_fill()


if __name__ == "__main__":
    import time

    screen = turtle.Screen()
    screen.setup(640, 520)
    pen = make_pen()
    for name, drawer in (("leaf", draw_leaf), ("footprint", draw_footprint), ("badge", draw_badge)):
        screen.title(f"kindcart. turtle drawing: {name}")
        pen.clear()
        drawer(pen)
        time.sleep(1.5)            # admire it, then draw the next one
    turtle.done()
