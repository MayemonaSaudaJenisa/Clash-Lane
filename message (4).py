        # Background (upor er ta)
        for bx in range(-2200, 2300, 180):
            h= 300 + abs(math.sin(bx*0.017))*470
            w= 95  + abs(math.cos(bx*0.011))*70
            d= 75  + abs(math.sin(bx*0.021))*35
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
                    if (wx + wy + bx)% 5!= 0:
                        glBegin(GL_QUADS)
                        glVertex3f(bx+wx-6, wy-11, sky_z+118)
                        glVertex3f(bx+wx+6, wy-11, sky_z+118)
                        glVertex3f(bx+wx+6, wy+11, sky_z+118)
                        glVertex3f(bx+wx-6, wy+11, sky_z+118)
                        glEnd()
 
        for i in range(far_z + 480, near_z + 720, 500):
            z= i + scene_offset
            h1= 300 + abs(math.sin(i*0.025))*340
            h2= 280 + abs(math.cos(i*0.018))*330
            colors= [[0.22,0.24,0.31],[0.18,0.21,0.28],
                     [0.29,0.26,0.24],[0.20,0.25,0.27]]
            for side_x, bh, bz, color_id in [(-660, h1, z, (i//500)% 4), ( 660, h2, z+180, (i//500+1)% 4)]:
                glPushMatrix()
                glTranslatef(side_x, bh/2 + 12, bz)
                glColor3f(*colors[color_id])
                glScalef(2.15, bh/60, 1.35)
                glutSolidCube(60)
                glPopMatrix()


                if side_x > 0:
                    face_x= side_x - 66
                else:
                    face_x= side_x + 66


                glColor3f(0.96, 0.82, 0.28)
                for wz in [-28, 0, 28]:
                    for wy in range(70, int(bh) - 45, 62):
                        if (wy + int(bz) + int(side_x) + wz)% 4!= 0:
                            glBegin(GL_QUADS)
                            glVertex3f(face_x, wy-12, bz+wz-9)
                            glVertex3f(face_x, wy+12, bz+wz-9)
                            glVertex3f(face_x, wy+12, bz+wz+9)
                            glVertex3f(face_x, wy-12, bz+wz+9)
                            glEnd()
            # Street lamps.
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
                glutSolidCube(30)
                glPopMatrix()
 
    elif current_scene == 1: # Desert
        # Sand dunes 
        for dx in range(-2200, 2300, 360):
            glColor3f(0.58, 0.40, 0.20)
            glBegin(GL_TRIANGLES)
            glVertex3f(dx-270, 0, sky_z+50)
            glVertex3f(dx+20, 220+abs(math.sin(dx))*90, sky_z+50)
            glVertex3f(dx+300, 0, sky_z+50)
            glEnd()
            glColor3f(0.88, 0.68, 0.35)
            glBegin(GL_TRIANGLES)
            glVertex3f(dx-80, 0, sky_z+70)
            glVertex3f(dx+70, 165+abs(math.cos(dx))*70, sky_z+70)
            glVertex3f(dx+250, 0, sky_z+70)
            glEnd()
        # Cactus 
        for i in range(far_z + 450, near_z + 500, 330):
            z= i + scene_offset
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
            # Cube rocks
            glPushMatrix()
            glTranslatef(-720, 26, z+80)
            glColor3f(0.42, 0.33, 0.22)
            glScalef(1.5, 0.55, 1.0)
            glutSolidCube(55)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(720, 18, z-55)
            glColor3f(0.51, 0.42, 0.29)
            glScalef(1.25, 0.45, 0.9)
            glutSolidCube(44)
            glPopMatrix()
 
    else: # Greenland
        # Mountains
        for mx in range(-2100, 2200, 420):
            glColor3f(0.25, 0.42, 0.35)
            glBegin(GL_TRIANGLES)
            glVertex3f(mx-320, 0, sky_z+50)
            glVertex3f(mx, 420+abs(math.sin(mx))*130, sky_z+50)
            glVertex3f(mx+330, 0, sky_z+50)
            glEnd()
            glColor3f(0.90, 0.93, 0.95)
            glBegin(GL_TRIANGLES)
            glVertex3f(mx-75, 310, sky_z+75)
            glVertex3f(mx, 420+abs(math.sin(mx))*130, sky_z+75)
            glVertex3f(mx+82, 310, sky_z+75)
            glEnd()
        # Trees
        for i in range(far_z + 400, near_z + 550, 270):
            z= i + scene_offset
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
                glutSolidCube(62)
                glPopMatrix()
                glPushMatrix()
                glTranslatef(x - 36, 85, z + 14)
                glColor3f(0.0, 0.32, 0.04)
                glutSolidCube(48)
                glPopMatrix()
            # Cube rocks
            glPushMatrix()
            glTranslatef(720, 22, z+50)
            glColor3f(0.70, 0.70, 0.75)
            glutSolidCube(42)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(-720, 16, z-50)
            glColor3f(0.65, 0.68, 0.70)
            glScalef(1.25, 0.55, 0.8)
            glutSolidCube(36)
            glPopMatrix()
 
 
# Game logic ---------
def update_player_movement():
    global current_speed, target_speed, distance_travelled, fuel, shield_timer, nitro_timer
    global horn_timer, player_angle, game_over, current_scene, player_life, target_x
    global lane_index, cheat_mode, frame_factor, magnet_timer
    global pause_game, best_distance, last_speed_level
 
    frame_factor= 1.0
 
    if pause_game and not game_over:
        return
    

    if game_over:
        if distance_travelled > best_distance:
            best_distance = distance_travelled
        return
 

    for attr in ['shield_timer', 'nitro_timer', 'magnet_timer', 'horn_timer']:
        val= globals()[attr]
        if val > 0:
            globals()[attr] = max(0, val - frame_factor)
 

    if fuel <= 0:
        fuel= 0
        target_speed= 0

    speed_level= int(distance_travelled // 500) + 1


    if speed_level > last_speed_level:
        last_speed_level = speed_level

    level_bonus= min((speed_level - 1)*0.55, 6.0)

    if nitro_timer > 0:
        active_max= nitro_speed + level_bonus
    else:
        active_max= max_speed + level_bonus


    if target_speed > active_max:
        target_speed= active_max

    if current_speed < target_speed:
        current_speed= min(current_speed + acceleration*frame_factor, target_speed)
    elif current_speed > target_speed:
        current_speed= max(current_speed - brake_power*frame_factor, target_speed)

    current_speed= min(current_speed, active_max)

    if fuel > 0 and current_speed < min_speed:
        current_speed= min_speed

    if fuel <= 0 and current_speed < 0:
        current_speed= 0
 
    # Cheatmode----------------
    if cheat_mode:
        safe_lane_ids= []
        best_lane= lane_index
        best_space= -1
        for i in range(len(lane_positions)):
            lane_blocked = False
            closest_block= 99999
            for enemy in enemies:
                if enemy[4] in (0, 1, 2, 3):
                    ahead= player_pos[2] - enemy[1]
                    if 0 < ahead < 1700 and abs(enemy[0] - lane_positions[i]) < 82:
                        lane_blocked = True
                        closest_block= min(closest_block, ahead)
            if not lane_blocked:
                safe_lane_ids.append(i)
                closest_block= 99999
            if closest_block > best_space:
                best_space= closest_block
                best_lane= i
 
        pickup_lane_choice= -1
        best_pickup_distance= 99999
        for enemy in enemies:
            if enemy[4] in (4, 5, 6, 8):
                ahead= player_pos[2] - enemy[1]
                
                if 0 < ahead < 1900:

                    # Find which lane the things is in
                    pickup_lane = 0
                    smallest_distance = abs(enemy[0] - lane_positions[0])

                    for i in range(len(lane_positions)):
                        lane_distance = abs(enemy[0] - lane_positions[i])

                        if lane_distance < smallest_distance:
                            smallest_distance = lane_distance
                            pickup_lane = i

                    # Check if that thing's lane is safe or not
                    pickup_safe = True

                    for d in enemies:
                        if d[4] in (0, 1, 2, 3):
                            danger_ahead = player_pos[2] - d[1]

                            if 0 < danger_ahead < ahead + 430:
                                if abs(d[0] - lane_positions[pickup_lane]) < 85:
                                    pickup_safe = False
                                    break

                    # Choose this thing if it is safe and closest
                    if pickup_safe:
                        if ahead < best_pickup_distance:
                            best_pickup_distance = ahead
                            pickup_lane_choice = pickup_lane



        if pickup_lane_choice != -1:
            lane_index= pickup_lane_choice

        elif lane_index not in safe_lane_ids:
            if safe_lane_ids:
                lane_index= min(safe_lane_ids, key=lambda i: abs(player_pos[0] - lane_positions[i]))
            else:
                lane_index= best_lane

        target_x = lane_positions[lane_index]


        emergency= False

        for d in enemies:
            if d[4] in (0, 1, 2, 3):
                danger_ahead= player_pos[2] - d[1]

                if 0 < danger_ahead < 250:
                    if abs(d[0] - player_pos[0]) < 88:
                        emergency= True
                        break


        if emergency and safe_lane_ids:
            player_pos[0]= target_x
 
    lane_step= turn_speed*frame_factor*(1.75 if cheat_mode else 1.0)
    if player_pos[0] < target_x:
        player_pos[0]= min(player_pos[0] + lane_step, target_x)
    elif player_pos[0] > target_x:
        player_pos[0]= max(player_pos[0] - lane_step, target_x)
 
    player_angle= max(-14, min(14, (target_x - player_pos[0])*-0.18))
 
    move_meters= current_speed * 0.085 * frame_factor
    distance_travelled += move_meters
    if current_speed > 0:
        fuel -= move_meters
 
    current_scene= int(distance_travelled // 500)% 3
 
    if fuel <= 0 and current_speed <= 0.05:
        current_speed = 0
        game_over= True
        if distance_travelled > best_distance:
            best_distance = distance_travelled
    if player_life <= 0:
        player_life= 0
        current_speed= 0
        target_speed= 0
        game_over= True
        if distance_travelled > best_distance:
            best_distance= distance_travelled