from OpenGL.GL import *
from OpenGL.GLUT import *  # Import all GLUT functions
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24  # Explicitly import the fonts
from OpenGL.GLU import *
import math
import random
import time

STATE_MENU = 0
STATE_COUNTDOWN = 1
STATE_RACING = 2
STATE_END_SCREEN = 3
current_game_state = STATE_MENU

difficulty_options = ["Easy", "Medium", "Hard"]
track_options = ["Nature", "City", "Desert"]
vehicle_options = ["Car", "Bike"]

selected_difficulty = -1
selected_track = -1
selected_vehicle = -1
current_section = 0  

window_width = 1000
window_height = 800

countdown_value = -1
showing_countdown = False
countdown_start_time = None 

final_position = 1 
final_lap_time = 93.4

camera_pos = (0, 5, 5)
camera_angle = 0
camera_height = 5
camera_distance = 5
track_follow = False

is_night = False

num_segments = 100
outer_radius_x = 8.0
outer_radius_y = 4.0
inner_radius_x = 6.0
inner_radius_y = 2.5
track_height = 0.1

grass_radius_x = 10.0
grass_radius_y = 6.0

race_start_time = None
race_current_time = 0

barrier_segments = [15, 45, 75]
tree_positions = [(random.uniform(8.5, 9.8) * math.cos(2 * math.pi * i / 30),
                   random.uniform(4.5, 5.8) * math.sin(2 * math.pi * i / 30))
                  for i in range(30)]

building_positions = tree_positions.copy()

cacti_positions = tree_positions.copy()

num_stars = 200
stars = [(random.uniform(-50, 50), random.uniform(10, 40), random.uniform(-50, 50),
          random.uniform(0.5, 1.0)) for _ in range(num_stars)] 

num_clouds = 15
clouds = [(random.uniform(-30, 30), random.uniform(15, 25), random.uniform(-30, 30),
           random.uniform(1.5, 3.0)) for _ in range(num_clouds)] 

car_angle = 0
car_speed = 0
max_speed = 0.3 
acceleration = 0.01 
deceleration = 0.005
turning_speed = 0.05
lap_count = 0
last_angle = 0
passed_start_line = False


def draw_text(x, y, text, r=1.0, g=1.0, b=1.0, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(r, g, b)

    if current_game_state == STATE_MENU or current_game_state == STATE_COUNTDOWN or current_game_state == STATE_END_SCREEN:
        glRasterPos2f(x, y)
    else:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRasterPos2f(x, y)

    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    if current_game_state == STATE_RACING:
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)


def draw_menu():
    section_titles = ["Select Difficulty:", "Select Track:", "Select Vehicle:"]
    options = [difficulty_options, track_options, vehicle_options]
    selected = [selected_difficulty, selected_track, selected_vehicle]
    base_ys = [525, 350, 175]

    for section_index in range(3):
        draw_text(50, base_ys[section_index] + 25, section_titles[section_index], 1.0, 1.0, 0.0)
        for i, option in enumerate(options[section_index]):
            y = base_ys[section_index] - i * 30
            is_selected = (i == selected[section_index])
            is_current_section = (section_index == current_section)
            color = (0.0, 1.0, 0.0) if is_selected and is_current_section else (1.0, 1.0, 1.0)
            draw_text(100, y, option, *color)

    for i, section_index in enumerate(range(3)):
        option_text = options[i][selected[i]] if selected[i] >= 0 else "None"
        color = (1.0, 1.0, 0.0) if selected[i] >= 0 else (1.0, 0.5, 0.5)
        title = section_titles[i].replace(":", "")

        draw_text(250, base_ys[i] + 25, f"Selected {title}: {option_text}", *color)
    y_start_button = 70
    if current_section == 3:
        draw_text(380, y_start_button + 10, "Start Game", 0.0, 1.0, 0.0)
    else:
        draw_text(380, y_start_button + 10, "Start Game", 1.0, 1.0, 1.0)

    draw_text(300, 700, "RACING SIMULATOR", 1.0, 0.5, 0.0, GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(450, 650, "2025", 1.0, 0.7, 0.2)

def draw_countdown():
    countdown_msg = "GO!" if countdown_value == 0 else f"Race starts in {countdown_value}"
    draw_text(350, 300, countdown_msg, 1.0, 0.0, 0.0, GLUT_BITMAP_TIMES_ROMAN_24)

def draw_end_screen():
    draw_text(300, 500, "Race Finished!", 1.0, 1.0, 0.0, GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(250, 420, f"Final Position: {final_position}st", 0.0, 1.0, 0.0)
    draw_text(250, 380, f"Final Lap Time: {final_lap_time:.2f} sec", 0.0, 1.0, 1.0)

    draw_text(250, 320, f"Difficulty: {difficulty_options[selected_difficulty]}", 1.0, 1.0, 1.0)
    draw_text(250, 290, f"Track: {track_options[selected_track]}", 1.0, 1.0, 1.0)
    draw_text(250, 260, f"Vehicle: {vehicle_options[selected_vehicle]}", 1.0, 1.0, 1.0)

    draw_text(250, 180, "Press Enter to return to Menu", 1.0, 0.8, 0.0)


def draw_track():
    if selected_track == 0:
        glColor3f(0.13, 0.55, 0.13)
    elif selected_track == 1:
        glColor3f(0.4, 0.4, 0.4)
    else:
        glColor3f(0.86, 0.76, 0.46)

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        glVertex3f(grass_radius_x * math.cos(angle), 0, grass_radius_y * math.sin(angle))
    glEnd()
    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_QUAD_STRIP)
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        glVertex3f(outer_radius_x * math.cos(angle), track_height, outer_radius_y * math.sin(angle))
        glVertex3f(inner_radius_x * math.cos(angle), track_height, inner_radius_y * math.sin(angle))
    glEnd()
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
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_QUADS)
    start_angle = 0
    width = 0.3
    start_x1 = outer_radius_x * math.cos(start_angle)
    start_z1 = outer_radius_y * math.sin(start_angle)
    start_x2 = inner_radius_x * math.cos(start_angle)
    start_z2 = inner_radius_y * math.sin(start_angle)

    start_x3 = outer_radius_x * math.cos(start_angle + width / outer_radius_x)
    start_z3 = outer_radius_y * math.sin(start_angle + width / outer_radius_y)
    start_x4 = inner_radius_x * math.cos(start_angle + width / inner_radius_x)
    start_z4 = inner_radius_y * math.sin(start_angle + width / inner_radius_y)

    glVertex3f(start_x1, track_height + 0.01, start_z1)
    glVertex3f(start_x2, track_height + 0.01, start_z2)
    glVertex3f(start_x4, track_height + 0.01, start_z4)
    glVertex3f(start_x3, track_height + 0.01, start_z3)
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
    if selected_track == 0:
        glColor3f(1.0, 0.0, 0.0)
    elif selected_track == 1:
        glColor3f(0.9, 0.9, 0.0)
    else:
        glColor3f(0.8, 0.4, 0.0)

    dx, dz = x2 - x1, z2 - z1
    length = math.sqrt(dx * dx + dz * dz)
    nx, nz = -dz / length * 0.2, dx / length * 0.2

    glBegin(GL_QUADS)
    glVertex3f(x1 + nx, 0, z1 + nz)
    glVertex3f(x1 - nx, 0, z1 - nz)
    glVertex3f(x2 - nx, 0, z2 - nz)
    glVertex3f(x2 + nx, 0, z2 + nz)
    glVertex3f(x1 + nx, 1.0, z1 + nz)
    glVertex3f(x2 + nx, 1.0, z2 + nz)
    glVertex3f(x2 - nx, 1.0, z2 - nz)
    glVertex3f(x1 - nx, 1.0, z1 - nz)
    glVertex3f(x1 + nx, 0, z1 + nz)
    glVertex3f(x2 + nx, 0, z2 + nz)
    glVertex3f(x2 + nx, 1.0, z2 + nz)
    glVertex3f(x1 + nx, 1.0, z1 + nz)
    glVertex3f(x1 - nx, 0, z1 - nz)
    glVertex3f(x1 - nx, 1.0, z1 - nz)
    glVertex3f(x2 - nx, 1.0, z2 - nz)
    glVertex3f(x2 - nx, 0, z2 - nz)
    glVertex3f(x1 + nx, 0, z1 + nz)
    glVertex3f(x1 + nx, 1.0, z1 + nz)
    glVertex3f(x1 - nx, 1.0, z1 - nz)
    glVertex3f(x1 - nx, 0, z1 - nz)
    glVertex3f(x2 + nx, 0, z2 + nz)
    glVertex3f(x2 - nx, 0, z2 - nz)
    glVertex3f(x2 - nx, 1.0, z2 - nz)
    glVertex3f(x2 + nx, 1.0, z2 + nz)
    glEnd()

    if selected_track == 1:
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_LINES)
        for i in range(5):
            t = i / 4.0
            stripe_x1 = x1 + t * (x2 - x1)
            stripe_z1 = z1 + t * (z2 - z1)
            glVertex3f(stripe_x1 + nx, 0.5, stripe_z1 + nz)
            glVertex3f(stripe_x1 - nx, 0.5, stripe_z1 - nz)
        glEnd()


