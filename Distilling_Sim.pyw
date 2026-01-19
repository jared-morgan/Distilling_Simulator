import pygame
import copy
import math
import random
import pyperclip
import re

from gui import *
from sounds import *
import os
import sys

script_path = sys.argv[0]
script_dir = os.path.dirname(script_path)

'''Setup for Pygame'''
pygame.init()
display_width = 800
display_height = 600
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Distilling Simulator')
black = (31, 31, 31)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (85, 162, 250)
grey = (150, 150, 150)
clock = pygame.time.Clock()
crashed = False
background_x = 0
background_y = 0

'''Text stuff'''
my_font = pygame.font.Font(os.path.join(script_dir, 'media', "Roboto-Regular.ttf"), 16)
my_font_large = pygame.font.Font(os.path.join(script_dir, 'media', "Roboto-Regular.ttf"), 24)
text_xxx = my_font.render("xxx", True, white)

'''Variables preloaded'''
action_queued = [0, 0, 0]
board_active = False
# piece_odds = [10, 10, 0, 1, 10]
pieces = [0, 1, 2, 3, 4]
piece_weights = [1, 0, -1, 0, -1]
mouse_last_location = [False, [-100, -100], [-1, -1]]
location_selected = [False, [-100, -100], [-1, -1]]
burn_duration = 1000
burn_column = [False, False, pygame.time.get_ticks(), []]

start_time = pygame.time.get_ticks()
time_of_last_burn = start_time
mouse_new_co = []
mouse_old_co = []
burn_waiting = False
score = 0
cc_chain = 0
columns_up = [0, {-1 : 0,
                  0 : 0,
                  1 : 0,
                  2 : 0,
                  3 : 0,
                  4 : 0,}]
whites_burnt = 0
burns_in_chamber = 0
warning_played = False
session_paused = [False, 0, 0]

speed_cap = 3.5                     # Maximum amount the normal speed can be multiplied by > 4 or so is effectively uncapped
distance_for_speed_increase = 55    # The minimum distance the piece needs to be away from it's destination to get a speed increase
speed_divider = 20                  # Distance from the end location is divided by this to find the new speed. 55 is the distance of 1 swap
distance_buffer = 55                # This distance is not taken into account when finding a new speed
speed_constant = 375                # Base speed a swap
is_create_seeded = False

time_passed = pygame.time.get_ticks() - start_time

practice_available = [[0, 1, 2, 3, 4, 5], #0
                      [0, 1, 2, 3, 4, 5, 6], #1
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], #2
                      [0, 1, 2, 3, 4, 5, 6], #3
                      [0, 1, 2, 3, 4, 5], #4
                      [0, 1, 2, 3, 4], #5
                      [0, 1, 2, 3, 4, 5, 6, 7], #6
                      [0, 1], #7
                      [0, 1], #8
                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]] #9
practice_names = [["Browns up through whites", "Whites down through browns", "Blacks down through whites", "Whites up through Blacks", "Blacks up through browns", "Brown down through blacks"], 
                  ["Browns right step down", "Browns right steps down", "Blacks right step up", "Blacks right, step up", "Line into the pack", "More sorting", "Board with low whites"], 
                  ["Staircase browns above", "Staircase browns below", "Staircase blacks above", "Staircase blacks below", "Staircase brown any", "Staircase black any", "White through staircase", "Unboxing", "Save the corners!", "Timerless easy board"], 
                  ["Crawling", "Butterfly", "Crawling & butterfly combined", "Horzontal drag", "Classic noob stuck", "Easy board, extended timer", "Almost normal board"], 
                  ["Raking the top", "Raking the bottom", "Butterfly & staircase", "Multiple brown crawl", "Multiple black crawl", "Normal spiceless board"], 
                  ["Common Spice stucks", "Staircase over spices", "Crawl under spices", "Reverse staircase", "Normal board"], 
                  ["Rescuing stuck pieces", "Stuck behind spices", "Evening board", "Rescuing a burn simple", "Rescuing a burn properly", "End game no timer", "Normal end game", "Normal end game with spices"], 
                  ["35 junk midgame", "35 junk midgame & spices"], 
                  ["18 junk midgame", "18 junk midgame & spices"], 
                  ["18 junk difficult midgame", "18 junk extra spicy midgame", "18 junk spicy difficult midgame", "Finish burn", "Crawling a burn", "Walking the dog", "Moving a burn up", "Moving a burn down", "Top corner burn, 2bl 1br", "Top corner burn, 1bl 2br", "Bot corner burn, 2bl 1br", "Bot corner burn, 1bl 2br", "Moving a burn wall", "Crawling multiple burns", "Walking the pack", "Arranging burns", "Dodging spices with burns", "Spice trap J30", "Spice trap J27", "Spice trap J23", "Spice trap J18", "Spice trap J13"]]

practice_group_names = {0 : "2 Colour Swaps:",
                        1 : "3 Colour Swaps:",
                        2 : "Multi Piece Sequences:",
                        3 : "Intermediate Sequences:",
                        4 : "Advanced Sequences:",
                        5 : "Spices:",
                        6 : "Endgame:",
                        7 : "Midgames (Master):",
                        8 : "Midgames (GM):",
                        9 : "Burn Play & Spice Traps:"
                        }

settings = {"Standard" : True,
            "Seeded" : False,
            "Create" : False,
            "Practice" : False,
            "Furnace Interval" : 15000,
            "Spawn Rates" : [10, 10, 0, 1, 10],
            "Difficulty" : 50,
            "Practice Num" : [0, 0],
            "Volume" : 3}

spawn_rates_default = [10, 10, 0, 1, 10]
seed = ["", ""]
original_seed = ["", ""]


'''-1 = empty
0 = black
1 = brown
2 = burnt
3 = spice
4 = white'''

swap_logic = {0 : [[1], [2, 4]],
              1 : [[2, 4], [0]],
              2 : [[0], [1]],
              3 : [[], []],
              4 : [[0], [1]],
              -1 : [[], []]}

piece_weights = {0 : -1,
              1 : 0,
              2 : 1,
              3 : 0,
              4 : 1,
              -1 : 0}

board = [[0 for _ in range(9)] for _ in range(10)]

swap_rules = [[False for _ in range(16)] for _ in range(9)]

valid_swaps = []
session_over = False
create_piece = 0
swapping_enabled = True
using_random_seed = True
paint_with = [False, -1]

# volume_level = config_settings[0]
sound_volumes(settings["Volume"] / 6)

def calc_swap(board, column, row, swap_rules):

    if board[column][8] == -1:
        column_height = "short"
    else:
        column_height = "long"

    if column_height == "short":
        
        if row < 8:
            if column > 0: 
                # left up check
                if board[column-1][row] in swap_logic[board[column][row]][0]:
                    swap_rules[column-1][row*2] = True
                else:
                    swap_rules[column-1][row*2] = False

                # left down check
                if board[column-1][row+1] in swap_logic[board[column][row]][1]:
                    swap_rules[column-1][row*2 + 1] = True
                else:
                    swap_rules[column-1][row*2 + 1] = False

            if column < 9:
                # right up check
                if board[column+1][row] in swap_logic[board[column][row]][0]:
                    swap_rules[column][row*2] = True
                else:
                    swap_rules[column][row*2] = False

                # right down check
                if board[column+1][row+1] in swap_logic[board[column][row]][1]:
                    swap_rules[column][row*2 + 1] = True
                else:
                    swap_rules[column][row*2 + 1] = False

    else: # column_height == "long"
        
        if column > 0: 
            # left up check
            if row > 0:
                if board[column-1][row-1] in swap_logic[board[column][row]][0]:
                    swap_rules[column-1][row*2 -1] = True
                else:
                    swap_rules[column-1][row*2 -1] = False

            # left down check
            if row < 8:
                if board[column-1][row] in swap_logic[board[column][row]][1]:
                    swap_rules[column-1][row*2] = True
                else:
                    swap_rules[column-1][row*2] = False
        
        if column < 9: 
            # right up check
            if row > 0:
                if board[column+1][row-1] in swap_logic[board[column][row]][0]:
                    swap_rules[column][row*2 -1] = True
                else:
                    swap_rules[column][row*2 -1] = False

            # right down check
            if row < 8:
                if board[column+1][row] in swap_logic[board[column][row]][1]:
                    swap_rules[column][row*2] = True
                else:
                    swap_rules[column][row*2] = False

    return swap_rules


def calc_swaps(board, furnace_height):
    if furnace_height == 8:
        long_columns = list(range(0, len(board), 2))
    else:
        long_columns = list(range(1, len(board), 2))

    swap_rules = [[False for _ in range(16)] for _ in range(9)]
    for column in long_columns:
        for row in list(range(9)):
            calc_swap(board, column, row, swap_rules)
    
    return swap_rules


def generate_seeded_column(spawn_rates, difficulty, seed, old_column_height): # Generates a column from a given set of pieces (K's distilling counter seed)
    if len(seed[0]) >= old_column_height:
        new_column = []
        for x in list(range(0, old_column_height)):
            new_column.append(int(seed[0][0]))
            seed[0] = seed[0][1:]
            if new_column[x] == 2:
                new_column[x] = 4
        if old_column_height == 8:
            new_column.append(-1)
        return new_column, seed
    else:
        return generate_column(spawn_rates, difficulty, seed)
    

def generate_column(spawn_rates, difficulty, seed):
    new_column = []
    current_spawn_rates = copy.deepcopy(spawn_rates)
    black_and_brown = spawn_rates[0] + spawn_rates[1]
    difficulty_adj = difficulty / 100
    chance_low_black = 2 * spawn_rates[0] * difficulty_adj
    chance_high_black = 2 * spawn_rates[0] - chance_low_black
    chance_high_brown = 2 * spawn_rates[1] * difficulty_adj
    chance_low_brown = 2 * spawn_rates[1] - chance_high_brown 
    for a in list(range(0, 9)):
        if a < 4:
            current_spawn_rates[0] = chance_high_black
            current_spawn_rates[1] = chance_high_brown
        elif a == 4:
            current_spawn_rates[0], current_spawn_rates[1] = spawn_rates[0], spawn_rates[1]
        elif a > 4:
            current_spawn_rates[0] = chance_low_black
            current_spawn_rates[1] = chance_low_brown
        new_column.append(random.choices(pieces, current_spawn_rates, k=1)[0])
    return new_column, seed


