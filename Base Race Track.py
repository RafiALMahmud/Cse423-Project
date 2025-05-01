from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Camera-related variables
camera_pos = (0, 5, 5)
camera_angle = 0
camera_height = 5
camera_distance = 5
track_follow = False

# Day/Night toggle
is_night = True

# Track parameters
num_segments = 100
outer_radius_x = 8.0
outer_radius_y = 4.0
inner_radius_x = 6.0
inner_radius_y = 2.5
track_height = 0.1

# Terrain parameters
grass_radius_x = 10.0
grass_radius_y = 6.0

# Barriers and trees
barrier_segments = [15, 45, 75]
tree_positions = [(random.uniform(8.5, 9.8) * math.cos(2 * math.pi * i / 30),
                   random.uniform(4.5, 5.8) * math.sin(2 * math.pi * i / 30))
                  for i in range(30)]

# Stars parameters
num_stars = 200
stars = [(random.uniform(-50, 50), random.uniform(10, 40), random.uniform(-50, 50),
          random.uniform(0.5, 1.0)) for _ in range(num_stars)]  # x, y, z, brightness

# Cloud parameters
num_clouds = 15
clouds = [(random.uniform(-30, 30), random.uniform(15, 25), random.uniform(-30, 30),
           random.uniform(1.5, 3.0)) for _ in range(num_clouds)]  # x, y, z, size


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_track():
    # grass
    glColor3f(0.13, 0.55, 0.13)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        glVertex3f(grass_radius_x * math.cos(angle), 0, grass_radius_y * math.sin(angle))
    glEnd()

    # track surface
    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_QUAD_STRIP)
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        glVertex3f(outer_radius_x * math.cos(angle), track_height, outer_radius_y * math.sin(angle))
        glVertex3f(inner_radius_x * math.cos(angle), track_height, inner_radius_y * math.sin(angle))
    glEnd()

    # track lines
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for i in range(0, num_segments, 10):
        angle1 = 2 * math.pi * i / num_segments
        angle2 = 2 * math.pi * (i + 5) / num_segments
        mid_x1 = (outer_radius_x + inner_radius_x) / 2 * math.cos(angle1)
        mid_z1 = (outer_radius_y + inner_radius_y) / 2 * math.sin(angle1)
        mid_x2 = (outer_radius_x + inner_radius_x) / 2 * math.cos(angle2)
        mid_z2 = (outer_radius_y + inner_radius_y) / 2 * math.sin(angle2)
        glVertex3f(mid_x1, track_height + 0.01, mid_z1)
        glVertex3f(mid_x2, track_height + 0.01, mid_z2)
    glEnd()


def draw_barriers():
    for i in barrier_segments:
        angle = 2 * math.pi * i / num_segments
        outer_x = outer_radius_x * math.cos(angle)
        outer_z = outer_radius_y * math.sin(angle)
        inner_x = inner_radius_x * math.cos(angle)
        inner_z = inner_radius_y * math.sin(angle)
        mid_x = (outer_x + inner_x) / 2
        mid_z = (outer_z + inner_z) / 2

        if i % 2 == 0:
            draw_barrier(inner_x, inner_z, mid_x, mid_z)
        else:
            draw_barrier(outer_x, outer_z, mid_x, mid_z)


def draw_barrier(x1, z1, x2, z2):
    glColor3f(1.0, 0.0, 0.0)
    dx, dz = x2 - x1, z2 - z1
    length = math.sqrt(dx * dx + dz * dz)
    nx, nz = -dz / length * 0.2, dx / length * 0.2

  
    glBegin(GL_QUADS)
    glVertex3f(x1 + nx, 0, z1 + nz)
    glVertex3f(x1 - nx, 0, z1 - nz)
    glVertex3f(x2 - nx, 0, z2 - nz)
    glVertex3f(x2 + nx, 0, z2 + nz)

    # Back face 
    glVertex3f(x1 + nx, 1.0, z1 + nz)
    glVertex3f(x2 + nx, 1.0, z2 + nz)
    glVertex3f(x2 - nx, 1.0, z2 - nz)
    glVertex3f(x1 - nx, 1.0, z1 - nz)

    # Sides
    glVertex3f(x1 + nx, 0, z1 + nz)
    glVertex3f(x2 + nx, 0, z2 + nz)
    glVertex3f(x2 + nx, 1.0, z2 + nz)
    glVertex3f(x1 + nx, 1.0, z1 + nz)

    glVertex3f(x1 - nx, 0, z1 - nz)
    glVertex3f(x1 - nx, 1.0, z1 - nz)
    glVertex3f(x2 - nx, 1.0, z2 - nz)
    glVertex3f(x2 - nx, 0, z2 - nz)

    # Ends
    glVertex3f(x1 + nx, 0, z1 + nz)
    glVertex3f(x1 + nx, 1.0, z1 + nz)
    glVertex3f(x1 - nx, 1.0, z1 - nz)
    glVertex3f(x1 - nx, 0, z1 - nz)

    glVertex3f(x2 + nx, 0, z2 + nz)
    glVertex3f(x2 - nx, 0, z2 - nz)
    glVertex3f(x2 - nx, 1.0, z2 - nz)
    glVertex3f(x2 + nx, 1.0, z2 + nz)
    glEnd()


def draw_trees():
    for x, z in tree_positions:
        draw_tree(x, z)


