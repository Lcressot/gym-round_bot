import pyglet
# import all of opengl functions
from pyglet.gl import *

win = pyglet.window.Window(15,15)
win.set_visible(False)

@win.event
def on_draw():
    win.clear()
    # create a line context
    glBegin(GL_LINES)
    # create a line, x,y,z
    glVertex3f(2,2,0.25)
    glVertex3f(7,7,-0.75)
    glEnd()
    data = (GLubyte * (3 * win.width * win.height))(0)
    glReadPixels(0, 0, win.width, win.height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, data)
    for i in range(3 * win.width * win.height):
        if data[i] is not 0:
            print(i, data[i])

pyglet.app.run()