def generate_board(spawn_rates, furnace_height, difficulty, seed):
    for a in list(range(0, len(board)-1)):
        output, seed = generate_column(spawn_rates, difficulty, seed)
        board[a] = copy.deepcopy(output)
    for c in list(range(0, furnace_height)):
        board[9][c] = 0
    for d in list(range((furnace_height + 1) % 2, 10, 2)):
        board[d][8] = -1

    ''' Board Presets '''

    ''' Messy board '''
    # board = [[1, 1, 1, 1, 0, 0, 1, 0, -1], [4, 4, 0, 4, 0, 0, 4, 0, 0], [4, 0, 4, 0, 1, 4, 0, 1, -1], [3, 0, 3, 0, 0, 1, 0, 0, 4], [1, 4, 4, 4, 1, 0, 4, 0, -1], [4, 1, 4, 0, 4, 1, 4, 4, 0], [4, 4, 0, 1, 4, 4, 1, 4, -1], [0, 1, 4, 4, 0, 4, 0, 0, 4], [3, 4, 4, 4, 0, 1, 4, 1, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0]]

    ''' Neat board '''
    # board = [[4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 0, -1], [3, 4, 3, 4, 4, 4, 4, 0, 0], [0, 0, 4, 0, 0, 0, 0, 0, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, -1], [0, 1, 1, 0, 0, 0, 0, 0, 0], [3, 1, 1, 1, 1, 1, 1, 1, -1], [0, 0, 1, 1, 1, 1, 1, 1, 1]]

    ''' Buggy board '''
    # board = [[4, 4, 1, 1, 0, 0, 1, 0, -1], [0, 4, 0, 4, 0, 0, 4, 0, 0], [4, 4, 4, 4, 1, 4, 0, 1, -1], [3, 4, 3, 4, 4, 4, 0, 0, 4], [4, 4, 4, 4, 4, 0, 4, 0, -1], [1, 4, 4, 0, 4, 4, 4, 4, 0], [1, 0, 4, 1, 0, 0, 1, 4, -1], [0, 1, 0, 0, 1, 1, 0, 0, 4], [3, 1, 0, 0, 0, 1, 0, 1, -1], [0, 0, 1, 1, 0, 0, 0, 0, 0]]

    '''Horizontal line board'''
    # board = [[4, 4, 4, 4, 4, 4, 4, 4, -1], [1, 4, 4, 1, 4, 4, 0, 4, 4], [4, 4, 0, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 0, 4, 4, 4], [4, 4, 0, 4, 4, 4, 3, 4, -1], [4, 4, 4, 4, 4, 4, 0, 4, 4], [4, 4, 0, 4, 4, 4, 4, 4, -1], [4, 1, 4, 4, 4, 3, 4, 0, 4], [4, 4, 0, 0, 0, 0, 4, 4, -1], [0, 0, 4, 4, 1, 0, 0, 0, 0]]

    # '''All White board'''
    # board = [[4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4]]
    
    '''Spice Trapped board'''
    # board = [[3, 4, 0, 0, 4, 0, 4, 3, -1], [1, 0, 4, 4, 4, 3, 4, 4, 1], [3, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 0, 4, 4, 4, 4, 4, 3], [4, 3, 1, 4, 4, 4, 4, 4, -1], [4, 3, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 3], [4, 4, 4, 4, 4, 4, 4, 4, -1], [0, 0, 0, 0, 0, 0, 3, 0, 1]]
    
    # '''Burns Recovery board'''
    # board = [[0, 0, 0, 4, 4, 3, 1, 0, 1], [1, 2, 4, 4, 4, 4, 4, 4, -1], [1, 2, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [1, 4, 2, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 2, -1], [2, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [2, 4, 4, 4, 4, 3, 4, 4, 4], [3, 4, 4, 4, 4, 4, 4, 4, -1]]
    
    ''' Struggle'''
    # board = [[4, 1, 4, 4, 0, 0, 1, 0, -1], [1, 4, 4, 4, 4, 4, 4, 1, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4], [3, 4, 3, 4, 4, 4, 4, 4, -1], [4, 0, 3, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 3, 4, 4, 4], [4, 4, 4, 4, 4, 1, 3, 4, -1], [4, 4, 4, 4, 4, 3, 4, 4, 4]]
   
    '''Spice Trapped board'''
    # board = [[3, 4, 0, 4, 0, 4, 4, 1, -1], [0, 4, 4, 4, 4, 4, 4, 1, 4], [3, 0, 4, 4, 4, 4, 4, 4, -1], [4, 1, 4, 4, 4, 4, 4, 3, 4], [4, 4, 4, 4, 4, 3, 4, 4, -1], [4, 4, 4, 3, 4, 4, 4, 4, 4], [4, 4, 4, 4, 3, 4, 4, 4, -1], [0, 4, 3, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [0, 4, 4, 0, 0, 0, 0, 4, 4]]
    
    # '''Test Board'''
    # board = [[4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 1, 4, 4, 4, 4, 4, 4, -1], [4, 1, 1, 4, 4, 4, 4, 4, 4], [4, 4, 0, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1], [4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 4, 4, 4, 4, 4, -1]]
    

    furnace_height = board_length(board)

    swap_rules = calc_swaps(board, furnace_height)

    return board, swap_rules, seed


def convert_seed(seed):
    # Takes an input seed which can be in various forms and transforms it into the form [piece sequence, rng decider]
    if "7" in seed:
        if seed[0] == "7":                 # We have no board, just an rng decider
            seed = ["", seed[1:]]
            return seed
        else:                               # We have both a board and an rng decider
            seed.split('7', 1)
    else:
        seed = [seed, ""]                   # There's only a board
    if seed[0][0] == "8" or seed[0][0] == "9":    # Seed generated through create mode where 8/9 is the furnace height
        return seed
    else:                                   # Seed generated through K's Distilling counter which uses different numbers to represent pieces
        seed[0] = seed[0].replace("1", "0")
        seed[0] = seed[0].replace("2", "1")
        seed[0] = seed[0].replace("5", "2")
        seed[0] = seed[0].replace("3", "6")       # 6 used as a temporary number
        seed[0] = seed[0].replace("4", "3")
        seed[0] = seed[0].replace("6", "4")
        

        return seed                         # [piece sequence, rng decider]


def import_board(seed):
    board = [[-1 for _ in range(9)] for _ in range(10)]
    if seed[0][0] == "9":
        column_lengths = [8, 9, 8, 9, 8, 9, 8, 9, 8, 9]
    else:
        column_lengths = [9, 8, 9, 8, 9, 8, 9, 8, 9, 8]
    if seed[0][0] == "9" or seed[0][0] == "8":    # The first char just tells us the length of the furnace column, can be ditched now
        seed[0] = seed[0][1:]
    for x in list(range(0, 10)):
        for y in list(range(0, column_lengths[x])):
            board[x][y] = int(seed[0][0])
            seed[0] = seed[0][1:]


    furnace_height = board_length(board)
    swap_rules = calc_swaps(board, furnace_height)
    

    return board, swap_rules, seed


def cursor_location(board, mouse_x, mouse_y, mouse_last_location):
        
        board_len = board_length(board)                     # The length of the burn column
        x_shift = 25                                        # This value is one smaller than the first image displayed because the images are only 38x38 and the board gaps are 40x40
        
        mouse_x_cell = math.floor((mouse_x - x_shift) / 40) # Column we are in

        if mouse_x_cell < 0:                                # Corrections for the edges of the board
            mouse_last_location[0] = False
            return mouse_last_location   
        elif mouse_x_cell > 9: 
            mouse_last_location[0] = False
            return mouse_last_location    

        mouse_x = mouse_x_cell * 40 + x_shift               # X position we want to display

        if mouse_x_cell % 2 == 0:                           # Then in a column with opposite length to board_len
            if board_len == 8:
                column_len = 9
            else:
                column_len = 8
        else:                                               # We are in the same column length
            column_len = board_len

        if column_len == 8:
            y_shift = 178                                   # This value is one smaller than the first image displayed because the images are only 38x38 and the board gaps are 40x40
        else:
            y_shift = 158                                   # This value is one smaller than the first image displayed because the images are only 38x38 and the board gaps are 40x40

        mouse_y_cell = math.floor((mouse_y - y_shift) / 40) # Row we are in

        if mouse_y_cell < 0:                                # Corrections for the edges of the board
            mouse_last_location[0] = False
            return mouse_last_location            
        if mouse_y_cell > column_len - 1: 
            mouse_last_location[0] = False
            return mouse_last_location   

        mouse_y = mouse_y_cell * 40 + y_shift              # Y position we want to display

        return [True, [mouse_x, mouse_y], [mouse_x_cell, mouse_y_cell]]


def pixel_value_of_piece(location, board):

    board_len = board_length(board)
    x_shift = 25

    if location[0] % 2 == 0:
        if board_len == 8:
            column_len = 9
        else:
            column_len = 8
    else:                                              
        column_len = board_len

    piece_x = location[0] * 40 + x_shift
    piece_y = location[1] * 40 + 158 + (9 - column_len) * 20

    return [piece_x, piece_y]


def coordinate_of_pixel_value(mouse_last_location, board):

    board_len = board_length(board)

    x_shift = 25
    x_coordinate = (mouse_last_location[0] - x_shift) // 40

    if x_coordinate % 2 == 0:
        if board_len == 8:
            column_len = 9
        else:
            column_len = 8
    else:                                              
        column_len = board_len

    
    if column_len == 8:
        y_shift = 178
    else:
        y_shift = 158

    y_coordinate = (mouse_last_location[1] - y_shift) // 40
    if column_len == 8 and y_coordinate == 8:
        y_coordinate = -1
    elif y_coordinate == 9:
        y_coordinate = -1

    return [x_coordinate, y_coordinate]


