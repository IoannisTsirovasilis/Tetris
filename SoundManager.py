import pygame as pg


class SoundManager:
    def __init__(self, sounds_path):
        self.mixer = pg.mixer
        self.mixer.pre_init(44100, -16, 2, 2048)
        self.mixer.init()
        self.sounds_path = sounds_path

    def play_sound(self, sound, channel, loop):
        self.mixer.Channel(channel).play(self.mixer.Sound(self.sounds_path + sound), loop)