def draw_tree(x, z):
    # trunk
    glColor3f(0.545, 0.271, 0.075)
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 0.1, 0.1, 0.5, 8, 1)

    # leaves
    glColor3f(0.0, 0.39, 0.0)  # Dark green for foliage
    glTranslatef(0.0, 0.0, 0.8)  # Position above the trunk
    glScalef(0.8, 0.8, 0.8)  # Scale the cube to look like foliage
    glutSolidCube(1.0)
    glPopMatrix()


def draw_stars():
    if not is_night:
        return

    # Temporarily disable lighting for stars
    glPushAttrib(GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)

    glPointSize(2.0)
    glBegin(GL_POINTS)
    for x, y, z, brightness in stars:
        # varying brightness slightly (twinkling)
        twinkle = brightness * (0.8 + 0.4 * random.random())
        glColor3f(twinkle, twinkle, twinkle)  #  tars with varying brightness
        glVertex3f(x, y, z)
    glEnd()

    # Restore lighting state
    glPopAttrib()


def draw_clouds():
    if is_night:
        return

    glPushAttrib(GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)

    for x, y, z, size in clouds:
        glPushMatrix()
        glTranslatef(x, y, z)

    
        glColor3f(1.0, 1.0, 1.0)  # White for clouds

        # Main cloud body
        glPushMatrix()
        glScalef(size, size * 0.6, size)
        glutSolidSphere(1.0, 12, 8)
        glPopMatrix()

        # Additional smaller puffs
        offsets = [(1.0, 0.3, 0.0), (-1.0, 0.3, 0.0),
                   (0.0, 0.3, 1.0), (0.0, 0.3, -1.0)]

        for dx, dy, dz in offsets:
            glPushMatrix()
            glTranslatef(dx * size / 2, dy * size / 2, dz * size / 2)
            glScalef(size * 0.7, size * 0.5, size * 0.7)
            glutSolidSphere(0.7, 10, 8)
            glPopMatrix()

        glPopMatrix()

    glPopAttrib()


def draw_car():
    angle = (glutGet(GLUT_ELAPSED_TIME) % 10000) / 10000.0 * 2 * math.pi
    track_x = ((outer_radius_x + inner_radius_x) / 2) * math.cos(angle)
    track_z = ((outer_radius_y + inner_radius_y) / 2) * math.sin(angle)

    glPushMatrix()
    glTranslatef(track_x, track_height + 0.1, track_z)
    glRotatef(math.atan2(math.cos(angle), -math.sin(angle)) * 180 / math.pi, 0, 1, 0)
    glColor3f(1.0, 0.0, 0.0)
    glScalef(0.4, 0.1, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()

    if track_follow:
        global camera_pos
        camera_pos = (track_x - (-math.sin(angle)) * 2, 1.0, track_z - math.cos(angle) * 2)


def keyboardListener(key, x, y):
    global track_follow, camera_height, camera_angle, camera_pos, is_night

    if key == b'w': camera_height += 0.5
    if key == b's': camera_height = max(0.5, camera_height - 0.5)
    if key == b'a': camera_angle += 0.1
    if key == b'd': camera_angle -= 0.1
    if key == b'f': track_follow = not track_follow
    if key == b'n': is_night = not is_night  # Toggle between night and day
    if key == b'r':
        camera_pos = (0, 5, 5)
        camera_angle = 0
        camera_height = 5
        track_follow = False


def specialKeyListener(key, x, y):
    global camera_distance
    if key == GLUT_KEY_UP: camera_distance = max(2, camera_distance - 0.5)
    if key == GLUT_KEY_DOWN: camera_distance += 0.5


def mouseListener(button, state, x, y):
    pass


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.25, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Update lighting based on day/night setting
    if is_night:
        # Night lighting (dimmer, more blue)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.6, 0.6, 0.8, 1.0])
    else:
        # Day lighting (brighter, more yellow)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.98, 0.8, 1.0])
        # Set light position to simulate sunlight
        glLightfv(GL_LIGHT0, GL_POSITION, [0.5, 1.0, 0.0, 0.0])

    x, y, z = camera_pos
    if track_follow:
        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)
    else:
        cam_x = math.sin(camera_angle) * camera_distance
        cam_z = math.cos(camera_angle) * camera_distance
        gluLookAt(cam_x, camera_height, cam_z, 0, 0, 0, 0, 1, 0)


def showScreen():
    # Set background color based on time of day
    if is_night:
        glClearColor(0.0, 0.0, 0.2, 1.0)  # Dark blue for night
    else:
        glClearColor(0.53, 0.81, 0.92, 1.0)  # Sky blue for day

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    # Draw sky elements first (background)
    draw_stars()  # Will only draw if is_night is True
    draw_clouds()  # Will only draw if is_night is False

    
    draw_track()
    draw_barriers()
    draw_trees()
    draw_car()  

    
    draw_text(10, 770, "3D Racing Track (No Depth Buffer)")
    draw_text(10, 740, "Controls: WASD - Move, F - Follow, R - Reset, N - Toggle Day/Night")

    # Display current mode
    mode_text = "Night Mode" if is_night else "Day Mode"
    draw_text(850, 770, mode_text)

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Racing Track Without Depth Test")



    # Simple lighting setup
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Different lighting for day and night modes
    # Initial setup is for night mode (will be updated in the display function)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(showScreen)

    glutMainLoop()


if __name__ == "__main__":
    main()
