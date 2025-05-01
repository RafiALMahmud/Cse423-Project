from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Camera
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

# Building/Street light
building_positions = tree_positions.copy()

# Cacti positions (reusing the same positions)
cacti_positions = tree_positions.copy()

# Stars parameters
num_stars = 200
stars = [(random.uniform(-50, 50), random.uniform(10, 40), random.uniform(-50, 50),
          random.uniform(0.5, 1.0)) for _ in range(num_stars)]  # x, y, z, brightness

# Cloud parameters
num_clouds = 15
clouds = [(random.uniform(-30, 30), random.uniform(15, 25), random.uniform(-30, 30),
           random.uniform(1.5, 3.0)) for _ in range(num_clouds)]  # x, y, z, size

# Map selection
current_map = 0  # 0 = nature map, 1 = city map, 2 = desert map
map_names = ["Nature Track", "City Track", "Desert Track"]


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
    # Draw ground based on current map
    if current_map == 0:
        # Nature map: grass
        glColor3f(0.13, 0.55, 0.13)
    elif current_map == 1:
        # City map: pavement
        glColor3f(0.4, 0.4, 0.4)
    else:
        # Desert map: sand
        glColor3f(0.86, 0.76, 0.46)

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
    # Change barrier color based on map
    if current_map == 0:
        # Nature map: red barriers
        glColor3f(1.0, 0.0, 0.0)
    elif current_map == 1:
        # City map: yellow and black barriers
        glColor3f(0.9, 0.9, 0.0)
    else:
        # Desert map: orange barriers
        glColor3f(0.8, 0.4, 0.0)

    dx, dz = x2 - x1, z2 - z1
    length = math.sqrt(dx * dx + dz * dz)
    nx, nz = -dz / length * 0.2, dx / length * 0.2

    glBegin(GL_QUADS)
    # Front face
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

    # Add stripes to city barriers
    if current_map == 1:
        glColor3f(0.0, 0.0, 0.0)  # Black stripes
        glBegin(GL_LINES)
        for i in range(5):
            t = i / 4.0
            stripe_x1 = x1 + t * (x2 - x1)
            stripe_z1 = z1 + t * (z2 - z1)
            glVertex3f(stripe_x1 + nx, 0.5, stripe_z1 + nz)
            glVertex3f(stripe_x1 - nx, 0.5, stripe_z1 - nz)
        glEnd()


def draw_trees():
    if current_map == 0:
        # Draw trees in nature map
        for x, z in tree_positions:
            draw_tree(x, z)
    elif current_map == 1:
        # Draw buildings/street lights in city map
        for x, z in building_positions:
            draw_building(x, z)
    else:
        # Draw cacti in desert map
        for x, z in cacti_positions:
            draw_cactus(x, z)


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


def draw_building(x, z):
    rand_seed = x * 1000 + z  # Use position as random seed for consistent buildings
    random.seed(rand_seed)

    height = random.uniform(1.0, 3.0)
    width = random.uniform(0.3, 0.7)

    # 50% chance to draw building, 50% chance to draw street light
    if random.random() > 0.5:
        # Building
        # Base color for the building
        r = random.uniform(0.4, 0.8)
        g = random.uniform(0.4, 0.8)
        b = random.uniform(0.4, 0.8)

        glPushMatrix()
        glTranslatef(x, 0, z)

        # Main building
        glColor3f(r, g, b)
        glPushMatrix()
        glScalef(width, height, width)
        glTranslatef(0, 0.5, 0)  # Move up so bottom is at y=0
        glutSolidCube(1.0)
        glPopMatrix()

        # Windows
        glColor3f(0.9, 0.9, 0.0)  # Yellow windows
        window_size = 0.1
        window_gap = 0.2
        num_floors = int(height / window_gap)

        for floor in range(num_floors):
            y_pos = (floor + 0.5) * window_gap

            # Front windows
            for i in range(2):
                x_pos = (i - 0.5) * window_gap * 2
                glPushMatrix()
                glTranslatef(x_pos, y_pos, width / 2 + 0.01)
                glScalef(window_size, window_size, 0.01)
                glutSolidCube(1.0)
                glPopMatrix()

            # Back windows
            for i in range(2):
                x_pos = (i - 0.5) * window_gap * 2
                glPushMatrix()
                glTranslatef(x_pos, y_pos, -width / 2 - 0.01)
                glScalef(window_size, window_size, 0.01)
                glutSolidCube(1.0)
                glPopMatrix()

            # Side windows
            for i in range(2):
                z_pos = (i - 0.5) * window_gap * 2
                glPushMatrix()
                glTranslatef(width / 2 + 0.01, y_pos, z_pos)
                glScalef(0.01, window_size, window_size)
                glutSolidCube(1.0)
                glPopMatrix()

                glPushMatrix()
                glTranslatef(-width / 2 - 0.01, y_pos, z_pos)
                glScalef(0.01, window_size, window_size)
                glutSolidCube(1.0)
                glPopMatrix()

        glPopMatrix()
    else:
        # Street light
        glPushMatrix()
        glTranslatef(x, 0, z)

        # Pole
        glColor3f(0.2, 0.2, 0.2)  # Dark gray
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.05, 0.05, 1.5, 8, 1)
        glPopMatrix()

        # Light fixture
        glColor3f(0.3, 0.3, 0.3)  # Slightly lighter gray
        glPushMatrix()
        glTranslatef(0, 1.5, 0)
        glScalef(0.2, 0.1, 0.2)
        glutSolidCube(1.0)
        glPopMatrix()

        # Light
        glColor3f(1.0, 1.0, 0.7)  # Warm yellow light
        glPushMatrix()
        glTranslatef(0, 1.4, 0)
        glutSolidSphere(0.1, 8, 8)
        glPopMatrix()

        glPopMatrix()

    # Reset the random seed
    random.seed()


