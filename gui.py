import pygame
import numpy as np
import math
import copy
import os
import sys
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

script_path = sys.argv[0]
script_dir = os.path.dirname(script_path)

pygame.init()

display_width = 800
display_height = 600

pieces_img = {-1: pygame.image.load(os.path.join(script_dir, 'media', "piece_nothing.png")),
              0: pygame.image.load(os.path.join(script_dir, 'media', "piece_black.png")),
              1: pygame.image.load(os.path.join(script_dir, 'media', "piece_brown.png")),
              2: pygame.image.load(os.path.join(script_dir, 'media', "piece_burnt.png")),
              3: pygame.image.load(os.path.join(script_dir, 'media', "piece_spice.png")),
              4: pygame.image.load(os.path.join(script_dir, 'media', "piece_white.png")),
              5: pygame.image.load(os.path.join(script_dir, 'media', "piece_shadow.png"))}

swap_img = {0: pygame.image.load(os.path.join(script_dir, 'media', "swap_up.png")),
            1: pygame.image.load(os.path.join(script_dir, 'media', "swap_down.png"))}

cursor_img = pygame.image.load(os.path.join(script_dir, 'media', "cursor.png"))
selected_glow_img = pygame.image.load(os.path.join(script_dir, 'media', 'selected_glow.png'))
background_img = pygame.image.load(os.path.join(script_dir, 'media', "background.png"))
background_two_img = pygame.image.load(os.path.join(script_dir, 'media', "background2.png"))
game_display = pygame.display.set_mode((display_width, display_height))
glass_img = pygame.image.load(os.path.join(script_dir, 'media', 'glass.png'))
vial_img = pygame.image.load(os.path.join(script_dir, 'media', 'vial_back_dark.png'))
glass_img.set_alpha(240)

box_one_img = pygame.image.load(os.path.join(script_dir, 'media', 'box_one.png'))
guidance_box_img = pygame.image.load(os.path.join(script_dir, 'media', 'guidance_box.png'))
checkbox_img = { False : pygame.image.load(os.path.join(script_dir, 'media', 'checkbox_no.png')),
                True : pygame.image.load(os.path.join(script_dir, 'media', 'checkbox_yes.png'))}

volume_img = {0 : pygame.image.load(os.path.join(script_dir, 'media', "volume_0.png")),
              1 : pygame.image.load(os.path.join(script_dir, 'media', "volume_1.png")),
              2 : pygame.image.load(os.path.join(script_dir, 'media', "volume_2.png")),
              3 : pygame.image.load(os.path.join(script_dir, 'media', "volume_3.png"))}

furance_hot_image = pygame.image.load(os.path.join(script_dir, 'media', 'furnace_hot.png'))


red_pixel_img = pygame.image.load(os.path.join(script_dir, 'media', 'red_pixel.png'))

        
long_y = 159
y_offset = 20
start_x = 26
gap_x = 40
gap_y = 40
swaps_gap_y = 20
swaps_long_y = 179
swaps_start_x = 56


def py_gui_things():
    return

def volume_display(volume_level):
    game_display.blit(volume_img[volume_level], (740, 540))


def colour_vial(vial_img, colours):
    base = pygame.Surface(vial_img.get_size())
    for x in range(vial_img.get_width()):
        for y in range(vial_img.get_height()):
            r, g, b, a = vial_img.get_at((x, y))
            r += colours[0]
            g += colours[1]
            b += colours[2]
            r = max(min(r, 255), 0)
            g = max(min(g, 255), 0)
            b = max(min(b, 255), 0)
            base.set_at((x, y), (r, g, b, a))
    return base


def background(background_x, background_y):
    game_display.blit(background_img, (background_x, background_y))


def get_vial_colour(score, columns_up):
    colour_change = 50

    max_score = columns_up[1][0] + columns_up[1][1] + columns_up[1][2] + columns_up[1][3] + columns_up[1][4]
    for x in list(range(0, columns_up[0])):
        max_score += x * 4
    if max_score == 0:
        return 0
    vial_colour = score / max_score
    vial_colour = int(round(vial_colour * colour_change * 2 - colour_change, 0))

    return vial_colour

