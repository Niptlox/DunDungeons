import math
from typing import Union, NewType, Any

import pygame as pg

from src.PhysicEngine import check_collision_circle_circle

EntityObj = NewType("Entity", Any)

STICK_WEAPON_IDX = 0
KNIFE_WEAPON_IDX = 1
SWORD_WEAPON_IDX = 2
CROSSBOW_WEAPON_IDX = 3

weapon_data = {
    STICK_WEAPON_IDX: {"damage": 10, "cost": 5}
}


class WeaponStick:
    index = STICK_WEAPON_IDX

    def __init__(self, owner: EntityObj, position: Union[tuple, pg.Vector2] = (0, 0)):
        self.owner = owner
        self.position = pg.Vector2(position)
        self.damage = self.get_value_from_data("damage")
        self.punching = False
        self.punch_anim_angle_speed = math.pi / 15
        self.punch_anim_angle = 0
        self.punch_anim_ticks = 5
        self.punch_anim_timer = 0

    def get_value_from_data(self, name_value, default=0):
        return weapon_data[self.index].get(name_value, default)

    def start_punch(self):
        if not self.punching:
            self.punching = True
            self.punch_anim_timer = self.punch_anim_ticks * 2

    def punch(self):
        r = self.owner.radius
        pos = self.owner.position.x + math.sin(self.owner.rotation) * r, \
              self.owner.position.y + math.cos(self.owner.rotation) * r
        for entity in self.owner.game_map.get_entities():
            if check_collision_circle_circle(pos, r, entity.position, entity.radius):
                print(entity, self.owner, self.owner.game_map.entities)
                if entity is not self.owner:
                    entity.get_damage(self.damage)
                    pass

    def anim_update(self):
        if self.punching:
            self.punch_anim_timer -= 1
            if self.punch_anim_timer == 0:
                self.punch_anim_angle = 0
            elif self.punch_anim_timer > 0:
                if self.punch_anim_timer == self.punch_anim_ticks:
                    self.punch()
                elif self.punch_anim_timer > self.punch_anim_ticks:
                    self.punch_anim_angle += self.punch_anim_angle_speed
                else:
                    self.punch_anim_angle -= self.punch_anim_angle_speed
            elif self.punch_anim_timer < -5:
                self.punching = False

    def draw(self, surface, owner_position, hand_dist=0, hand_offset_angle=0):
        self.anim_update()
        ox, oy = owner_position
        if self.owner:
            rotation = self.owner.rotation
            dist1 = hand_dist + 1
            dist2 = hand_dist + 4

            pos_h1 = ox + math.sin(rotation + hand_offset_angle + self.punch_anim_angle) * dist1, \
                     oy + math.cos(rotation + hand_offset_angle + self.punch_anim_angle) * dist1
            # pg.draw.circle(self.display, entity.color_hand, pos_h1, r // 2)
            pos_h2 = ox + math.sin(rotation - hand_offset_angle + self.punch_anim_angle) * dist2, \
                     oy + math.cos(rotation - hand_offset_angle + self.punch_anim_angle) * dist2
            vec = pg.Vector2(pos_h2) - pg.Vector2(pos_h1)
            vec *= 2
            pos2 = pg.Vector2(pos_h1) + vec
            pg.draw.line(surface, "brown", pos_h1, pos2, 3)
        else:
            rotation = 0
            r = 0


weapon_cls = {
    STICK_WEAPON_IDX: WeaponStick
}