def draw_trees():
    if selected_track == 0:
        for x, z in tree_positions:
            draw_tree(x, z)
    elif selected_track == 1:
        for x, z in building_positions:
            draw_building(x, z)
    else:
        for x, z in cacti_positions:
            draw_cactus(x, z)


def draw_tree(x, z):
    glColor3f(0.545, 0.271, 0.075)
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 0.1, 0.1, 0.5, 8, 1)
    glColor3f(0.0, 0.39, 0.0) 
    glTranslatef(0.0, 0.0, 0.8) 
    glScalef(0.8, 0.8, 0.8)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_building(x, z):
    rand_seed = x * 1000 + z  
    random.seed(rand_seed)
    height = random.uniform(1.0, 3.0)
    width = random.uniform(0.3, 0.7)
    if random.random() > 0.5:
        r = random.uniform(0.4, 0.8)
        g = random.uniform(0.4, 0.8)
        b = random.uniform(0.4, 0.8)

        glPushMatrix()
        glTranslatef(x, 0, z)
        glColor3f(r, g, b)
        glPushMatrix()
        glScalef(width, height, width)
        glTranslatef(0, 0.5, 0) 
        glutSolidCube(1.0)
        glPopMatrix()
        glColor3f(0.9, 0.9, 0.0)
        window_size = 0.1
        window_gap = 0.2
        num_floors = int(height / window_gap)

        for floor in range(num_floors):
            y_pos = (floor + 0.5) * window_gap
            for i in range(2):
                x_pos = (i - 0.5) * window_gap * 2
                glPushMatrix()
                glTranslatef(x_pos, y_pos, width / 2 + 0.01)
                glScalef(window_size, window_size, 0.01)
                glutSolidCube(1.0)
                glPopMatrix()

            for i in range(2):
                x_pos = (i - 0.5) * window_gap * 2
                glPushMatrix()
                glTranslatef(x_pos, y_pos, -width / 2 - 0.01)
                glScalef(window_size, window_size, 0.01)
                glutSolidCube(1.0)
                glPopMatrix()

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
        glPushMatrix()
        glTranslatef(x, 0, z)

        glColor3f(0.2, 0.2, 0.2) 
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.05, 0.05, 1.5, 8, 1)
        glPopMatrix()

        glColor3f(0.3, 0.3, 0.3) 
        glPushMatrix()
        glTranslatef(0, 1.5, 0)
        glScalef(0.2, 0.1, 0.2)
        glutSolidCube(1.0)
        glPopMatrix()
        glColor3f(1.0, 1.0, 0.7) 
        glPushMatrix()
        glTranslatef(0, 1.4, 0)
        glutSolidSphere(0.1, 8, 8)
        glPopMatrix()

        glPopMatrix()
    random.seed()


def draw_cactus(x, z):
    rand_seed = x * 1000 + z 
    random.seed(rand_seed)
    scale = random.uniform(0.8, 1.2)
    has_arms = random.random() > 0.3 

    glPushMatrix()
    glTranslatef(x, 0, z)
    glColor3f(0.0, 0.5, 0.0) 
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 0.15 * scale, 0.15 * scale, 1.0 * scale, 8, 1)
    glTranslatef(0, 0, 1.0 * scale)
    glutSolidSphere(0.15 * scale, 8, 8)
    glPopMatrix()

    if has_arms:
        arm_heights = [0.4 * scale, 0.7 * scale]
        arm_angles = [random.uniform(30, 60), random.uniform(-30, -60)]
        arm_lengths = [random.uniform(0.3, 0.6) * scale, random.uniform(0.3, 0.6) * scale]

        for i in range(2):
            glPushMatrix()
            glTranslatef(0, arm_heights[i], 0)
            glRotatef(arm_angles[i], 0, 0, 1)

            glColor3f(0.0, 0.5, 0.0)
            gluCylinder(gluNewQuadric(), 0.1 * scale, 0.1 * scale, arm_lengths[i], 8, 1)

            glTranslatef(0, 0, arm_lengths[i])
            glutSolidSphere(0.1 * scale, 8, 8)
            glPopMatrix()

    glColor3f(0.9, 0.9, 0.7) 
    for i in range(8):
        angle = i * 45

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
    random.seed()


def draw_stars():
    if not is_night:
        return

    glPointSize(2.0)
    glBegin(GL_POINTS)
    for x, y, z, brightness in stars:
        twinkle = brightness * (0.8 + 0.4 * random.random())
        glColor3f(twinkle, twinkle, twinkle) 
        glVertex3f(x, y, z)
    glEnd()