def display_vial(score, columns_up):

    game_display.blit(vial_img, (235, 55))
    vial_start_y = 55
    vial_start_x = 235
    vial_width = 42
    vial_height = 75
    vial_filled = min(vial_height, vial_height / 12 * columns_up[0])
    vial_colour = get_vial_colour(score, columns_up)
    vial_new_image = colour_vial(vial_img, [vial_colour, vial_colour, vial_colour])
    
    game_display.blit(vial_new_image, (vial_start_x, vial_start_y + vial_height - vial_filled), (0, vial_height-vial_filled, vial_width, vial_filled))
    game_display.blit(glass_img, (235, 55))
    pygame.draw.line(game_display, (255, 255, 255), (vial_start_x, vial_start_y + vial_height - vial_filled), (vial_start_x + vial_width, vial_start_y + vial_height - vial_filled), 1)


def background_two(background_x, background_y):
    game_display.blit(background_two_img, (background_x, background_y))


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def board_length(board):
    if board[0][8] == -1: 
        board_len = 9
    else: 
        board_len = 8
    return board_len


def display_board(board, swapping_board, burn_column, time_passed, burn_duration):

    board_len = board_length(board)
    if burn_column[0]:
        burn_completion = (time_passed - burn_column[2]) / burn_duration
        animated_x = gap_x * burn_completion - gap_x
    else:
        animated_x = 0

    for a in list(range(0, len(swapping_board))):

        if board_len == 8:
            column_offset = 0 + (a%2  * 1)
        else:
            column_offset = 1 - (a%2 * 1) 
        for b in list(range(0, len(swapping_board[a]))):
            piece_x = start_x + (a*gap_x) + animated_x
            
            
            piece_y = long_y + (column_offset * y_offset) + (b * gap_y)
            game_display.blit(pieces_img[swapping_board[a][b]], (piece_x, piece_y))
            # game_display.blit(guidance_box_img, (piece_x-1, piece_y-1))


def sign(number):
    if number < 0:
        return -1
    else:
        return 1


def display_moving_pieces(moving_pieces):
    for piece in moving_pieces:
        game_display.blit(pieces_img[piece[0]], (piece[1][0]+1, piece[1][1]+1)) # Pieces look better 1 pixel lower, I assume this is due to rounding errors but didn't really check
        if piece[2]:
            game_display.blit(selected_glow_img, (piece[1][0], piece[1][1]))



def display_burn_column(board, burn_column, time_passed, burn_duration):

    burn_completion = (time_passed - burn_column[2]) / burn_duration
    board_len = board_length(board)
    burn_height = board_len * gap_y
    

    if board_len == 8:
        column_offset = 0 + (9%2  * 1)
    else:
        column_offset = 1 - (9%2 * 1) 

    for i in list(range(len(burn_column[3]))):
        animated_y = burn_height * burn_completion
        if burn_column[1]:
            animated_y = animated_y * -1
        if burn_column[3][8] == -1:
            piece_y = 179 + (i * gap_y) + animated_y
        else:
            animated_y = animated_y * 11 / 9 
            piece_y = 159 + (i * gap_y) + animated_y
        # quit()
        game_display.blit(pieces_img[burn_column[3][i]], (386, piece_y))


