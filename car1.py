from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random
 
# ── Camera-related variables ──────────────────────────────────────────────────
camera_pos = (0, 520, 1250)         # tuple – matches template style
camera_mode = 0
fovY = 64                           # Field of view
GRID_LENGTH = 12000                 # Length of grid lines
 
# ── Player state ──────────────────────────────────────────────────────────────
player_pos = [0, 0, 240]
player_angle = 0
player_life = 5
 
lane_positions = [-140, 0, 140]
lane_index = 1
target_x = lane_positions[lane_index]
 
base_speed    = 6.4
current_speed = base_speed
target_speed  = base_speed
max_speed     = 24.0
nitro_speed   = 34.0
min_speed     = 4.0
acceleration  = base_speed * 0.25
brake_power   = base_speed * 0.18
turn_speed    = 27.0
 
distance_travelled = 0.0
coins_collected    = 0
fuel               = 1000.0
next_fuel_distance = 300.0
 
shield_timer   = 0
nitro_timer    = 0
cheat_mode     = False
horn_timer     = 0
horn_pushes    = 0
current_scene  = 0
game_over      = False
last_update_time = 0
frame_factor   = 1.0
 
magnet_timer   = 0
pause_game     = False
difficulty_mode  = 2
difficulty_names = ["", "Easy", "Normal", "Hard"]
best_distance    = 0
last_speed_level = 1
 
enemies     = []        # [x, z, scale, scale_dir, type]
num_enemies = 8
 
scene_names = ["City", "Desert", "Greenland"]
 
 
# ── HUD text helper – identical pattern to template ───────────────────────────
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)     # left, right, bottom, top
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
 
 
# ── Primitive helpers (only allowed functions) ────────────────────────────────
 
def draw_cylinder(base_r, top_r, height, slices=10, stacks=10):
    """Thin wrapper – gluCylinder is in the template."""
    gluCylinder(gluNewQuadric(), base_r, top_r, height, slices, stacks)
 
 
def draw_sphere(radius, slices=10, stacks=10):
    """Thin wrapper – gluSphere is in the template."""
    gluSphere(gluNewQuadric(), radius, slices, stacks)
 
 
def draw_torus_quad(inner_r, outer_r, steps=16):
    """
    Torus built from GL_QUADS – replaces glutSolidTorus which is NOT in the template.
    Drawn centred at the origin in the XY plane.
    """
    step = 2 * math.pi / steps
    for i in range(steps):
        a0, a1 = i * step, (i + 1) * step
        for j in range(steps):
            b0, b1 = j * step, (j + 1) * step
            def pt(a, b):
                cx = (outer_r + inner_r * math.cos(b)) * math.cos(a)
                cy = (outer_r + inner_r * math.cos(b)) * math.sin(a)
                cz = inner_r * math.sin(b)
                return cx, cy, cz
            glBegin(GL_QUADS)
            glVertex3f(*pt(a0, b0))
            glVertex3f(*pt(a1, b0))
            glVertex3f(*pt(a1, b1))
            glVertex3f(*pt(a0, b1))
            glEnd()
 
 
def draw_cone_quad(base_r, height, slices=12):
    """
    Cone built from GL_TRIANGLES – replaces glutSolidCone which is NOT in the template.
    Tip at (0, height, 0), base on the XZ plane.
    """
    step = 2 * math.pi / slices
    for i in range(slices):
        a0, a1 = i * step, (i + 1) * step
        # Side face
        glBegin(GL_TRIANGLES)
        glVertex3f(0, height, 0)
        glVertex3f(base_r * math.cos(a0), 0, base_r * math.sin(a0))
        glVertex3f(base_r * math.cos(a1), 0, base_r * math.sin(a1))
        glEnd()
        # Base cap
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(base_r * math.cos(a1), 0, base_r * math.sin(a1))
        glVertex3f(base_r * math.cos(a0), 0, base_r * math.sin(a0))
        glEnd()
 
 
def draw_wire_sphere_quad(radius, slices=12, stacks=8):
    """
    Wire-sphere approximation using GL_QUADS latitude bands –
    replaces glutWireSphere which is NOT in the template.
    """
    lat_step = math.pi / stacks
    lon_step = 2 * math.pi / slices
    for i in range(stacks):
        lat0 = -math.pi / 2 + i * lat_step
        lat1 = lat0 + lat_step
        r0 = math.cos(lat0) * radius
        r1 = math.cos(lat1) * radius
        y0 = math.sin(lat0) * radius
        y1 = math.sin(lat1) * radius
        glBegin(GL_QUADS)
        for j in range(slices):
            lon0, lon1 = j * lon_step, (j + 1) * lon_step
            glVertex3f(r0 * math.cos(lon0), y0, r0 * math.sin(lon0))
            glVertex3f(r0 * math.cos(lon1), y0, r0 * math.sin(lon1))
            glVertex3f(r1 * math.cos(lon1), y1, r1 * math.sin(lon1))
            glVertex3f(r1 * math.cos(lon0), y1, r1 * math.sin(lon0))
        glEnd()
 
 
# ── Player car ────────────────────────────────────────────────────────────────
def draw_green_car():
    glPushMatrix()
    glTranslatef(player_pos[0], 28, player_pos[2])
    glRotatef(player_angle, 0, 0, 1)
 
    # Body
    glColor3f(0.0, 0.65, 0.15)
    glPushMatrix()
    glScalef(1.35, 0.35, 2.2)
    glutSolidCube(55)
    glPopMatrix()
 
    # Cabin
    glPushMatrix()
    glTranslatef(0, 25, -12)
    glColor3f(0.0, 0.90, 0.25)
    glScalef(0.85, 0.45, 1.05)
    glutSolidCube(45)
    glPopMatrix()
 
    # Headlights
    glPushMatrix()
    glTranslatef(-22, 5, -65)
    glColor3f(1, 1, 0)
    glutSolidCube(12)
    glTranslatef(44, 0, 0)
    glutSolidCube(12)
    glPopMatrix()
 
    # Wheels – GL_QUADS torus (no glutSolidTorus)
    glColor3f(0, 0, 0)
    for wx in [-43, 43]:
        for wz in [-48, 48]:
            glPushMatrix()
            glTranslatef(wx, -10, wz)
            glRotatef(90, 0, 1, 0)
            draw_torus_quad(inner_r=7, outer_r=14, steps=12)
            glPopMatrix()
 
    glPopMatrix()
 
 