def draw_clouds():
    if is_night:
        return

    for x, y, z, size in clouds:
        glPushMatrix()
        glTranslatef(x, y, z)

        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glScalef(size, size * 0.6, size)
        glutSolidSphere(1.0, 12, 8)
        glPopMatrix()
        offsets = [(1.0, 0.3, 0.0), (-1.0, 0.3, 0.0),
                   (0.0, 0.3, 1.0), (0.0, 0.3, -1.0)]

        for dx, dy, dz in offsets:
            glPushMatrix()
            glTranslatef(dx * size / 2, dy * size / 2, dz * size / 2)
            glScalef(size * 0.7, size * 0.5, size * 0.7)
            glutSolidSphere(0.7, 10, 8)
            glPopMatrix()
        glPopMatrix()


def draw_car(controlled=True):
    global car_angle, car_speed, lap_count, last_angle, passed_start_line
    if controlled:
        track_x = ((outer_radius_x + inner_radius_x) / 2 + car_speed * 5) * math.cos(car_angle)
        track_z = ((outer_radius_y + inner_radius_y) / 2 + car_speed * 5) * math.sin(car_angle)
        if car_angle < 0.1 and last_angle > 6.0 and passed_start_line:
            lap_count += 1
            passed_start_line = False 
        if car_angle > 0.1 and not passed_start_line:
            passed_start_line = True

        last_angle = car_angle
    else:
        angle = (glutGet(GLUT_ELAPSED_TIME) % 10000) / 10000.0 * 2 * math.pi
        track_x = ((outer_radius_x + inner_radius_x) / 2) * math.cos(angle)
        track_z = ((outer_radius_y + inner_radius_y) / 2) * math.sin(angle)
        car_angle = angle 

    glPushMatrix()
    glTranslatef(track_x, track_height + 0.1, track_z)
    glRotatef(math.atan2(math.cos(car_angle), -math.sin(car_angle)) * 180 / math.pi, 0, 1, 0)

    if controlled:
        if selected_vehicle == 0:
            if selected_track == 0:
                glColor3f(1.0, 0.0, 0.0)
            elif selected_track == 1:
                glColor3f(0.0, 0.3, 0.8)  
            else:
                glColor3f(0.8, 0.6, 0.0)  

            glPushMatrix()
            glScalef(0.4, 0.1, 0.2)
            glutSolidCube(1.0)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(0, 0.1, 0)
            glScalef(0.2, 0.1, 0.18)
            glutSolidCube(1.0)
            glPopMatrix()
        else:
            if selected_track == 0:
                glColor3f(0.0, 0.8, 0.0) 
            elif selected_track == 1:
                glColor3f(1.0, 0.0, 0.0)  
            else:
                glColor3f(0.5, 0.5, 0.5)  

            glPushMatrix()
            glScalef(0.3, 0.05, 0.1)
            glutSolidCube(1.0)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(0.15, 0.05, 0)
            glRotatef(-30, 0, 0, 1)
            glScalef(0.1, 0.2, 0.02)
            glutSolidCube(1.0)
            glPopMatrix()
    else:
        glColor3f(0.5, 0.5, 0.5)
        glPushMatrix()
        glScalef(0.4, 0.1, 0.2)
        glutSolidCube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0.1, 0)
        glScalef(0.2, 0.1, 0.18)
        glutSolidCube(1.0)
        glPopMatrix()
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

    if track_follow and controlled:
        global camera_pos
        camera_pos = (track_x - (-math.sin(car_angle)) * 2, 1.0, track_z - math.cos(car_angle) * 2)

    return track_x, track_z


def check_for_race_end():
    global current_game_state, final_lap_time, lap_count

    if lap_count >= 3: 
        current_game_state = STATE_END_SCREEN
        if race_start_time:
            final_lap_time = race_current_time
        return True
    return False

def special_keys(key, x, y):
    global selected_difficulty, selected_track, selected_vehicle, current_section
    global car_angle, car_speed, track_follow

    if current_game_state == STATE_MENU:
        if current_section < 3:
            if key == GLUT_KEY_UP:
                if current_section == 0:
                    selected_difficulty = (selected_difficulty - 1) % len(difficulty_options)
                elif current_section == 1:
                    selected_track = (selected_track - 1) % len(track_options)
                elif current_section == 2:
                    selected_vehicle = (selected_vehicle - 1) % len(vehicle_options)

            elif key == GLUT_KEY_DOWN:
                if current_section == 0:
                    selected_difficulty = (selected_difficulty + 1) % len(difficulty_options)
                elif current_section == 1:
                    selected_track = (selected_track + 1) % len(track_options)
                elif current_section == 2:
                    selected_vehicle = (selected_vehicle + 1) % len(vehicle_options)

        if key == GLUT_KEY_LEFT:
            current_section = (current_section - 1) % 4
        elif key == GLUT_KEY_RIGHT:
            current_section = (current_section + 1) % 4

    elif current_game_state == STATE_RACING:
        if key == GLUT_KEY_UP:
            car_speed = min(car_speed + acceleration, max_speed)
        elif key == GLUT_KEY_DOWN:
            car_speed = max(car_speed - acceleration, -max_speed / 2)
        elif key == GLUT_KEY_LEFT:
            car_angle += turning_speed * (1 + car_speed)
            if car_angle > 2 * math.pi:
                car_angle -= 2 * math.pi
        elif key == GLUT_KEY_RIGHT:
            car_angle -= turning_speed * (1 + car_speed)
            if car_angle < 0:
                car_angle += 2 * math.pi

    glutPostRedisplay()


def normal_keys(key, x, y):
    global current_section, current_game_state, showing_countdown
    global track_follow, camera_height, camera_angle, camera_pos, is_night
    global car_speed

    if key == b'\r' or key == b'\n':
        if current_game_state == STATE_MENU and current_section == 3:
            if selected_difficulty >= 0 and selected_track >= 0 and selected_vehicle >= 0:
                start_countdown()
            else:
                print("Please select all options before starting.")
        elif current_game_state == STATE_END_SCREEN:
            current_game_state = STATE_MENU
            showing_countdown = False
            car_angle = 0
            car_speed = 0
            lap_count = 0
            passed_start_line = False

    elif key == b'\x1b': 
        if current_game_state == STATE_RACING:
            current_game_state = STATE_MENU
        else:
            glutLeaveMainLoop()

    if current_game_state == STATE_RACING:
        if key == b'w':
            camera_height += 0.5
        if key == b's':
            camera_height = max(0.5, camera_height - 0.5)
        if key == b'a':
            camera_angle += 0.1
        if key == b'd':
            camera_angle -= 0.1
        if key == b'f':
            track_follow = not track_follow
        if key == b'n':
            is_night = not is_night 
        if key == b'r':
            camera_pos = (0, 5, 5)
            camera_angle = 0
            camera_height = 5
            track_follow = False
        if key == b' ':  
            car_speed = max(0, car_speed - deceleration * 2)  

    glutPostRedisplay()


def mouseListener(button, state, x, y):
    pass


