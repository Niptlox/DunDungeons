import pygame as pg

from src.ClassUI import SurfaceUI

ACENTER = "center"
ALEFT = "left"


class TextLabel(SurfaceUI):
    def __init__(self, rect, text, font, color, bg_color=(0, 0, 0, 0), text_align=ACENTER):
        super(TextLabel, self).__init__(rect)
        self.convert_alpha()
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.font: pg.font.Font = font
        self.text_align = text_align
        self.render_text()

    def get_text_position(self, img):
        if self.text_align == ACENTER:
            w, h = img.get_size()
            x, y = (self.rect.w - w) // 2, (self.rect.h - h) // 2
        elif self.text_align == ALEFT:
            w, h = img.get_size()
            x, y = 0, (self.rect.h - h) // 2
        else:
            x, y = 0, 0
        return x, y

    def set_text(self, text):
        self.text = text
        self.render_text()

    def render_text(self):
        self.fill(self.bg_color)
        text = self.font.render(self.text, True, self.color)
        pos = self.get_text_position(text)
        self.blit(text, pos)





