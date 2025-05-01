from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Window size
width, height = 1000, 800

# Camera-related variables
camera_pos = (0, 5, 5)  # Initial camera position (x, y, z)
camera_angle = 0
camera_height = 5
camera_distance = 5
track_follow = False  # Toggle for camera to follow track

# Track parameters
num_segments = 100
outer_radius_x = 8.0
outer_radius_y = 4.0
inner_radius_x = 6.0
inner_radius_y = 2.5
track_height = 0.1  # Height of the track surface

# Terrain parameters
grass_radius_x = 10.0
grass_radius_y = 6.0

# Barriers placed at specific segments
barrier_segments = [15, 45, 75]

# Generate random tree positions
tree_positions = []
for i in range(30):
    angle = 2 * math.pi * i / 30
    radius_x = random.uniform(8.5, 9.8)
    radius_y = random.uniform(4.5, 5.8)
    x = radius_x * math.cos(angle)
    y = radius_y * math.sin(angle)
    tree_positions.append((x, y))


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, width, 0, height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    # Restore original matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_track():
    # Draw grass background (ground plane)
    glColor3f(0.13, 0.55, 0.13)  # Forest green
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)  # Center point
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        x = grass_radius_x * math.cos(angle)
        y = grass_radius_y * math.sin(angle)
        glVertex3f(x, 0, y)  # Note: y-axis is up in 3D, z is depth
    glEnd()

    # Draw track surface (black asphalt)
    glColor3f(0.1, 0.1, 0.1)  # Dark gray track

    # Draw the track using quad strips
    glBegin(GL_QUAD_STRIP)
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        x1 = outer_radius_x * math.cos(angle)
        z1 = outer_radius_y * math.sin(angle)
        x2 = inner_radius_x * math.cos(angle)
        z2 = inner_radius_y * math.sin(angle)

        # Outer point with slight elevation
        glVertex3f(x1, track_height, z1)
        # Inner point with slight elevation
        glVertex3f(x2, track_height, z2)
    glEnd()

    # Draw the white lines in the middle of the track
    glColor3f(1.0, 1.0, 1.0)  # White
    glLineWidth(2.0)

    glBegin(GL_LINES)
    for i in range(0, num_segments, 10):  # Draw dashed lines
        angle1 = 2 * math.pi * i / num_segments
        angle2 = 2 * math.pi * (i + 5) / num_segments  # Length of line segment

        # Calculate midpoints between inner and outer edge
        mx1 = (outer_radius_x * math.cos(angle1) + inner_radius_x * math.cos(angle1)) / 2
        mz1 = (outer_radius_y * math.sin(angle1) + inner_radius_y * math.sin(angle1)) / 2
        mx2 = (outer_radius_x * math.cos(angle2) + inner_radius_x * math.cos(angle2)) / 2
        mz2 = (outer_radius_y * math.sin(angle2) + inner_radius_y * math.sin(angle2)) / 2

        # Draw line slightly above track surface
        glVertex3f(mx1, track_height + 0.01, mz1)
        glVertex3f(mx2, track_height + 0.01, mz2)
    glEnd()


def draw_barriers():
    for i in barrier_segments:
        angle = 2 * math.pi * i / num_segments

        # Outer and inner points at this segment
        outer_x = outer_radius_x * math.cos(angle)
        outer_z = outer_radius_y * math.sin(angle)
        inner_x = inner_radius_x * math.cos(angle)
        inner_z = inner_radius_y * math.sin(angle)

        # Midpoint between inner and outer
        mid_x = (outer_x + inner_x) / 2
        mid_z = (outer_z + inner_z) / 2

        # Choose randomly to block from inner or outer edge
        if i % 2 == 0:  # Using fixed pattern instead of random for consistency
            draw_barrier(inner_x, inner_z, mid_x, mid_z)
        else:
            draw_barrier(outer_x, outer_z, mid_x, mid_z)


def draw_barrier(x1, z1, x2, z2):
    glColor3f(1.0, 0.0, 0.0)  # Red barrier

    # Calculate direction vector
    dx = x2 - x1
    dz = z2 - z1

    # Calculate perpendicular vector (for width)
    length = math.sqrt(dx * dx + dz * dz)
    nx = -dz / length * 0.2  # Width of barrier
    nz = dx / length * 0.2

    # Draw 3D barrier (extruded rectangle)
    glBegin(GL_QUADS)

    # Front face
    glVertex3f(x1 + nx, 0, z1 + nz)
    glVertex3f(x1 - nx, 0, z1 - nz)
    glVertex3f(x2 - nx, 0, z2 - nz)
    glVertex3f(x2 + nx, 0, z2 + nz)

    # Back face (same as front but elevated)
    glVertex3f(x1 + nx, 1.0, z1 + nz)
    glVertex3f(x2 + nx, 1.0, z2 + nz)
    glVertex3f(x2 - nx, 1.0, z2 - nz)
    glVertex3f(x1 - nx, 1.0, z1 - nz)

    # Connect front and back faces

    # Side 1
    glVertex3f(x1 + nx, 0, z1 + nz)
    glVertex3f(x2 + nx, 0, z2 + nz)
    glVertex3f(x2 + nx, 1.0, z2 + nz)
    glVertex3f(x1 + nx, 1.0, z1 + nz)

    # Side 2
    glVertex3f(x1 - nx, 0, z1 - nz)
    glVertex3f(x1 - nx, 1.0, z1 - nz)
    glVertex3f(x2 - nx, 1.0, z2 - nz)
    glVertex3f(x2 - nx, 0, z2 - nz)

    # End caps
    # End 1
    glVertex3f(x1 + nx, 0, z1 + nz)
    glVertex3f(x1 + nx, 1.0, z1 + nz)
    glVertex3f(x1 - nx, 1.0, z1 - nz)
    glVertex3f(x1 - nx, 0, z1 - nz)

    # End 2
    glVertex3f(x2 + nx, 0, z2 + nz)
    glVertex3f(x2 - nx, 0, z2 - nz)
    glVertex3f(x2 - nx, 1.0, z2 - nz)
    glVertex3f(x2 + nx, 1.0, z2 + nz)

    glEnd()