def start_countdown():
    global countdown_value, showing_countdown, countdown_start_time, current_game_state
    global race_start_time, race_current_time

    countdown_value = 3
    showing_countdown = True
    countdown_start_time = time.time()
    current_game_state = STATE_COUNTDOWN
    race_current_time = 0


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.25, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if is_night:
        ambient = [0.1, 0.1, 0.2, 1.0]
        diffuse = [0.6, 0.6, 0.8, 1.0]
    else:
        if selected_track == 2:  
            ambient = [0.5, 0.4, 0.2, 1.0]
            diffuse = [1.0, 0.9, 0.7, 1.0]
        else: 
            ambient = [0.4, 0.4, 0.3, 1.0]
            diffuse = [1.0, 0.98, 0.8, 1.0]

    x, y, z = camera_pos
    if track_follow:
        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)
    else:
        cam_x = math.sin(camera_angle) * camera_distance
        cam_z = math.cos(camera_angle) * camera_distance
        gluLookAt(cam_x, camera_height, cam_z, 0, 0, 0, 0, 1, 0)


def update_game_physics():
    global car_speed, max_speed

    if selected_difficulty == 0:  
        max_speed = 0.2
    elif selected_difficulty == 1: 
        max_speed = 0.3
    else:  
        max_speed = 0.4
    if car_speed > 0:
        car_speed = max(0, car_speed - deceleration)
    elif car_speed < 0:
        car_speed = min(0, car_speed + deceleration)


def idle():
    global countdown_value, showing_countdown, countdown_start_time
    global current_game_state, race_start_time, race_current_time

    if current_game_state == STATE_COUNTDOWN and showing_countdown and countdown_start_time is not None:
        elapsed = time.time() - countdown_start_time

        if countdown_value > 0 and elapsed >= (3 - countdown_value + 1):
            countdown_value -= 1
        elif countdown_value == 0 and elapsed >= 4:
            showing_countdown = False
            countdown_start_time = None
            print("Game Started!")
            current_game_state = STATE_RACING
            race_start_time = time.time()
    if current_game_state == STATE_RACING:
        update_game_physics()

        if race_start_time:
            race_current_time = time.time() - race_start_time

        check_for_race_end()

    glutPostRedisplay()


def setup_projection_for_menu():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def setup_projection_for_racing():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.25, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def draw_hud():
    draw_text(10, 770, f"Lap: {lap_count}/3", 1.0, 1.0, 0.0)
    draw_text(10, 740, f"Time: {race_current_time:.2f}s", 1.0, 1.0, 1.0)
    speed_percentage = (car_speed / max_speed) * 100 if max_speed > 0 else 0
    draw_text(10, 710, f"Speed: {speed_percentage:.0f}%", 1.0, 0.0, 0.0)
    draw_text(window_width - 250, 770, f"Track: {track_options[selected_track]}", 0.0, 1.0, 1.0)
    mode_text = "Night Mode" if is_night else "Day Mode"
    draw_text(window_width - 250, 740, mode_text, 1.0, 1.0, 0.0)
    draw_text(window_width / 2 - 200, 50,
              "Controls: Arrow Keys - Drive, F - Follow, Space - Brake, N - Toggle Day/Night", 0.8, 0.8, 0.8)


def showScreen():
    if current_game_state == STATE_MENU or current_game_state == STATE_COUNTDOWN or current_game_state == STATE_END_SCREEN:
        glClearColor(0.1, 0.1, 0.3, 1.0) 
    else:  
        if is_night:
            glClearColor(0.0, 0.0, 0.2, 1.0) 
        else:
            if selected_track == 2: 
                glClearColor(0.85, 0.80, 0.75, 1.0)  
            else:
                glClearColor(0.53, 0.81, 0.92, 1.0)  

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, window_width, window_height)

    if current_game_state == STATE_MENU:
        setup_projection_for_menu()
        draw_menu()
    elif current_game_state == STATE_COUNTDOWN:
        setup_projection_for_menu()
        draw_countdown()
    elif current_game_state == STATE_END_SCREEN:
        setup_projection_for_menu()
        draw_end_screen()
    elif current_game_state == STATE_RACING:
        setup_projection_for_racing()
        setupCamera()

        draw_stars() 
        draw_clouds()  

        draw_track()
        draw_barriers()
        draw_trees() 
        player_x, player_z = draw_car(True)  
        draw_car(False)  
        draw_hud()

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Racing Simulator 2025")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(normal_keys)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()
if __name__ == "__main__":
    main()





###### from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLUT.fonts import GLUT_BITMAP_HELVETICA_18
# from OpenGL.GLU import *
# import math
# import random

# # Global variables
# GRID_LENGTH = 400
# TRACK_WIDTH = 100

# # Camera variables
# camera_pos = [0, 200, 300]  # Default position
# camera_angle = 0  # Rotation angle around the world
# camera_mode = 0  # 0: Follow, 1: First-person, 2: Overhead

# # Vehicle properties
# player_pos = [0, 0, 0]  # Position (x, y, z)
# player_angle = 0  # Rotation angle in degrees
# player_speed = 0
# MAX_SPEED = 10
# player_acceleration = 0.5
# player_deceleration = 0.3
# player_steering_speed = 5
# VEHICLE_TYPE = 0  # 0: Car, 1: Bike
# wheel_rotation = 0  # Wheel rotation angle

# # Color schemes
# CAR_COLORS = [
#     [1.0, 0.0, 0.0],  # Red
#     [0.0, 0.0, 1.0],  # Blue
#     [0.0, 1.0, 0.0],  # Green
#     [1.0, 1.0, 0.0],  # Yellow
#     [1.0, 0.5, 0.0],  # Orange
# ]
# BIKE_COLORS = [
#     [0.5, 0.0, 0.5],  # Purple
#     [0.0, 0.8, 0.8],  # Cyan
#     [0.8, 0.8, 0.8],  # Silver
#     [0.2, 0.2, 0.2],  # Dark Gray
#     [1.0, 0.4, 0.7],  # Pink
# ]
# current_color_index = 0

# # Track definition - simple oval
# track_segments = []
# for i in range(36):
#     angle = i * 10 * math.pi / 180
#     x = math.cos(angle) * 300
#     y = math.sin(angle) * 200
#     track_segments.append((x, y))

# # Opponent vehicles
# opponents = []
# opponent_colors = []

# # Game state
# game_started = False
# current_lap = 1
# MAX_LAPS = 3
# lap_start_time = 0
# current_time = 0
# best_lap_time = float('inf')
# player_position = 1
# checkpoint_passed = False
# start_line_passed = False
# countdown = 3
# countdown_start_time = 0

# # Checkpoints to verify full laps
# checkpoints = [
#     (0, 200),   # Top
#     (300, 0),   # Right
#     (0, -200),  # Bottom
#     (-300, 0),  # Left
# ]
# current_checkpoint = 0

# def initialize_opponents():
#     global opponents, opponent_colors
#     opponents = []
#     opponent_colors = []
    
