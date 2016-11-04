#! /usr/bin/env python
"""
ninja_mvp.py

The main game logic of Ninja MVP, which It's a action-based multi-player shooting game
using Leap Motion to track a player's hand movements and gestures for control and
adopts a scoring rules using principles of Game Theory.

author:
Guang XIONG, gx239<at>nyu.edu
Ruyu GUAN, rg2482@nyu.edu

date: 10/14/2014
version: 1.0
Support Python version 2.7 and Pygame version 1.9.1
"""

# 1 - Import Libraries
import os
import sys
import thread
import time
import random
import Tkinter
import pygame
from pygame.locals import *
# import Leap
# from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

# 2 - Initialize the game
#2.1 the background stage
root = Tkinter.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

pygame.init()

flags = DOUBLEBUF
screen = pygame.display.set_mode((screen_width, screen_height), flags)
width, height = screen.get_size()  # get the size of the fullscreen display
print width, height


backgroundimg = pygame.image.load('../resources/images/background.png').convert()
backgroundimg = pygame.transform.scale(backgroundimg,(screen_width, screen_height))

# backgroundimg.set_alpha(0)
# backgroundimgRect = backgroundimg.get_rect()

#movement adjusting parameters
move_increment = int(screen_height * 0.01)
bullet_velosity = int(move_increment * 1.7)
target_velosity = int(move_increment * 0.9)
target_velosity_mixed = int(move_increment * 0.3)
loop_mixed_get_shot = 170   #190 # the bigger the easier
reset_val_for_another_turn = 180
reset_val_for_another_turn_later = 90
bullet_limit = 2

p1_x_max = int(screen_width * 0.4)
p1_x_min = -70
p1_y_max = int(screen_height * 0.8)
p1_y_min = -30

p3_x_min = int(screen_width * 0.6)
p3_x_max = int(screen_width * 0.9)
p3_y_max = p1_y_max
p3_y_min = -30

t_x_min = int(screen_width * 0.5)

p1_x_0 = int(0.5 * (p1_x_min + p1_x_max))
p1_y_0 = int(0.5 * (p1_y_min + p1_y_max))
p3_x_0 = int(0.5 * (p3_x_min + p3_x_max))
p3_y_0 = int(0.5 * (p3_y_min + p3_y_max))

##difine Speed of players
pure_target_timer_p1=[50]
pure_target_timer_p11=[100]

all_pure_targets_p1=[[t_x_min, random.randint(int(screen_width * 1.4), int(screen_width * 1.8))]]
all_pure_targets_p11=[[t_x_min, random.randint(int(screen_width * -0.5), int(screen_width * -0.3))]]

mixed_target_timer_p1p3 = [200]
mixed_target_timer_p11p33 = [200]
all_mixed_targets_p1p3=[[t_x_min, random.randint(int(screen_width * 1.4), int(screen_width * 1.8))]]
all_mixed_targets_p11p33=[[t_x_min, random.randint(int(screen_width * -0.5), int(screen_width * -0.3))]]

#2.2 keyboard setting
keys_player1 = [False, False, False, False]
player1_pos = [p1_x_0, p1_y_0]

keys_player3 = [False, False, False, False]
player3_pos = [p3_x_0, p3_y_0]

# 3 - Load images
#player1's stuff
player1 = pygame.image.load("../resources/images/player1nn.png").convert_alpha()
player1 = pygame.transform.scale(player1, (int(0.1*screen_width), int(0.1*screen_width)))
player1_rect = pygame.Rect(player1.get_rect())
acc_player1 = [0, 0]
acc_player1[1] = 1
all_bullets_player1 = []
bullet_player1 = pygame.image.load("../resources/images/bullet_p1n.png").convert_alpha()
bullet_player1_rect = pygame.Rect(bullet_player1.get_rect())

