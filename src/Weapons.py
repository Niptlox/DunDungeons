import math
from typing import Union, NewType, Any

import pygame as pg

from src.PhysicEngine import check_collision_circle_circle

EntityObj = NewType("Entity", Any)

HAND_WEAPON_IDX = 0
STICK_WEAPON_IDX = 65
KNIFE_WEAPON_IDX = 2
SWORD_WEAPON_IDX = 3
CROSSBOW_WEAPON_IDX = 4
METAL_STICK_WEAPON_IDX = 66
RED_STICK_WEAPON_IDX = 68

weapon_data = {
    HAND_WEAPON_IDX: {"damage": 5},
    STICK_WEAPON_IDX: {"damage": 8},
    METAL_STICK_WEAPON_IDX: {"damage": 15},
    RED_STICK_WEAPON_IDX: {"damage": 30},
}


def draw_hands(surface, entity, pos, hand_dist, hand_offset_angle, offset_angle=0):
    r = entity.size[0] // 4
    px, py = pos
    pos_h1 = px + math.sin(entity.rotation + hand_offset_angle + offset_angle) * hand_dist, \
             py + math.cos(entity.rotation + hand_offset_angle + offset_angle) * hand_dist
    pg.draw.circle(surface, entity.color_hand, pos_h1, r)
    pos_h2 = px + math.sin(entity.rotation - hand_offset_angle + offset_angle) * hand_dist, \
             py + math.cos(entity.rotation - hand_offset_angle + offset_angle) * hand_dist
    pg.draw.circle(surface, entity.color_hand, pos_h2, r)


class Weapon:
    index = HAND_WEAPON_IDX
    punch_anim_ticks = 5

    def __init__(self, owner: EntityObj, position: Union[tuple, pg.Vector2] = (0, 0)):
        self.owner = owner
        self.position = pg.Vector2(position)
        self.damage = self.get_value_from_data("damage")
        self.punching = False
        self.punch_anim_timer = 0
        self.punch_anim_angle = 0
        self.hand_dist_offset = [0, 0]

    def get_value_from_data(self, name_value, default=0):
        return weapon_data[self.index].get(name_value, default)

    def start_punch(self):
        if not self.punching:
            self.punching = True
            self.punch_anim_timer = self.punch_anim_ticks * 2

    def punch(self):
        r = self.owner.radius
        pos = self.owner.center.x + math.sin(self.owner.rotation) * r, \
              self.owner.center.y + math.cos(self.owner.rotation) * r
        for entity in self.owner.game_map.get_entities():
            if check_collision_circle_circle(pos, r, entity.center, entity.radius):
                # print(entity, self.owner, self.owner.game_map.entities)
                if entity is not self.owner:
                    entity.get_damage(self.damage, self.owner)
                    pass

    def anim_update(self):
        if self.punching:
            self.punch_anim_timer -= 1
            if self.punch_anim_timer < -5:
                self.punching = False
            elif self.punch_anim_timer == 0:
                self.punch_anim_angle = 0
            elif self.punch_anim_timer > 0:
                if self.punch_anim_timer == self.punch_anim_ticks:
                    self.punch()

    def draw_hands(self, surface, pos, hand_dist, hand_offset_angle):
        offset_angle = self.punch_anim_angle
        entity = self.owner
        r = entity.size[0] // 4
        px, py = pos
        pos_h1 = px + math.sin(entity.rotation + hand_offset_angle + offset_angle) * (
                hand_dist + self.hand_dist_offset[0]), \
                 py + math.cos(entity.rotation + hand_offset_angle + offset_angle) * (
                         hand_dist + self.hand_dist_offset[0])
        pg.draw.circle(surface, entity.color_hand, pos_h1, r)
        pos_h2 = px + math.sin(entity.rotation - hand_offset_angle + offset_angle) * (
                hand_dist + self.hand_dist_offset[1]), \
                 py + math.cos(entity.rotation - hand_offset_angle + offset_angle) * (
                         hand_dist + self.hand_dist_offset[1])
        pg.draw.circle(surface, entity.color_hand, pos_h2, r)

    def draw(self, surface, owner_position, hand_dist=0, hand_offset_angle=0):
        self.anim_update()


class Hands(Weapon):
    punch_anim_hand_speed = 1
    iter = 0

    def start_punch(self):
        if not self.punching:
            self.iter ^= 1
        super(Hands, self).start_punch()

    def anim_update(self):
        if self.punching:
            self.punch_anim_timer -= 1
            if self.punch_anim_timer < -5:
                self.punching = False
            if self.punch_anim_timer == 0:
                self.hand_dist_offset[self.iter] = 0
            elif self.punch_anim_timer > 0:
                if self.punch_anim_timer == self.punch_anim_ticks:
                    self.punch()
                elif self.punch_anim_timer > self.punch_anim_ticks:
                    self.hand_dist_offset[self.iter] += self.punch_anim_hand_speed
                elif self.punch_anim_timer > self.punch_anim_ticks:
                    self.hand_dist_offset[self.iter] -= self.punch_anim_hand_speed


class WeaponWoodStick(Weapon):
    index = STICK_WEAPON_IDX
    punch_anim_angle_speed = math.pi / 15
    punch_anim_ticks = 5
    color = 'brown'

    def __init__(self, owner: EntityObj, position: Union[tuple, pg.Vector2] = (0, 0)):
        super(WeaponWoodStick, self).__init__(owner, position)

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
            pg.draw.line(surface, self.color, pos_h1, pos2, 3)
        else:
            rotation = 0
            r = 0


class WeaponMetalStick(WeaponWoodStick):
    index = METAL_STICK_WEAPON_IDX
    color = '#334155'


class WeaponRedStick(WeaponWoodStick):
    index = RED_STICK_WEAPON_IDX
    color = '#FCD34D'


weapon_cls = {
    STICK_WEAPON_IDX: WeaponWoodStick,
    METAL_STICK_WEAPON_IDX: WeaponMetalStick,
    RED_STICK_WEAPON_IDX: WeaponRedStick,
}