def draw_cactus(x, z):
    rand_seed = x * 1000 + z  # Use position as random seed for consistent cacti
    random.seed(rand_seed)

    # Randomize cactus size
    scale = random.uniform(0.8, 1.2)
    has_arms = random.random() > 0.3  # 70% chance to have arms

    glPushMatrix()
    glTranslatef(x, 0, z)

    # Main cactus body
    glColor3f(0.0, 0.5, 0.0)  # Cactus green
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 0.15 * scale, 0.15 * scale, 1.0 * scale, 8, 1)

    # Top of cactus
    glTranslatef(0, 0, 1.0 * scale)
    glutSolidSphere(0.15 * scale, 8, 8)
    glPopMatrix()

    # Add arms if needed
    if has_arms:
        arm_heights = [0.4 * scale, 0.7 * scale]
        arm_angles = [random.uniform(30, 60), random.uniform(-30, -60)]
        arm_lengths = [random.uniform(0.3, 0.6) * scale, random.uniform(0.3, 0.6) * scale]

        for i in range(2):
            glPushMatrix()
            glTranslatef(0, arm_heights[i], 0)
            glRotatef(arm_angles[i], 0, 0, 1)

            # Arm cylinder
            glColor3f(0.0, 0.5, 0.0)
            gluCylinder(gluNewQuadric(), 0.1 * scale, 0.1 * scale, arm_lengths[i], 8, 1)

            # Arm tip
            glTranslatef(0, 0, arm_lengths[i])
            glutSolidSphere(0.1 * scale, 8, 8)
            glPopMatrix()

    # Add spikes
    glColor3f(0.9, 0.9, 0.7)  # Light yellowish for spikes
    for i in range(8):
        angle = i * 45

        # Spikes on main body
        for h in range(1, 4):
            height = h * 0.25 * scale
            glPushMatrix()
            glTranslatef(0.16 * scale * math.cos(math.radians(angle)),
                         height,
                         0.16 * scale * math.sin(math.radians(angle)))
            glRotatef(90, 0, 1, 0)
            glRotatef(angle, 1, 0, 0)
            glutSolidCone(0.01 * scale, 0.08 * scale, 4, 1)
            glPopMatrix()

    glPopMatrix()

    # Reset the random seed
    random.seed()


def draw_stars():
    if not is_night:
        return

    # Temporarily disable lighting for stars
    glPushAttrib(GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)

    glPointSize(2.0)
    glBegin(GL_POINTS)
    for x, y, z, brightness in stars:
        # varying brightness slightly
        twinkle = brightness * (0.8 + 0.4 * random.random())
        glColor3f(twinkle, twinkle, twinkle)  # White stars with varying brightness
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

    # Car color based on map
    if current_map == 0:
        glColor3f(1.0, 0.0, 0.0)  # Red car for nature map
    elif current_map == 1:
        glColor3f(0.0, 0.3, 0.8)  # Blue car for city map
    else:
        glColor3f(0.8, 0.6, 0.0)  # Golden/tan car for desert map

    # Car body
    glPushMatrix()
    glScalef(0.4, 0.1, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()

    # Car top
    glPushMatrix()
    glTranslatef(0, 0.1, 0)
    glScalef(0.2, 0.1, 0.18)
    glutSolidCube(1.0)
    glPopMatrix()

    # Wheels
    glColor3f(0.2, 0.2, 0.2)
    wheel_positions = [
        (0.15, -0.05, 0.12),
        (0.15, -0.05, -0.12),
        (-0.15, -0.05, 0.12),
        (-0.15, -0.05, -0.12)
    ]

    for wheel_x, wheel_y, wheel_z in wheel_positions:
        glPushMatrix()
        glTranslatef(wheel_x, wheel_y, wheel_z)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 0.05, 0.05, 0.02, 8, 1)
        glPopMatrix()

    glPopMatrix()

    if track_follow:
        global camera_pos
        camera_pos = (track_x - (-math.sin(angle)) * 2, 1.0, track_z - math.cos(angle) * 2)


def keyboardListener(key, x, y):
    global track_follow, camera_height, camera_angle, camera_pos, current_map, is_night

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
    if key == b'm':  # Toggle map
        current_map = (current_map + 1) % len(map_names)


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

    # Update lighting based on day/night and map settings
    if is_night:
        # Night lighting (dimmer, more blue)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.6, 0.6, 0.8, 1.0])
    else:
        if current_map == 2:  # Desert day lighting (brighter, more yellow/orange)
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.4, 0.2, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.9, 0.7, 1.0])
        else:  # Regular day lighting
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
    # Set background color based on time of day and map
    if is_night:
        glClearColor(0.0, 0.0, 0.2, 1.0)  # Dark blue for night
    else:
        if current_map == 2:  # Desert sky is more pale/hazy
            glClearColor(0.85, 0.80, 0.75, 1.0)  # Pale sandy sky for desert day
        else:
            glClearColor(0.53, 0.81, 0.92, 1.0)  # Sky blue for regular day

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    # Draw sky elements first (background)
    draw_stars()  # Will only draw if is_night is True
    draw_clouds()  # Will only draw if is_night is False

    draw_track()
    draw_barriers()
    draw_trees()  # Will draw either trees, buildings, or cacti based on current_map
    draw_car()

    draw_text(10, 770, f"3D Racing Track - {map_names[current_map]} (No Depth Buffer)")
    draw_text(10, 740, "Controls: WASD - Move, F - Follow, R - Reset, M - Toggle Map, N - Toggle Day/Night")

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
