# TODO:
# - Track rotation while inside vehicle
# - Save/load paths
# - Replay paths (botw heros path style)
#   -- include arrow, with rotation, at path head
#   -- smoothly animate across teleport lines
# - Track P2
# - Export path as image

# COMPLETED:
# - Only track if inside the city

import pygame
import math
from mem_stuff import *

WIDTH = 1280
HEIGHT = 720
FPS = 60

BG_COLOUR = (0,0,0)

pygame.init()

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("LCU Heatmap")

clock = pygame.time.Clock()

# Load Images
map_img = pygame.image.load("map.png")
p1_arrow = pygame.image.load("p1_arrow.png")


# Used to rotate player arrow
# Stolen from http://www.pygame.org/wiki/RotateCenter
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


# Calculates the distance between two [x,y] points
def distance_between_points(p1: list, p2: list):
    x_diff = abs(p1[0] - p2[0])
    y_diff = abs(p1[1] - p2[1])
    dist = abs(math.sqrt(x_diff**2 + y_diff**2))
    return dist


# Initialise starting map position, zoom, zoom step (amount to zoom per scroll/key press), and path thickness
camera_focus = [0,0]
zoom = 1
zoom_step = 0.25
path_thickness = 4

# Constants to convert an in-game coordinate to a pixel on the map 
# These are approximations - vertical especially so - but are good enough
x_scaler = 4.876729342
x_offset = 3073
y_scaler = -4.884172716
y_offset = 3073

# Test positions used to evaluate the above constants, as well as calculate them
# in the first place.
test_points = [
    [(-243.349 * x_scaler) + x_offset, (225.653 * y_scaler) + y_offset],
    [(-207.554 * x_scaler) + x_offset, (362.027 * y_scaler) + y_offset],
    [(0 * x_scaler) + x_offset, (0 * y_scaler) + y_offset],
    [(-200.6225 * x_scaler) + x_offset, (-245.2455 * y_scaler) + y_offset],
    [(160.3569 * x_scaler) + x_offset, (-320.3813 * y_scaler) + y_offset],
    [(563.3430 * x_scaler) + x_offset, (-224.1314 * y_scaler) + y_offset],
    [(574.2821 * x_scaler) + x_offset, (-276.7794 * y_scaler) + y_offset]
]

# Initialise player 1 rotation and position, and convert the position to a map pixel
player_rot = 0
player_pos = [0, 0]
player_pos[0] = (player_pos[0] * x_scaler) + x_offset
player_pos[1] = (player_pos[1] * y_scaler) + y_offset

# Arrays to store points/lines from recorded player movement
points = []
lines = []

