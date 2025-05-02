from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.fonts import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *
import math
import random

# Global variables
GRID_LENGTH = 400
TRACK_WIDTH = 100

# Camera variables
camera_pos = [0, 200, 300]  # Default position
camera_angle = 0  # Rotation angle around the world
camera_mode = 0  # 0: Follow, 1: First-person, 2: Overhead

# Vehicle properties
player_pos = [0, 0, 0]  # Position (x, y, z)
player_angle = 0  # Rotation angle in degrees
player_speed = 0
MAX_SPEED = 10
player_acceleration = 0.5
player_deceleration = 0.3
player_steering_speed = 5
VEHICLE_TYPE = 0  # 0: Car, 1: Bike
wheel_rotation = 0  # Wheel rotation angle

# Color schemes
CAR_COLORS = [
    [1.0, 0.0, 0.0],  # Red
    [0.0, 0.0, 1.0],  # Blue
    [0.0, 1.0, 0.0],  # Green
    [1.0, 1.0, 0.0],  # Yellow
    [1.0, 0.5, 0.0],  # Orange
]
BIKE_COLORS = [
    [0.5, 0.0, 0.5],  # Purple
    [0.0, 0.8, 0.8],  # Cyan
    [0.8, 0.8, 0.8],  # Silver
    [0.2, 0.2, 0.2],  # Dark Gray
    [1.0, 0.4, 0.7],  # Pink
]
current_color_index = 0

# Track definition - simple oval
track_segments = []
for i in range(36):
    angle = i * 10 * math.pi / 180
    x = math.cos(angle) * 300
    y = math.sin(angle) * 200
    track_segments.append((x, y))

# Opponent vehicles
opponents = []
opponent_colors = []

# Game state
game_started = False
current_lap = 1
MAX_LAPS = 3
lap_start_time = 0
current_time = 0
best_lap_time = float('inf')
player_position = 1
checkpoint_passed = False
start_line_passed = False
countdown = 3
countdown_start_time = 0

# Checkpoints to verify full laps
checkpoints = [
    (0, 200),   # Top
    (300, 0),   # Right
    (0, -200),  # Bottom
    (-300, 0),  # Left
]
current_checkpoint = 0

def initialize_opponents():
    global opponents, opponent_colors
    opponents = []
    opponent_colors = []
    
    # Create 3 opponents with different starting positions
    for i in range(3):
        angle_offset = i * 30
        x = math.cos(angle_offset * math.pi / 180) * 300
        y = math.sin(angle_offset * math.pi / 180) * 200
        opponents.append([x, y, 0, angle_offset])
        
        # Random color for each opponent
        if random.random() > 0.5:
            opponent_colors.append(random.choice(CAR_COLORS))
        else:
            opponent_colors.append(random.choice(BIKE_COLORS))

def is_on_track(x, y):
    """Check if position is on the track"""
    for i in range(len(track_segments)):
        cx, cy = track_segments[i]
        # Simple distance check from track center line
        dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        if dist < TRACK_WIDTH:
            return True
    return False