#player3's stuff
player3 = pygame.image.load("../resources/images/player3nn.png").convert_alpha()
player3 = pygame.transform.scale(player3, (int(0.1*screen_width), int(0.1*screen_width)))
player3_rect = pygame.Rect(player3.get_rect())
acc_player3 = [0, 0]
acc_player3[1] = 1
all_bullets_player3 = []
bullet_player3 = pygame.image.load("../resources/images/bullet_p2n.png").convert_alpha()
bullet_player3_rect = pygame.Rect(bullet_player3.get_rect())

pure_target_p1 = pygame.image.load("../resources/images/pure_common_target.png").convert_alpha()
pure_target_p1_rect=pygame.Rect(pure_target_p1.get_rect())

#mixed target
mixed_target_p1p3 = pygame.image.load("../resources/images/mixed_p1p3.png").convert_alpha()
mixed_target_p1p3 = pygame.transform.scale(mixed_target_p1p3,(int(screen_width * 0.14), int(screen_width * 0.14)))
mixed_target_p1p3_rect = pygame.Rect(mixed_target_p1p3.get_rect())

#targets utility functions
# 3.2 - Load audio
hit = pygame.mixer.Sound("../resources/audio/explode.wav")
enemy = pygame.mixer.Sound("../resources/audio/enemy.wav")
shoot2 = pygame.mixer.Sound("../resources/audio/huodun.wav")
shoot1 = pygame.mixer.Sound("../resources/audio/luoxuanwan.wav")
click = pygame.mixer.Sound("../resources/audio/huoqiu.mp3")
hit.set_volume(0.05)
enemy.set_volume(0.05)
shoot1.set_volume(0.1)
shoot2.set_volume(0.1)
click.set_volume(0.25)
pygame.mixer.music.load('../resources/audio/background.wav')
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.20)

sentinel_p1 = [0]
sentinel_p3 = [0]
set_sentinels_zero = 0

font = pygame.font.Font(None, 45)
font2 = pygame.font.Font(None, 30)
font3 = pygame.font.Font(None, 85)


# class SampleListener(Leap.Listener):

#     finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
#     bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
#     state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

#     def on_init(self, controller):
#         print "Initialized"

#     def on_connect(self, controller):
#         print "Connectedeeee"
#         # Enable gestures
#         controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
#         # controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
#         # controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
#         # controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
#         # print(Leap.Gesture.TYPE_CIRCLE)

#     def on_disconnect(self, controller):
#         # Note: not dispatched when running in a debugger.
#         print "Disconnected"

#     def on_exit(self, controller):
#         print "Exited"

#     def on_frame(self, controller):
# #################experiment#######################
#         print "on framelll"
#         frame = controller.frame()
#         # previous = controller.frame(1)
#         handList = frame.hands
#         hand1 = handList.leftmost
#         hand2 = handList.rightmost

#         hand1_speed = hand1.palm_velocity
#         hand2_speed = hand2.palm_velocity

#         hand1_position = hand1.palm_position
#         hand2_position = hand2.palm_position
#         print "hand1_postion:    " +str(hand1_position)
#         print "hand2_postion:    "+ str(hand2_position)
#################experiment#######################

    ####relative_position

        ##speed########## the bigger the slower
#         DEFINEDSPPED = 50
#         player1_pos[0] = int(player1_pos[0] + hand1_speed[0]*1.5 / DEFINEDSPPED)
#         player1_pos[1] = int(player1_pos[1] - hand1_speed[1]*1.5 / DEFINEDSPPED)

#         # player1_pos[0] = hand1_position[0]*1.5 + screen_height * 0.5
#         # player1_pos[1] = -hand1_position[1]*1.5 + screen_width * 0.3

#         if hand2 != hand1:
#             player3_pos[0] = int(player3_pos[0] + hand2_speed[0]*1.5 / DEFINEDSPPED)
#             player3_pos[1] = int(player3_pos[1] - hand2_speed[1]*1.5 / DEFINEDSPPED)

