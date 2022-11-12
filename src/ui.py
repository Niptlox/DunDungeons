from src.Button import Button, TextButton, DEF_COLOR_SCHEME_BUT
from src.ClassUI import *

# (bg_color, color_text)
from src.ElementsUI import TextLabel

button_color_schema = DEF_COLOR_SCHEME_BUT


class RestartUI(SurfaceUI):
    bgcolor = (63, 63, 70, 200)

    def __init__(self, game, running=False):
        from src.Game import WSIZE
        self.running = running
        self.game = game
        size = WSIZE
        super(RestartUI, self).__init__(((0, 0), size))
        self.rect.center = (WSIZE[0] // 2, WSIZE[1] // 2)
        self.convert_alpha()
        self.group = GroupUI([])

        button = TextButton(lambda _: self.game.restart(), (0, 0, 200, 30), "restart", screenXY=self.rect.topleft,
                            color_schema=button_color_schema)
        button.setCenter((self.rect.centerx, self.rect.centery + 40))
        self.group.add(button)
        label = TextLabel((0, 0, 400, 150), "YOU DIED", pg.font.SysFont("Roboto", 95), "#DC2626")
        label.rect.center = (self.rect.centerx, self.rect.centery - 100)
        self.group.add(label)
        label = self.level = TextLabel((0, 0, 400, 150), "LEVEL 0", pg.font.SysFont("Roboto", 35), "#FDE047")
        label.rect.center = (self.rect.centerx, self.rect.centery - 55)
        self.group.add(label)

        label = self.record = TextLabel((0, 0, 180, 30), "record 0", pg.font.SysFont("Roboto", 25), "#FDE047",
                                        text_align="left")
        label.rect.bottomleft = 8, self.rect.bottom
        self.group.add(label)

    def set_level(self, level, record):
        self.level.set_text(f"LEVEL: {level}")
        self.record.set_text(f"HIGH LEVEL: {record}")

    def pg_event(self, event: pg.event.Event):
        if self.running:
            self.group.pg_event(event)

    def draw(self, surface):
        self.fill(self.bgcolor)
        self.group.draw(self)
        surface.blit(self, self.rect)