def get_valid_swaps(location_selected, board, swap_rules):

    board_len = board_length(board)
    if location_selected[2][0] % 2 == 0:
        if board_len == 8:
            column_len = 9
        else:
            column_len = 8
    else:                                              
        column_len = board_len

    valid_swaps = []
    
    if column_len == 8:
        if location_selected[2][0] > 0:
            if swap_rules[location_selected[2][0]-1][location_selected[2][1]*2]:
                valid_swaps.append([location_selected[2][0]-1, location_selected[2][1]])
            if swap_rules[location_selected[2][0]-1][location_selected[2][1]*2+1]:
                valid_swaps.append([location_selected[2][0]-1, location_selected[2][1]+1])
        if location_selected[2][0] < 9:
            if swap_rules[location_selected[2][0]][location_selected[2][1]*2]:
                valid_swaps.append([location_selected[2][0]+1, location_selected[2][1]])
            if swap_rules[location_selected[2][0]][location_selected[2][1]*2+1]:
                valid_swaps.append([location_selected[2][0]+1, location_selected[2][1]+1])
    
    
    if column_len == 9:
        if location_selected[2][0] > 0:
            if location_selected[2][1] > 0:
                if swap_rules[location_selected[2][0]-1][location_selected[2][1]*2-1]:
                    valid_swaps.append([location_selected[2][0]-1, location_selected[2][1]-1])
            if location_selected[2][1] < 8:
                if swap_rules[location_selected[2][0]-1][location_selected[2][1]*2]:
                    valid_swaps.append([location_selected[2][0]-1, location_selected[2][1]])
        if location_selected[2][0] < 9:
            if location_selected[2][1] > 0:
                if swap_rules[location_selected[2][0]][location_selected[2][1]*2-1]:
                    valid_swaps.append([location_selected[2][0]+1, location_selected[2][1]-1])
            if location_selected[2][1] < 8:
                if swap_rules[location_selected[2][0]][location_selected[2][1]*2]:
                    valid_swaps.append([location_selected[2][0]+1, location_selected[2][1]])

    return valid_swaps


def swap_check(mouse_last_location, valid_swaps, location_selected, board):

    for valid_swap in valid_swaps:
        if mouse_last_location == valid_swap:
            board_len = board_length(board)
            
            if not location_selected[2][0] % 2:
                if board_len == 9:
                    board_len = 8
                else:
                    board_len = 9
            if board_len == 9:
                if valid_swap[1] == location_selected[2][1]:
                    play_sound("swap_down")
                else:
                    play_sound("swap_up")
            else:
                if valid_swap[1] == location_selected[2][1]:
                    play_sound("swap_up")
                else:
                    play_sound("swap_down")

            return valid_swap
    
    return False


def smooth_path(destinations):

    smooth_amount = 0.8   # A number between 0 and 1, when set to 1 each piece will travel in a straight line from the antepenultimate to the last piece
    smooth_toggle = 0  # Difference required before smoothing

    if destinations[-3][0] < destinations[-2][0]:
        if destinations[-1][0] < destinations[-2][0]:
            difference = [destinations[-2][0] - destinations[-3][0], destinations[-2][0] - destinations[-1][0], []]
            difference[2] = min(difference[0:1])
            if difference[2] > smooth_toggle:
                difference[2] = difference[2] * smooth_amount
            destinations[-2][0] -= difference[2]
    else:
        if destinations[-1][0] > destinations[-2][0]:
            difference = [destinations[-3][0] - destinations[-2][0], destinations[-1][0] - destinations[-2][0], []]
            difference[2] = min(difference[0:1])
            if difference[2] > smooth_toggle:
                difference[2] = difference[2] * smooth_amount
            destinations[-2][0] += difference[2]

    if destinations[-3][1] < destinations[-2][1]:
        if destinations[-1][1] < destinations[-2][1]:
            difference = [destinations[-2][1] - destinations[-3][1], destinations[-2][1] - destinations[-1][1], []]
            difference[2] = min(difference[0:1])
            if difference[2] > smooth_toggle:
                difference[2] = difference[2] * smooth_amount
            destinations[-2][1] -= difference[2]
    else:
        if destinations[-1][1] > destinations[-2][1]:
            difference = [destinations[-3][1] - destinations[-2][1], destinations[-1][1] - destinations[-2][1], []]
            difference[2] = min(difference[0:1])
            if difference[2] > smooth_toggle:
                difference[2] = difference[2] * smooth_amount
            destinations[-2][1] += difference[2]

    return destinations


def find_distance_of_list(destinations):
    distance = 0
    for x in list(range(0, len(destinations)-1)):
        distance += math.sqrt((destinations[x][0] - destinations[x+1][0]) ** 2 + (destinations[x][1] - destinations[x+1][1]) ** 2)
    return distance


def speed_of_swap(destinations, swapping_board, x):
    
    speed = 1

    old_speed = swapping_board[1][x][3]

    if len(destinations) > 2:
        destinations = smooth_path(destinations)
    destinations_temp = []
    for destination in destinations:
        if destination not in destinations_temp:
            destinations_temp.append(destination)
    destinations = copy.deepcopy(destinations_temp)
    distance_to_travel = find_distance_of_list(destinations)
    
    new_speed = min((distance_to_travel - distance_buffer) / speed_divider, speed_cap)
    # if old_speed > new_speed:
    #     speed = (old_speed + new_speed) / 2
    #     # speed = old_speed
    if distance_to_travel > distance_for_speed_increase:
        speed = new_speed

    if speed < 1:
        speed = 1        

    return destinations, speed


def perform_swap(board, swap_rules, swap_with, location_selected, time_passed, swapping_board):

    # swap_with is the coordinates of the piece not selected
    # location_selected[1] is the pixel location of start
    # location_selected[2] is the coordinate location of start
    # swap_with is coordinate value of start

    swapping_board[0][swap_with[0]][swap_with[1]] = -1 # We don't want the moving pieces to show normally
    swapping_board[0][location_selected[2][0]][location_selected[2][1]] = -1

    deletion = []
    temporary_pieces = [[], []]

    # The piece on the cursor
    moving_piece_found = False
    
    for x in list(range(len(swapping_board[1]))):
        if swapping_board[1][x][1] == location_selected[2]:
            
            moving_piece_found = True

            '''If I want checkpoints'''
            destinations = swapping_board[1][x][0]
            destinations.append(pixel_value_of_piece(swap_with, board))

            '''If I don't want checkpoints'''
            # destinations = [swapping_board[1][x][0][0], pixel_value_of_piece(swap_with, board)]

            destinations, new_speed = speed_of_swap(destinations, swapping_board, x)

            temporary_pieces[0] = [copy.deepcopy(destinations), 
                                   copy.deepcopy(swap_with), 
                                   board[location_selected[2][0]][location_selected[2][1]], 
                                   new_speed, 
                                   swapping_board[1][x][4], 
                                   True]
            deletion.append(x)

    if not moving_piece_found:
        temporary_pieces[0] = [[copy.deepcopy(location_selected[1]), copy.deepcopy(pixel_value_of_piece(swap_with, board))],  # [0][0] pixel start, [0][-1] pixel end, 
                               copy.deepcopy(swap_with),                                                                      # [1] coordinate end 
                               board[location_selected[2][0]][location_selected[2][1]],                                       # [2] piece type 
                               1,                                                                                             # [3] speed 
                               time_passed,                                                                                   # [4] time of last update 
                               True]                                                                                          # [5] if piece is selected by mouse cursor
    if deletion != []:
        swapping_board[1].pop(deletion[0])
        deletion = []
    
    # The piece moved by the piece on the cursor
    moving_piece_found = False
    for x in list(range(len(swapping_board[1]))):
        if swapping_board[1][x][1] == swap_with:
            moving_piece_found = True

            '''If I want checkpoints'''
            destinations = swapping_board[1][x][0]
            destinations.append(location_selected[1])

            '''If I don't want checkpoints'''
            # destinations = [swapping_board[1][x][0][0], location_selected[1]]
            
            destinations, new_speed = speed_of_swap(destinations, swapping_board, x)
            temporary_pieces[1] = [copy.deepcopy(destinations), 
                                   copy.deepcopy(location_selected[2]), 
                                   board[swap_with[0]][swap_with[1]], 
                                   new_speed, 
                                   swapping_board[1][x][4], 
                                   False]
            
            deletion.append(x)

    if not moving_piece_found:
        temporary_pieces[1] = [[copy.deepcopy(pixel_value_of_piece(swap_with, board)), copy.deepcopy(location_selected[1])],
                                copy.deepcopy(location_selected[2]),
                                board[swap_with[0]][swap_with[1]],
                                1, 
                                time_passed, 
                                False]                                                                              
    if deletion != []:
        swapping_board[1].pop(deletion[0])

    swapping_board[1].append(temporary_pieces[0])
    swapping_board[1].append(temporary_pieces[1])

    # Sorting out the pieces on the normal board now that they are correct on the swap board
    temp_piece =  board[swap_with[0]][swap_with[1]]
    board[swap_with[0]][swap_with[1]] = board[location_selected[2][0]][location_selected[2][1]]
    board[location_selected[2][0]][location_selected[2][1]] = temp_piece
    location_selected[2] = swap_with
    location_selected[1] = pixel_value_of_piece(location_selected[2], board)

    swap_rules = calc_swaps(board, board_length(board))

    return board, swap_rules, location_selected, swapping_board


def calculate_moving(board, swapping_board, burn_column, time_passed):
    # speed_constant = 350
    board_len = board_length(board)
    moving_pieces = []

    if swapping_board[1] != []:
        pieces_for_deletion = []
        
        for p in list(range(len(swapping_board[1]))):

            piece = copy.deepcopy(swapping_board[1][p])
            x_change = piece[0][1][0] - piece[0][0][0]
            y_change = piece[0][1][1] - piece[0][0][1]
            total_change = math.sqrt(x_change ** 2 + y_change ** 2)
            time_change = time_passed - piece[4]
            speed = piece[3] * speed_constant
            pixels_to_change = speed * time_change / 1000

            destinations_reach = 0
            piece_at_finish = False

            if abs(pixels_to_change) >= total_change: 
                if len(piece[0]) == 2:
                    piece_at_finish = True                                      # Piece has reached it's end
                    swapping_board[0][piece[1][0]][piece[1][1]] = piece[2]
                    pieces_for_deletion.append(p)
                else:
                    destinations_reach = 1                                                       # Piece must continue to the next checkpoint
                    x_change = piece[0][2][0] - piece[0][1][0]
                    y_change = piece[0][2][1] - piece[0][1][1]
                    total_change = math.sqrt(x_change ** 2 + y_change ** 2)
                    time_change = time_change * (1 - (pixels_to_change / total_change)) # How much time we have left after hitting the prior checkpoint
                    speed = piece[3] * speed_constant
                    pixels_to_change = speed * time_change / 1000

            if not piece_at_finish:
                try: 
                    swap_x = math.sqrt(pixels_to_change ** 2 / (1 + abs(y_change)/abs(x_change)))
                except:
                    swap_x = 0
                if abs(swap_x) > abs(piece[0][0][0] - piece[0][1][0]):
                    swap_x = abs(piece[0][0][0] - piece[0][1][0])
                    swap_y = abs(piece[0][0][1] - piece[0][1][1])
                    piece[0][0][0] = piece[0][1][0]
                    if len(piece[0]) == 2:
                        piece_at_finish = True                                      # Piece has reached it's end
                        swapping_board[0][piece[1][0]][piece[1][1]] = piece[2]
                        pieces_for_deletion.append(p)

                elif swap_x == 0:
                    swap_y = pixels_to_change
                else:
                    swap_y = swap_x * abs(y_change) / abs(x_change)
            
            if not piece_at_finish:

                swap_x = swap_x * sign(x_change)
                swap_y = swap_y * sign(y_change)
                
                
                piece[0][destinations_reach][0] = round(piece[0][destinations_reach][0] + swap_x, 2)
                piece[0][destinations_reach][1] = round(piece[0][destinations_reach][1] + swap_y, 2)
                if destinations_reach == 1:
                    piece[0] = piece[0][1:]

                swapping_board[1][p] = piece
                swapping_board[1][p][4] = time_passed    
                moving_pieces.append([piece[2], (piece[0][0][0], piece[0][0][1]), piece[5]])
                # if piece[5]:
                #     game_display.blit(selected_glow_img, (piece[0][0][0]-1, piece[0][0][1]-1))
        if pieces_for_deletion != []:
            to_delete = []
            for p in pieces_for_deletion:
                to_delete.append(swapping_board[1][p])
            for d in to_delete:
                swapping_board[1].pop(swapping_board[1].index(d))
            

    return swapping_board, moving_pieces