#         # Get gestures
#         for gesture in frame.gestures():
#             if gesture.type == Leap.Gesture.TYPE_CIRCLE:
#                 ###for hand1  https://developer.leapmotion.com/documentation/skeletal/python/api/Leap.Gesture.html#Leap.Gesture.hands
#                 if gesture.hands.leftmost == hand1:
#                     all_bullets_player1.append([player1_pos[0]+130, player1_pos[1]+25])
#                     shoot1.play()
#                 ###for hand2
#                 else:
#                     all_bullets_player3.append([player3_pos[0], player3_pos[1]+25])
#                     shoot2.play()

#     def state_string(self, state):
#         if state == Leap.Gesture.STATE_START:
#             return "STATE_START"

#         if state == Leap.Gesture.STATE_UPDATE:
#             return "STATE_UPDATE"

#         if state == Leap.Gesture.STATE_STOP:
#             return "STATE_STOP"

#         if state == Leap.Gesture.STATE_INVALID:
#             return "STATE_INVALID"

# ######################################################line####################################
# # utility functions
#     #targets generator


# ######################################################line####################################
# controller = Leap.Controller()
# listener = SampleListener()
# controller.add_listener(listener)

def bullet_check_range(all_bullets_playerx, bullet_playerx, right_plus_direction):
    bullet_playerx_counter = 0
    for bullet in all_bullets_playerx:
        bullet[0] += bullet_velosity * right_plus_direction
        if (bullet[0] < -10 or bullet[0] > screen_width + 10) or bullet_playerx_counter > bullet_limit:
            all_bullets_playerx.pop(bullet_playerx_counter)
        else:
            bullet_playerx_counter += 1
            screen.blit(bullet_playerx, bullet)

def target_generator(timer, all_target_list, start_y_pos, reset_val):
    timer[0] -= 1
    if timer[0]== 0:
        all_target_list.append([random.randint(t_x_min-int(screen_width*0.1), t_x_min+int(screen_width*0.1)), start_y_pos])
        timer[0] = reset_val

def player_getshot(playerx, playerx_pos, playerx_rect, acc_playerx,
                   all_bullets_playery, bullet_playery_rect, acc_playery):

    player_rect = pygame.Rect(playerx_rect)
    player_rect.top = playerx_pos[1]
    player_rect.left = playerx_pos[0]

    bullet_playerx_counter = 0
    for bullet in all_bullets_playery:
        bullet_rect = pygame.Rect(bullet_playery_rect)
        bullet_rect.left = bullet[0]
        bullet_rect.top = bullet[1]

        if player_rect.colliderect(bullet_rect):
            click.play()
            acc_playery[0] += 0
            acc_playerx[0] -= 10
            all_bullets_playery.pop(bullet_playerx_counter)
            # all_pure_targets_px.pop(pure_target_px_counter)
        bullet_playerx_counter += 1

    screen.blit(playerx, playerx_pos)


    #targets shooting score

def pure_target_shooting_score(orientation, all_pure_targets_px, pure_target_px_rect, \
        pure_target_px, all_bullets_playerx, bullet_playerx_rect, acc_playerx, \
        all_bullets_playera, bullet_playera_rect, acc_playera):

    pure_target_px_counter = 0
    for target in all_pure_targets_px:
        if target[1] < int(screen_height * -0.3) or target[1] > int(screen_height * 1.3):
            all_pure_targets_px.pop(pure_target_px_counter)
        target[1] -= target_velosity * orientation   #up +1 or down -1
        target_rect = pygame.Rect(pure_target_px_rect)
        target_rect.top = target[1]
        target_rect.left = target[0]

        bullet_playerx_counter = 0
        for bullet in all_bullets_playerx:
            bullet_rect = pygame.Rect(bullet_playerx_rect)
            bullet_rect.left = bullet[0]
            bullet_rect.top = bullet[1]

            if target_rect.colliderect(bullet_rect):
                enemy.play()
                acc_playerx[0] += 10
                all_bullets_playerx.pop(bullet_playerx_counter)
                if all_pure_targets_px:
                    all_pure_targets_px.pop(pure_target_px_counter)
            bullet_playerx_counter += 1

        bullet_playerx_counter = 0
        for bullet in all_bullets_playera:
            bullet_rect = pygame.Rect(bullet_playera_rect)
            bullet_rect.left = bullet[0]
            bullet_rect.top = bullet[1]

            if target_rect.colliderect(bullet_rect):
                click.play()
                acc_playera[0] += 10
                all_bullets_playera.pop(bullet_playerx_counter)
                if all_pure_targets_px:
                    all_pure_targets_px.pop(pure_target_px_counter)
            bullet_playerx_counter += 1

        pure_target_px_counter += 1

    for target in all_pure_targets_px:
        screen.blit(pure_target_px, target)