#     # Create 3 opponents with different starting positions
#     for i in range(3):
#         angle_offset = i * 30
#         x = math.cos(angle_offset * math.pi / 180) * 300
#         y = math.sin(angle_offset * math.pi / 180) * 200
#         opponents.append([x, y, 0, angle_offset])
        
#         # Random color for each opponent
#         if random.random() > 0.5:
#             opponent_colors.append(random.choice(CAR_COLORS))
#         else:
#             opponent_colors.append(random.choice(BIKE_COLORS))

# def is_on_track(x, y):
#     """Check if position is on the track"""
#     for i in range(len(track_segments)):
#         cx, cy = track_segments[i]
#         # Simple distance check from track center line
#         dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
#         if dist < TRACK_WIDTH:
#             return True
#     return False

# def calculate_friction(x, y):
#     """Calculate friction based on terrain"""
#     if is_on_track(x, y):
#         return 0.98  # Road friction
#     else:
#         return 0.90  # Off-road (grass) friction - higher friction = slower

# def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
#     glColor3f(1, 1, 1)
#     glMatrixMode(GL_PROJECTION)
#     glPushMatrix()
#     glLoadIdentity()
#     gluOrtho2D(0, 1000, 0, 800)
#     glMatrixMode(GL_MODELVIEW)
#     glPushMatrix()
#     glLoadIdentity()
#     glRasterPos2f(x, y)
#     for ch in text:
#         glutBitmapCharacter(font, ord(ch))
#     glPopMatrix()
#     glMatrixMode(GL_PROJECTION)
#     glPopMatrix()
#     glMatrixMode(GL_MODELVIEW)

# def draw_track():
#     """Draw the racing track"""
#     # Draw track segments
#     for i in range(len(track_segments)):
#         # Draw road
#         glColor3f(0.3, 0.3, 0.3)  # Dark gray for road
#         x1, y1 = track_segments[i]
#         x2, y2 = track_segments[(i + 1) % len(track_segments)]
        
#         # Inner edge
#         angle1 = math.atan2(y1, x1)
#         inner_x1 = math.cos(angle1) * (math.sqrt(x1*x1 + y1*y1) - TRACK_WIDTH/2)
#         inner_y1 = math.sin(angle1) * (math.sqrt(x1*x1 + y1*y1) - TRACK_WIDTH/2)
        
#         angle2 = math.atan2(y2, x2)
#         inner_x2 = math.cos(angle2) * (math.sqrt(x2*x2 + y2*y2) - TRACK_WIDTH/2)
#         inner_y2 = math.sin(angle2) * (math.sqrt(x2*x2 + y2*y2) - TRACK_WIDTH/2)
        
#         # Outer edge
#         outer_x1 = math.cos(angle1) * (math.sqrt(x1*x1 + y1*y1) + TRACK_WIDTH/2)
#         outer_y1 = math.sin(angle1) * (math.sqrt(x1*x1 + y1*y1) + TRACK_WIDTH/2)
        
#         outer_x2 = math.cos(angle2) * (math.sqrt(x2*x2 + y2*y2) + TRACK_WIDTH/2)
#         outer_y2 = math.sin(angle2) * (math.sqrt(x2*x2 + y2*y2) + TRACK_WIDTH/2)
        
#         # Draw the inner and outer edges using lines
#         glColor3f(0.3, 0.3, 0.3)  # Dark gray for road
#         glBegin(GL_LINES)
#         glVertex3f(inner_x1, inner_y1, 0)
#         glVertex3f(inner_x2, inner_y2, 0)
#         glVertex3f(outer_x1, outer_y1, 0)
#         glVertex3f(outer_x2, outer_y2, 0)
#         glEnd()
        
#         # Draw start line at the beginning of the track
#         if i == 0:
#             glColor3f(1.0, 1.0, 1.0)  # White for start line
#             glLineWidth(3.0)
#             glBegin(GL_LINES)
#             glVertex3f(inner_x1, inner_y1, 0.1)
#             glVertex3f(outer_x1, outer_y1, 0.1)
#             glEnd()
#             glLineWidth(1.0)
    
#     # Draw checkpoints as colored lines
#     for i, (cx, cy) in enumerate(checkpoints):
#         angle = math.atan2(cy, cx)
#         inner_x = math.cos(angle) * (math.sqrt(cx*cx + cy*cy) - TRACK_WIDTH/2)
#         inner_y = math.sin(angle) * (math.sqrt(cx*cx + cy*cy) - TRACK_WIDTH/2)
#         outer_x = math.cos(angle) * (math.sqrt(cx*cx + cy*cy) + TRACK_WIDTH/2)
#         outer_y = math.sin(angle) * (math.sqrt(cx*cx + cy*cy) + TRACK_WIDTH/2)
        
#         # Draw checkpoint line
#         if i == current_checkpoint:
#             glColor3f(0.0, 1.0, 0.0)  # Green for active checkpoint
#         else:
#             glColor3f(0.5, 0.5, 0.5)  # Gray for inactive checkpoint
        
#         glLineWidth(2.0)
#         glBegin(GL_LINES)
#         glVertex3f(inner_x, inner_y, 0.1)
#         glVertex3f(outer_x, outer_y, 0.1)
#         glEnd()
#         glLineWidth(1.0)

# def draw_ground():
#     """Draw the ground/grass"""
#     size = GRID_LENGTH * 2
#     cell_size = size / 10  # Size of each grid cell
    
#     for i in range(-10, 11):
#         for j in range(-10, 11):
#             # Skip cells that are on the track to avoid z-fighting
#             skip = False
#             for seg_x, seg_y in track_segments:
#                 if (abs(i*cell_size - seg_x) < TRACK_WIDTH and 
#                     abs(j*cell_size - seg_y) < TRACK_WIDTH):
#                     skip = True
#                     break
            
#             if skip:
#                 continue
                
#             # Alternating grass pattern
#             if (i + j) % 2 == 0:
#                 glColor3f(0.1, 0.6, 0.1)  # Dark green
#             else:
#                 glColor3f(0.2, 0.7, 0.2)  # Light green
                
#             x1 = i * cell_size - cell_size/2
#             x2 = i * cell_size + cell_size/2
#             y1 = j * cell_size - cell_size/2
#             y2 = j * cell_size + cell_size/2
            
#             glBegin(GL_QUADS)
#             glVertex3f(x1, y1, -0.1)  # Slightly below track level
#             glVertex3f(x2, y1, -0.1)
#             glVertex3f(x2, y2, -0.1)
#             glVertex3f(x1, y2, -0.1)
#             glEnd()

# def draw_car_model():
#     """Draw a car model using primitives"""
#     # Body
#     glPushMatrix()
#     current_color = CAR_COLORS[current_color_index]
#     glColor3f(current_color[0], current_color[1], current_color[2])
    
#     # Main body
#     glPushMatrix()
#     glScalef(30, 15, 8)  # Width, length, height
#     glutSolidCube(1)
#     glPopMatrix()
    