def calculate_friction(x, y):
    """Calculate friction based on terrain"""
    if is_on_track(x, y):
        return 0.98  # Road friction
    else:
        return 0.90  # Off-road (grass) friction - higher friction = slower

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
    """Draw the racing track"""
    # Draw track segments
    for i in range(len(track_segments)):
        # Draw road
        glColor3f(0.3, 0.3, 0.3)  # Dark gray for road
        x1, y1 = track_segments[i]
        x2, y2 = track_segments[(i + 1) % len(track_segments)]
        
        # Inner edge
        angle1 = math.atan2(y1, x1)
        inner_x1 = math.cos(angle1) * (math.sqrt(x1*x1 + y1*y1) - TRACK_WIDTH/2)
        inner_y1 = math.sin(angle1) * (math.sqrt(x1*x1 + y1*y1) - TRACK_WIDTH/2)
        
        angle2 = math.atan2(y2, x2)
        inner_x2 = math.cos(angle2) * (math.sqrt(x2*x2 + y2*y2) - TRACK_WIDTH/2)
        inner_y2 = math.sin(angle2) * (math.sqrt(x2*x2 + y2*y2) - TRACK_WIDTH/2)
        
        # Outer edge
        outer_x1 = math.cos(angle1) * (math.sqrt(x1*x1 + y1*y1) + TRACK_WIDTH/2)
        outer_y1 = math.sin(angle1) * (math.sqrt(x1*x1 + y1*y1) + TRACK_WIDTH/2)
        
        outer_x2 = math.cos(angle2) * (math.sqrt(x2*x2 + y2*y2) + TRACK_WIDTH/2)
        outer_y2 = math.sin(angle2) * (math.sqrt(x2*x2 + y2*y2) + TRACK_WIDTH/2)
        
        # Draw the inner and outer edges using lines
        glColor3f(0.3, 0.3, 0.3)  # Dark gray for road
        glBegin(GL_LINES)
        glVertex3f(inner_x1, inner_y1, 0)
        glVertex3f(inner_x2, inner_y2, 0)
        glVertex3f(outer_x1, outer_y1, 0)
        glVertex3f(outer_x2, outer_y2, 0)
        glEnd()
        
        # Draw start line at the beginning of the track
        if i == 0:
            glColor3f(1.0, 1.0, 1.0)  # White for start line
            glLineWidth(3.0)
            glBegin(GL_LINES)
            glVertex3f(inner_x1, inner_y1, 0.1)
            glVertex3f(outer_x1, outer_y1, 0.1)
            glEnd()
            glLineWidth(1.0)
    
    # Draw checkpoints as colored lines
    for i, (cx, cy) in enumerate(checkpoints):
        angle = math.atan2(cy, cx)
        inner_x = math.cos(angle) * (math.sqrt(cx*cx + cy*cy) - TRACK_WIDTH/2)
        inner_y = math.sin(angle) * (math.sqrt(cx*cx + cy*cy) - TRACK_WIDTH/2)
        outer_x = math.cos(angle) * (math.sqrt(cx*cx + cy*cy) + TRACK_WIDTH/2)
        outer_y = math.sin(angle) * (math.sqrt(cx*cx + cy*cy) + TRACK_WIDTH/2)
        
        # Draw checkpoint line
        if i == current_checkpoint:
            glColor3f(0.0, 1.0, 0.0)  # Green for active checkpoint
        else:
            glColor3f(0.5, 0.5, 0.5)  # Gray for inactive checkpoint
        
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex3f(inner_x, inner_y, 0.1)
        glVertex3f(outer_x, outer_y, 0.1)
        glEnd()
        glLineWidth(1.0)

def draw_ground():
    """Draw the ground/grass"""
    size = GRID_LENGTH * 2
    cell_size = size / 10  # Size of each grid cell
    
    for i in range(-10, 11):
        for j in range(-10, 11):
            # Skip cells that are on the track to avoid z-fighting
            skip = False
            for seg_x, seg_y in track_segments:
                if (abs(i*cell_size - seg_x) < TRACK_WIDTH and 
                    abs(j*cell_size - seg_y) < TRACK_WIDTH):
                    skip = True
                    break
            
            if skip:
                continue
                
            # Alternating grass pattern
            if (i + j) % 2 == 0:
                glColor3f(0.1, 0.6, 0.1)  # Dark green
            else:
                glColor3f(0.2, 0.7, 0.2)  # Light green
                
            x1 = i * cell_size - cell_size/2
            x2 = i * cell_size + cell_size/2
            y1 = j * cell_size - cell_size/2
            y2 = j * cell_size + cell_size/2
            
            glBegin(GL_QUADS)
            glVertex3f(x1, y1, -0.1)  # Slightly below track level
            glVertex3f(x2, y1, -0.1)
            glVertex3f(x2, y2, -0.1)
            glVertex3f(x1, y2, -0.1)
            glEnd()