def get_column_weight(board):
    column_weight = 0
    for piece in board[9]:
        column_weight += piece_weights[piece]
    
    return column_weight


def deal_with_burns(burn_column, board, burns_in_chamber, whites_burnt):

    if not burn_column[1]:
        for piece in burn_column[3]:
            if piece == 4:
                whites_burnt += 1
                if whites_burnt % 2 == 0:
                    burns_in_chamber += 1

    for x in list(range(len(board[0]))):
        if burns_in_chamber > 0:
            if board[0][x] == 4:
                burns_in_chamber -= 1
                board[0][x] = 2
    return board, burns_in_chamber, whites_burnt


def activate_furnace(board, location_selected, time_passed, burns_in_chamber, whites_burnt, settings, seed):

    old_column_height = board_length(board)
    burn_column = [True, False, time_passed, board[9]] # [Is burning?, column up?, time burn starts, pieces in burn column]
    if get_column_weight(board) > -1:
        burn_column[1] = True
    board.pop(9)
    if settings["Standard"] or settings["Create"] or settings["Practice"]:
        new_column, seed = generate_column(settings["Spawn Rates"], settings["Difficulty"], seed)
        board.insert(0, new_column)
    elif settings["Seeded"]:
        seeded_column, seed = generate_seeded_column(settings["Spawn Rates"], settings["Difficulty"], seed, old_column_height)
        board.insert(0, seeded_column)

    if old_column_height == 8:
        board[0][8] = -1

    board, burns_in_chamber, whites_burnt = deal_with_burns(burn_column, board, burns_in_chamber, whites_burnt)
    

    swap_rules = calc_swaps(board, board_length(board))
    valid_swaps = []
    if location_selected[0]:
        if location_selected[2][0] == 9:
            location_selected[0] = False
        else:
            location_selected[1][0] += 40
            location_selected[2][0] += 1
            valid_swaps = get_valid_swaps(location_selected, board, swap_rules)

    return  board, location_selected, valid_swaps, swap_rules, burn_column, burns_in_chamber, whites_burnt, seed


def find_skipped_coordinatees(mouse_change, mouse_old_co, board):
    coords_to_check = []
    if mouse_change[0] == 0 and mouse_change[1] == 0:
        return coords_to_check
    
    if abs(mouse_change[0]) >= abs(mouse_change[1]): # There are more x values than y so I should solve for x
        delta_y = mouse_change[1] / abs(mouse_change[0])
        if delta_y == 0:
            for change_x in list(range(1, abs(mouse_change[0]) + 1)):
                coords_to_check.append([int(mouse_old_co[0] + (change_x * mouse_change[0] / abs(mouse_change[0]))), 
                                        mouse_old_co[1]])
        else:
            for change_x in list(range(1, abs(mouse_change[0]) + 1)):
                coords_to_check.append([int(mouse_old_co[0] + (change_x * mouse_change[0] / abs(mouse_change[0]))), 
                                        int(round(mouse_old_co[1] + (change_x * delta_y), 0 ))])
            
    else:
        delta_x = mouse_change[0] / abs(mouse_change[1])
        if delta_x == 0:
            for change_y in list(range(1, abs(mouse_change[1]) + 1)):
                coords_to_check.append([mouse_old_co[0], 
                                       int(mouse_old_co[1] + (change_y * mouse_change[1] / abs(mouse_change[1])))])
        else:
            for change_y in list(range(1, abs(mouse_change[1]) + 1)):
                coords_to_check.append([int(round(mouse_old_co[0] + (change_y * delta_x), 0 )), 
                                        int(mouse_old_co[1] + (change_y * mouse_change[1] / abs(mouse_change[1])))])
    
    cells_to_check = []
    for coordinates in coords_to_check:
        cell = coordinate_of_pixel_value(coordinates, board)
        if cell[1] > -1 and cell not in cells_to_check:
            if check_if_mouse_in_circle(cell, coordinates, board):
                cells_to_check.append(cell)


    return cells_to_check


def check_if_mouse_in_circle(cell, coordinates, board):

    transparant_values = {(15, 39), (26, 39), (7, 35), (8, 0), (19, 0), (30, 0), (0, 5), (0, 14), (0, 23), (4, 2), (34, 3), (10, 36), (2, 32), (33, 38), (3, 6), (37, 8), (3, 33), (37, 35), 
                          (38, 0), (38, 9), (7, 3), (8, 4), (6, 34), (29, 36), (0, 0), (11, 0), (0, 9), (33, 33), (2, 36), (3, 1), (14, 1), (37, 3), (25, 38), (3, 10), (37, 12), (37, 30), 
                          (3, 37), (38, 4), (36, 34), (17, 39), (28, 39), (6, 38), (33, 1), (33, 37), (34, 2), (22, 0), (2, 31), (3, 5), (37, 7), (36, 29), (7, 2), (36, 38), (9, 39), (6, 33), 
                          (10, 3), (33, 5), (25, 1), (2, 8), (10, 39), (34, 6), (2, 35), (37, 2), (32, 36), (3, 0), (14, 0), (3, 9), (37, 11), (26, 1), (36, 33), (5, 36), (29, 3), (28, 38), 
                          (6, 37), (33, 0), (2, 3), (20, 39), (2, 12), (2, 30), (3, 4), (1, 34), (36, 1), (35, 36), (36, 10), (36, 37), (6, 5), (9, 38), (39, 29), (10, 2), (33, 4), (39, 38), 
                          (25, 0), (2, 7), (12, 39), (23, 39), (32, 35), (1, 29), (35, 31), (1, 38), (36, 5), (28, 1), (36, 32), (5, 35), (29, 2), (28, 37), (6, 0), (39, 24), (39, 33), (2, 2), 
                          (32, 3), (31, 38), (2, 11), (35, 8), (4, 39), (1, 15), (32, 39), (1, 33), (35, 35), (36, 0), (36, 9), (5, 3), (9, 1), (5, 39), (6, 4), (39, 10), (11, 37), (39, 19), 
                          (0, 37), (39, 28), (39, 37), (12, 38), (35, 3), (4, 34), (1, 10), (1, 28), (1, 37), (36, 4), (17, 0), (28, 0), (38, 32), (5, 7), (39, 5), (8, 36), (31, 1), (30, 36), 
                          (39, 14), (0, 32), (39, 23), (39, 32), (31, 37), (32, 2), (1, 5), (35, 7), (4, 38), (34, 39), (1, 14), (1, 32), (38, 27), (5, 2), (38, 36), (9, 0), (7, 39), (18, 39), 
                          (39, 0), (0, 18), (39, 9), (0, 27), (39, 18), (12, 1), (0, 36), (39, 27), (4, 6), (35, 2), (1, 0), (4, 33), (34, 34), (1, 9), (37, 39), (38, 13), (38, 31), (5, 6), 
                          (26, 38), (7, 34), (0, 4), (0, 13), (27, 39), (39, 4), (0, 22), (8, 35), (20, 0), (31, 0), (39, 13), (0, 31), (39, 22), (4, 1), (32, 1), (1, 4), (35, 6), (34, 38), 
                          (1, 13), (3, 32), (37, 34), (38, 8), (38, 26), (38, 35), (7, 38), (8, 3), (30, 3), (0, 8), (0, 17), (39, 8), (0, 26), (31, 4), (0, 35), (12, 0), (23, 0), (4, 5), 
                          (34, 33), (37, 29), (3, 36), (15, 1), (38, 3), (37, 38), (38, 12), (38, 30), (27, 2), (29, 39), (0, 3), (0, 12), (0, 21), (33, 36), (34, 1), (4, 0), (2, 39), (37, 6), 
                          (34, 37), (3, 31), (37, 33), (38, 7), (7, 1), (7, 37), (8, 2), (30, 2), (0, 7), (21, 39), (0, 16), (10, 38), (34, 5), (2, 34), (37, 1), (3, 8), (37, 10), (37, 28), 
                          (22, 39), (3, 35), (38, 2), (15, 0), (26, 0), (38, 11), (7, 5), (27, 1), (11, 2), (6, 36), (29, 38), (0, 2), (33, 35), (34, 0), (2, 29), (2, 38), (3, 3), (37, 5), 
                          (3, 30), (36, 36), (7, 0), (18, 0), (9, 37), (10, 1), (33, 3), (2, 6), (10, 37), (34, 4), (2, 33), (32, 34), (37, 0), (3, 7), (37, 9), (13, 39), (24, 39), (35, 39), 
                          (36, 31), (7, 4), (5, 34), (29, 1), (6, 35), (29, 37), (2, 1), (2, 10), (2, 28), (2, 37), (3, 2), (37, 4), (32, 38), (35, 34), (36, 8), (16, 39), (36, 35), (5, 38), 
                          (6, 3), (9, 36), (6, 39), (33, 2), (10, 0), (39, 36), (2, 5), (1, 27), (1, 36), (36, 3), (13, 38), (24, 38), (35, 38), (36, 30), (36, 39), (5, 33), (29, 0), (39, 31), 
                          (31, 36), (2, 0), (2, 9), (4, 37), (32, 37), (1, 31), (35, 33), (36, 7), (5, 1), (5, 37), (6, 2), (21, 0), (8, 39), (19, 39), (30, 39), (39, 17), (39, 26), (39, 35), 
                          (2, 4), (13, 1), (24, 1), (35, 1), (4, 32), (1, 8), (1, 26), (1, 35), (36, 2), (35, 37), (5, 5), (9, 3), (38, 39), (5, 32), (6, 6), (27, 38), (39, 3), (39, 12), (0, 30), 
                          (0, 39), (11, 39), (39, 21), (39, 30), (39, 39), (31, 35), (32, 0), (1, 3), (35, 5), (4, 36), (1, 12), (1, 30), (35, 32), (1, 39), (36, 6), (38, 25), (28, 2), (5, 0), 
                          (38, 34), (6, 1), (39, 7), (0, 25), (8, 38), (31, 3), (30, 38), (39, 16), (0, 34), (39, 25), (4, 4), (39, 34), (31, 39), (32, 4), (13, 0), (24, 0), (4, 31), (34, 32), 
                          (35, 0), (1, 7), (37, 37), (1, 25), (38, 29), (5, 4), (9, 2), (38, 38), (0, 11), (27, 37), (39, 2), (0, 20), (39, 11), (0, 29), (11, 38), (39, 20), (0, 38), (4, 8), 
                          (1, 2), (35, 4), (4, 35), (34, 36), (16, 0), (1, 11), (37, 32), (3, 39), (38, 6), (14, 39), (38, 15), (38, 24), (38, 33), (7, 36), (8, 1), (30, 1), (0, 6), (0, 15), 
                          (39, 6), (0, 24), (8, 37), (31, 2), (30, 37), (39, 15), (0, 33), (4, 3), (33, 39), (1, 6), (37, 27), (3, 34), (38, 1), (37, 36), (38, 10), (38, 28), (38, 37), (27, 0), 
                          (11, 1), (0, 1), (0, 10), (39, 1), (0, 19), (0, 28), (12, 2), (33, 34), (4, 7), (25, 39), (1, 1), (34, 35), (37, 31), (3, 38), (38, 5), (14, 38), (38, 14)}
    
    pixel_value_of_cell = pixel_value_of_piece(cell, board)
    pixel_value_in_cell = (coordinates[0] - pixel_value_of_cell[0], coordinates[1] - pixel_value_of_cell[1])

    if pixel_value_in_cell in transparant_values:
        return False
    else:
        return True


