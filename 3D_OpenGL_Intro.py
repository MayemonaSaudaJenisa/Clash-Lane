from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random

# -----------------------------
# Camera and Game Variables
# -----------------------------
camera_pos = [0, 500, 500]  # Camera position
camera_mode = 0  # 0 = default third-person, 1 = first-person
fovY = 60
GRID_LENGTH = 600
player_pos = [0, 0, 0]
player_angle = 0
player_life = 5

cheat_mode = False
auto_follow = False

bullets = []  # [x, z, angle]
missed_bullets = 0
max_misses = 10

enemies = []  # [x, z, scale, scale_dir]
num_enemies = 5

# -----------------------------
# Draw Utilities
# -----------------------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
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

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], 0, player_pos[2])
    glRotatef(player_angle, 0, 1, 0)
    glColor3f(0,0,1)
    glutSolidCube(60)
    # Gun (cylinder)
    glPushMatrix()
    glTranslatef(30, 30, 0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(1,0,0)
    gluCylinder(gluNewQuadric(), 5, 5, 50, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_enemy(enemy):
    x, z, scale, _ = enemy
    glPushMatrix()
    glTranslatef(x, 30, z)
    glScalef(scale, scale, scale)
    glColor3f(1,0,0)
    glutSolidSphere(30, 10, 10)
    glPopMatrix()

def draw_bullets():
    glColor3f(1,1,0)
    for b in bullets:
        x, z, _ = b
        glPushMatrix()
        glTranslatef(x, 30, z)
        glutSolidCube(10)
        glPopMatrix()

def draw_grid():
    glColor3f(1,1,1)
    step = 50
    for i in range(-GRID_LENGTH, GRID_LENGTH+1, step):
        glBegin(GL_LINES)
        glVertex3f(i,0,-GRID_LENGTH)
        glVertex3f(i,0,GRID_LENGTH)
        glVertex3f(-GRID_LENGTH,0,i)
        glVertex3f(GRID_LENGTH,0,i)
        glEnd()

# -----------------------------
# Update Functions
# -----------------------------
def update_bullets():
    global bullets, missed_bullets
    new_bullets = []
    for b in bullets:
        x, z, angle = b
        x += math.sin(math.radians(angle))*10
        z += math.cos(math.radians(angle))*10
        if abs(x) > GRID_LENGTH or abs(z) > GRID_LENGTH:
            missed_bullets += 1
        else:
            new_bullets.append([x, z, angle])
    bullets[:] = new_bullets

def update_enemies():
    for enemy in enemies:
        ex, ez, scale, dir = enemy
        dx = player_pos[0]-ex
        dz = player_pos[2]-ez
        dist = math.sqrt(dx*dx + dz*dz)
        if dist != 0:
            enemy[0] += dx/dist * 1
            enemy[1] += dz/dist * 1
        # Animate scale
        if dir:
            enemy[2] += 0.01
            if enemy[2] >= 1.2: enemy[3] = False
        else:
            enemy[2] -= 0.01
            if enemy[2] <= 0.8: enemy[3] = True

def check_collisions():
    global bullets, enemies, player_life
    new_enemies = []
    for enemy in enemies:
        hit = False
        ex, ez, _, _ = enemy
        for b in bullets:
            bx, bz, _ = b
            if abs(bx-ex)<20 and abs(bz-ez)<20:
                hit = True
        if hit:
            enemy = [random.uniform(-GRID_LENGTH, GRID_LENGTH), random.uniform(-GRID_LENGTH, GRID_LENGTH),1.0, True]
        if abs(player_pos[0]-enemy[0])<35 and abs(player_pos[2]-enemy[1])<35:
            player_life -= 1
        new_enemies.append(enemy)
    enemies[:] = new_enemies

# -----------------------------
# Camera
# -----------------------------
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1000/800, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_mode==0:
        x, y, z = camera_pos
        gluLookAt(x, y, z, 0,0,0,0,0,1)
    else:
        cam_x = player_pos[0] - math.sin(math.radians(player_angle))*200
        cam_z = player_pos[2] - math.cos(math.radians(player_angle))*200
        gluLookAt(player_pos[0],60,player_pos[2],
                  player_pos[0]+math.sin(math.radians(player_angle))*50,60,player_pos[2]+math.cos(math.radians(player_angle))*50,
                  0,1,0)

# -----------------------------
# Keyboard / Mouse
# -----------------------------
def keyboardListener(key, x, y):
    global player_pos, player_angle, cheat_mode, auto_follow, bullets, player_life
    step = 10
    if key==b'w': player_pos[0]+=math.sin(math.radians(player_angle))*step; player_pos[2]+=math.cos(math.radians(player_angle))*step
    if key==b's': player_pos[0]-=math.sin(math.radians(player_angle))*step; player_pos[2]-=math.cos(math.radians(player_angle))*step
    if key==b'a': player_angle-=5
    if key==b'd': player_angle+=5
    if key==b'c': cheat_mode = not cheat_mode
    if key==b'v': auto_follow = not auto_follow
    if key==b'r':
        player_pos[:] = [0,0,0]
        player_angle=0
        bullets.clear()
        player_life=5

def specialKeyListener(key, x, y):
    global camera_pos
    if key==GLUT_KEY_UP: camera_pos[1]+=10
    if key==GLUT_KEY_DOWN: camera_pos[1]-=10
    if key==GLUT_KEY_LEFT: camera_pos[0]-=10
    if key==GLUT_KEY_RIGHT: camera_pos[0]+=10

def mouseListener(button, state, x, y):
    global bullets, camera_mode
    if button==GLUT_LEFT_BUTTON and state==GLUT_DOWN:
        bullets.append([player_pos[0], player_pos[2], player_angle])
    if button==GLUT_RIGHT_BUTTON and state==GLUT_DOWN:
        camera_mode = 1 - camera_mode

# -----------------------------
# Display / Idle
# -----------------------------
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0,0,1000,800)
    setupCamera()
    draw_grid()
    draw_player()
    for e in enemies: draw_enemy(e)
    draw_bullets()
    draw_text(10,770,f"Player Life: {player_life}")
    draw_text(10,740,f"Missed Bullets: {missed_bullets}")
    glutSwapBuffers()

def idle():
    update_bullets()
    update_enemies()
    check_collisions()
    if cheat_mode:
        player_angle+=10
        bullets.append([player_pos[0], player_pos[2], player_angle])
    glutPostRedisplay()

# -----------------------------
# Main
# -----------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000,800)
    glutCreateWindow(b"Bullet Frenzy 3D Game")
    glEnable(GL_DEPTH_TEST)
    for _ in range(num_enemies):
        enemies.append([random.uniform(-GRID_LENGTH, GRID_LENGTH), random.uniform(-GRID_LENGTH, GRID_LENGTH),1.0, True])
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__=="__main__":
    main()