def draw_car_model():
    """Draw a car model using primitives"""
    # Body
    glPushMatrix()
    current_color = CAR_COLORS[current_color_index]
    glColor3f(current_color[0], current_color[1], current_color[2])
    
    # Main body
    glPushMatrix()
    glScalef(30, 15, 8)  # Width, length, height
    glutSolidCube(1)
    glPopMatrix()
    
    # Front part (hood)
    glPushMatrix()
    glTranslatef(0, 20, 0)
    glScalef(25, 10, 6)
    glutSolidCube(1)
    glPopMatrix()
    
    # Cabin/roof
    glColor3f(0.1, 0.1, 0.1)  # Dark color for windows
    glPushMatrix()
    glTranslatef(0, 5, 10)
    glScalef(20, 10, 6)
    glutSolidCube(1)
    glPopMatrix()
    
    # Wheels (4)
    glColor3f(0.2, 0.2, 0.2)  # Black for tires
    
    # Function to draw a wheel at given position
    def draw_wheel(x, y, z):
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(90, 0, 1, 0)  # Orient wheel properly
        glRotatef(wheel_rotation, 0, 0, 1)  # Rotate wheel based on vehicle movement
        gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Tire
        
        # Wheel rim (using GL_LINES to approximate a disk)
        glColor3f(0.7, 0.7, 0.7)  # Silver for rim
        glBegin(GL_LINES)
        for i in range(0, 360, 15):  # Approximate rim using small lines
            angle1 = math.radians(i)
            angle2 = math.radians(i + 15)
            x1 = math.cos(angle1) * 5
            y1 = math.sin(angle1) * 5
            x2 = math.cos(angle2) * 5
            y2 = math.sin(angle2) * 5
            glVertex3f(x1, y1, 3)
            glVertex3f(x2, y2, 3)
        glEnd()
        
        glPopMatrix()

    # Draw all four wheels
    draw_wheel(15, 15, 0)  # Front right
    draw_wheel(-15, 15, 0)  # Front left
    draw_wheel(15, -15, 0)  # Rear right
    draw_wheel(-15, -15, 0)  # Rear left
    
    # Headlights
    glColor3f(1.0, 1.0, 0.8)  # Yellow-white for headlights
    glPushMatrix()
    glTranslatef(10, 25, 4)
    glutSolidCube(4)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-10, 25, 4)
    glutSolidCube(4)
    glPopMatrix()
    
    # Taillights
    glColor3f(1.0, 0.0, 0.0)  # Red for taillights
    glPushMatrix()
    glTranslatef(10, -25, 4)
    glutSolidCube(4)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-10, -25, 4)
    glutSolidCube(4)
    glPopMatrix()
    
    glPopMatrix()


def draw_bike_model():
    """Draw a bike model using primitives"""
    # Body
    glPushMatrix()
    current_color = BIKE_COLORS[current_color_index]
    glColor3f(current_color[0], current_color[1], current_color[2])
    
    # Main body/frame
    glPushMatrix()
    glRotatef(-20, 1, 0, 0)  # Tilt the frame
    glScalef(5, 25, 3)
    glutSolidCube(1)
    glPopMatrix()
    
    # Front fork
    glPushMatrix()
    glTranslatef(0, 20, 0)
    glRotatef(-30, 1, 0, 0)
    glScalef(3, 15, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    # Seat
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, -5, 8)
    glScalef(8, 15, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    # Handlebar
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(0, 20, 10)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 1, 1, 12, 8, 1)
    glTranslatef(0, 0, -12)
    gluCylinder(gluNewQuadric(), 1, 1, 12, 8, 1)
    glPopMatrix()
    
    # Wheels (2)
    glColor3f(0.2, 0.2, 0.2)  # Black for tires
    
    # Function to draw a wheel at given position
    def draw_wheel(y, z):
        glPushMatrix()
        glTranslatef(0, y, z)
        glRotatef(90, 0, 1, 0)  # Orient wheel properly
        glRotatef(wheel_rotation, 0, 0, 1)  # Rotate wheel based on vehicle movement
        gluCylinder(gluNewQuadric(), 8, 8, 2, 16, 1)  # Tire
        
        # Wheel rim (using GL_LINES to approximate the disk)
        glColor3f(0.7, 0.7, 0.7)  # Silver for rim
        glBegin(GL_LINES)
        for i in range(0, 360, 15):  # Approximate rim using small lines
            angle1 = math.radians(i)
            angle2 = math.radians(i + 15)
            x1 = math.cos(angle1) * 8
            y1 = math.sin(angle1) * 8
            x2 = math.cos(angle2) * 8
            y2 = math.sin(angle2) * 8
            glVertex3f(x1, y1, 2)
            glVertex3f(x2, y2, 2)
        glEnd()
        
        glPopMatrix()
    
    # Draw both wheels
    draw_wheel(20, 0)  # Front wheel
    draw_wheel(-15, 0)  # Rear wheel
    
    # Headlight (simulated sphere using cylinder)
    glColor3f(1.0, 1.0, 0.8)  # Yellow-white for headlight
    glPushMatrix()
    glTranslatef(0, 25, 5)
    gluCylinder(gluNewQuadric(), 3, 3, 3, 8, 1)  # Simulate sphere with a cylinder
    glPopMatrix()
    
    # Taillight (simulated sphere using cylinder)
    glColor3f(1.0, 0.0, 0.0)  # Red for taillight
    glPushMatrix()
    glTranslatef(0, -25, 5)
    gluCylinder(gluNewQuadric(), 2, 2, 2, 8, 1)  # Simulate sphere with a cylinder
    glPopMatrix()
    
    glPopMatrix()