def draw_trees():
    for (x, z) in tree_positions:
        draw_tree(x, z)


def draw_tree(x, z):
    # Tree trunk (brown cylinder)
    glColor3f(0.545, 0.271, 0.075)  # Brown
    glPushMatrix()
    glTranslatef(x, 0, z)

    # Draw trunk using cylinder - rotate to make it vertical
    glRotatef(-90, 1, 0, 0)  # Rotate 90 degrees around X-axis to point up

    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.1, 0.1, 0.5, 8, 1)  # base radius, top radius, height, slices, stacks

    # Tree foliage (green cone)
    glColor3f(0.0, 0.39, 0.0)  # Dark green
    glTranslatef(0, 0, 0.5)  # Move up to top of trunk
    glutSolidCone(0.4, 1.0, 8, 5)  # base radius, height, slices, stacks

    glPopMatrix()


def draw_car():
    # Get position on track based on time
    angle = (glutGet(GLUT_ELAPSED_TIME) % 10000) / 10000.0 * 2 * math.pi
    # Position car on midpoint of track
    track_x = ((outer_radius_x + inner_radius_x) / 2) * math.cos(angle)
    track_z = ((outer_radius_y + inner_radius_y) / 2) * math.sin(angle)

    # Calculate direction vector tangent to the track
    dir_x = -math.sin(angle)
    dir_z = math.cos(angle)

    glPushMatrix()

    # Position the car
    glTranslatef(track_x, track_height + 0.1, track_z)

    # Rotate car to face direction of travel
    # Calculate rotation angle in degrees
    rotation = math.atan2(dir_z, dir_x) * 180 / math.pi
    glRotatef(rotation, 0, 1, 0)

    # Draw car body (red box)
    glColor3f(1.0, 0.0, 0.0)  # Red
    glScalef(0.4, 0.1, 0.2)  # Scale for car dimensions
    glutSolidCube(1.0)

    glPopMatrix()

    # Update camera position if track follow is enabled
    global camera_pos
    if track_follow:
        # Position camera behind the car
        camera_x = track_x - dir_x * 2
        camera_z = track_z - dir_z * 2
        camera_y = 1.0  # Camera height above track
        camera_pos = (camera_x, camera_y, camera_z)


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Extract camera position
    x, y, z = camera_pos

    # If track follow is enabled, camera looks at the track center
    if track_follow:
        # Look at center of track
        gluLookAt(x, y, z,  # Camera position
                  0, 0, 0,  # Look at center of track
                  0, 1, 0)  # Up vector (y-axis is up)
    else:
        # Orbit camera around center
        camera_x = math.sin(camera_angle) * camera_distance
        camera_z = math.cos(camera_angle) * camera_distance

        gluLookAt(camera_x, camera_height, camera_z,  # Camera position
                  0, 0, 0,  # Look at center of track
                  0, 1, 0)  # Up vector (y-axis is up)


def keyboardListener(key, x, y):
    global track_follow, camera_height, camera_angle, camera_pos

    if key == b'w':  # Move camera up
        camera_height += 0.5

    if key == b's':  # Move camera down
        camera_height = max(0.5, camera_height - 0.5)

    if key == b'a':  # Move camera left (orbit)
        camera_angle += 0.1

    if key == b'd':  # Move camera right (orbit)
        camera_angle -= 0.1

    if key == b'f':  # Toggle camera follow mode
        track_follow = not track_follow

    if key == b'r':  # Reset camera
        camera_pos = (0, 5, 5)
        camera_angle = 0
        camera_height = 5
        track_follow = False


def specialKeyListener(key, x, y):
    global camera_distance

    if key == GLUT_KEY_UP:  # Zoom in
        camera_distance = max(2, camera_distance - 0.5)

    if key == GLUT_KEY_DOWN:  # Zoom out
        camera_distance += 0.5


def mouseListener(button, state, x, y):
    pass  # No specific mouse functionality for now


def idle():
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    setupCamera()

    # Enable depth testing for 3D rendering
    glEnable(GL_DEPTH_TEST)

    # Draw the 3D race track components
    draw_track()
    draw_barriers()
    draw_trees()
    draw_car()

    # Display info text
    draw_text(10, height - 30, "3D Racing Track")
    draw_text(10, height - 60,
              "Controls: W/S - Camera up/down, A/D - Orbit camera, F - Toggle follow mode, R - Reset camera")
    draw_text(10, height - 90, "Arrow keys: Up/Down - Zoom in/out")

    glutSwapBuffers()


# Initialize OpenGL settings
def init():
    glClearColor(0.529, 0.808, 0.922, 1.0)  # Sky blue background
    glEnable(GL_DEPTH_TEST)  # Enable depth testing for 3D
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Set up light 0
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])

    # Enable color material for easier coloring
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Racing Track")

    init()  # Initialize OpenGL settings

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()