def mixed_target_shooting_add_score(orientation, all_mixed_targets_pxpy, mixed_target_pxpy_rect, \
        mixed_target_pxpy, all_bullets_playerx, all_bullets_playery, bullet_playerx_rect \
        , bullet_playery_rect, acc_playerx, acc_playery, sentinel_px, sentinel_py):

    mixed_target_pxpy_counter = 0
    for target in all_mixed_targets_pxpy:
        if target[1] < int(screen_height * -0.3) or target[1] > int(screen_height * 1.3):
            all_mixed_targets_pxpy.pop(mixed_target_pxpy_counter)
        target[1] -= target_velosity_mixed * orientation
        target_rect = pygame.Rect(mixed_target_p1p3_rect)
        target_rect.top = target[1]
        target_rect.left = target[0]

        bullet_playerx_counter = 0
        for bullet in all_bullets_playerx:
            bullet_rect = pygame.Rect(bullet_playerx_rect)
            bullet_rect.left = bullet[0]
            bullet_rect.top = bullet[1]

            if target_rect.colliderect(bullet_rect):
                enemy.play()
                sentinel_px[0] = 1
                if all_bullets_playerx:
                    all_bullets_playerx.pop(bullet_playerx_counter)
            bullet_playerx_counter += 1

        bullet_playery_counter = 0
        for bullet in all_bullets_playery:
            bullet_rect = pygame.Rect(bullet_playery_rect)
            bullet_rect.left = bullet[0]
            bullet_rect.top = bullet[1]

            if target_rect.colliderect(bullet_rect):
                enemy.play()
                sentinel_py[0] = 1
                if all_bullets_playery:
                    all_bullets_playery.pop(bullet_playery_counter)
            bullet_playery_counter += 1

        bullet_playerx_counter = 0
        for bullet in all_bullets_playerx:
            bullet_rect = pygame.Rect(bullet_playerx_rect)
            bullet_rect.left = bullet[0]
            bullet_rect.top = bullet[1]

            if target_rect.colliderect(bullet_rect):
                enemy.play()
                sentinel_px[0] = 1
                if all_bullets_playerx:
                    all_bullets_playerx.pop(bullet_playerx_counter)
            bullet_playerx_counter += 1

        bullet_playery_counter = 0
        for bullet in all_bullets_playery:
            bullet_rect = pygame.Rect(bullet_playery_rect)
            bullet_rect.left = bullet[0]
            bullet_rect.top = bullet[1]

            if target_rect.colliderect(bullet_rect):
                enemy.play()
                sentinel_py[0] = 1
                if all_bullets_playery:
                    all_bullets_playery.pop(bullet_playery_counter)
            bullet_playery_counter += 1




        if sentinel_px[0] and sentinel_py[0]:
            acc_playerx[0] += 100
            acc_playery[0] += 100
            hit.play()
            if all_mixed_targets_pxpy:
                all_mixed_targets_pxpy.pop(mixed_target_pxpy_counter)
            sentinel_px[0] = 0
            sentinel_py[0] = 0
        # sentinel_px = 0
        # sentinel_py = 0
        mixed_target_pxpy_counter += 1

    for target in all_mixed_targets_pxpy:
        screen.blit(mixed_target_pxpy, target)