def check_for_burn(time_passed, time_of_last_burn, burn_interval):

    if burn_interval - time_passed + time_of_last_burn < 0:
        return True
    else:
        return False


def check_for_burn_warning(time_passed, time_of_last_burn, burn_interval):
    warning_time = 2500
    if burn_interval - warning_time - time_passed + time_of_last_burn < 0:
        play_sound("burn_warning")
        return True
    else:
        return False


def score_column(burn_column, cc_chain, score, columns_up):
    bad_pieces = [0, 1, 2]
    piece_scores = {True: {
                    -1 : 0,
                    0 : -1,
                    1 : 0,
                    2 : 0,
                    3 : 3,
                    4 : 1,},
                False: {
                    -1 : 0,
                    0 : 0,
                    1 : 0,
                    2 : 0,
                    3 : -3,
                    4 : 0,}}
    pieces_in_column = {-1 : 0,
                        0 : 0,
                        1 : 0,
                        2 : 0,
                        3 : 0,
                        4 : 0}
    

    for piece in burn_column[3]:
        pieces_in_column[piece] += 1

    if burn_column[1]:
        columns_up[0] += 1
        if pieces_in_column[0] == 0 and pieces_in_column[1] == 0 and pieces_in_column[2] == 0:
            score += cc_chain * 4
            cc_chain += 1
            random_boolean = random.choice([True, False])
            if random_boolean:
                play_sound("crystal_clear")
            else:
                play_sound("crystal_clear2")
        else:
            cc_chain = 0
        if pieces_in_column[0] + pieces_in_column[2] == pieces_in_column[4]:
            random_boolean = random.choice([True, False])
            if random_boolean:
                play_sound("blecch")
            else:
                play_sound("blecch2")
        elif  pieces_in_column[0] == 0 and pieces_in_column[2] == 0 and (pieces_in_column[4] > pieces_in_column[1]) and cc_chain < 1:
            play_sound("smooth")
        if 3 in burn_column[3]:
            play_sound("spicy")
    else:
        cc_chain = 0
        play_sound("burn")
        if 4 in burn_column[3]:
            play_sound("burnt")
    if burn_column[1]:
        for piece in pieces_in_column:
            columns_up[1][piece] += pieces_in_column[piece]
        
    for piece in burn_column[3]:
        score += piece_scores[burn_column[1]][piece]
        
    session_over = False
    if columns_up[0] > 11:
        if cc_chain <12 or not burn_column[1]:
            session_over = True

    return score, cc_chain, columns_up, session_over
    

def calculate_overall_score(score, columns_up):
    overall_score = score / columns_up
    return overall_score


def adjust_settings(setting, button, default, min, max, interval):
    if button == 1 or button == 4:
        if setting < max:
            setting += interval
        elif setting > max:
            setting = default
    elif button == 3 or button == 5:
        if setting > max:
            setting = default
        elif setting > min:
            setting -= interval
    return setting


def adjust_settings_mode(settings, mode):
    modes = {"Standard", "Seeded", "Create", "Practice"}
    modes.remove(mode)
    settings[mode] = True
    for m in modes:
        settings[m] = False

    return settings


def is_paste_legal(paste, seed):
    pattern = r'[^0-9]'
    if type(paste) == str:
        if not bool(re.search(pattern, paste)):
            seed = str(paste)
            seed = convert_seed(seed)
    return seed


def modify_piece(mouse_pos, board, swapping_board, event_type, input, swap_rules):
    mouse_co = coordinate_of_pixel_value(mouse_pos, board)
    
    normal_order = [0, 1, 2, 3, 4]
    useful_order = [0, 1, 4, 3, 2]
    if mouse_co[1] == -1:
        return board, swap_rules, swapping_board
    else:
        if event_type == "Scroll":
            scroll_direction = int((input - 4.5) * -2)
            piece_index = useful_order.index(board[mouse_co[0]][mouse_co[1]]) + scroll_direction
            if piece_index == -1:
                piece_index = 4
            elif piece_index == 5:
                piece_index = 0
            
            board[mouse_co[0]][mouse_co[1]] = useful_order[piece_index]

            swapping_board[0]  = copy.deepcopy(board)
            swap_rules = calc_swaps(board, board_length(board))
        
        elif event_type == "Number":
            board[mouse_co[0]][mouse_co[1]] = useful_order[normal_order.index(input)]
            swapping_board[0]  = copy.deepcopy(board)
            swap_rules = calc_swaps(board, board_length(board))

        return board, swap_rules, swapping_board
    

def get_create_seed(board):
    furnace_height = board_length(board)
    seed = str(furnace_height)
    for x in list(range(0, 10)):
        for y in list(range(0, 9)):
            if board[x][y] != -1:
                seed += str(board[x][y])
    pyperclip.copy(seed)
    return    


def generate_seed(need_copy):
    original_seed = "7"
    original_seed += str(random.randint(10**19, (10**20)-1)) # Appends a random 20 digit number onto the end
    if need_copy:
        pyperclip.copy(original_seed)
    return original_seed


def start_procedure(settings, original_seed, is_create_seeded, random_seed, using_random_seed, furnace_interval, spawn_rates, difficulty):
    seed = copy.deepcopy(original_seed)
    session_over = False

    if settings["Standard"]:
        original_seed = ["", random_seed[1:]]
        seed = copy.deepcopy(original_seed)
        random_seed = "7"+ str(int(random_seed[1:]) + 1)
        random.seed(seed[1])
        board, swap_rules, seed = generate_board(settings["Spawn Rates"], 8, settings["Difficulty"], seed)

    elif settings["Seeded"]:
        if using_random_seed:
            seed[1] = random_seed[1:]
            original_seed[1] = seed[1]
            random_seed = "7"+ str(int(random_seed[1:]) + 1)
        random.seed(seed[1])
        if original_seed[0] != "":
            board, swap_rules, seed = import_board(seed)
        else:
            board, swap_rules, seed = generate_board(settings["Spawn Rates"], 8, settings["Difficulty"], seed)
            original_seed = ["", seed[1]]

    elif settings["Create"]:
        if is_create_seeded: # Is it using a set board
            if using_random_seed: # Is it using a set rng generator
                seed[1] = random_seed[1:]
                random_seed = "7"+ str(int(random_seed[1:]) + 1)
            
            random.seed(seed[1])
            board, swap_rules, seed = import_board(seed)
        else:
            original_seed = ["", random_seed[1:]]
            seed = copy.deepcopy(original_seed)
            random_seed = "7"+ str(int(random_seed[1:]) + 1)
            random.seed(seed[1])
            board, swap_rules, seed = generate_board(settings["Spawn Rates"], 8, settings["Difficulty"], seed)

    elif settings["Practice"]:

        original_seed = ["", random_seed[1:]]
        seed = copy.deepcopy(original_seed)
        random_seed = "7"+ str(int(random_seed[1:]) + 1)
        random.seed(seed[1])

        spawn_rates, furnace_interval, difficulty = get_practice_settings(settings["Practice Num"])
        board, swap_rules, seed = get_practice_board(settings["Practice Num"], spawn_rates, difficulty, seed)

    swapping_board = [copy.deepcopy(board), []]
    session_paused = [False, 0, 0]
    whites_burnt = 0
    burns_in_chamber = 0
    warning_played = False
    cc_chain = 0
    score = 0
    burn_waiting = False
    start_time = pygame.time.get_ticks()
    time_of_last_burn = 0
    mouse_new_co = []
    mouse_old_co = []
    mouse_last_location = [False, [-100, -100], [-1, -1]]
    location_selected = [False, [-100, -100], [-1, -1]]
    burn_column = [False, False, pygame.time.get_ticks() - start_time, []]
    time_passed = pygame.time.get_ticks() - start_time - session_paused[2]
    columns_up = [0, {-1 : 0,
                    0 : 0,
                    1 : 0,
                    2 : 0,
                    3 : 0,
                    4 : 0,}]

    return session_over, board, swap_rules, seed, swapping_board, session_paused, whites_burnt, burns_in_chamber, warning_played, cc_chain, score, burn_waiting, start_time, time_of_last_burn, mouse_new_co, mouse_old_co, mouse_last_location, location_selected, burn_column, time_passed, columns_up, random_seed, furnace_interval, spawn_rates, difficulty, original_seed


