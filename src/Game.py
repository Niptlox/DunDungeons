import math
import os
import random
from math import cos, sin, atan
from typing import List

import pygame as pg
from random import randint

# frame rate per second
from pygame import Rect
from pygame.math import Vector2

from src.ClassUI import SurfaceUI
from src.PhysicEngine import physic_colliding_circle_square, physic_colliding_circle_circle
from src.RandomDangeonGenerator import dMap, random_pos_in_room
from src.Ray import raycast_DDA
from src.ui import RestartUI

FPS = 60

# window screen size
WSIZE = (1420, 980)
screen = pg.display.set_mode(WSIZE)

# size of tile
TSIDE = 40
TSIZE = TSIDE, TSIDE
DRAW_RAYS = False
DRAW_ENTITY_RECT = False


def create_none_img(size=TSIZE):
    img = pg.Surface(size).convert_alpha()
    img.fill((0, 0, 0, 0))
    return img


def create_cell_img(color, size=TSIZE):
    img = pg.Surface(size)
    img.fill(color)
    # img.fill(color, (1, 1, TSIDE - 2, TSIDE - 2))
    return img


def create_key_img(color="blue", size=TSIZE):
    side = size[0]
    img = pg.Surface((side, side)).convert_alpha()
    img.fill((0, 0, 0, 0))
    img = create_cell_img("gray", size=size)
    r = side // 8
    x, y = side // 6, side // 6
    pg.draw.circle(img, color, (x, y), r)
    x2 = x + TSIDE // 4
    pg.draw.line(img, color, (x, y), (x2, y))
    pg.draw.line(img, color, (x2, y), (x2, y + TSIDE // 10))
    return img


def create_portal_img(color="purple", size=TSIZE):
    img = create_none_img(size)
    img = create_cell_img("gray", size=size)
    pg.draw.circle(img, color, (size[0] // 2, size[0] // 2), size[0] // 3, 4)
    return img


def create_medkit_img(size=TSIZE):
    color = "red"
    img = create_cell_img("gray", size=size)
    if size[0] > 5:
        ofs = size[0] // 16
        w, h = size[0] // 5, size[1] // 3 * 2
        pg.draw.rect(img, "white", (ofs, ofs, h, h))
        pg.draw.rect(img, color, (ofs * 2 + h // 2 - w // 2, ofs * 3, w - ofs * 2, h - ofs * 4))
        pg.draw.rect(img, color, (ofs * 3, ofs * 2 + h // 2 - w // 2, h - ofs * 4, w - ofs * 2))
    else:
        img.fill("white")
        img.fill("red", (1, 1, size[0] - 2, size[1] - 2))
    return img


def one_coin_img():
    r = 8
    img = pg.Surface((r * 2, r * 2))
    img.set_colorkey("black")
    pg.draw.circle(img, "yellow", (r, r), r)
    pg.draw.circle(img, "orange", (r, r), r, 2)
    return img


def create_coin_img(size=TSIZE, c=2):
    color = "yellow"
    img = create_cell_img("gray", size=size)
    if size[0] > 5:
        r = max(2, size[0] // 8)
        pg.draw.circle(img, color, (size[0] // 2 - 1, size[0] // 2 - 2), r)
        pg.draw.circle(img, "orange", (size[0] // 2 - 1, size[0] // 2 - 2), r, 1)
        pg.draw.circle(img, color, (size[0] // 2 + 2, size[0] // 2 + 2), r)
        pg.draw.circle(img, "orange", (size[0] // 2 + 2, size[0] // 2 + 2), r, 1)
        if c == 3:
            pg.draw.circle(img, color, (size[0] // 2 + 5, size[0] // 2 - 3), r)
            pg.draw.circle(img, "orange", (size[0] // 2 + 5, size[0] // 2 - 3), r, 1)
    else:
        img.fill("orange")
        img.fill("yellow", (1, 1, size[0] - 3, size[1] - 3))

    return img


cell_img = create_cell_img("black")
cell_imgs = {
    0: create_cell_img("gray"),
    2: create_cell_img("black"),
    3: create_cell_img("yellow"),
    4: create_cell_img("blue"),
    5: create_cell_img("black"),
    7: create_portal_img(),
    9: create_key_img(),
    11: create_coin_img(),
    12: create_coin_img(c=3),
    15: create_medkit_img(),
}
minimap_size = (40, 40)
MINISIDE = 5
minimap_cell_size = (MINISIDE, MINISIDE)
minimap_cell_imgs = {
    0: create_cell_img("gray", minimap_cell_size),
    2: create_cell_img("black", minimap_cell_size),
    3: create_cell_img("yellow", minimap_cell_size),
    4: create_cell_img("blue", minimap_cell_size),
    5: create_cell_img("black", minimap_cell_size),
    7: create_portal_img(size=minimap_cell_size),
    9: create_key_img(size=minimap_cell_size),
    11: create_coin_img(minimap_cell_size),
    12: create_coin_img(minimap_cell_size, c=3),
    15: create_medkit_img(size=minimap_cell_size),

}

path_data_file = os.getcwd() + "/data.f"


def get_record():
    if os.path.isfile(path_data_file):
        with open(path_data_file, "r") as f:
            t = f.readline()
        return int(t) if t.isdigit() else 0
    return 0


def set_record(record):
    last_record = get_record()
    with open(path_data_file, "w") as f:
        f.write(str(max(last_record, record)))


PHYSICAL_TILES = {2, 1, 4}


def rect_vertexes(rect):
    if rect.w > TSIDE or rect.h > TSIDE:
        vertexes = [(rect.right - 1, rect.top), (
            rect.right - 1, rect.bottom - 1)]
        x, y = rect.topleft
        for i in range(0, rect.w - 1, TSIDE - 1):
            for j in range(0, rect.h - 1, TSIDE - 1):
                vertexes.append((x + i, y + j))
        for i in range(0, rect.w - 1, TSIDE - 1):
            vertexes.append((x + i, rect.bottom - 1))
        for j in range(0, rect.h - 1, TSIDE - 1):
            vertexes.append((rect.right - 1, y + j))
    else:
        vertexes = [rect.topleft, (rect.left, rect.bottom - 1), (rect.right - 1, rect.top), (
            rect.right - 1, rect.bottom - 1)]
    return vertexes


class Player:
    size = (TSIDE * 2 // 3, TSIDE * 2 // 3)
    # 0 - arrows; 1 - with rotate, 2 - with rotate mouse
    type_movement = 2
    FOV = 60  # degres
    cof_line = 800
    cof_angle = int(FOV / 360 * 2 * cof_line)
    color = "white"
    collider = "circle"
    max_lives = 100

    def __init__(self, game, position, game_map):
        self.game = game
        self.position = Vector2(position)
        self.size = self.size
        self.half_size = self.size[0] // 2, self.size[1] // 2
        self.game_map = game_map
        self.speed = 0.2
        self.rot_speed = 0.005
        self.rotation = 0
        self.screen_position = (-1, -1)
        self.key = None
        self.collision_entities = False
        self.lives = self.max_lives
        self.punch = 10
        self.alive = True
        self.coins = 0

    def restart(self):
        self.alive = True
        self.lives = self.max_lives
        self.coins = 0

    @property
    def rect(self):
        return pg.Rect(self.position, self.size)

    @property
    def center(self):
        return self.position + Vector2(self.half_size)

    def getting_key(self, key):
        self.key = key
        self.game_map.collision_exclusion = {4, }

    def viewed_tiles(self):
        lsts = set()
        vecs = []
        walls = set()
        center = self.position + Vector2(self.half_size)

        for i in range(-self.cof_angle, self.cof_angle):
            i /= self.cof_line
            pos_2 = Vector2(center.x + math.sin(self.rotation + i * math.pi),
                            center.y + math.cos(self.rotation + i * math.pi))
            lst, vec, last_tile = raycast_DDA(Vector2(center), pos_2, TSIDE, Vector2(self.game_map.size),
                                              self.game_map.array_map,
                                              walls={2, 1, 4, 5} ^ self.game_map.collision_exclusion)
            vecs.append(vec)
            lsts |= lst
            walls.add(last_tile)
        xy = (int(center.x) // TSIDE, int(center.y) // TSIDE)
        if 0 <= xy[0] < self.game_map.size[0] and 0 <= xy[1] < self.game_map.size[1]:
            lsts.add(xy)
        return lsts, vecs, walls

    def set_screen_position(self, position):
        self.screen_position = position

    def pg_event(self, event):
        pass

    def update(self, tick=20):
        keys = pg.key.get_pressed()
        movement = [0, 0]
        speed = self.speed * tick
        if self.type_movement == 0:
            if keys[pg.K_LEFT]:
                movement[0] -= speed
            elif keys[pg.K_RIGHT]:
                movement[0] += speed
            if keys[pg.K_UP]:
                movement[1] -= speed
            elif keys[pg.K_DOWN]:
                movement[1] += speed

            if movement[0] and movement[1]:
                at = atan(movement[1] / movement[0])
                movement = movement[0] * abs(sin(at)), movement[1] * abs(cos(at))
        elif self.type_movement in {1, 2}:
            if self.type_movement == 1:
                rot_speed = self.rot_speed * tick
                if keys[pg.K_RIGHT]:
                    self.rotation -= rot_speed
                elif keys[pg.K_LEFT]:
                    self.rotation += rot_speed
            elif self.type_movement == 2:
                self.rotation = -Vector2((0, 0)).angle_to(Vector2(pg.mouse.get_pos()) - Vector2(self.screen_position)) \
                                / 180 * math.pi + math.pi / 2
            movement = Vector2()
            if keys[pg.K_UP] or keys[pg.K_w]:
                movement += Vector2(math.sin(self.rotation), math.cos(self.rotation)) * speed
            elif keys[pg.K_DOWN] or keys[pg.K_s]:
                movement += Vector2(-math.sin(self.rotation), -math.cos(self.rotation)) * speed
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                movement += Vector2(math.sin(self.rotation + math.pi / 2),
                                    math.cos(self.rotation + math.pi / 2)) * speed
            elif keys[pg.K_RIGHT] or keys[pg.K_d]:
                movement += Vector2(math.sin(self.rotation - math.pi / 2),
                                    math.cos(self.rotation - math.pi / 2)) * speed
            # print((movement[1]), self.rect.y)
        self.movement = movement
        self.move(movement)
        center = self.center
        tx, ty = int(center.x // TSIDE), int(center.y // TSIDE)
        tile_index = self.game_map.get_tile_with_def((tx, ty))
        if tile_index == 9:
            self.getting_key(9)
            self.game_map.set_tile((tx, ty), 0)
        elif tile_index == 7:
            self.game.new_level()
        elif tile_index == 11:
            self.coins += randint(1, 2)
            self.game_map.set_tile((tx, ty), 0)
        elif tile_index == 12:
            self.coins += 3
            self.game_map.set_tile((tx, ty), 0)
        elif tile_index == 15:
            self.add_lives(20)
            self.game_map.set_tile((tx, ty), 0)

    def move(self, movement):
        # TODo: переевести с rect на position
        off = 10
        r = self.size[0] // 2
        self.position += Vector2(movement)
        punching = pg.mouse.get_pressed() or isinstance(self, Zombie)
        if self.collision_entities:
            for collide_entity in self.game_map.rect_collision_entities(self):
                collide_rect = collide_entity.rect
                if self.collider == "circle":
                    cx, cy = physic_colliding_circle_circle(Vector2(self.rect.center), r, Vector2(collide_rect.center),
                                                            collide_rect.w // 2)
                else:
                    cx, cy = physic_colliding_circle_square(self.rect.center, r, collide_rect)
                self.position.xy = cx - self.size[0] // 2, cy - self.size[1] // 2
                if punching:
                    collide_entity.get_damage(self.punch)
        for collision in self.game_map.rect_collision_tiles(self.rect):
            collide_rect = (collision[0] * TSIDE, collision[1] * TSIDE, TSIDE, TSIDE)
            cx, cy = physic_colliding_circle_square(self.rect.center, r, collide_rect)
            self.position.xy = cx - self.size[0] // 2, cy - self.size[1] // 2

        # print(movement, self.position, self.__class__)

    def get_damage(self, damage):
        self.lives -= damage
        if self.lives <= 0:
            self.kill()

    def add_lives(self, lives):
        self.lives = min(self.max_lives, self.lives + lives)

    def kill(self):
        self.alive = False


class Zombie(Player):
    color = "green"
    max_lives = 50

    def __init__(self, game, position, game_map):
        super(Zombie, self).__init__(game, position, game_map)
        self.collision_entities = True
        self.speed = 0.1
        self.punch = 1

    def update(self, tick=20):
        nvec = (Vector2(self.game.player.rect.center) - Vector2(self.rect.center))
        length2 = nvec.length_squared()
        if length2 != 0:
            nvec.normalize_ip()

            lst, vec, last_tile = raycast_DDA(Vector2(self.rect.center), Vector2(self.rect.center) + nvec, TSIDE,
                                              Vector2(self.game_map.size),
                                              self.game_map.array_map,
                                              walls={2, 1, 4, 5} ^ self.game_map.collision_exclusion)

            if vec.length_squared() * (TSIDE ** 2) > length2:
                speed = self.speed * tick
                self.rotation = -Vector2((0, 0)).angle_to(nvec) / 180 * math.pi + math.pi / 2
                self.move(nvec * speed)
                # print(self.position)


type_generate = 2


class GameMap:
    default = 0

    def __init__(self, game, size):
        self.game = game
        self.size = size
        self.array_map = self.set_map_of_sym(self.default)
        self.collision_exclusion = set()
        self.player_position = (0, 0)
        self.entities = []
        self.type_generate = type_generate
        self.clear_map()

    def update(self, tick):
        i = 0
        while i < len(self.entities):
            entity = self.entities[i]
            entity.update(tick)
            if not entity.alive:
                self.entities.pop(i)
                i -= 1
            i += 1

    def clear_map(self):
        self.array_map = self.set_map_of_sym(self.default)
        self.entities = []
        self.collision_exclusion = set()
        self.player_position = (0, 0)

    def set_size(self, size):
        self.size = size
        self.clear_map()

    def pg_event(self, event):
        pass

    def get_tile(self, position):
        return self.array_map[position[1]][position[0]]

    def coords_iterator(self):
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                yield x, y

    def set_tile(self, position, tile):
        self.array_map[position[1]][position[0]] = tile

    def get_tile_with_def(self, position, default=None):
        if 0 <= position[0] < self.size[0] and 0 <= position[1] < self.size[1]:
            return self.get_tile(position)
        return default

    def load(self, text: str):
        arr2d = [list(map(int, st)) for st in text.split("\n") if st]
        self.size = (len(arr2d[0]), len(arr2d))
        self.array_map = arr2d

    def set_map_of_sym(self, sym=0):
        self.array_map = [[sym for i in range(self.size[0])] for j in range(self.size[1])]
        return self.array_map

    def random_set(self, points=10):
        self.clear_map()
        for i in range(points):
            x, y = randint(0, self.size[0] - 1), randint(0, self.size[1] - 1)
            self.array_map[y][x] = 1

    def map_generate(self):
        if self.type_generate == 0:
            self.bigroom_generate()
        elif self.type_generate == 1:
            self.random_set()
        elif self.type_generate == 2:
            self.dungeon_generate()

    def bigroom_generate(self):
        self.clear_map()
        self.array_map = [[2] * self.size[0]] + [[2] + [0] * (self.size[0] - 2) + [2] for i in
                                                 range(self.size[1] - 2)] + [[2] * self.size[0]]
        print(self.array_map)
        self.player_position = self.size[0] // 2 * TSIDE, self.size[1] // 2 * TSIDE
        cnt = randint(1, 100)
        cnt = 1
        for i in range(cnt):
            ix, iy = randint(1, self.size[0] - 3), randint(1, self.size[0] - 3)
            zombie = Zombie(self.game, (ix * TSIDE, iy * TSIDE), self)
            self.add_entity(zombie)

    def add_entity(self, obj):
        self.entities.append(obj)

    def dungeon_generate(self):
        self.clear_map()
        gen = dMap()
        gen.makeMap(self.size[0], self.size[1], 70, 30, (self.size[0] * self.size[1]) ** 0.5)
        self.array_map = gen.mapArr
        # zombs
        print(gen.roomList)
        for room in gen.roomList[1:]:
            for i in range(randint(0, 2) * randint(0, 1)):
                ix, iy = random_pos_in_room(room)
                zombie = Zombie(self.game, (ix * TSIDE, iy * TSIDE), self)
                self.add_entity(zombie)
        for room in random.choices(gen.roomList, k=len(gen.roomList) // 3):
            if randint(0, 5) > 1:
                self.set_tile(random_pos_in_room(room), 11)
            else:
                self.set_tile(random_pos_in_room(room), 12)

        for room in random.choices(gen.roomList, k=len(gen.roomList) // 6):
            self.set_tile(random_pos_in_room(room), 15)

        # key
        room = gen.roomList[0]
        self.set_tile(random_pos_in_room(room), 9)
        self.player_position = (room[2] * TSIDE, (room[3] + 1) * TSIDE)
        #  portal
        room = random.choice(gen.roomList[1:]) if len(gen.roomList) > 1 else random.choice(gen.roomList)
        self.set_tile((room[2] + room[1] // 2, room[3] + room[0] // 2), 7)

    def rect_collision_tiles(self, rect: pg.Rect):
        collisions = []
        for x, y in rect_vertexes(rect):
            if self.get_tile_with_def((x // TSIDE, y // TSIDE)) in (PHYSICAL_TILES ^ self.collision_exclusion):
                collisions.append((x // TSIDE, y // TSIDE))
        return collisions

    def rect_collision_entities(self, p_entity):
        collisions: List[Rect] = []
        rect = p_entity.rect
        for entity in self.entities + [self.game.player]:
            if entity is not p_entity and rect.colliderect(entity.rect):
                collisions.append(entity)
        return collisions


class Game:
    def __init__(self):
        self.screen = screen
        self.game_map = GameMap(self, (40, 80))
        self.player = Player(self, self.game_map.player_position, self.game_map)
        self.camera = Camera(self)
        self.clock = pg.time.Clock()
        self.running = True
        self.level = 0
        self.record_level = get_record()
        self.new_level()
        self.restart_ui = RestartUI(self, running=False)

    def pg_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_t and pg.key.get_mods() & pg.KMOD_CTRL:
                    self.new_level(new_level=1)
                elif event.key == pg.K_h and pg.key.get_mods() & pg.KMOD_CTRL:
                    self.camera.b_shadows = not self.camera.b_shadows
                elif event.key == pg.K_f and pg.key.get_mods() & pg.KMOD_CTRL:
                    self.player.getting_key(9)
                elif event.key == pg.K_k and pg.key.get_mods() & pg.KMOD_CTRL:
                    self.player.kill()
            self.player.pg_event(event)
            self.game_map.pg_event(event)
            self.restart_ui.pg_event(event)

    def restart(self):
        self.level = 0
        self.player.restart()
        self.new_level()
        self.restart_ui.running = False

    def new_level(self, new_level=1):
        self.level += new_level

        self.camera.reset_game_map()
        self.game_map.set_size((15 + 3 * self.level, 15 + 3 * self.level))
        self.game_map.map_generate()
        self.player.position = Vector2(self.game_map.player_position)

    def main(self):
        self.running = True
        while self.running:
            self.update()

    def update(self):
        tick = self.clock.tick(FPS)
        pg.display.set_caption(f"FPS: {self.clock.get_fps()}")
        self.pg_events()
        if self.player.alive:
            self.player.update(tick)
        elif not self.restart_ui.running:
            self.record_level = max(self.record_level, self.level)
            self.restart_ui.running = True
            set_record(self.record_level)
            self.restart_ui.set_level(self.level, self.record_level)
        self.game_map.update(tick)
        self.camera.draw(self.screen)
        if self.restart_ui.running:
            self.restart_ui.draw(self.screen)
        pg.display.flip()

    def exit(self):
        self.running = False


pg.font.init()
font = pg.font.SysFont("Roboto", 25)


class Camera:
    def __init__(self, game: Game):
        self.game = game
        self.game_map = game.game_map
        self.player = game.player
        self.size = WSIZE
        self.position = Vector2(0, 0)
        self.move_to_player()
        self.display = pg.Surface(WSIZE)
        self.view_tiles = set()
        self.view_rays = []
        self.view_walls = set()
        self.b_shadows = True
        self.minimap_surface = SurfaceUI((0, 0, MINISIDE * minimap_size[0], MINISIDE * minimap_size[1]))
        self.minimap_surface.rect.right = self.size[0]

    def move_to_player(self):
        self.position.x = self.player.position.x - WSIZE[0] // 2
        self.position.y = self.player.position.y - WSIZE[1] // 2

    @property
    def int_position(self):
        return int(self.position.x), int(self.position.y)

    @property
    def rect(self):
        return pg.Rect(self.position, self.size)

    def reset_game_map(self):
        self.view_tiles = set()

    def draw(self, surface):
        self.display.fill("#A3A3A3")

        self.position.x += (self.player.position.x - self.position[0] - WSIZE[0] // 2) / 5
        self.position.y += (self.player.position.y - self.position[1] - WSIZE[1] // 2) / 5
        tiles, self.view_rays, self.view_walls = self.player.viewed_tiles()
        self.view_tiles |= tiles
        if self.b_shadows:
            self.draw_view_tiles()
            self.draw_entities()
            self.draw_shadow()
            self.draw_walls()
        else:
            self.draw_tiles(self.game_map.coords_iterator())
            self.draw_entities()

        self.draw_player()
        self.draw_ui()
        # self.display.blit(cell_imgs[12], (280, 0))
        surface.blit(self.display, (0, 0))

    def draw_tiles(self, tiles):
        for ix, iy in tiles:
            t = self.game_map.get_tile((ix, iy))
            if t in cell_imgs:
                tx, ty = ix * TSIDE - self.int_position[0], iy * TSIDE - self.int_position[1]
                self.display.blit(cell_imgs[t], (tx, ty))
        pg.draw.rect(self.display, "black", (-self.int_position[0], -self.int_position[1],
                                             self.game_map.size[0] * TSIDE, self.game_map.size[1] * TSIDE), 1)

    def draw_view_tiles(self):
        self.draw_tiles(self.view_tiles)

    def draw_walls(self):
        self.draw_tiles(self.view_walls)

    def draw_player(self):
        self.draw_player_entity(self.player)

    def draw_player_entity(self, entity):
        hs = entity.half_size
        px, py = entity.position.x - self.int_position[0] + hs[0], entity.position.y - self.int_position[1] + hs[1]
        entity.set_screen_position((px, py))
        pos_2 = px + math.sin(entity.rotation) * 10, \
                py + math.cos(entity.rotation) * 10
        pg.draw.circle(self.display, entity.color, (px, py), entity.size[0] // 2)
        pg.draw.line(self.display, "black", (px, py), pos_2, 1)
        if DRAW_ENTITY_RECT:
            pg.draw.rect(self.display, "red",
                         ((entity.position.x - self.int_position[0], entity.position.y - self.int_position[1]),
                          entity.size), 1)

    def draw_shadow(self):
        pvec = Vector2(self.player.rect.centerx - self.int_position[0], self.player.rect.centery - self.int_position[1])
        if DRAW_RAYS:
            for vec in self.view_rays:
                pg.draw.line(self.display, "orange", pvec, pvec + vec * TSIDE)

        sur = pg.Surface(self.size)
        sur.fill("#44403C")
        points = [pvec + vec * TSIDE for vec in self.view_rays] + [pvec]
        pg.draw.polygon(sur, "white", points)
        sur.set_colorkey("white")
        self.display.blit(sur, (0, 0))

    def draw_entities(self):
        for entity in self.game_map.entities:
            self.draw_player_entity(entity)

    def draw_ui(self):
        text = font.render(f"Level: {self.game.level}", True, "white")
        self.display.blit(text, (5, 25))
        text = font.render(f"{self.player.coins}", True, "white")
        coin = one_coin_img()
        self.display.blit(coin, (5, 53))
        self.display.blit(text, (25, 54))

        pg.draw.rect(self.display, "black", (3, 3, 200 + 4, 13))
        pg.draw.rect(self.display, "#A3F635", (5, 5, self.player.lives / self.player.max_lives * 200, 9))

        self.draw_minimap()

    def draw_minimap(self):
        tiles = self.view_tiles
        mside = minimap_cell_size[0]

        # minimap_surface = pg.Surface(surface_size)
        scroll = int(self.player.position.x / TSIDE * MINISIDE - self.minimap_surface.rect.w // 2), \
                 int(self.player.position.y / TSIDE * MINISIDE - self.minimap_surface.rect.h // 2)
        self.minimap_surface.fill("#1E293B")
        for ix, iy in tiles:
            t = self.game_map.get_tile((ix, iy))
            if t in minimap_cell_imgs:
                tx, ty = ix * mside - scroll[0], iy * mside - scroll[1]
                self.minimap_surface.blit(minimap_cell_imgs[t], (tx, ty))
        pg.draw.rect(self.minimap_surface, "#171717", (-scroll[0], -scroll[1],
                                                       self.game_map.size[0] * mside, self.game_map.size[1] * mside), 1)
        self.minimap_surface.draw(self.display)


def main():
    return Game().main()