def display_swaps(board, swapping_board, swap_rules, burn_column, time_passed, burn_duration):

    board_len = board_length(board)
    
    if burn_column[0]:
        burn_completion = (time_passed - burn_column[2]) / burn_duration
        animated_x = gap_x * burn_completion - gap_x
    else:
        animated_x = 0

    for a in list(range(0, len(swap_rules))):
        
        for b in list(range(0, len(swap_rules[a]))):

            if swap_rules[a][b]:
                #Find the pieces that it connects, if both there, show swap
                
                if a%2 == 0:
                    swap_is_after_long_column = False
                else: 
                    swap_is_after_long_column = True
                if board_len == 8:
                    swap_is_after_long_column = not swap_is_after_long_column
                
                should_display_swap = True

                if swap_is_after_long_column:
                    
                    if swapping_board[a][(b//2 + b%2)] == -1:
                        should_display_swap = False
                    elif swapping_board[a+1][b//2] == -1:
                        should_display_swap = False
                
                else:
                    if swapping_board[a][b//2] == -1:
                        should_display_swap = False
                    elif swapping_board[a+1][(b//2 + b%2)] == -1:
                        should_display_swap = False
                if should_display_swap:

                    piece_x = swaps_start_x + (a * gap_x) + animated_x
                    piece_y = swaps_long_y + (b * swaps_gap_y)
                    
                    if board_len == 9:
                        if a%2 == b%2:
                            swap_direction = 1 # \
                        else:
                            swap_direction = 0 # /
                    else:
                        if a%2 == b%2:
                            swap_direction = 0 # /
                        else:
                            swap_direction = 1 # \

                    game_display.blit(swap_img[swap_direction], (piece_x-swap_direction+1, piece_y)) # one image is slightly off so small correction needed
                

def display_cursor(x, y, burn_column, time_passed, burn_duration, swapping_board):
    game_display.blit(cursor_img, (x, y))


def display_selected(x, y, burn_column, time_passed, burn_duration, swapping_board):
    cursor_in_swap = False
    for swap in swapping_board[1]:
        if swap[5]:
            cursor_in_swap = True
    if not cursor_in_swap:
        game_display.blit(selected_glow_img, (x, y))


def display_furnace(time_passed, time_of_last_burn, burn_interval, burning_now):
    if time_of_last_burn + burn_interval < time_passed:
        time_of_last_burn = time_passed - burn_interval

    time_left = burn_interval - time_passed + time_of_last_burn
    furnace_dimensions = [109, 66]
    image_start_y = 11
    image_end_y = furnace_dimensions[1] - 5
    image_change_y = image_end_y - image_start_y # The amount of the image we care about
    pixels_to_show = int(round((1- (time_left / burn_interval)) * image_change_y, 0))
    highest_pixel_reached = image_start_y + image_change_y - pixels_to_show

    game_display.blit(furance_hot_image, (341, 534 + highest_pixel_reached), (0, highest_pixel_reached, furnace_dimensions[0], pixels_to_show))



def display_texts(settings, score, cc_chain, time_passed, columns_up, board_active, session_paused, practice_names, practice_group_names):
    
    black = (31, 31, 31)
    true_black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (85, 162, 250)
    grey = (150, 150, 150)

    my_font = pygame.font.Font(os.path.join(script_dir, "media", "Roboto-Regular.ttf"), 24)
    my_font_medium = pygame.font.Font(os.path.join(script_dir, "media", "Roboto-Regular.ttf"), 45)
    my_font_large = pygame.font.Font(os.path.join(script_dir, "media", "Roboto-Regular.ttf"), 72)
    my_font_small = pygame.font.Font(os.path.join(script_dir, "media", "Roboto-Regular.ttf"), 12)

    text_standard = my_font.render("Standard", True, white)
    text_seeded = my_font.render("Seeded", True, white)
    text_create = my_font.render("Create", True, white)
    text_practice = my_font.render("Practice", True, grey)

    text_furnace_interval = my_font.render("Burn Timer", True, white)
    text_furnace_interval_num = my_font.render(str(settings["Furnace Interval"]), True, white)
    text_spawn_rates = my_font.render("Spawn Rates", True, white)
    text_start = my_font.render("Start", True, white)
    text_stop = my_font.render("Stop", True, white)
    text_pause = my_font.render("Pause", True, white)
    text_resume = my_font.render("Resume", True, white)
    text_difficulty = my_font.render("Difficulty", True, white)
    text_difficulty_num = my_font.render(str(settings["Difficulty"]), True, white)

    text_score = my_font.render("Score", True, white)
    text_score_number = my_font.render(str(round(score/max(columns_up[0], 1), 2)), True, white)

    text_chain = my_font.render("Chain", True, white)
    text_chain_number = my_font.render(str(cc_chain), True, white)

    text_c = my_font_small.render("C", True, white)
    text_g = my_font_small.render("G", True, white)
    text_p = my_font_small.render("P", True, white)

    text_spawn_rates_2 = { 0 : my_font_small.render(str(settings["Spawn Rates"][0]), True, white),
                           1 : my_font_small.render(str(settings["Spawn Rates"][1]), True, white),
                           2 : my_font_small.render(str(settings["Spawn Rates"][2]), True, white),
                           3 : my_font_small.render(str(settings["Spawn Rates"][3]), True, white),
                           4 : my_font_small.render(str(settings["Spawn Rates"][4]), True, white)
                          }

    text_spawn_rates_3 = { 0 : my_font_small.render("Bl", True, white),
                           1 : my_font_small.render("Br", True, white),
                           2 : my_font_small.render("Bu", True, white),
                           3 : my_font_small.render("Sp", True, white),
                           4 : my_font_small.render("Wh", True, white)
                          }

    game_display.blit(text_standard, (460, 10))
    game_display.blit(text_seeded, (460, 35))
    game_display.blit(text_create, (460, 60))
    game_display.blit(text_practice, (460, 85))

    game_display.blit(text_furnace_interval, (460, 130))
    game_display.blit(text_difficulty, (460, 155))
    game_display.blit(text_spawn_rates, (460, 180))

    game_display.blit(text_spawn_rates_2[0], (610, 180))
    game_display.blit(text_spawn_rates_3[0], (610, 190))
    game_display.blit(text_spawn_rates_2[1], (635, 180))
    game_display.blit(text_spawn_rates_3[1], (635, 190))
    game_display.blit(text_spawn_rates_2[4], (660, 180))
    game_display.blit(text_spawn_rates_3[4], (660, 190))
    game_display.blit(text_spawn_rates_2[3], (685, 180))
    game_display.blit(text_spawn_rates_3[3], (685, 190))
    game_display.blit(text_spawn_rates_2[2], (710, 180))
    game_display.blit(text_spawn_rates_3[2], (710, 190))

    
    game_display.blit(text_furnace_interval_num, (605, 130))
    game_display.blit(text_difficulty_num, (605, 155))

    game_display.blit(box_one_img, (455, 440))
    if board_active:
        game_display.blit(text_stop, (475, 440))
    else:
        game_display.blit(text_start, (475, 440))
    
    game_display.blit(box_one_img, (455, 470))
    if session_paused[0]:
        game_display.blit(text_resume, (475, 470))
    else:
        game_display.blit(text_pause, (475, 470))
    

    game_display.blit(text_score, (460, 525))
    game_display.blit(text_score_number, (550, 525))
    game_display.blit(text_chain, (460, 550))
    game_display.blit(text_chain_number, (550, 550))

    if settings["Seeded"] or settings["Create"]:
        if settings["Create"]:
            shift = 25
        else:
            shift = 0
        
        game_display.blit(text_c, (588, 43 + shift))
        game_display.blit(checkbox_img[False], (585, 43 + shift))
        game_display.blit(text_p, (608, 43 + shift))
        game_display.blit(checkbox_img[False], (605, 43 + shift))
        game_display.blit(text_g, (628, 43 + shift))
        game_display.blit(checkbox_img[False], (625, 43 + shift))
    
    
    game_display.blit(text_c, (588, 18))
    game_display.blit(checkbox_img[False], (585, 18))
    
    
    if settings["Practice"]:
        practice_num = settings["Practice Num"]
        
        text_practice_difficulty = my_font.render(str(practice_num[0]), True, white)
        text_practice_level = my_font.render(str(practice_num[1]), True, white)
        text_practice_description = my_font_small.render(str(practice_names[practice_num[0]][practice_num[1]]), True, white)
        text_practice_group = my_font_small.render(str(practice_group_names[practice_num[0]]), True, white)
        game_display.blit(text_practice_difficulty, (600, 90))
        game_display.blit(text_practice_level, (630, 90))
        game_display.blit(text_practice_description, (600, 115))
        game_display.blit(text_practice_group, (460, 115))
        pass

def display_create(create_piece):
    for x in list(range(0, 5)):
        useful_order = [0, 1, 4, 3, 2]
        game_display.blit(pieces_img[5], (20 + (x*45) - 2, 90 - 2))
        game_display.blit(pieces_img[useful_order[x]], (20 + (x*45), 90))
    game_display.blit(selected_glow_img, (create_piece*45 + 20 - 1, 90 - 1))
        


def draw_red_line(red_line_pixels):
    for x in red_line_pixels:
        game_display.blit(red_pixel_img, (x[0], x[1]))


def display_checkboxes(settings):

    checkbox_locations = {"Standard" : (565, 18),
                          "Seeded" : (565, 43),
                          "Create" : (565, 68),
                          "Practice" : (565, 93)}

    for x in ["Standard", "Seeded", "Create", "Practice"]:
        game_display.blit(checkbox_img[settings[x]], checkbox_locations[x])

    