def get_practice_settings(practice_num):
    practice_settings = {(0, 0) : [15000000, 50, [0, 1, 0, 0, 2]],
                         (0, 1): [15000000, 50, [0, 2, 0, 0, 1]],
                         (0, 2) : [15000000, 50, [1, 0, 0, 0, 2]],
                         (0, 3) : [15000000, 50, [2, 0, 0, 0, 1]],
                         (0, 4) : [15000000, 50, [2, 1, 0, 0, 0]],
                         (0, 5) : [15000000, 50, [1, 2, 0, 0, 0]],
                         
                         (1, 6) : [15000000, 50, [10, 10, 0, 0, 3]],

                         (2, 9) : [15000000, 50, [10, 10, 0, 0, 3]],

                         (3, 5) : [45000, 50, [10, 10, 0, 0, 3]],
                         (3, 6) : [30000, 50, [10, 10, 0, 0, 7]],

                         (4, 5) : [15000, 50, [10, 10, 0, 0, 10]],

                         (5, 4) : [15000, 50, [10, 10, 0, 1, 10]],

                         (6, 5) : [15000000, 50, [10, 10, 0, 0, 10]],
                         (6, 6) : [15000, 50, [10, 10, 0, 0, 10]],
                         (6, 7) : [15000, 50, [10, 10, 0, 1, 10]],

                         (7, 0) : [15000, 50, [10, 10, 0, 0, 10]],
                         (7, 1) : [15000, 50, [10, 10, 0, 1, 10]],

                         (8, 0) : [15000, 50, [10, 10, 0, 0, 10]],
                         (8, 1) : [15000, 50, [10, 10, 0, 1, 10]],
                         
                         (9, 0) : [15000, 75, [10, 10, 0, 1, 10]],
                         (9, 1) : [15000, 50, [10, 10, 0, 3, 10]],
                         (9, 2) : [15000, 75, [10, 10, 0, 3, 10]],
                         (9, 17) : [15000, 50, [10, 10, 0, 1, 10]],
                         (9, 18) : [15000, 50, [10, 10, 0, 1, 10]],
                         (9, 19) : [15000, 50, [10, 10, 0, 1, 10]],
                         (9, 20) : [15000, 50, [10, 10, 0, 1, 10]],
                         (9, 21) : [15000, 50, [10, 10, 0, 1, 10]]
                         
                         }
    timed_practice = []
    
    if tuple(practice_num) in practice_settings:
        furnace_interval, difficulty, spawn_rates = practice_settings[tuple(practice_num)]
    elif practice_num in timed_practice:
        furnace_interval, difficulty, spawn_rates = 15000, 50, [10, 10, 0, 1, 10]
    else:
        furnace_interval, difficulty, spawn_rates = 15000000, 50, [10, 10, 0, 1, 10]

    return spawn_rates, furnace_interval, difficulty


def alternate_8_and_9(number):
    if number == 8: return 9
    else: return 8

def create_junk_board(junk, spawn_rates, furnace_height, seed):
    junk_left = junk
    board = [[4 for _ in range(9)] for _ in range(10)] # All white starting board
    
    for a in list(range(9-furnace_height, 10, 2)):  # if furnace_height 8 then odd columns have piece removed, if 9 then even columns:
        board[a][8] = -1    # Remove extra pieces from short columns
    

    if junk_left > 0:       # I want atleast one good black and brown
        board[0][0] = 0
        junk_left -= 1
    if junk_left > 0:
        board[0][alternate_8_and_9(furnace_height)-1] = 1
        junk_left -= 1
    
    

    junk_height = furnace_height
    column = 9

    while junk_left >= junk_height:  # Full columns of black junk on the right
        for row in list(range(0, junk_height)):
            board[column][row] = 0
        column -= 1
        junk_left -= junk_height
        junk_height = alternate_8_and_9(junk_height)
        
    if junk_left == 0 and column < 9: # If it added a full column and ran out of junk I want a bottom right brown.
        board[column+1][alternate_8_and_9(junk_height)-1] = 1
    else:
        for row in list(range(0, junk_left-1)): # Else fill the column with black leaving one junk for bottom right
            board[column][row] = 0
        board[column][junk_height-1] = 1

    # Replace some whites with spices
    total_odds = 0
    for a in spawn_rates:
        total_odds += a
    whites_and_spice_odds = [spawn_rates[3], total_odds-spawn_rates[3]]  # Odds of spice, odds of white
    for column in list(range(0, 10)):
        for row in list(range(0, 9)):
            if board[column][row] == 4:
                board[column][row] = random.choices(population=[3, 4], weights=whites_and_spice_odds, k=1)[0]
    
    swap_rules = calc_swaps(board, furnace_height)
    return board, swap_rules, seed

def create_trap_board(junk, spawn_rates, furnace_height, seed):
    board, swap_rules, seed = create_junk_board(junk-9, spawn_rates, furnace_height, seed)
    trap_at_top = random.choice([False, True])
    board[0] = generate_column([1, 1, 0, 0, 0], 50, seed)[0]
    board[0][8] = -1
    if trap_at_top:
        board[0][0] = 3
        board[1][0] = 0
        board[2][0] = 3
        board[1][1] = 0
        board[1][8] = 1
    else:
        board[0][7] = 3
        board[1][8] = 0
        board[2][7] = 3
        board[1][0] = 0
        board[1][7] = 1

    swap_rules = calc_swaps(board, 9)

    return board, swap_rules, seed



def get_practice_board(practice_num, spawn_rates, difficulty, seed):
    furnace_height = 8

    requires_generate_board = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [1, 6], [2, 9], [3, 5], [3, 6], [4, 5], [5, 4]]
    requires_junk_board = [[7, 0], [7, 1], [8, 0], [8, 1], [9, 0], [9, 1], [9, 2]]
    junk_amounts = [36, 36, 19, 19, 19 ,19, 19]
    spice_trapped_boards = [[9, 17], [9, 18], [9, 19], [9, 20], [9, 21]]
    spice_trapped_junks = [30, 27, 23, 18, 13]
    
    requires_seed = []
    set_seeds = {(1, 0) : [84444111144444444444444441144444444444444441444444444444444414444444444444444044444444],
                 (1, 1) : [84444111144444444444444441144444444444444444444444444444444044444444044444444044444444, 81444114441444414441444444441444444444441444404444444404404444404404444444404444444444, 84144444414414444444444444404044444404444401400444044440444404444440444444444400000444],
                 (1, 2) : [84000044444444444400444444444444444044444444444444440444444444444444414444444444444444],
                 (1, 3) : [84000044444444444440444444404444444444444444444444444144444441444444414444444444444444, 84444444444444444044444440444444404444444444444444144444441444444414444444444444444444, 84444444044444440444404404444444444444144444441444144414444444444441444144414444444444],
                 (1, 4) : [81444444441444444401444444401444444001444444001444440000000000000000000000000000000000, 84444444404444444044444440144444401444444010444440100000011001100100000100000000000000],
                 (1, 5) : [84444444444444444444444444044444440444444400444444000000000000001000000000000000000000, 84444444444444444414444444414444444114444444114444440000000000000000000000000000000000],
                 
                 (2, 0) : [80344444441344444441344444441344444441344444444344444444444444444444444444444444444444],
                 (2, 1) : [84444444440444444431444444431444444431444444434444444434444444444444444444444444444444],
                 (2, 2) : [84444444434444441344444403444444034444440344444403444444444444444444444444444444444444],
                 (2, 3) : [84444443144444430444444304444443044444430444444344444444444444444444444444444444444444],
                 (2, 4) : [84444444441444444441444444441444444441444444440444444444444444444444444444444444444444],
                 (2, 5) : [84444444444444440444444404444444044444440444444414444444444444444444444444444444444444],
                 (2, 6) : [80144444010144440140344431440444414444444444444444444444444444444444444444444444444444],
                 (2, 7) : [84144444041144440001444440144444444444444444444444444444444444444444444444444444444444, 84144444044144440401144400144144044444444444444444444444444444444444444444444444444444, 81144444001144440004144404144444444444444444444444444444444444444444444444444444444444, 80114440014114400444144404444444444444444444444444444444444444444444444444444444444444, 80414440414114400444444444414444440444444444444444444444444444444444444444444444444444, 84444444441444444001444440141444404144444440444444444444444444444444444444444444444444, 84044444144144440444144404444444444144444440444444444444444444444444444444444444444444, 80144444014144440411144400044444444444444444444444444444444444444444444444444444444444, 80144444010144440141144400444144044444041444444444444444444444444444444444444444444444, 84444444444444444440144401441444404441444044444444444444444444444444444444444444444444, 84444444444444444440144401441344304441444044444444444444444444444444444444444444444444, 84444444444444444440144410441444414431444134444444444444444444444444444444444444444444, 84444444444104410444144404444444444441444044444444444444444444444444444444444444444444, 84444444444414444444414444444414444441404444414444444444444444444444444444444444444444, 84444444444444404444444044444440444444414044444444044444444444444444444444444444444444],
                 (2, 8) : [81044444101444444044444444444444444444444444444444444444444444444444400000000100000000],

                 (3, 0) : [84444414444444404444444444444444444444444444444444444444444444444444444444444400004400],
                 (3, 1) : [84444444444444444444444444444444444144444444044444444444444444444444444444444444444444],
                 (3, 2) : [844444440444444414444444444444444444444444444444444444444444444444444444444444044000002131, 84144444444044444444444444444444444444444444444444444444444444444444444444444400000440],
                 (3, 3) : [84144444041044441044444444440444414444444444404444144444444444044441444444444400000011, 81444444400444444144444444404444441444444444044444414444444440444444144444444400000001],
                 (3, 4) : [84114014411010040000440140114401404014014001104014441140141141441440010404041400000000, 84114011411014011000140140111141404011410001114141441141101141440100010444041400000000, 84114014411040014000440140114401404014001401104011441144014141440144010440441400000000],
                 
                 (4, 0) : [81444444144444441144444441444444444444444444444444444444444444444444400000001100000001],
                 (4, 1) : [80044444400044444444444444444444444444444444444444444444444444444444400000001100000011],
                 (4, 2) : [84144044141144444141444444444444444444444444444444444444444444444444444000000100000000, 80044144004444444044444440444444444444444444444444444444444444444444400000000100000000, 80044144044444440444444400444444440444444444444444444444444444444444400000000000000000],
                 (4, 3) : [84410144444444444444444444444444444444444444444444444444444444444444444444444404400001],
                 (4, 4) : [84444401044444444444444444444444444444444444444444444444444444444444444444444400000441],
                 
                 (5, 0) : [94444444414444444034444443444444444444444444443344444444444400000001100000001000000000],
                 (5, 1) : [90444444130444441330444413434444434444444444444444444444444400000000100000000000000000],
                 (5, 2) : [904444441104444410444444444344444344444444444444444444444444000000001000000000000000003],
                 (5, 3) : [80444444444444444444444441444444440444444440444443444444444444444443344444400000000000, 84444444444444444444444441444444440444444440444444444444444444444444444444444444444444, 84444444444444444444444414444444404444444404444444404444444404444444444444444444444444,84444444444044444441444444414444444144444444444444444444444444444444444444444444444444, 84444444441444444041444440440444414444444444444444444444444444444444444444444444444444],
                 
                 (6, 0) : [84014440144444444444444444444444444444444444444444441444444404444444444444444444444444],
                 (6, 1) : [80014000114444444144444444134444443144444443444444344444444304444444344444444444444444],
                 (6, 2) : [80110101110101000010110011110001000010041444000044440004444444444444444444444444444444],
                 (6, 3) : [80004111110444111144444441444444444444444444444444442444444444444444444444444444444444],
                 (6, 4) : [80444414444444444444444444444444444444444444444444442444444444444444444444444444444444],
                 (6, 5) : [84444444444444444444444444444444444444444444444444444444444444444444444444444444444444],
                 (6, 6) : [84444444444444444444444444444444444444444444444444444444444444444444444444444444444444],
                 (6, 7) : [84444444444444444444444444444444444444444444444444444444444444444444444444444444444444],

                 (9, 3) : [84444444444444444444444444444444444444444444444444444041424242424041441404140444444444],
                 (9, 4) : [80444244414444444444444444444444444444444444444444444444444444444444444444444444444444],
                 (9, 5) : [80444244414444444444444444444444444444444444444444444444444444444444444444444444444444],
                 (9, 6) : [84444424434444444344444143444440434444444344444443444444434444444344444443444444434444],
                 (9, 7) : [83442444443444444443444144443440444443444444443444444443444444443444444443444444443444],
                 (9, 8) : [82001444444444444444444444444444444344444444444444444444444444444444444444444444444444],
                 (9, 9) : [82101444444444444444444444444444444344444444444444444444444444444444444444444444444444],
                 (9, 10) : [84444400124444444444444444444444444444444443444444444444444444444444444444444444444444],
                 (9, 11) : [84444401124444444444444444444444444444444443444444444444444444444444444444444444444444],
                 (9, 12) : [80442244414444444444444444444444444444444444444444444444444444444444444444444444444444],
                 (9, 13) : [80444244414444444444442444444444444444444444444444444444444444444444444444444444444444],
                 (9, 14) : [80444244414444444444442444444444444444444444444444444444444444444444444444444444444444],
                 (9, 15) : [84444241444042444444444444444444444444444444444444444444444444444444444444444444444444, 84444241444044244444444444444444444444444444444444444444444444444444444444444444444444, 80424241444444444444444444444444444444444444444444444444444444444444444444444444444444, 80024421114444444404444444444444444444444444444444444444444444444444444444444444444444, 82404441142444444444444444444444444444444444444444444444444444444444444444444444444444],
                 (9, 16) : [84440241414444444444444444444444444443334444444444444444444444444444444444444444444444, 84440241444444444444444444444444444444444444444444444433334444444444444444444444444444, 92011444444444444444444444444444444344444441444444443444444444444444444444444444444444, 92001444444444444444444444444444444344444441444444443444444444444444444444444444444444, 94444001244444444444444444444444444444444434444444414444444344444444444444444444444444, 94444010244444444444444444444444444444444434444444414444444344444444444444444444444444]
                 }
    
    if practice_num in requires_generate_board:
        return generate_board(spawn_rates, furnace_height, difficulty, seed)
    if practice_num in requires_junk_board:
        junk = junk_amounts[requires_junk_board.index(practice_num)]
        return create_junk_board(junk, spawn_rates, furnace_height, seed)
    if tuple(practice_num) in set_seeds:
        seeds = set_seeds[tuple(practice_num)]
        seed[0] = str(random.choice(seeds))
        return import_board(seed)
    if practice_num in spice_trapped_boards:
        junk = spice_trapped_junks[spice_trapped_boards.index(practice_num)]
        return create_trap_board(junk, spawn_rates, 9, seed)


    