def draw_player_vehicle():
    """Draw the player's vehicle based on selected type"""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(-player_angle, 0, 0, 1)  # Negative angle because we're rotating the world
    
    if VEHICLE_TYPE == 0:
        draw_car_model()
    else:
        draw_bike_model()
    
    glPopMatrix()
def draw_opponent_vehicle(index, pos_x, pos_y, angle):
    """Draw an opponent vehicle"""
    glPushMatrix()
    glTranslatef(pos_x, pos_y, 0)
    glRotatef(-angle, 0, 0, 1)
    
    # Use opponent's color
    color = opponent_colors[index]
    
    # Determine if it's a car or bike based on the color
    if index % 2 == 0:  # Even indices are cars
        # Draw a simpler car model
        glColor3f(color[0], color[1], color[2])
        glPushMatrix()
        glScalef(25, 15, 8)
        glutSolidCube(1)  # Main body
        glPopMatrix()
        
        # Wheels
        glColor3f(0.2, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(15, 10, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Simulate wheel as a cylinder
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-15, 10, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Simulate wheel as a cylinder
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(15, -10, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Simulate wheel as a cylinder
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-15, -10, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 3, 8, 1)  # Simulate wheel as a cylinder
        glPopMatrix()
    else:  # Odd indices are bikes
        # Draw a simpler bike model
        glColor3f(color[0], color[1], color[2])
        glPushMatrix()
        glScalef(5, 25, 5)
        glutSolidCube(1)  # Main body
        glPopMatrix()
        
        # Wheels
        glColor3f(0.2, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(0, 15, 0)
        gluCylinder(gluNewQuadric(), 8, 8, 2, 16, 1)  # Simulate wheel as a cylinder
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -15, 0)
        gluCylinder(gluNewQuadric(), 8, 8, 2, 16, 1)  # Simulate wheel as a cylinder
        glPopMatrix()
    
    glPopMatrix()


def draw_opponents():
    """Draw all opponent vehicles"""
    for i, opponent in enumerate(opponents):
        pos_x, pos_y, _, angle = opponent
        draw_opponent_vehicle(i, pos_x, pos_y, angle)

def draw_ui():
    """Draw UI elements like speedometer, position, lap counter, etc."""
    # Speed indicator
    speed_percentage = abs(player_speed) / MAX_SPEED * 100
    draw_text(10, 770, f"Speed: {speed_percentage:.0f}%")
    
    # Position indicator
    draw_text(10, 740, f"Position: {player_position}/4")
    
    # Lap counter
    draw_text(10, 710, f"Lap: {current_lap}/{MAX_LAPS}")
    
    # Timer
    if game_started:
        time_elapsed = (glutGet(GLUT_ELAPSED_TIME) - lap_start_time) / 1000.0
        draw_text(10, 680, f"Time: {time_elapsed:.2f}s")
        
        # Best lap time
        if best_lap_time < float('inf'):
            draw_text(10, 650, f"Best: {best_lap_time:.2f}s")
    
    # Vehicle type indicator
    vehicle_type = "Car" if VEHICLE_TYPE == 0 else "Bike"
    draw_text(850, 770, f"Vehicle: {vehicle_type}")
    
    # Camera mode indicator
    camera_modes = ["Follow", "First-person", "Overhead"]
    draw_text(850, 740, f"Camera: {camera_modes[camera_mode]}")
    
    # Display controls
    draw_text(850, 40, "Controls:")
    draw_text(850, 25, "WASD: Drive   C: Change Vehicle")
    draw_text(850, 10, "V: Change Color   Space: Start Race")

def draw_countdown():
    """Draw the countdown at the start of the race"""
    if countdown > 0:
        glColor3f(1.0, 0.0, 0.0)  # Red
        draw_text(480, 400, str(countdown))
    elif countdown == 0:
        glColor3f(0.0, 1.0, 0.0)  # Green
        draw_text(450, 400, "GO!")

def update_countdown():
    """Update the countdown timer"""
    global countdown, game_started, lap_start_time, countdown_start_time
    
    if not game_started and countdown >= 0:
        current_time = glutGet(GLUT_ELAPSED_TIME)
        time_since_start = (current_time - countdown_start_time) / 1000.0
        
        if time_since_start > 1:
            countdown -= 1
            countdown_start_time = current_time
            
            if countdown < 0:
                game_started = True
                lap_start_time = current_time

def update_player():
    """Update player position and physics"""
    global player_pos, player_angle, player_speed, wheel_rotation
    
    if not game_started:
        return
    
    # Calculate new position based on speed and angle
    angle_rad = math.radians(player_angle)
    delta_x = -math.sin(angle_rad) * player_speed
    delta_y = math.cos(angle_rad) * player_speed
    
    new_x = player_pos[0] + delta_x
    new_y = player_pos[1] + delta_y
    
    # Apply friction based on terrain
    friction = calculate_friction(new_x, new_y)
    player_speed *= friction
    
    # Update position
    player_pos[0] = new_x
    player_pos[1] = new_y
    
    # Update wheel rotation based on speed
    wheel_rotation += player_speed * 10
    if wheel_rotation > 360:
        wheel_rotation -= 360

def update_opponents():
    """Update opponent vehicles' positions"""
    global opponents
    
    if not game_started:
        return
    
    for i, opponent in enumerate(opponents):
        pos_x, pos_y, _, angle = opponent
        
        # Calculate target point (next track segment)
        segment_index = (i * 3 + int(angle / 10)) % len(track_segments)
        target_x, target_y = track_segments[segment_index]
        
        # Calculate direction to target
        dx = target_x - pos_x
        dy = target_y - pos_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Calculate angle to target
        target_angle = math.degrees(math.atan2(-dx, dy)) % 360
        
        # Adjust angle (simple steering)
        angle_diff = (target_angle - angle) % 360
        if angle_diff > 180:
            angle_diff -= 360
        
        # Steer towards target, with some randomness
        new_angle = angle + max(-3, min(3, angle_diff * 0.1 + random.uniform(-0.5, 0.5)))
        
        # Calculate speed (slower when turning sharply)
        speed = 2.0 + (3.0 - 3.0 * min(1.0, abs(angle_diff) / 90.0))
        
        # Move opponent
        new_angle_rad = math.radians(new_angle)
        new_x = pos_x - math.sin(new_angle_rad) * speed
        new_y = pos_y + math.cos(new_angle_rad) * speed
        
        # Update opponent data
        opponents[i] = [new_x, new_y, 0, new_angle]

def check_lap_completion():
    """Check if player has completed a lap"""
    global current_checkpoint, current_lap, lap_start_time, best_lap_time, checkpoint_passed, start_line_passed
    
    # Check if player has reached the current checkpoint
    checkpoint_x, checkpoint_y = checkpoints[current_checkpoint]
    dx = player_pos[0] - checkpoint_x
    dy = player_pos[1] - checkpoint_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance < TRACK_WIDTH:
        if current_checkpoint == 0 and checkpoint_passed:
            # Passed checkpoint 0 (top) after passing at least one other checkpoint
            start_line_passed = True
        
        # Move to next checkpoint
        current_checkpoint = (current_checkpoint + 1) % len(checkpoints)
        checkpoint_passed = True
        
        # Check if completed a full lap (passed all checkpoints and crossed start line)
        if current_checkpoint == 0 and checkpoint_passed and start_line_passed:
            # Calculate lap time
            current_time = glutGet(GLUT_ELAPSED_TIME)
            lap_time = (current_time - lap_start_time) / 1000.0
            lap_start_time = current_time
            
            # Update best lap time
            if lap_time < best_lap_time:
                best_lap_time = lap_time
            
            # Increment lap counter
            current_lap += 1
            checkpoint_passed = False
            start_line_passed = False

def update_player_position():
    """Update player's race position relative to opponents"""
    global player_position
    
    # Simple position calculation based on track completion
    # In a more complex implementation, this would consider actual track progress
    player_position = 1
    
    for i, opponent in enumerate(opponents):
        # For simplicity, compare lap count and checkpoint progress
        # This is a very basic implementation - a real game would need more sophisticated tracking
        player_position += 1

def keyboardListener(key, x, y):
    """Handle keyboard input"""
    global player_speed, player_angle, VEHICLE_TYPE, current_color_index
    global game_started, countdown, countdown_start_time, camera_mode
    
    # Acceleration (W key)
    if key == b'w':
        player_speed = min(player_speed + player_acceleration, MAX_SPEED)
    
    # Braking/Reverse (S key)
    if key == b's':
        player_speed = max(player_speed - player_acceleration, -MAX_SPEED/2)
    
    # Steering left (A key)
    if key == b'a':
        player_angle = (player_angle + player_steering_speed) % 360
    
    # Steering right (D key)
    if key == b'd':
        player_angle = (player_angle - player_steering_speed) % 360
    
    # Change vehicle type (C key)
    if key == b'c':
        VEHICLE_TYPE = 1 - VEHICLE_TYPE  # Toggle between 0 (car) and 1 (bike)
    
    # Change vehicle color (V key)
    if key == b'v':
        if VEHICLE_TYPE == 0:  # Car
            current_color_index = (current_color_index + 1) % len(CAR_COLORS)
        else:  # Bike
            current_color_index = (current_color_index + 1) % len(BIKE_COLORS)
    
    # Start race (Spacebar)
    if key == b' ' and not game_started:
        countdown = 3
        countdown_start_time = glutGet(GLUT_ELAPSED_TIME)
    
    # Change camera view (B key)
    if key == b'b':
        camera_mode = (camera_mode + 1) % 3

def specialKeyListener(key, x, y):
    """Handle special key input"""
    global camera_pos, camera_angle
    
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_pos[2] += 10
        camera_pos[2] = min(800, camera_pos[2])
    
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_pos[2] -= 10
        camera_pos[2] = max(100, camera_pos[2])
    
    # Rotate camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle - 5) % 360
    
    # Rotate camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle + 5) % 360

# ------------------------------------------------------------------
# Display & update loop
# ------------------------------------------------------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, 1000, 800)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # simple perspective
    gluPerspective(60, 1000/800, 1, 2000)
    
    # Camera setup
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Compute camera based on mode
    if camera_mode == 0:  # Follow camera
        # Behind & above the player
        ang = math.radians(player_angle)
        behind = 70
        height = 40
        camX = player_pos[0] + math.sin(ang) * behind
        camY = player_pos[1] - math.cos(ang) * behind
        camZ = player_pos[2] + height
        gluLookAt(camX, camY, camZ,
                  player_pos[0], player_pos[1], player_pos[2] + 5,
                  0, 0, 1)
    elif camera_mode == 1:  # First-person
        ang = math.radians(player_angle)
        forward = 5
        camX = player_pos[0] - math.sin(ang) * forward
        camY = player_pos[1] + math.cos(ang) * forward
        camZ = player_pos[2] + 5
        tgtX = player_pos[0] - math.sin(ang) * (forward + 20)
        tgtY = player_pos[1] + math.cos(ang) * (forward + 20)
        gluLookAt(camX, camY, camZ,
                  tgtX, tgtY, player_pos[2] + 5,
                  0, 0, 1)
    else:  # Overhead
        gluLookAt(0, 0, 600,
                  0, 0, 0,
                  0, 1, 0)

    # Draw scene
    draw_ground()
    draw_track()
    draw_opponents()
    draw_player_vehicle()
    draw_ui()
    draw_countdown()
    glutSwapBuffers()

def idle():
    # update physics & timers
    update_countdown()
    update_player()
    update_opponents()
    check_lap_completion()
    update_player_position()
    glutPostRedisplay()

# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  # Removed GLUT_DEPTH as it's not allowed
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"CSE423: Simple Car Race")
    glClearColor(0.4, 0.7, 1.0, 1.0)  # sky-blue background
    initialize_opponents()  # place AI cars
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)

    glutMainLoop()

if __name__ == "__main__":
    main()