#     # Front part (hood)
#     glPushMatrix()
#     glTranslatef(0, 20, 0)
#     glScalef(25, 10, 6)
#     glutSolidCube(1)
#     glPopMatrix()
    
#     # Cabin/roof
#     glColor3f(0.1, 0.1, 0.1)  # Dark color for windows
#     glPushMatrix()
#     glTranslatef(0, 5, 10)
#     glScalef(20, 10, 6)
#     glutSolidCube(1)
#     glPopMatrix()
    
#     # Wheels (4)
#     glColor3f(0.2, 0.2, 0.2)  # Black for tires
    
#     # Function to draw a wheel at given position
#     def draw_wheel(x, y, z):
#         glPushMatrix()
#         glTranslatef(x, y, z)
#         glRotatef(90, 0, 1, 0)  # Orient wheel properly
#         glRotatef(wheel_rotation, 0, 0, 1)  # Rotate wheel based on vehicle movement
#         gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Tire
        
#         # Wheel rim (using GL_LINES to approximate a disk)
#         glColor3f(0.7, 0.7, 0.7)  # Silver for rim
#         glBegin(GL_LINES)
#         for i in range(0, 360, 15):  # Approximate rim using small lines
#             angle1 = math.radians(i)
#             angle2 = math.radians(i + 15)
#             x1 = math.cos(angle1) * 5
#             y1 = math.sin(angle1) * 5
#             x2 = math.cos(angle2) * 5
#             y2 = math.sin(angle2) * 5
#             glVertex3f(x1, y1, 3)
#             glVertex3f(x2, y2, 3)
#         glEnd()
        
#         glPopMatrix()

#     # Draw all four wheels
#     draw_wheel(15, 15, 0)  # Front right
#     draw_wheel(-15, 15, 0)  # Front left
#     draw_wheel(15, -15, 0)  # Rear right
#     draw_wheel(-15, -15, 0)  # Rear left
    
#     # Headlights
#     glColor3f(1.0, 1.0, 0.8)  # Yellow-white for headlights
#     glPushMatrix()
#     glTranslatef(10, 25, 4)
#     glutSolidCube(4)
#     glPopMatrix()
    
#     glPushMatrix()
#     glTranslatef(-10, 25, 4)
#     glutSolidCube(4)
#     glPopMatrix()
    
#     # Taillights
#     glColor3f(1.0, 0.0, 0.0)  # Red for taillights
#     glPushMatrix()
#     glTranslatef(10, -25, 4)
#     glutSolidCube(4)
#     glPopMatrix()
    
#     glPushMatrix()
#     glTranslatef(-10, -25, 4)
#     glutSolidCube(4)
#     glPopMatrix()
    
#     glPopMatrix()


# def draw_bike_model():
#     """Draw a bike model using primitives"""
#     # Body
#     glPushMatrix()
#     current_color = BIKE_COLORS[current_color_index]
#     glColor3f(current_color[0], current_color[1], current_color[2])
    
#     # Main body/frame
#     glPushMatrix()
#     glRotatef(-20, 1, 0, 0)  # Tilt the frame
#     glScalef(5, 25, 3)
#     glutSolidCube(1)
#     glPopMatrix()
    
#     # Front fork
#     glPushMatrix()
#     glTranslatef(0, 20, 0)
#     glRotatef(-30, 1, 0, 0)
#     glScalef(3, 15, 2)
#     glutSolidCube(1)
#     glPopMatrix()
    
#     # Seat
#     glColor3f(0.2, 0.2, 0.2)
#     glPushMatrix()
#     glTranslatef(0, -5, 8)
#     glScalef(8, 15, 2)
#     glutSolidCube(1)
#     glPopMatrix()
    
#     # Handlebar
#     glColor3f(0.7, 0.7, 0.7)
#     glPushMatrix()
#     glTranslatef(0, 20, 10)
#     glRotatef(90, 0, 1, 0)
#     gluCylinder(gluNewQuadric(), 1, 1, 12, 8, 1)
#     glTranslatef(0, 0, -12)
#     gluCylinder(gluNewQuadric(), 1, 1, 12, 8, 1)
#     glPopMatrix()
    
#     # Wheels (2)
#     glColor3f(0.2, 0.2, 0.2)  # Black for tires
    
#     # Function to draw a wheel at given position
#     def draw_wheel(y, z):
#         glPushMatrix()
#         glTranslatef(0, y, z)
#         glRotatef(90, 0, 1, 0)  # Orient wheel properly
#         glRotatef(wheel_rotation, 0, 0, 1)  # Rotate wheel based on vehicle movement
#         gluCylinder(gluNewQuadric(), 8, 8, 2, 16, 1)  # Tire
        
#         # Wheel rim (using GL_LINES to approximate the disk)
#         glColor3f(0.7, 0.7, 0.7)  # Silver for rim
#         glBegin(GL_LINES)
#         for i in range(0, 360, 15):  # Approximate rim using small lines
#             angle1 = math.radians(i)
#             angle2 = math.radians(i + 15)
#             x1 = math.cos(angle1) * 8
#             y1 = math.sin(angle1) * 8
#             x2 = math.cos(angle2) * 8
#             y2 = math.sin(angle2) * 8
#             glVertex3f(x1, y1, 2)
#             glVertex3f(x2, y2, 2)
#         glEnd()
        
#         glPopMatrix()
    
#     # Draw both wheels
#     draw_wheel(20, 0)  # Front wheel
#     draw_wheel(-15, 0)  # Rear wheel
    
#     # Headlight (simulated sphere using cylinder)
#     glColor3f(1.0, 1.0, 0.8)  # Yellow-white for headlight
#     glPushMatrix()
#     glTranslatef(0, 25, 5)
#     gluCylinder(gluNewQuadric(), 3, 3, 3, 8, 1)  # Simulate sphere with a cylinder
#     glPopMatrix()
    
#     # Taillight (simulated sphere using cylinder)
#     glColor3f(1.0, 0.0, 0.0)  # Red for taillight
#     glPushMatrix()
#     glTranslatef(0, -25, 5)
#     gluCylinder(gluNewQuadric(), 2, 2, 2, 8, 1)  # Simulate sphere with a cylinder
#     glPopMatrix()
    
#     glPopMatrix()
# def draw_player_vehicle():
#     """Draw the player's vehicle based on selected type"""
#     glPushMatrix()
#     glTranslatef(player_pos[0], player_pos[1], player_pos[2])
#     glRotatef(-player_angle, 0, 0, 1)  # Negative angle because we're rotating the world
    
#     if VEHICLE_TYPE == 0:
#         draw_car_model()
#     else:
#         draw_bike_model()
    
#     glPopMatrix()
# def draw_opponent_vehicle(index, pos_x, pos_y, angle):
#     """Draw an opponent vehicle"""
#     glPushMatrix()
#     glTranslatef(pos_x, pos_y, 0)
#     glRotatef(-angle, 0, 0, 1)
    