running = 1
exitcode = 0

# listener.on_init(controller)
# listener.on_connect(controller)

counter1 = 0
# 4 - keep looping through
pygame.font.init()

while running:
    counter1 += 1
    print("counter1: " + str(counter1))

    # listener.on_frame(controller)

    screen.blit(backgroundimg, (0, 0))

    # 5 - clear the screen before drawing it again and draw tunnel
    # 5,1 to check if either player is out of range of the screen
    if player1_pos[0] > p1_x_max:
        player1_pos[0] = p1_x_max
    elif player1_pos[0] < p1_x_min:
        player1_pos[0] = p1_x_min
    elif player1_pos[1] > p1_y_max:
        player1_pos[1] = p1_y_max
    elif player1_pos[1] < p1_y_min:
        player1_pos[1] = p1_y_min
    screen.blit(player1, player1_pos)


    if player3_pos[0] < p3_x_min:
        player3_pos[0] = p3_x_min
    elif player3_pos[0] > p3_x_max:
        player3_pos[0] = p3_x_max
    elif player3_pos[1] > p3_y_max:
        player3_pos[1] = p3_y_max
    elif player3_pos[1] < p3_y_min:
        player3_pos[1] = p3_y_min
    screen.blit(player3, player3_pos)

    #the fonts that show score
    # 6.4 - Draw clock
    if pygame.time.get_ticks()>=75000:

        survivedtext = font3.render(str((120000-pygame.time.get_ticks())/60000)+":"\
                       +str((120000-pygame.time.get_ticks())/1000%60).zfill(2), True, (0,255,0))
        reset_val_for_another_turn = reset_val_for_another_turn_later
    else:
        survivedtext = font3.render(str((120000-pygame.time.get_ticks())/60000)+":"\
                       +str((120000-pygame.time.get_ticks())/1000%60).zfill(2), True, (0,0,0))

    screen.blit(survivedtext, (int(screen_width * 0.5), int(screen_height * 0.5)))
    text1 = font.render("Player1 Score: "+str(acc_player1[0]),True, (255,0,0))
    screen.blit(text1, (40, 50))
    text3 = font.render("Player2 Score: "+str(acc_player3[0]),True, (255,0,0))
    screen.blit(text3, (screen_width*0.8, 50))

    #5.1 checking bullets to see whether or not out of range
    bullet_check_range(all_bullets_player1, bullet_player1, 1)
    bullet_check_range(all_bullets_player3, bullet_player3, -1)

    #all targets POSITIONS generators
    target_generator(pure_target_timer_p1,all_pure_targets_p1,
                     random.randint(int(screen_height), int(screen_height * 1.5)),reset_val_for_another_turn*0.4)

    target_generator(pure_target_timer_p11,all_pure_targets_p11,
                     random.randint(int(screen_height*-0.7), -100), reset_val_for_another_turn*0.5)

    pure_target_shooting_score(1,all_pure_targets_p1, pure_target_p1_rect, \
        pure_target_p1, all_bullets_player1, bullet_player1_rect, acc_player1, all_bullets_player3,\
        bullet_player3_rect, acc_player3)

    pure_target_shooting_score(-1,all_pure_targets_p11, pure_target_p1_rect, \
        pure_target_p1, all_bullets_player1, bullet_player1_rect, acc_player1, \
        all_bullets_player3, bullet_player3_rect, acc_player3)

    target_generator(mixed_target_timer_p1p3,all_mixed_targets_p1p3,
                     random.randint(int(screen_height*-0.7), -100), reset_val_for_another_turn*1.5)

    target_generator(mixed_target_timer_p11p33,all_mixed_targets_p11p33,
                     random.randint(int(screen_height), int(screen_height * 1.5)), reset_val_for_another_turn*1.5)



    mixed_target_shooting_add_score(-1, all_mixed_targets_p1p3, mixed_target_p1p3_rect, \
        mixed_target_p1p3, all_bullets_player1, all_bullets_player3, bullet_player1_rect \
        , bullet_player3_rect, acc_player1, acc_player3, sentinel_p1, sentinel_p3)

    mixed_target_shooting_add_score(1, all_mixed_targets_p11p33, mixed_target_p1p3_rect, \
        mixed_target_p1p3, all_bullets_player1, all_bullets_player3, bullet_player1_rect \
        , bullet_player3_rect, acc_player1, acc_player3, sentinel_p1, sentinel_p3)

    # detect player get shot
    player_getshot(player1, player1_pos, player1_rect, acc_player1, \
        all_bullets_player3, bullet_player3_rect, acc_player3)

    player_getshot(player3, player3_pos, player3_rect, acc_player3, \
        all_bullets_player1, bullet_player1_rect, acc_player1)

    set_sentinels_zero += 1
    if set_sentinels_zero > loop_mixed_get_shot: # the more the easier
        sentinel_p1[0] = 0
        sentinel_p3[0] = 0
        set_sentinels_zero = 0

    # 7 - update the screen
    pygame.display.update()

    # 8 - loop through the events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        # check if the event is the X button
        #player1's key detection
        if event.type == pygame.KEYDOWN:
            if event.key==K_w:
                keys_player1[0]=True
            elif event.key==K_a:
                keys_player1[1]=True
            elif event.key==K_s:
                keys_player1[2]=True
            elif event.key==K_d:
                keys_player1[3]=True
            elif event.key==K_z:
                acc_player1[1] += 1
                if len(all_bullets_player1) <= bullet_limit:
                    all_bullets_player1.append([player1_pos[0]+130, player1_pos[1]+25])

        if event.type == pygame.KEYUP:
            if event.key==pygame.K_w:
                keys_player1[0]=False
            elif event.key==pygame.K_a:
                keys_player1[1]=False
            elif event.key==pygame.K_s:
                keys_player1[2]=False
            elif event.key==pygame.K_d:
                keys_player1[3]=False

        #player3's key detection

        if event.type == pygame.KEYDOWN:
            if event.key==K_UP:
                keys_player3[0]=True
            elif event.key==K_LEFT:
                keys_player3[1]=True
            elif event.key==K_DOWN:
                keys_player3[2]=True
            elif event.key==K_RIGHT:
                keys_player3[3]=True
            elif event.key==K_p:
                acc_player3[1] += 1
                all_bullets_player3.append([player3_pos[0], player3_pos[1]+25])
                shoot2.play()

        if event.type == pygame.KEYUP:
            if event.key==pygame.K_UP:
                keys_player3[0]=False
            elif event.key==pygame.K_LEFT:
                keys_player3[1]=False
            elif event.key==pygame.K_DOWN:
                keys_player3[2]=False
            elif event.key==pygame.K_RIGHT:
                keys_player3[3]=False

    # 9 - Move players
    # moving player1
    if keys_player1[0]:
        player1_pos[1] -= move_increment
    if keys_player1[2]:
        player1_pos[1] += move_increment
    if keys_player1[1]:
        player1_pos[0] -= move_increment
    if keys_player1[3]:
        player1_pos[0] += move_increment

    # moving player3
    if keys_player3[0]:
        player3_pos[1] -= move_increment
    if keys_player3[2]:
        player3_pos[1] += move_increment
    if keys_player3[1]:
        player3_pos[0] -= move_increment
    if keys_player3[3]:
        player3_pos[0] += move_increment

     #10 - Win/Lose check

    if pygame.time.get_ticks() >= 120000:
        running=0
        exitcode=1

print("counter1: " + str(counter1))

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()




