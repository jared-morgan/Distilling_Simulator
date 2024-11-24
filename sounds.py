import pygame
import os
import sys
import sounddevice as sd

script_path = sys.argv[0]
script_dir = os.path.dirname(script_path)

pygame.init()

sounds = {"blecch" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "blecch.ogg")),
          "blecch2" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "blecch2.ogg")),
          "burn" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "burn.ogg")),
          "burn_warning" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "burn_warning.ogg")),
          "burnt" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "burnt.ogg")),
          "crystal_clear" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "crystal_clear.ogg")),
          "crystal_clear2" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "crystal_clear2.ogg")),
          "finished" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "finished.ogg")),
          "smooth" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "smooth.ogg")),
          "spicy" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "spicy.ogg")),
          "swap_down" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "swap_down.ogg")),
          "swap_up" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "swap_up.ogg")),
          "options_change" : pygame.mixer.Sound(os.path.join(script_dir, 'media', "options_change.ogg"))}

def check_audio_devices(): # If the user has no audo device it will crash if I try to play one. I should only check this once but this is a quick patch.
    try:
        devices = sd.query_devices()
        if devices:
            return True
        else:
            return False
    except Exception as e:
        return False

def play_sound(x):
    if check_audio_devices():
        pygame.mixer.Sound.play(sounds[x])

def sound_volumes(volume_in):
    for sound in sounds:
        pygame.mixer.Sound.set_volume(sounds[sound], volume_in)