random_seed = generate_seed(False) # I need a random number selected before the user sets the seed so that they can escape the loop of non randomness if desired.

# Main Loop
while not crashed:
    game_display.fill(black)
    
    background_two(0, 0)
    # print(F"{board = }")
    time_passed = pygame.time.get_ticks() - start_time - session_paused[2]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            '''Incase I want to add keyboard controls later'''
            action_queued[0] = event.button
            action_queued[1] = pygame.mouse.get_pos()
            mouse_pos = pygame.mouse.get_pos()
            if 740 <= mouse_pos[0] <= 800 and 540 <= mouse_pos[1] <= 600: # Change volume level
                if settings["Volume"] == 3:
                    settings["Volume"] = 0
                else:
                    settings["Volume"] += 1
                sound_volumes(settings["Volume"] / 6)
            if 585 <= mouse_pos[0] <= 605 and 18 <= mouse_pos[1] <= 38: # Copy board
                play_sound("options_change")
                get_create_seed(board)

            if settings["Practice"]:
                if 600 < mouse_pos[0] < 628 and 90 < mouse_pos[1] < 114: # Change difficulty of Practice
                    if (event.button == 1 or event.button == 4) and settings["Practice Num"][0] < 9:
                        settings["Practice Num"][0] += 1
                        settings["Practice Num"][1] = 0
                    elif (event.button == 3 or event.button == 5) and settings["Practice Num"][0] > 0:
                        settings["Practice Num"][0] -= 1
                        settings["Practice Num"][1] = 0
                if 630 < mouse_pos[0] < 658 and 90 < mouse_pos[1] < 114: # Change difficulty of Practice
                    if (event.button == 1 or event.button == 4) and settings["Practice Num"][1] < max(practice_available[settings["Practice Num"][0]]):
                        settings["Practice Num"][1] += 1
                    elif (event.button == 3 or event.button == 5) and settings["Practice Num"][1] > 0:
                        settings["Practice Num"][1] -= 1
                
            if board_active and settings["Create"]:
                if 20 < mouse_pos[0] < 245 and 90 < mouse_pos[1] < 130: 
                    if event.button == 1: # Does nothing useful, remnant of old code
                        create_piece = (mouse_pos[0] - 20) // 45
                    elif event.button == 2: # Change the entire board to the piece when middle clicked
                        furnace_height = board_length(board)
                        piece_code = ((mouse_pos[0] - 20) // 45)
                        if piece_code == 2:
                            piece_code = 4
                        elif piece_code == 4:
                            piece_code = 2
                        board = [[piece_code for _ in range(9)] for _ in range(10)]
                        for d in list(range((furnace_height + 1) % 2, 10, 2)):
                            board[d][8] = -1
                        swapping_board[0] = copy.deepcopy(board)
                        swap_rules = calc_swaps(board, board_length(board))

                elif 585 < mouse_pos[0] < 600 and 68 < mouse_pos[1] < 83: # Copies a seed in Create mode
                    play_sound("options_change")
                    get_create_seed(board)

                elif 605 < mouse_pos[0] < 620 and 68 < mouse_pos[1] < 83: # Pastes a seed in Create mode
                    play_sound("options_change")
                    original_seed = is_paste_legal(pyperclip.paste(), seed)
                    if original_seed[1] == "":
                        using_random_seed = True
                    else:
                        using_random_seed = False
                    # if original_seed[1] != "":
                    is_create_seeded = True
                    if board_active:
                        session_over, board, swap_rules, seed, swapping_board, session_paused, whites_burnt, burns_in_chamber, warning_played, cc_chain, score, burn_waiting, start_time, time_of_last_burn, mouse_new_co, mouse_old_co, mouse_last_location, location_selected, burn_column, time_passed, columns_up, random_seed, settings["Furnace Interval"], settings["Spawn Rates"], settings["Difficulty"], original_seed = start_procedure(settings, original_seed, is_create_seeded, random_seed, using_random_seed, settings["Furnace Interval"], settings["Spawn Rates"], settings["Difficulty"] )
                
                elif 625 < mouse_pos[0] < 640 and 68 < mouse_pos[1] < 83: # Generates a seed in Create mode
                    play_sound("options_change")
                    is_create_seeded = False
                    session_over, board, swap_rules, seed, swapping_board, session_paused, whites_burnt, burns_in_chamber, warning_played, cc_chain, score, burn_waiting, start_time, time_of_last_burn, mouse_new_co, mouse_old_co, mouse_last_location, location_selected, burn_column, time_passed, columns_up, random_seed, settings["Furnace Interval"], settings["Spawn Rates"], settings["Difficulty"], original_seed  = start_procedure(settings, original_seed, is_create_seeded, random_seed, using_random_seed, settings["Furnace Interval"], settings["Spawn Rates"], settings["Difficulty"] )
                    get_create_seed(board)

            if 455 < mouse_pos[0] < 630 and 440 < mouse_pos[1] < 465:
                # if settings["Standard"] or settings["Seeded"] or settings["Create"]: # I no longer need this now that practice does something
                board_active = not board_active
                if board_active:
                    session_over, board, swap_rules, seed, swapping_board, session_paused, whites_burnt, burns_in_chamber, warning_played, cc_chain, score, burn_waiting, start_time, time_of_last_burn, mouse_new_co, mouse_old_co, mouse_last_location, location_selected, burn_column, time_passed, columns_up, random_seed, settings["Furnace Interval"], settings["Spawn Rates"], settings["Difficulty"], original_seed  = start_procedure(settings, original_seed, is_create_seeded, random_seed, using_random_seed, settings["Furnace Interval"], settings["Spawn Rates"], settings["Difficulty"] )
                else:
                    session_paused[0] = False

            if board_active and not session_paused[0]:
                if not burn_column[0]:

                    if event.button == 1:
                    
                        if 25 < mouse_pos[0] < 425 and 157 < mouse_pos[1] < 517: # A click has been made on the board
                            new_location_selected = cursor_location(board, mouse_pos[0], mouse_pos[1], location_selected)
                            if board[new_location_selected[2][0]][new_location_selected[2][1]] != 3:
                                    location_selected = new_location_selected
                                    valid_swaps = get_valid_swaps(location_selected, board, swap_rules)
                                        
                    elif event.button == 3: # Player wants to burn a column
                        if not burn_column[0]:
                            burn_waiting = True

                    elif settings["Create"] and 3 < event.button < 6:
                        if 25 < mouse_pos[0] < 425 and 157 < mouse_pos[1] < 517: # Change piece using scroll wheel in create mode
                            board, swap_rules, swapping_board = modify_piece(mouse_pos, board, swapping_board, "Scroll", event.button, swap_rules)
                        
            if (not board_active and not session_paused[0]) or settings["Create"]:
                if 610 < mouse_pos[0] < 630 and 180 < mouse_pos[1] < 200: # Change black spawn rate
                    settings["Spawn Rates"][0] = adjust_settings(settings["Spawn Rates"][0], event.button, spawn_rates_default[0], 0, 999, 1)
                elif 635 < mouse_pos[0] < 655 and 180 < mouse_pos[1] < 200: # Change brown spawn rate
                    settings["Spawn Rates"][1] = adjust_settings(settings["Spawn Rates"][1], event.button, spawn_rates_default[1], 0, 999, 1)
                elif 660 < mouse_pos[0] < 680 and 180 < mouse_pos[1] < 200: # Change white spawn rate
                    settings["Spawn Rates"][4] = adjust_settings(settings["Spawn Rates"][4], event.button, spawn_rates_default[4], 0, 999, 1)
                elif 685 < mouse_pos[0] < 705 and 180 < mouse_pos[1] < 200: # Change spice spawn rate
                    settings["Spawn Rates"][3] = adjust_settings(settings["Spawn Rates"][3], event.button, spawn_rates_default[3], 0, 999, 1)
                elif 710 < mouse_pos[0] < 730 and 180 < mouse_pos[1] < 200: # Change burnt spawn rate
                    settings["Spawn Rates"][2] = adjust_settings(settings["Spawn Rates"][2], event.button, spawn_rates_default[2], 0, 999, 1)
                elif 600 < mouse_pos[0] < 660 and 155 < mouse_pos[1] < 175:  # Change difficulty
                    settings["Difficulty"] = adjust_settings(settings["Difficulty"], event.button, 50, 0, 100, 1)
                elif 600 < mouse_pos[0] < 720 and 130 < mouse_pos[1] < 150: # Change furnace interval
                    settings["Furnace Interval"] = adjust_settings(settings["Furnace Interval"], event.button, 15000, 1000, 120000, 500)
                elif 565 < mouse_pos[0] < 580 and 18 < mouse_pos[1] < 35: # Standard Mode selected
                    settings = adjust_settings_mode(settings, "Standard")
                    settings["Furnace Interval"] = 15000
                    board_active = False
                    burn_duration = 1000
                elif 565 < mouse_pos[0] < 580 and 43 < mouse_pos[1] < 60: # Seeded Mode selected
                    settings = adjust_settings_mode(settings, "Seeded")
                    settings["Furnace Interval"] = 15000
                    board_active = False
                    burn_duration = 1000
                elif 565 < mouse_pos[0] < 580 and 68 < mouse_pos[1] < 85: # Create Mode selected
                    settings = adjust_settings_mode(settings, "Create")
                    is_create_seeded = False
                    settings["Furnace Interval"] = 15000000
                    burn_duration = 100
                elif 565 < mouse_pos[0] < 580 and 93 < mouse_pos[1] < 110: # Practice Mode selected
                    settings = adjust_settings_mode(settings, "Practice")
                    board_active = False
                    burn_duration = 1000
                elif settings["Seeded"]:
                    if 588 < mouse_pos[0] < 603 and 45 < mouse_pos[1] < 60: # Copy seed in Seeded mode
                        play_sound("options_change")
                        copy_seed = original_seed[0]
                        if original_seed[1] != "":
                            copy_seed += "7" + original_seed[1]
                        pyperclip.copy(copy_seed)
                        pass
                    if 608 < mouse_pos[0] < 623 and 45 < mouse_pos[1] < 60: # Paste seed in Seeded mode
                        play_sound("options_change")
                        original_seed = is_paste_legal(pyperclip.paste(), seed)
                        if original_seed[1] == "":
                            using_random_seed = True
                        else:
                            using_random_seed = False
                    if 628 < mouse_pos[0] < 643 and 45 < mouse_pos[1] < 60: # Generate and copy a seed in Seeded mode
                        play_sound("options_change")
                        original_seed = generate_seed(True)
                        original_seed = convert_seed(original_seed)
                        using_random_seed = False
                    


                if 455 < mouse_pos[0] < 800 and 180 < mouse_pos[1] < 200 and event.button == 2: # Middle click sets spawn to default
                    if settings["Spawn Rates"] == spawn_rates_default:
                        settings["Spawn Rates"] = [0, 0, 0, 0, 1]
                    else:
                        settings["Spawn Rates"] = copy.deepcopy(spawn_rates_default)
                elif 455 < mouse_pos[0] < 800 and 155 < mouse_pos[1] < 175 and event.button == 2: # Middle click sets difficulty to default
                    settings["Difficulty"] = 50
                elif 455 < mouse_pos[0] < 800 and 130 < mouse_pos[1] < 150 and event.button == 2: # Middle click switches furnace interval between defaults
                    if settings["Furnace Interval"] == 15000:
                        settings["Furnace Interval"] = 15000000
                    else:
                        settings["Furnace Interval"] = 15000

        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:

            if settings["Create"]:
                mouse_pos = pygame.mouse.get_pos()
                if 48 < event.key < 54:
                    if event.type == pygame.KEYDOWN:
                        paint_with = [True, event.key - 49]
                    elif event.type == pygame.KEYUP and paint_with[1] == event.key - 49:
                        paint_with = [False, -1]

                    # create_piece = event.key - 49
                    # if 25 < mouse_pos[0] < 425 and 157 < mouse_pos[1] < 517:
                    #     board, swap_rules, swapping_board = modify_piece(mouse_pos, board, swapping_board, "Number", event.key - 49, swap_rules)
            
            if board_active and event.type == pygame.KEYDOWN:
                if event.key == 27:
                    if session_paused[0]:
                        session_paused[0] = False
                        session_paused[2] += time_passed - session_paused[1]
                        time_passed = time_passed - session_paused[2]
                    else:
                        session_paused = [True, time_passed, session_paused[2]]
                

        if board_active:                
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    location_selected[0] = False
                    if swapping_board[1] != []:
                        for x in list(range(len(swapping_board[1]))):
                            swapping_board[1][x][5] = False

    if board_active and not session_paused[0]:
        if burn_column[0]:
            display_burn_column(board, burn_column, time_passed, burn_duration)
        swapping_board, moving_pieces = calculate_moving(board, swapping_board, burn_column, time_passed)
        display_board(board, swapping_board[0], burn_column, time_passed, burn_duration)
        display_moving_pieces(moving_pieces)
        display_swaps(board, swapping_board[0],  swap_rules, burn_column, time_passed, burn_duration)
        mouse_pos = pygame.mouse.get_pos()

        if 25 < mouse_pos[0] < 425 and 157 < mouse_pos[1] < 517:

            
            if paint_with[0] and settings["Create"]:
                board, swap_rules, swapping_board = modify_piece(mouse_pos, board, swapping_board, "Number", paint_with[1], swap_rules)
            coords_to_check = []
            mouse_new_location = cursor_location(board, mouse_pos[0], mouse_pos[1], mouse_last_location)

            if mouse_new_co != []:
                mouse_old_co = copy.deepcopy(mouse_new_co)
            mouse_new_co = [mouse_pos[0], mouse_pos[1]]
            if mouse_old_co != []:
                mouse_change = [mouse_new_co[0]-mouse_old_co[0], mouse_new_co[1]-mouse_old_co[1]]
                coords_to_check = find_skipped_coordinatees(mouse_change, mouse_old_co, board)
            

            if location_selected[0] and not burn_column[0] and coords_to_check != [] and not burn_waiting:
                for potential_swap in coords_to_check:
                    mouse_last_location[1] = pixel_value_of_piece(potential_swap, board)
                    swap_with = swap_check(potential_swap, valid_swaps, location_selected, board)
                    if not swap_with:
                        pass
                    else:
                        mouse_last_location[1] = pixel_value_of_piece(swap_with, board)
                        board, swap_rules, location_selected, swapping_board = perform_swap(board, swap_rules, swap_with, location_selected, time_passed, swapping_board)
                        valid_swaps = get_valid_swaps(location_selected, board, swap_rules)
                    
            if location_selected[0]:
                display_cursor(mouse_last_location[1][0], mouse_last_location[1][1], burn_column, time_passed, burn_duration, swapping_board)
            else:
                mouse_last_location = copy.deepcopy(mouse_new_location)
                display_cursor(mouse_last_location[1][0], mouse_last_location[1][1], burn_column, time_passed, burn_duration, swapping_board)
        else:
            mouse_new_co = []
        if not burn_column[0]:
            if not warning_played:
                warning_played = check_for_burn_warning(time_passed, time_of_last_burn, settings["Furnace Interval"])
            if check_for_burn(time_passed, time_of_last_burn, settings["Furnace Interval"]):
                burn_waiting = True

            if location_selected[0]:
                display_selected(location_selected[1][0], location_selected[1][1], burn_column, time_passed, burn_duration, swapping_board)
        
        if burn_waiting and swapping_board[1] == []: # Initiates a burn if one is ready and no pieces are swapping.
            board, location_selected, valid_swaps, swap_rules, burn_column, burns_in_chamber, whites_burnt, seed = activate_furnace(board, location_selected, time_passed, burns_in_chamber, whites_burnt, settings, seed)
            swapping_board = [copy.deepcopy(board), []]
            score, cc_chain, columns_up, session_over = score_column(burn_column, cc_chain, score, columns_up)
            burn_waiting = False
            
        elif burn_column[0]:
            if time_passed > burn_column[2] + burn_duration: # If burn finished reset things
                burn_column[0] = False
                time_of_last_burn = time_passed - burn_duration
                warning_played = False
                if session_over and not settings["Create"]:
                    board_active = False
        
    background(0, 0)
    if board_active:
        if session_paused[0]:
            display_furnace(time_passed, burn_column[2]-session_paused[1]+time_passed, settings["Furnace Interval"], burn_column[0])
        else:
            display_furnace(time_passed, burn_column[2], settings["Furnace Interval"], burn_column[0])
    display_vial(score, columns_up)
    display_texts(settings, score, cc_chain, time_passed, columns_up, board_active, session_paused, practice_names, practice_group_names)
    display_checkboxes(settings)
    volume_display(settings["Volume"])
    if settings["Create"]:
        display_create(create_piece)

    # draw_red_line(red_line_pixels)

    pygame.display.update()
    clock.tick(120)

pygame.quit()