# ── Road objects ──────────────────────────────────────────────────────────────
def draw_road_object(enemy):
    x, z, scale, scale_dir, item_type = enemy
    glPushMatrix()
    glTranslatef(x, 25, z)
 
    if item_type == 0:          # Small red car
        glColor3f(0.9, 0.05, 0.05)
        glPushMatrix()
        glScalef(1.25, 0.35, 1.9)
        glutSolidCube(55)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 24, -8)
        glColor3f(0.9, 0.35, 0.15)
        glScalef(0.85, 0.45, 0.95)
        glutSolidCube(42)
        glPopMatrix()
        glColor3f(0, 0, 0)
        for wx in [-40, 40]:
            for wz in [-42, 42]:
                glPushMatrix()
                glTranslatef(wx, -8, wz)
                glRotatef(90, 0, 1, 0)
                draw_torus_quad(inner_r=6, outer_r=12, steps=10)
                glPopMatrix()
 
    elif item_type == 1:        # Truck
        glPushMatrix()
        glColor3f(0.7, 0.1, 0.1)
        glTranslatef(0, 0, 25)
        glScalef(1.35, 0.65, 2.0)
        glutSolidCube(60)
        glPopMatrix()
        glPushMatrix()
        glColor3f(0.95, 0.45, 0.05)
        glTranslatef(0, 8, -65)
        glScalef(1.15, 0.75, 0.9)
        glutSolidCube(55)
        glPopMatrix()
        glColor3f(0, 0, 0)
        for wx in [-48, 48]:
            for wz in [-70, 0, 70]:
                glPushMatrix()
                glTranslatef(wx, -18, wz)
                glRotatef(90, 0, 1, 0)
                draw_torus_quad(inner_r=7, outer_r=14, steps=10)
                glPopMatrix()
 
    elif item_type == 2:        # Road cones – GL_TRIANGLES cone (no glutSolidCone)
        glColor3f(0.55, 0.55, 0.55)
        for sx in [-24, 0, 24]:
            glPushMatrix()
            glTranslatef(sx, -20, 0)
            glRotatef(-90, 1, 0, 0)
            draw_cone_quad(base_r=18, height=55)
            glPopMatrix()
 
    elif item_type == 3:        # Street lamp
        glColor3f(0.45, 0.45, 0.45)
        glPushMatrix()
        glTranslatef(0, 5, 0)
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(10, 10, 42)   # gluCylinder – in template
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 55, 0)
        glColor3f(1.0, 0.78, 0.55)
        draw_sphere(15)             # gluSphere – in template
        glPopMatrix()
        glColor3f(0.45, 0.45, 0.45)
        for ax in [-18, 18]:
            glPushMatrix()
            glTranslatef(ax, 25, 0)
            glScalef(0.25, 1.1, 0.25)
            glutSolidCube(25)
            glPopMatrix()
 
    elif item_type == 4:        # Coin – GL_QUADS torus ring
        glPushMatrix()
        glRotatef(scale * 120, 0, 1, 0)
        glColor3f(1.0, 0.82, 0.0)
        draw_torus_quad(inner_r=7, outer_r=24, steps=20)
        glPopMatrix()
 
    elif item_type == 5:        # Shield – GL_QUADS wire-sphere + cube core
        glColor3f(0.0, 0.8, 1.0)
        draw_wire_sphere_quad(radius=32 + scale * 3)
        glPushMatrix()
        glScalef(0.7, 0.9, 0.18)
        glutSolidCube(45)
        glPopMatrix()
 
    elif item_type == 6:        # Nitro – cylinder + GL_TRIANGLES cone tip
        glPushMatrix()
        glColor3f(0.0, 0.25, 1.0)
        glRotatef(-90, 1, 0, 0)
        draw_cylinder(15, 15, 55)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 58, 0)
        glColor3f(0.0, 0.25, 1.0)
        draw_cone_quad(base_r=18, height=32)
        glPopMatrix()
 
    elif item_type == 7:        # Magnet – two cylinders + cube crossbar
        glColor3f(0.95, 0.05, 0.95)
        for tx in [-12, 12]:
            glPushMatrix()
            glTranslatef(tx, 0, 0)
            glRotatef(-90, 1, 0, 0)
            draw_cylinder(7, 7, 50)
            glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 50, 0)
        glScalef(1.2, 0.25, 0.25)
        glutSolidCube(42)
        glPopMatrix()
 
    elif item_type == 8:        # Fuel canister – cube body + cube cap
        glColor3f(0.0, 0.85, 0.15)
        glPushMatrix()
        glScalef(0.9, 1.25, 0.65)
        glutSolidCube(42)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 34, 0)
        glColor3f(0.02, 0.35, 0.05)
        glScalef(0.45, 0.25, 0.45)
        glutSolidCube(35)
        glPopMatrix()
 
    elif item_type == 9:        # Heart / life – two spheres + rotated cube
        glColor3f(1.0, 0.0, 0.0)
        for tx in [-12, 12]:
            glPushMatrix()
            glTranslatef(tx, 8, 0)
            draw_sphere(18)     # gluSphere – in template
            glPopMatrix()
        glPushMatrix()
        glTranslatef(0, -8, 0)
        glRotatef(-45, 0, 0, 1)
        glScalef(1.15, 1.15, 0.35)
        glutSolidCube(28)
        glPopMatrix()
 
    glPopMatrix()
 
 