#     # Use opponent's color
#     color = opponent_colors[index]
    
#     # Determine if it's a car or bike based on the color
#     if index % 2 == 0:  # Even indices are cars
#         # Draw a simpler car model
#         glColor3f(color[0], color[1], color[2])
#         glPushMatrix()
#         glScalef(25, 15, 8)
#         glutSolidCube(1)  # Main body
#         glPopMatrix()
        
#         # Wheels
#         glColor3f(0.2, 0.2, 0.2)
#         glPushMatrix()
#         glTranslatef(15, 10, 0)
#         gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Simulate wheel as a cylinder
#         glPopMatrix()
        
#         glPushMatrix()
#         glTranslatef(-15, 10, 0)
#         gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Simulate wheel as a cylinder
#         glPopMatrix()
        
#         glPushMatrix()
#         glTranslatef(15, -10, 0)
#         gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Simulate wheel as a cylinder
#         glPopMatrix()
        
#         glPushMatrix()
#         glTranslatef(-15, -10, 0)
#         gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Simulate wheel as a cylinder
#         glPopMatrix()
#     else:  # Odd indices are bikes
#         # Draw a simpler bike model
#         glColor3f(color[0], color[1], color[2])
#         glPushMatrix()
#         glScalef(5, 25, 5)
#         glutSolidCube(1)  # Main body
#         glPopMatrix()
        
#         # Wheels
#         glColor3f(0.2, 0.2, 0.2)
#         glPushMatrix()
#         glTranslatef(0, 15, 0)
#         gluCylinder(gluNewQuadric(), 8, 8, 2, 16, 1)  # Simulate wheel as a cylinder
#         glPopMatrix()
        
#         glPushMatrix()
#         glTranslatef(0, -15, 0)
#         gluCylinder(gluNewQuadric(), 8, 8, 2, 16, 1)  # Simulate wheel as a cylinder
#         glPopMatrix()
    
#     glPopMatrix()


# def draw_opponents():
#     """Draw all opponent vehicles"""
#     for i, opponent in enumerate(opponents):
#         pos_x, pos_y, _, angle = opponent
#         draw_opponent_vehicle(i, pos_x, pos_y, angle)

# def draw_ui():
#     """Draw UI elements like speedometer, position, lap counter, etc."""
#     # Speed indicator
#     speed_percentage = abs(player_speed) / MAX_SPEED * 100
#     draw_text(10, 770, f"Speed: {speed_percentage:.0f}%")
    
#     # Position indicator
#     draw_text(10, 740, f"Position: {player_position}/4")
    
#     # Lap counter
#     draw_text(10, 710, f"Lap: {current_lap}/{MAX_LAPS}")
    
#     # Timer
#     if game_started:
#         time_elapsed = (glutGet(GLUT_ELAPSED_TIME) - lap_start_time) / 1000.0
#         draw_text(10, 680, f"Time: {time_elapsed:.2f}s")
        
#         # Best lap time
#         if best_lap_time < float('inf'):
#             draw_text(10, 650, f"Best: {best_lap_time:.2f}s")
    
#     # Vehicle type indicator
#     vehicle_type = "Car" if VEHICLE_TYPE == 0 else "Bike"
#     draw_text(850, 770, f"Vehicle: {vehicle_type}")
    
#     # Camera mode indicator
#     camera_modes = ["Follow", "First-person", "Overhead"]
#     draw_text(850, 740, f"Camera: {camera_modes[camera_mode]}")
    
#     # Display controls
#     draw_text(850, 40, "Controls:")
#     draw_text(850, 25, "WASD: Drive   C: Change Vehicle")
#     draw_text(850, 10, "V: Change Color   Space: Start Race")

# def draw_countdown():
#     """Draw the countdown at the start of the race"""
#     if countdown > 0:
#         glColor3f(1.0, 0.0, 0.0)  # Red
#         draw_text(480, 400, str(countdown))
#     elif countdown == 0:
#         glColor3f(0.0, 1.0, 0.0)  # Green
#         draw_text(450, 400, "GO!")

# def update_countdown():
#     """Update the countdown timer"""
#     global countdown, game_started, lap_start_time, countdown_start_time
    
#     if not game_started and countdown >= 0:
#         current_time = glutGet(GLUT_ELAPSED_TIME)
#         time_since_start = (current_time - countdown_start_time) / 1000.0
        
#         if time_since_start > 1:
#             countdown -= 1
#             countdown_start_time = current_time
            
#             if countdown < 0:
#                 game_started = True
#                 lap_start_time = current_time

# def update_player():
#     """Update player position and physics"""
#     global player_pos, player_angle, player_speed, wheel_rotation
    
#     if not game_started:
#         return
    
#     # Calculate new position based on speed and angle
#     angle_rad = math.radians(player_angle)
#     delta_x = -math.sin(angle_rad) * player_speed
#     delta_y = math.cos(angle_rad) * player_speed
    
#     new_x = player_pos[0] + delta_x
#     new_y = player_pos[1] + delta_y
    
#     # Apply friction based on terrain
#     friction = calculate_friction(new_x, new_y)
#     player_speed *= friction
    
#     # Update position
#     player_pos[0] = new_x
#     player_pos[1] = new_y
    
#     # Update wheel rotation based on speed
#     wheel_rotation += player_speed * 10
#     if wheel_rotation > 360:
#         wheel_rotation -= 360

# def update_opponents():
#     """Update opponent vehicles' positions"""
#     global opponents
    
#     if not game_started:
#         return
    
#     for i, opponent in enumerate(opponents):
#         pos_x, pos_y, _, angle = opponent
        
#         # Calculate target point (next track segment)
#         segment_index = (i * 3 + int(angle / 10)) % len(track_segments)
#         target_x, target_y = track_segments[segment_index]
        
#         # Calculate direction to target
#         dx = target_x - pos_x
#         dy = target_y - pos_y
#         distance = math.sqrt(dx*dx + dy*dy)
        
#         # Normalize direction
#         if distance > 0:
#             dx /= distance
#             dy /= distance
        
#         # Calculate angle to target
#         target_angle = math.degrees(math.atan2(-dx, dy)) % 360
        
#         # Adjust angle (simple steering)
#         angle_diff = (target_angle - angle) % 360
#         if angle_diff > 180:
#             angle_diff -= 360
        
#         # Steer towards target, with some randomness
#         new_angle = angle + max(-3, min(3, angle_diff * 0.1 + random.uniform(-0.5, 0.5)))
        
#         # Calculate speed (slower when turning sharply)
#         speed = 2.0 + (3.0 - 3.0 * min(1.0, abs(angle_diff) / 90.0))
        
#         # Move opponent
#         new_angle_rad = math.radians(new_angle)
#         new_x = pos_x - math.sin(new_angle_rad) * speed
#         new_y = pos_y + math.cos(new_angle_rad) * speed
        
#         # Update opponent data
#         opponents[i] = [new_x, new_y, 0, new_angle]