# Main loop
running = True
while running:
    screen.fill(BG_COLOUR)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False; break

        if event.type == pygame.KEYDOWN:
            match event.key:
                # Map Zoom
                case pygame.K_PAGEUP:
                    zoom -= zoom_step
                case pygame.K_PAGEDOWN:
                    zoom += zoom_step
                
                # Reload addresses/position (latter is obsolete, but former is useful when changing levels in-game)
                case pygame.K_F5:
                    reload_addrs()
                case pygame.K_F6:
                    player_pos = read_positions()
                    player_pos[0] = (player_pos[0] * x_scaler) + x_offset
                    player_pos[1] = (player_pos[1] * y_scaler) + y_offset
                
                # Reset path
                case pygame.K_F1:
                    points = []
                    lines = []
                
                # Change path thickness
                case pygame.K_MINUS:
                    path_thickness -= 1
                case pygame.K_EQUALS:
                    path_thickness += 1
        
        # Map Zoom
        if event.type == pygame.MOUSEWHEEL:
            match event.y:
                case 1:
                    zoom -= zoom_step
                case -1:
                    zoom += zoom_step

    # Map Movement
    if pygame.mouse.get_pressed()[0]:
        rel = pygame.mouse.get_rel()
        camera_focus[0] -= rel[0]*zoom
        camera_focus[1] -= rel[1]*zoom
    else:
        pygame.mouse.get_rel()
    
    # Limit zoom amount
    if zoom < zoom_step:
        zoom = zoom_step
    if zoom > 5:
        zoom = 5

    # Constrain camera movement to map boundaries
    if camera_focus[0] > 7168:
        camera_focus[0] = 7168
    if camera_focus[0] < 0:
        camera_focus[0] = 0
    if camera_focus[1] > 512*13:
        camera_focus[1] = 512*13
    if camera_focus[1] < 0:
        camera_focus[1] = 0

    # Change rendering method based on zoom level (it's a mess, but it improves performance a lot, though it does lag a bit still)
    if zoom <= 2.0:
        sect = pygame.Surface((WIDTH * zoom, HEIGHT * zoom))
        sect.blit(map_img, (0,0), (camera_focus[0]-(WIDTH//2)*zoom, camera_focus[1]-(HEIGHT//2)*zoom, WIDTH*zoom, HEIGHT*zoom))
        sect = pygame.transform.scale_by(sect, 1/zoom)
        screen.blit(sect, (0,0))
    else:
        t_zoom = 1/zoom
        temp_map = pygame.transform.scale_by(map_img, t_zoom)
        screen.blit(temp_map, (-((camera_focus[0] - (WIDTH // 2)/t_zoom) * t_zoom), -((camera_focus[1] - (HEIGHT // 2)/t_zoom) * t_zoom)))

    ## Draw test points
    #for i in test_points:
    #    cx = (i[0] - camera_focus[0])/zoom + (WIDTH // 2)
    #    cy = (i[1] - camera_focus[1])/zoom + (HEIGHT // 2)
    #    if cx < 0 or cx > WIDTH or cy < 0 or cy > HEIGHT: 
    #        pass
    #    else:
    #        pygame.draw.circle(screen, (255,0,0), (cx, cy), 4/zoom)
    
    # Update player position and rotation
    try:
        if check_city_loaded():
            player_pos = read_positions()
            player_pos[0] = (player_pos[0] * x_scaler) + x_offset
            player_pos[1] = (player_pos[1] * y_scaler) + y_offset

            if len(points) == 0:
                points.append(player_pos)
            elif (dist := distance_between_points(player_pos, points[len(points)-1])) >= 1:
                points.append(player_pos)
                if dist >= 10:
                    lines.append([points[len(points)-2], player_pos])

            player_rot = read_rotation()
    except:
        pass # If we can't access the player position for some reason, just ignore it and move on.

    # Draw path onto map
    for point in points:
        cx = (point[0] - camera_focus[0])/zoom + (WIDTH // 2)
        cy = (point[1] - camera_focus[1])/zoom + (HEIGHT // 2)
        if cx < 0 or cx > WIDTH or cy < 0 or cy > HEIGHT: 
            pass
        else:
            pygame.draw.circle(screen, (0,0,255), (cx, cy), path_thickness/zoom)

    # Draw teleport lines (if needed) onto map
    for line in lines:
        p1 = line[0]
        p2 = line[1]

        p1x = (p1[0] - camera_focus[0])/zoom + (WIDTH // 2)
        p1y = (p1[1] - camera_focus[1])/zoom + (HEIGHT // 2)
        p2x = (p2[0] - camera_focus[0])/zoom + (WIDTH // 2)
        p2y = (p2[1] - camera_focus[1])/zoom + (HEIGHT // 2)

        pygame.draw.line(screen, (128,0,255), (p1x, p1y), (p2x, p2y), int(path_thickness/zoom))

    # Draw player position onto map
    cx = (player_pos[0] - camera_focus[0])/zoom + (WIDTH // 2)
    cy = (player_pos[1] - camera_focus[1])/zoom + (HEIGHT // 2)
    if cx < 0 or cx > WIDTH or cy < 0 or cy > HEIGHT: 
        pass
    else:
        #pygame.draw.circle(screen, (0,255,0), (cx, cy), 10/zoom)
        #pygame.draw.circle(screen, (255,0,255), (cx, cy), 8/zoom)
        scaled_p1_arrow = pygame.transform.scale_by(p1_arrow, 0.4/zoom)
        scaled_p1_arrow = rot_center(scaled_p1_arrow, -math.degrees(player_rot))
        screen.blit(scaled_p1_arrow, (cx - ((64*0.4)/zoom), cy - ((64*0.4)/zoom)))
    

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()