# ── Active power-up effects ───────────────────────────────────────────────────
def draw_active_effects():
    if shield_timer > 0:
        glPushMatrix()
        glTranslatef(player_pos[0], 35, player_pos[2])
        glColor3f(0.0, 0.8, 1.0)
        draw_wire_sphere_quad(radius=90)    # GL_QUADS – no glutWireSphere
        glPopMatrix()
 
    if nitro_timer > 0:
        glColor3f(0.0, 0.25, 1.0)
        for sx in [-28, 0, 28]:
            glPushMatrix()
            glTranslatef(player_pos[0] + sx, 12, player_pos[2] + 82)
            glRotatef(90, 1, 0, 0)
            draw_cone_quad(base_r=10, height=45)  # GL_TRIANGLES – no glutSolidCone
            glPopMatrix()
 
    if magnet_timer > 0:
        glPushMatrix()
        glTranslatef(player_pos[0], 38, player_pos[2])
        glColor3f(0.95, 0.05, 0.95)
        draw_wire_sphere_quad(radius=125)   # GL_QUADS – no glutWireSphere
        glPopMatrix()
 
 
# ── Environment ───────────────────────────────────────────────────────────────
def draw_environment():
    road_width     = 470
    shoulder_width = 820
    near_z         = 1600
    far_z          = -GRID_LENGTH
    sky_z          = far_z - 80
    sky_top        = 3000
    scene_offset   = (distance_travelled * 32) % 280
    line_offset    = (distance_travelled * 42) % 180
 
    if current_scene == 0:
        sky_bottom     = [0.04, 0.05, 0.09]
        sky_upper      = [0.18, 0.23, 0.34]
        ground_color   = [0.15, 0.15, 0.17]
        shoulder_color = [0.27, 0.27, 0.30]
    elif current_scene == 1:
        sky_bottom     = [0.90, 0.58, 0.26]
        sky_upper      = [0.98, 0.77, 0.42]
        ground_color   = [0.76, 0.63, 0.38]
        shoulder_color = [0.64, 0.51, 0.31]
    else:
        sky_bottom     = [0.45, 0.70, 0.95]
        sky_upper      = [0.72, 0.90, 1.00]
        ground_color   = [0.12, 0.55, 0.16]
        shoulder_color = [0.08, 0.42, 0.10]
 
    # Sky back wall
    glBegin(GL_QUADS)
    glColor3f(*sky_bottom)
    glVertex3f(-GRID_LENGTH * 2, 0,       sky_z)
    glVertex3f( GRID_LENGTH * 2, 0,       sky_z)
    glColor3f(*sky_upper)
    glVertex3f( GRID_LENGTH * 2, sky_top, sky_z)
    glVertex3f(-GRID_LENGTH * 2, sky_top, sky_z)
    glEnd()
 
    # Sky ceiling
    glBegin(GL_QUADS)
    glColor3f(*sky_upper)
    glVertex3f(-GRID_LENGTH * 2, sky_top, near_z)
    glVertex3f( GRID_LENGTH * 2, sky_top, near_z)
    glVertex3f( GRID_LENGTH * 2, sky_top, sky_z)
    glVertex3f(-GRID_LENGTH * 2, sky_top, sky_z)
    glEnd()
 
    # Sky side walls
    glBegin(GL_QUADS)
    glColor3f(*sky_bottom)
    glVertex3f(-GRID_LENGTH * 2, 0,       near_z)
    glVertex3f(-GRID_LENGTH * 2, 0,       sky_z)
    glColor3f(*sky_upper)
    glVertex3f(-GRID_LENGTH * 2, sky_top, sky_z)
    glVertex3f(-GRID_LENGTH * 2, sky_top, near_z)
    glColor3f(*sky_bottom)
    glVertex3f( GRID_LENGTH * 2, 0,       sky_z)
    glVertex3f( GRID_LENGTH * 2, 0,       near_z)
    glColor3f(*sky_upper)
    glVertex3f( GRID_LENGTH * 2, sky_top, near_z)
    glVertex3f( GRID_LENGTH * 2, sky_top, sky_z)
    glEnd()
 
    # Sun / moon – gluSphere is in the template
    glPushMatrix()
    if current_scene == 0:
        glTranslatef(800, 900, sky_z + 40)
        glColor3f(0.90, 0.90, 1.0)
    elif current_scene == 1:
        glTranslatef(760, 950, sky_z + 40)
        glColor3f(1.0, 0.82, 0.15)
    else:
        glTranslatef(-760, 950, sky_z + 40)
        glColor3f(1.0, 0.95, 0.45)
    draw_sphere(85, 20, 20)
    glPopMatrix()
 
    # Ground
    glColor3f(*ground_color)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH * 2, 0, far_z)
    glVertex3f( GRID_LENGTH * 2, 0, far_z)
    glVertex3f( GRID_LENGTH * 2, 0, near_z)
    glVertex3f(-GRID_LENGTH * 2, 0, near_z)
    glEnd()
 
    # Shoulder
    glColor3f(*shoulder_color)
    glBegin(GL_QUADS)
    glVertex3f(-shoulder_width/2, 2, far_z)
    glVertex3f( shoulder_width/2, 2, far_z)
    glVertex3f( shoulder_width/2, 2, near_z)
    glVertex3f(-shoulder_width/2, 2, near_z)
    glEnd()
 
    # Road surface
    glColor3f(0.055, 0.055, 0.065)
    glBegin(GL_QUADS)
    glVertex3f(-road_width/2, 5, far_z)
    glVertex3f( road_width/2, 5, far_z)
    glVertex3f( road_width/2, 5, near_z)
    glVertex3f(-road_width/2, 5, near_z)
    glEnd()
 
    # Road edges
    glColor3f(1.0, 1.0, 1.0)
    for x in [-road_width/2, road_width/2]:
        glBegin(GL_QUADS)
        glVertex3f(x - 8, 8, far_z)
        glVertex3f(x + 8, 8, far_z)
        glVertex3f(x + 8, 8, near_z)
        glVertex3f(x - 8, 8, near_z)
        glEnd()
 
    # Lane dashes
    glColor3f(1.0, 0.92, 0.20)
    for x in [-78, 78]:
        for z in range(far_z - 220, near_z + 180, 180):
            dz = z + line_offset
            glBegin(GL_QUADS)
            glVertex3f(x - 7, 10, dz)
            glVertex3f(x + 7, 10, dz)
            glVertex3f(x + 7, 10, dz + 95)
            glVertex3f(x - 7, 10, dz + 95)
            glEnd()
 
    # Road shadow detail marks
    glColor3f(0.10, 0.10, 0.115)
    for z in range(far_z, near_z, 260):
        dz = z + (distance_travelled * 18) % 260
        glBegin(GL_QUADS)
        glVertex3f(-190, 11, dz);      glVertex3f(-120, 11, dz + 20)
        glVertex3f(-126, 11, dz + 34); glVertex3f(-198, 11, dz + 12)
        glEnd()
        glBegin(GL_QUADS)
        glVertex3f(118, 11, dz + 90);  glVertex3f(192, 11, dz + 68)
        glVertex3f(200, 11, dz + 84);  glVertex3f(128, 11, dz + 108)
        glEnd()
 
    # ── Scene-specific decoration ─────────────────────────────────────────────
    if current_scene == 0:      # City
        glColor3f(0.32, 0.32, 0.34)
        glBegin(GL_QUADS)
        glVertex3f(-620, 12, far_z);  glVertex3f(-250, 12, far_z)
        glVertex3f(-250, 12, near_z); glVertex3f(-620, 12, near_z)
        glVertex3f( 250, 12, far_z);  glVertex3f( 620, 12, far_z)
        glVertex3f( 620, 12, near_z); glVertex3f( 250, 12, near_z)
        glEnd()
 
        # Background skyline – glutSolidCube is in the template
        for bx in range(-2200, 2300, 180):
            h = 300 + abs(math.sin(bx * 0.017)) * 470
            w = 95  + abs(math.cos(bx * 0.011)) * 70
            d = 75  + abs(math.sin(bx * 0.021)) * 35
            glPushMatrix()
            glTranslatef(bx, h/2, sky_z + 75)
            glColor3f(0.11 + abs(math.sin(bx))*0.07,
                      0.13 + abs(math.cos(bx))*0.06,
                      0.19 + abs(math.sin(bx*0.3))*0.08)
            glScalef(w/60, h/60, d/60)
            glutSolidCube(60)
            glPopMatrix()
            glColor3f(1.0, 0.86, 0.32)
            for wx in range(int(-w/2) + 18, int(w/2) - 8, 32):
                for wy in range(75, int(h) - 35, 64):
                    if (wx + wy + bx) % 5 != 0:
                        glBegin(GL_QUADS)
                        glVertex3f(bx+wx-6, wy-11, sky_z+118)
                        glVertex3f(bx+wx+6, wy-11, sky_z+118)
                        glVertex3f(bx+wx+6, wy+11, sky_z+118)
                        glVertex3f(bx+wx-6, wy+11, sky_z+118)
                        glEnd()
 
        for i in range(far_z + 480, near_z + 720, 500):
            z = i + scene_offset
            h1 = 300 + abs(math.sin(i * 0.025)) * 340
            h2 = 280 + abs(math.cos(i * 0.018)) * 330
            colors = [[0.22,0.24,0.31],[0.18,0.21,0.28],
                      [0.29,0.26,0.24],[0.20,0.25,0.27]]
            for side_x, bh, bz, color_id in [
                    (-660, h1, z,     (i//500) % 4),
                    ( 660, h2, z+180, (i//500+1) % 4)]:
                glPushMatrix()
                glTranslatef(side_x, bh/2 + 12, bz)
                glColor3f(*colors[color_id])
                glScalef(2.15, bh/60, 1.35)
                glutSolidCube(60)
                glPopMatrix()
                face_x = side_x - 66 if side_x > 0 else side_x + 66
                glColor3f(0.96, 0.82, 0.28)
                for wz in [-28, 0, 28]:
                    for wy in range(70, int(bh) - 45, 62):
                        if (wy + int(bz) + int(side_x) + wz) % 4 != 0:
                            glBegin(GL_QUADS)
                            glVertex3f(face_x, wy-12, bz+wz-9)
                            glVertex3f(face_x, wy+12, bz+wz-9)
                            glVertex3f(face_x, wy+12, bz+wz+9)
                            glVertex3f(face_x, wy-12, bz+wz+9)
                            glEnd()
            # Street lamps – gluCylinder + gluSphere (both in template)
            for lx in [-335, 335]:
                glPushMatrix()
                glTranslatef(lx, 68, z + 60)
                glColor3f(0.04, 0.04, 0.045)
                glRotatef(-90, 1, 0, 0)
                draw_cylinder(6, 6, 128)
                glPopMatrix()
                glPushMatrix()
                glTranslatef(lx, 140, z + 60)
                glColor3f(1.0, 0.96, 0.58)
                draw_sphere(18)
                glPopMatrix()
 
    elif current_scene == 1:    # Desert
        # Sand dunes – GL_TRIANGLES (in template)
        for dx in range(-2200, 2300, 360):
            glColor3f(0.58, 0.40, 0.20)
            glBegin(GL_TRIANGLES)
            glVertex3f(dx-270, 0,                        sky_z+50)
            glVertex3f(dx+20,  220+abs(math.sin(dx))*90, sky_z+50)
            glVertex3f(dx+300, 0,                        sky_z+50)
            glEnd()
            glColor3f(0.88, 0.68, 0.35)
            glBegin(GL_TRIANGLES)
            glVertex3f(dx-80,  0,                         sky_z+70)
            glVertex3f(dx+70,  165+abs(math.cos(dx))*70,  sky_z+70)
            glVertex3f(dx+250, 0,                         sky_z+70)
            glEnd()
        # Cacti – gluCylinder trunk + glutSolidCube arms (both in template)
        for i in range(far_z + 450, near_z + 500, 330):
            z = i + scene_offset
            for x in [-520, 520]:
                glPushMatrix()
                glTranslatef(x, 45, z)
                glColor3f(0.05, 0.45, 0.10)
                glRotatef(-90, 1, 0, 0)
                draw_cylinder(10, 10, 95)
                glPopMatrix()
                for armx in [-26, 26]:
                    glPushMatrix()
                    glTranslatef(x + armx, 78, z)
                    glColor3f(0.05, 0.45, 0.10)
                    glScalef(0.28, 1.25, 0.28)
                    glutSolidCube(38)
                    glPopMatrix()
            # Boulders – gluSphere (in template)
            glPushMatrix()
            glTranslatef(-720, 26, z+80)
            glColor3f(0.42, 0.33, 0.22)
            glScalef(1.5, 0.55, 1.0)
            draw_sphere(38)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(720, 18, z-55)
            glColor3f(0.51, 0.42, 0.29)
            glScalef(1.25, 0.45, 0.9)
            draw_sphere(30)
            glPopMatrix()
 
    else:                       # Greenland
        # Mountains – GL_TRIANGLES (in template)
        for mx in range(-2100, 2200, 420):
            glColor3f(0.25, 0.42, 0.35)
            glBegin(GL_TRIANGLES)
            glVertex3f(mx-320, 0,                         sky_z+50)
            glVertex3f(mx,     420+abs(math.sin(mx))*130, sky_z+50)
            glVertex3f(mx+330, 0,                         sky_z+50)
            glEnd()
            glColor3f(0.90, 0.93, 0.95)
            glBegin(GL_TRIANGLES)
            glVertex3f(mx-75, 310,                         sky_z+75)
            glVertex3f(mx,    420+abs(math.sin(mx))*130,   sky_z+75)
            glVertex3f(mx+82, 310,                         sky_z+75)
            glEnd()
        # Trees – gluCylinder trunk + gluSphere foliage (both in template)
        for i in range(far_z + 400, near_z + 550, 270):
            z = i + scene_offset
            for x in [-520, 520]:
                glPushMatrix()
                glTranslatef(x, 35, z)
                glColor3f(0.35, 0.18, 0.08)
                glRotatef(-90, 1, 0, 0)
                draw_cylinder(10, 10, 80)
                glPopMatrix()
                glPushMatrix()
                glTranslatef(x, 105, z)
                glColor3f(0.0, 0.38, 0.05)
                draw_sphere(44)
                glPopMatrix()
                glPushMatrix()
                glTranslatef(x - 36, 85, z + 14)
                glColor3f(0.0, 0.32, 0.04)
                draw_sphere(32)
                glPopMatrix()
            # Rocks – gluSphere (in template)
            glPushMatrix()
            glTranslatef(720, 22, z+50)
            glColor3f(0.70, 0.70, 0.75)
            draw_sphere(29)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(-720, 16, z-50)
            glColor3f(0.65, 0.68, 0.70)
            glScalef(1.25, 0.55, 0.8)
            draw_sphere(25)
            glPopMatrix()
 
 
# ── Game logic ────────────────────────────────────────────────────────────────
def update_player_movement():
    global current_speed, target_speed, distance_travelled, fuel, shield_timer, nitro_timer
    global horn_timer, player_angle, game_over, current_scene, player_life, target_x
    global lane_index, cheat_mode, last_update_time, frame_factor, magnet_timer
    global pause_game, best_distance, last_speed_level
 
    elapsed_time = glutGet(GLUT_ELAPSED_TIME)
    if last_update_time == 0:
        frame_factor = 1.0
    else:
        frame_factor = (elapsed_time - last_update_time) / 16.0
        frame_factor = max(0.25, min(2.5, frame_factor))
    last_update_time = elapsed_time
 
    if pause_game and not game_over:
        return
    if game_over:
        if distance_travelled > best_distance:
            best_distance = distance_travelled
        return
 
    for attr in ['shield_timer', 'nitro_timer', 'magnet_timer', 'horn_timer']:
        val = globals()[attr]
        if val > 0:
            globals()[attr] = max(0, val - frame_factor)
 
    if fuel <= 0:
        fuel = 0
        target_speed = 0
 
    speed_level = int(distance_travelled // 500) + 1
    if speed_level > last_speed_level:
        last_speed_level = speed_level
    level_bonus  = min((speed_level - 1) * 0.55, 6.0)
    active_max   = (nitro_speed if nitro_timer > 0 else max_speed) + level_bonus
    if target_speed > active_max:
        target_speed = active_max
 
    if current_speed < target_speed:
        current_speed = min(current_speed + acceleration * frame_factor, target_speed)
    elif current_speed > target_speed:
        current_speed = max(current_speed - brake_power * frame_factor, target_speed)
    current_speed = min(current_speed, active_max)
    if fuel > 0 and current_speed < min_speed:
        current_speed = min_speed
    if fuel <= 0 and current_speed < 0:
        current_speed = 0
 
    # Cheat-mode AI
    if cheat_mode:
        safe_lane_ids = []
        best_lane     = lane_index
        best_space    = -1
        for i in range(len(lane_positions)):
            lane_blocked  = False
            closest_block = 99999
            for enemy in enemies:
                if enemy[4] in (0, 1, 2, 3):
                    ahead = player_pos[2] - enemy[1]
                    if 0 < ahead < 1700 and abs(enemy[0] - lane_positions[i]) < 82:
                        lane_blocked  = True
                        closest_block = min(closest_block, ahead)
            if not lane_blocked:
                safe_lane_ids.append(i)
                closest_block = 99999
            if closest_block > best_space:
                best_space = closest_block
                best_lane  = i
 
        pickup_lane_choice   = -1
        best_pickup_distance = 99999
        for enemy in enemies:
            if enemy[4] in (4, 5, 6, 8):
                ahead = player_pos[2] - enemy[1]
                if 0 < ahead < 1900:
                    pickup_lane = min(range(len(lane_positions)),
                                      key=lambda i: abs(enemy[0] - lane_positions[i]))
                    pickup_safe = all(
                        not (d[4] in (0,1,2,3) and
                             0 < player_pos[2]-d[1] < ahead+430 and
                             abs(d[0]-lane_positions[pickup_lane]) < 85)
                        for d in enemies
                    )
                    if pickup_safe and ahead < best_pickup_distance:
                        best_pickup_distance = ahead
                        pickup_lane_choice   = pickup_lane
 
        if pickup_lane_choice != -1:
            lane_index = pickup_lane_choice
        elif lane_index not in safe_lane_ids:
            if safe_lane_ids:
                lane_index = min(safe_lane_ids,
                                 key=lambda i: abs(player_pos[0] - lane_positions[i]))
            else:
                lane_index = best_lane
        target_x = lane_positions[lane_index]
 
        emergency = any(
            d[4] in (0,1,2,3) and
            0 < player_pos[2]-d[1] < 250 and
            abs(d[0]-player_pos[0]) < 88
            for d in enemies
        )
        if emergency and safe_lane_ids:
            player_pos[0] = target_x
 
    lane_step = turn_speed * frame_factor * (1.75 if cheat_mode else 1.0)
    if player_pos[0] < target_x:
        player_pos[0] = min(player_pos[0] + lane_step, target_x)
    elif player_pos[0] > target_x:
        player_pos[0] = max(player_pos[0] - lane_step, target_x)
 
    player_angle = max(-14, min(14, (target_x - player_pos[0]) * -0.18))
 
    move_meters = current_speed * 0.070 * frame_factor
    distance_travelled += move_meters
    if current_speed > 0:
        fuel -= move_meters
 
    current_scene = int(distance_travelled // 500) % 3
 
    if fuel <= 0 and current_speed <= 0.05:
        current_speed = 0
        game_over = True
        if distance_travelled > best_distance:
            best_distance = distance_travelled
    if player_life <= 0:
        player_life   = 0
        current_speed = 0
        target_speed  = 0
        game_over     = True
        if distance_travelled > best_distance:
            best_distance = distance_travelled
 
 
def _random_type():
    r = random.randint(0, 199)
    if   r < 26:  return 0
    elif r < 46:  return 1
    elif r < 60:  return 2
    elif r < 78:  return 3
    elif r < 152: return 4
    elif r < 172: return 5
    elif r < 188: return 6
    elif r < 199: return 7
    else:         return 9
 
 
def _safe_spawn_z(existing):
    new_z = -GRID_LENGTH + 750 + random.uniform(0, 850)
    for _ in range(12):
        if all(abs(new_z - e[1]) >= 850 for e in existing):
            break
        new_z += 900
        if new_z > -900:
            new_z = -GRID_LENGTH + 750 + random.uniform(0, 850)
    return new_z
 
 
def update_road_objects():
    global enemies, next_fuel_distance
    if game_over or pause_game:
        return
 
    while distance_travelled >= next_fuel_distance:
        fz = -GRID_LENGTH + 750 + random.uniform(0, 850)
        for oe in enemies:
            if abs(fz - oe[1]) < 800:
                fz += 850
                if fz > -900:
                    fz = -GRID_LENGTH + 750 + random.uniform(0, 850)
        enemies.append([random.choice(lane_positions), fz, 1.0, True, 8])
        next_fuel_distance += 300
 
    new_enemies = []
    for enemy in enemies:
        enemy[1] += current_speed * 2.35 * frame_factor
        if enemy[3]:
            enemy[2] += 0.02 * frame_factor
            if enemy[2] >= 1.25: enemy[3] = False
        else:
            enemy[2] -= 0.02 * frame_factor
            if enemy[2] <= 0.75: enemy[3] = True
        if enemy[1] > 1700:
            if enemy[4] == 8:
                continue
            enemy = [random.choice(lane_positions),
                     _safe_spawn_z(new_enemies), 1.0, True, _random_type()]
        new_enemies.append(enemy)
    enemies[:] = new_enemies
 
 
def handle_collisions_and_pickups():
    global enemies, player_life, coins_collected, shield_timer, nitro_timer, fuel
    global current_speed, target_speed, game_over, lane_index, target_x, magnet_timer
    global best_distance
    if game_over or pause_game:
        return
 
    new_enemies = []
    for enemy in enemies:
        hit = False
        ex, ez, scale, scale_dir, item_type = enemy
 
        if magnet_timer > 0 and item_type in (4, 5, 6, 8, 9):
            if abs(player_pos[0] - ex) < 360 and -120 < player_pos[2] - ez < 1500:
                hit = True
        if not hit and abs(player_pos[0] - ex) < 48 and abs(player_pos[2] - ez) < 62:
            hit = True
 
        if hit:
            if cheat_mode and item_type in (0, 1, 2, 3):
                for i in range(len(lane_positions)):
                    danger_here = any(
                        d[4] in (0,1,2,3) and
                        0 < player_pos[2]-d[1] < 470 and
                        abs(d[0]-lane_positions[i]) < 85
                        for d in enemies
                    )
                    if not danger_here:
                        lane_index    = i
                        target_x      = lane_positions[lane_index]
                        player_pos[0] = target_x
                        hit = False
                        break
 
            if hit:
                if   item_type == 4: coins_collected += 1
                elif item_type == 5: shield_timer = 360
                elif item_type == 6:
                    nitro_timer  = 260
                    target_speed = nitro_speed
                elif item_type == 7: magnet_timer = 420
                elif item_type == 8: fuel = 1000.0
                elif item_type == 9:
                    if player_life < 5:
                        player_life += 1
                else:
                    if shield_timer > 0:
                        shield_timer = max(0, shield_timer - 120)
                    else:
                        player_life  -= 1
                        current_speed = max(
                            min_speed if fuel > 0 else 0,
                            current_speed * 0.45
                        )
                        if target_speed > current_speed:
                            target_speed = current_speed
                if item_type == 8:
                    continue
                enemy = [random.choice(lane_positions),
                         _safe_spawn_z(new_enemies), 1.0, True, _random_type()]
 
        new_enemies.append(enemy)
    enemies[:] = new_enemies
 
    if player_life <= 0:
        player_life   = 0
        current_speed = 0
        target_speed  = 0
        game_over     = True
        if distance_travelled > best_distance:
            best_distance = distance_travelled
 
 
# ── Camera ────────────────────────────────────────────────────────────────────
def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()              # Reset the projection matrix
    gluPerspective(fovY, 1.25, 0.1, 16000)  # aspect ratio 1.25 matches 1000/800
    glMatrixMode(GL_MODELVIEW)   # Switch to model-view matrix mode
    glLoadIdentity()              # Reset the model-view matrix
 
    # Extract camera position and set orientation
    cx, cy, cz = camera_pos
    if camera_mode == 0:
        gluLookAt(player_pos[0], cy, cz,
                  player_pos[0], 50, -5400,
                  0, 1, 0)
    else:
        gluLookAt(player_pos[0], 85, player_pos[2] + 35,
                  player_pos[0], 65, player_pos[2] - 5400,
                  0, 1, 0)
 
 
# ── Input listeners ───────────────────────────────────────────────────────────
def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement, camera updates, and game controls.
    """
    global target_speed, lane_index, target_x, camera_mode, player_life, current_speed
    global distance_travelled, coins_collected, fuel, next_fuel_distance, shield_timer
    global nitro_timer, horn_timer, horn_pushes, game_over, current_scene, enemies
    global player_angle, cheat_mode, last_update_time, frame_factor, magnet_timer
    global pause_game, difficulty_mode, max_speed, nitro_speed, min_speed
    global acceleration, brake_power, turn_speed, num_enemies, last_speed_level
 
    # Reset game (R key)
    if key == b'r':
        player_pos[:]      = [0, 0, 240]
        player_angle       = 0
        player_life        = 5
        lane_index         = 1
        target_x           = lane_positions[lane_index]
        current_speed      = base_speed
        target_speed       = base_speed
        distance_travelled = 0.0
        coins_collected    = 0
        fuel               = 1000.0
        next_fuel_distance = 300.0
        shield_timer = nitro_timer = magnet_timer = horn_timer = horn_pushes = 0
        pause_game   = cheat_mode = game_over = False
        current_scene      = 0
        last_update_time   = 0
        frame_factor       = 1.0
        last_speed_level   = 1
        enemies.clear()
        for i in range(num_enemies):
            sz = -GRID_LENGTH + 900 + i * 1050 + random.uniform(-140, 140)
            enemies.append([random.choice(lane_positions), sz, 1.0, True, _random_type()])
        return
 
    # Toggle cheat mode (C key)
    if key == b'c':
        cheat_mode = not cheat_mode
        return
 
    # Toggle pause (P key)
    if key == b'p':
        pause_game = not pause_game
        return
 
    # Difficulty (1 / 2 / 3 keys)
    if key in (b'1', b'2', b'3'):
        if key == b'1':
            difficulty_mode = 1
            max_speed = 18.0;  nitro_speed = 27.0;  min_speed = 3.0
            acceleration = base_speed * 0.18;  brake_power = base_speed * 0.15
            turn_speed = 29.0;  num_enemies = 6
        elif key == b'2':
            difficulty_mode = 2
            max_speed = 24.0;  nitro_speed = 34.0;  min_speed = 4.0
            acceleration = base_speed * 0.25;  brake_power = base_speed * 0.18
            turn_speed = 31.0;  num_enemies = 8
        else:
            difficulty_mode = 3
            max_speed = 30.0;  nitro_speed = 42.0;  min_speed = 5.0
            acceleration = base_speed * 0.32;  brake_power = base_speed * 0.20
            turn_speed = 34.0;  num_enemies = 10
        while len(enemies) < num_enemies:
            enemies.append([random.choice(lane_positions),
                            -GRID_LENGTH + 900 + len(enemies)*850 + random.uniform(-120, 120),
                            1.0, True, _random_type()])
        while len(enemies) > num_enemies:
            enemies.pop()
        return
 
    if game_over:
        return
 
    # Accelerate (W key)
    if key == b'w' and fuel > 0:
        target_speed = nitro_speed if nitro_timer > 0 else max_speed
 
    # Brake (S key)
    if key == b's':
        target_speed = min_speed
        if current_speed > min_speed:
            current_speed = max(min_speed, current_speed - brake_power * 2.0)
 
    # Move left (A key)
    if key == b'a':
        lane_index = max(0, lane_index - 1)
        target_x   = lane_positions[lane_index]
 
    # Move right (D key)
    if key == b'd':
        lane_index = min(len(lane_positions) - 1, lane_index + 1)
        target_x   = lane_positions[lane_index]
 
    # Toggle camera (V key)
    if key == b'v':
        camera_mode = 1 - camera_mode
 
    # Horn (Space / H key)
    if key in (b' ', b'h') and horn_timer <= 0:
        _trigger_horn()
 
 
def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for movement and speed control.
    """
    global target_speed, lane_index, target_x, current_speed
    if game_over or pause_game:
        return
 
    # Accelerate (UP arrow key)
    if key == GLUT_KEY_UP and fuel > 0:
        target_speed = nitro_speed if nitro_timer > 0 else max_speed
 
    # Brake (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        target_speed = min_speed
        if current_speed > min_speed:
            current_speed = max(min_speed, current_speed - brake_power * 2.0)
 
    # Move left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        lane_index = max(0, lane_index - 1)
        target_x   = lane_positions[lane_index]
 
    # Move right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        lane_index = min(len(lane_positions) - 1, lane_index + 1)
        target_x   = lane_positions[lane_index]
 
 
def mouseListener(button, state, x, y):
    """
    Handles mouse inputs: left click triggers horn, right click toggles camera.
    """
    global camera_mode
    # Toggle camera (right mouse button)
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = 1 - camera_mode
 
    # Horn (left mouse button)
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_over and not pause_game and horn_timer <= 0:
            _trigger_horn()
 
 
def _trigger_horn():
    """Push nearby traffic to a clear adjacent lane; starts horn cooldown."""
    global horn_timer, horn_pushes
    horn_timer = 180
    for enemy in enemies:
        if enemy[4] in (0, 1, 3):
            ahead = player_pos[2] - enemy[1]
            if 0 < ahead < 1250 and abs(enemy[0] - player_pos[0]) < 95:
                current_lane = min(range(len(lane_positions)),
                                   key=lambda i: abs(enemy[0] - lane_positions[i]))
                possible_lanes = []
                if current_lane > 0:
                    possible_lanes.append(current_lane - 1)
                if current_lane < len(lane_positions) - 1:
                    possible_lanes.append(current_lane + 1)
                best_lane      = current_lane
                best_clearance = -1
                for pl in possible_lanes:
                    clearance = 9999
                    blocked   = False
                    for other in enemies:
                        if other is not enemy and other[4] in (0, 1, 2, 3):
                            if abs(other[0] - lane_positions[pl]) < 85:
                                z_gap = abs(other[1] - enemy[1])
                                if z_gap < 360:
                                    blocked = True
                                clearance = min(clearance, z_gap)
                    if not blocked and clearance > best_clearance:
                        best_clearance = clearance
                        best_lane      = pl
                if best_lane != current_lane:
                    enemy[0] = lane_positions[best_lane]
                    horn_pushes += 1
 
 
# ── Display ───────────────────────────────────────────────────────────────────
def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything on the screen.
    """
    if current_scene == 0:
        glClearColor(0.12, 0.17, 0.28, 1)
    elif current_scene == 1:
        glClearColor(0.94, 0.69, 0.38, 1)
    else:
        glClearColor(0.45, 0.70, 0.95, 1)
 
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()             # Reset modelview matrix
    glViewport(0, 0, 1000, 800) # Set viewport size
 
    setupCamera()                # Configure camera perspective
 
    draw_environment()
    for e in enemies:
        draw_road_object(e)
    draw_green_car()
    draw_active_effects()
 
    # Display game info text at fixed screen positions
    score = int(distance_travelled * coins_collected * 2)
    draw_text(10, 770, "Clash Lane")
    draw_text(10, 740, f"Lives: {player_life}")
    draw_text(10, 710, f"Speed: {current_speed:.1f}/{nitro_speed if nitro_timer > 0 else max_speed:.1f}")
    draw_text(10, 680, f"Fuel: {int(fuel)} m")
    draw_text(10, 650, f"Distance: {int(distance_travelled)} m")
    draw_text(10, 620, f"Coins: {coins_collected}")
    draw_text(10, 590, f"Score = Distance x Coins x 2: {score}")
    draw_text(10, 560, f"Scene: {scene_names[current_scene]}")
    draw_text(10, 530, f"Speed Level: {int(distance_travelled // 500) + 1}")
    draw_text(10, 500, f"Difficulty: {difficulty_names[difficulty_mode]}")
    if shield_timer > 0:
        draw_text(760, 770, f"Shield: {int(shield_timer)//60 + 1}")
    if nitro_timer > 0:
        draw_text(760, 740, f"Nitro: {int(nitro_timer)//60 + 1}")
    if magnet_timer > 0:
        draw_text(760, 710, f"Magnet: {int(magnet_timer)//60 + 1}")
    if fuel < 350 and not game_over:
        draw_text(405, 710, "LOW FUEL!")
    if pause_game and not game_over:
        draw_text(440, 430, "PAUSED")
        draw_text(350, 400, "Press P to continue")
    if cheat_mode:
        draw_text(760, 680, "Cheat: ON")
    if horn_timer > 0:
        draw_text(760, 650, f"Horn Cooldown: {int(horn_timer // 60) + 1}s")
    else:
        draw_text(760, 650, "Horn Ready")
    draw_text(10, 30,
              "W/Up: Accelerate | S/Down: Brake | A/D/Arrows: Turn | "
              "C: Cheat | P: Pause | 1/2/3: Difficulty | "
              "Space/H/Click: Horn (3s cooldown) | R: Restart")
    if fuel <= 0 and not game_over:
        draw_text(390, 430, "OUT OF FUEL")
    if game_over:
        final_score = int(distance_travelled * coins_collected * 2)
        draw_text(410, 460, "GAME OVER")
        draw_text(360, 430, f"Distance Travelled: {int(distance_travelled)} m")
        draw_text(385, 400, f"Coins Collected: {coins_collected}")
        draw_text(410, 370, f"Final Score: {final_score}")
        draw_text(390, 340, f"Best Distance: {int(best_distance)} m")
        draw_text(355, 310, "Press R to restart Clash Lane")
 
    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()
 
 
# ── Idle ──────────────────────────────────────────────────────────────────────
def idle():
    """
    Idle function that runs continuously:
    - Updates game state.
    - Triggers screen redraw for real-time updates.
    """
    update_player_movement()
    update_road_objects()
    handle_collisions_and_pickups()
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()
 
 
# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB colour, depth test
    glutInitWindowSize(1000, 800)    # Window size
    glutInitWindowPosition(0, 0)     # Window position
    glutCreateWindow(b"Clash Lane")  # Create the window
 
    glEnable(GL_DEPTH_TEST)          # Allowed depth exception per instructions
 
    # Spawn initial enemies
    for i in range(num_enemies):
        sz = -GRID_LENGTH + 900 + i * 1050 + random.uniform(-140, 140)
        enemies.append([random.choice(lane_positions), sz, 1.0, True, _random_type()])
 
    glutDisplayFunc(showScreen)          # Register display function
    glutKeyboardFunc(keyboardListener)   # Register keyboard listener
    glutSpecialFunc(specialKeyListener)  # Register special-key listener
    glutMouseFunc(mouseListener)         # Register mouse listener
    glutIdleFunc(idle)                   # Register idle function
 
    glutMainLoop()                       # Enter the GLUT main loop
 
 
if __name__ == "__main__":
    main()