# def check_lap_completion():
#     """Check if player has completed a lap"""
#     global current_checkpoint, current_lap, lap_start_time, best_lap_time, checkpoint_passed, start_line_passed
    
#     # Check if player has reached the current checkpoint
#     checkpoint_x, checkpoint_y = checkpoints[current_checkpoint]
#     dx = player_pos[0] - checkpoint_x
#     dy = player_pos[1] - checkpoint_y
#     distance = math.sqrt(dx*dx + dy*dy)
    
#     if distance < TRACK_WIDTH:
#         if current_checkpoint == 0 and checkpoint_passed:
#             # Passed checkpoint 0 (top) after passing at least one other checkpoint
#             start_line_passed = True
        
#         # Move to next checkpoint
#         current_checkpoint = (current_checkpoint + 1) % len(checkpoints)
#         checkpoint_passed = True
        
#         # Check if completed a full lap (passed all checkpoints and crossed start line)
#         if current_checkpoint == 0 and checkpoint_passed and start_line_passed:
#             # Calculate lap time
#             current_time = glutGet(GLUT_ELAPSED_TIME)
#             lap_time = (current_time - lap_start_time) / 1000.0
#             lap_start_time = current_time
            
#             # Update best lap time
#             if lap_time < best_lap_time:
#                 best_lap_time = lap_time
            
#             # Increment lap counter
#             current_lap += 1
#             checkpoint_passed = False
#             start_line_passed = False

# def update_player_position():
#     """Update player's race position relative to opponents"""
#     global player_position
    
#     # Simple position calculation based on track completion
#     # In a more complex implementation, this would consider actual track progress
#     player_position = 1
    
#     for i, opponent in enumerate(opponents):
#         # For simplicity, compare lap count and checkpoint progress
#         # This is a very basic implementation - a real game would need more sophisticated tracking
#         player_position += 1

# def keyboardListener(key, x, y):
#     """Handle keyboard input"""
#     global player_speed, player_angle, VEHICLE_TYPE, current_color_index
#     global game_started, countdown, countdown_start_time, camera_mode
    
#     # Acceleration (W key)
#     if key == b'w':
#         player_speed = min(player_speed + player_acceleration, MAX_SPEED)
    
#     # Braking/Reverse (S key)
#     if key == b's':
#         player_speed = max(player_speed - player_acceleration, -MAX_SPEED/2)
    
#     # Steering left (A key)
#     if key == b'a':
#         player_angle = (player_angle + player_steering_speed) % 360
    
#     # Steering right (D key)
#     if key == b'd':
#         player_angle = (player_angle - player_steering_speed) % 360
    
#     # Change vehicle type (C key)
#     if key == b'c':
#         VEHICLE_TYPE = 1 - VEHICLE_TYPE  # Toggle between 0 (car) and 1 (bike)
    
#     # Change vehicle color (V key)
#     if key == b'v':
#         if VEHICLE_TYPE == 0:  # Car
#             current_color_index = (current_color_index + 1) % len(CAR_COLORS)
#         else:  # Bike
#             current_color_index = (current_color_index + 1) % len(BIKE_COLORS)
    
#     # Start race (Spacebar)
#     if key == b' ' and not game_started:
#         countdown = 3
#         countdown_start_time = glutGet(GLUT_ELAPSED_TIME)
    
#     # Change camera view (B key)
#     if key == b'b':
#         camera_mode = (camera_mode + 1) % 3

# def specialKeyListener(key, x, y):
#     """Handle special key input"""
#     global camera_pos, camera_angle
    
#     # Move camera up (UP arrow key)
#     if key == GLUT_KEY_UP:
#         camera_pos[2] += 10
#         camera_pos[2] = min(800, camera_pos[2])
    
#     # Move camera down (DOWN arrow key)
#     if key == GLUT_KEY_DOWN:
#         camera_pos[2] -= 10
#         camera_pos[2] = max(100, camera_pos[2])
    
#     # Rotate camera left (LEFT arrow key)
#     if key == GLUT_KEY_LEFT:
#         camera_angle = (camera_angle - 5) % 360
    
#     # Rotate camera right (RIGHT arrow key)
#     if key == GLUT_KEY_RIGHT:
#         camera_angle = (camera_angle + 5) % 360

# # ------------------------------------------------------------------
# # Display & update loop
# # ------------------------------------------------------------------
# def display():
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#     glViewport(0, 0, 1000, 800)
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     # simple perspective
#     gluPerspective(60, 1000/800, 1, 2000)
    
#     # Camera setup
#     glMatrixMode(GL_MODELVIEW)
#     glLoadIdentity()
#     # Compute camera based on mode
#     if camera_mode == 0:  # Follow camera
#         # Behind & above the player
#         ang = math.radians(player_angle)
#         behind = 70
#         height = 40
#         camX = player_pos[0] + math.sin(ang) * behind
#         camY = player_pos[1] - math.cos(ang) * behind
#         camZ = player_pos[2] + height
#         gluLookAt(camX, camY, camZ,
#                   player_pos[0], player_pos[1], player_pos[2] + 5,
#                   0, 0, 1)
#     elif camera_mode == 1:  # First-person
#         ang = math.radians(player_angle)
#         forward = 5
#         camX = player_pos[0] - math.sin(ang) * forward
#         camY = player_pos[1] + math.cos(ang) * forward
#         camZ = player_pos[2] + 5
#         tgtX = player_pos[0] - math.sin(ang) * (forward + 20)
#         tgtY = player_pos[1] + math.cos(ang) * (forward + 20)
#         gluLookAt(camX, camY, camZ,
#                   tgtX, tgtY, player_pos[2] + 5,
#                   0, 0, 1)
#     else:  # Overhead
#         gluLookAt(0, 0, 600,
#                   0, 0, 0,
#                   0, 1, 0)

#     # Draw scene
#     draw_ground()
#     draw_track()
#     draw_opponents()
#     draw_player_vehicle()
#     draw_ui()
#     draw_countdown()
#     glutSwapBuffers()

# def idle():
#     # update physics & timers
#     update_countdown()
#     update_player()
#     update_opponents()
#     check_lap_completion()
#     update_player_position()
#     glutPostRedisplay()

# # ------------------------------------------------------------------
# # Entry point
# # ------------------------------------------------------------------
# def main():
#     glutInit()
#     glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  # Removed GLUT_DEPTH as it's not allowed
#     glutInitWindowSize(1000, 800)
#     glutInitWindowPosition(100, 100)
#     glutCreateWindow(b"CSE423: Simple Car Race")
#     glClearColor(0.4, 0.7, 1.0, 1.0)  # sky-blue background
#     initialize_opponents()  # place AI cars
#     glutDisplayFunc(display)
#     glutIdleFunc(idle)
#     glutKeyboardFunc(keyboardListener)
#     glutSpecialFunc(specialKeyListener)

#     glutMainLoop()

# if __name__ == "__main__":
#     main()