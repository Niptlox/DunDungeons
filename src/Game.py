import math
import random
from math import cos, sin, atan

import pygame as pg
from random import randint

# frame rate per second
from pygame.math import Vector2

from src.RandomDangeonGenerator import dMap
from src.Ray import raycast_DDA

FPS = 60

# window screen size
WSIZE = (1220, 780)
screen = pg.display.set_mode(WSIZE)

# size of tile
TSIDE = 32
TSIZE = TSIDE, TSIDE


def create_none_img(size):
    img = pg.Surface(size).convert_alpha()
    img.fill((0, 0, 0, 0))
    return img


def create_cell_img(color):
    img = pg.Surface(TSIZE)
    img.fill(color)
    # img.fill(color, (1, 1, TSIDE - 2, TSIDE - 2))
    return img


def create_key_img(color):
    img = pg.Surface(TSIZE).convert_alpha()
    img.fill((0, 0, 0, 0))
    pg.draw.circle(img, color, (5, 5), 4)
    pg.draw.line(img, color, (5, 5), (12, 5))
    pg.draw.line(img, color, (12, 5), (12, 8))
    return img


def create_portal_img(color):
    img = create_none_img(TSIZE)
    pg.draw.circle(img, color, (TSIDE // 2, TSIDE // 2), TSIDE // 3, 4)
    return img


cell_img = create_cell_img("black")
cell_imgs = {
    0: create_cell_img("gray"),
    2: create_cell_img("black"),
    3: create_cell_img("yellow"),
    4: create_cell_img("blue"),
    5: create_cell_img("black"),
    9: create_key_img("blue"),
    7: create_portal_img("purple")
}

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

    def __init__(self, game, position, game_map):
        self.game = game
        self.rect = pg.Rect(position, self.size)
        self.game_map = game_map
        self.speed = 0.2
        self.rot_speed = 0.005
        self.rotation = 0
        self.screen_position = (-1, -1)
        self.key = None

    def getting_key(self, key):
        self.key = key
        self.game_map.collision_exclusion = {4, }

    def viewed_tiles(self):
        lsts = set()
        vecs = []
        cof_line = 8
        walls = set()
        for i in range(-40 * cof_line, 40 * cof_line):
            i /= 100 * cof_line
            pos_2 = Vector2(self.rect.centerx + math.sin(self.rotation + i * math.pi),
                            self.rect.centery + math.cos(self.rotation + i * math.pi))
            lst, vec, last_tile = raycast_DDA(Vector2(self.rect.center), pos_2, TSIDE, Vector2(self.game_map.size),
                                              self.game_map.array_map,
                                              walls={2, 1, 4, 5} ^ self.game_map.collision_exclusion)
            vecs.append(vec)
            lsts |= lst
            walls.add(last_tile)
        xy = (int(self.rect.centerx) // TSIDE, int(self.rect.centery) // TSIDE)
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
            if keys[pg.K_UP]:
                movement = Vector2(math.sin(self.rotation), math.cos(self.rotation)) * speed
            elif keys[pg.K_DOWN]:
                movement = Vector2(-math.sin(self.rotation), -math.cos(self.rotation)) * speed
        self.move(movement)
        tx, ty = self.rect.centerx // TSIDE, self.rect.centery // TSIDE
        if self.game_map.get_tile_with_def((tx, ty)) == 9:
            self.getting_key(9)
            self.game_map.set_tile((tx, ty), 0)
        if self.game_map.get_tile_with_def((tx, ty)) == 7:
            self.game.new_dungeon()

    def move(self, movement):
        self.rect.x += movement[0]
        for collision in self.game_map.rect_collision(self.rect):
            if movement[0] > 0:
                self.rect.right = collision[0] * TSIDE
            elif movement[0] < 0:
                self.rect.left = collision[0] * TSIDE + TSIDE
        self.rect.y += movement[1]
        for collision in self.game_map.rect_collision(self.rect):
            if movement[1] > 0:
                self.rect.bottom = collision[1] * TSIDE
            elif movement[1] < 0:
                self.rect.top = collision[1] * TSIDE + TSIDE


class GameMap:
    default = 0

    def __init__(self, size, ):
        self.size = size
        self.array_map = self.set_map_of_sym(self.default)
        self.collision_exclusion = set()
        self.player_position = (0, 0)

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
        for i in range(points):
            x, y = randint(0, self.size[0] - 1), randint(0, self.size[1] - 1)
            self.array_map[y][x] = 1

    def bigroom_generate(self):
        self.array_map = [[2] * self.size[0]] + [[2] + [0] * (self.size[0] - 2) + [2] for i in
                                                 range(self.size[1] - 2)] + [[2] * self.size[0]]
        print(self.array_map)
        self.player_position = self.size[0] // 2 * TSIDE, self.size[1] // 2 * TSIDE

    def dungeon_generate(self):
        self.collision_exclusion = set()
        gen = dMap()
        gen.makeMap(self.size[0], self.size[1], 70, 30, (self.size[0]*self.size[1])**0.5)
        self.array_map = gen.mapArr
        # key
        room = gen.roomList[0]
        self.set_tile((room[2] + randint(0, max(1, room[0] - 3)), room[3] + randint(0, max(1, room[1] - 3))), 9)
        self.player_position = (room[2] * TSIDE, (room[3] + 1) * TSIDE)
        #  portal
        room = random.choice(gen.roomList)
        self.set_tile((room[2] + room[1] // 2, room[3] + room[0] // 2), 7)

    def rect_collision(self, rect: pg.Rect):
        collisions = []
        for x, y in rect_vertexes(rect):
            if self.get_tile_with_def((x // TSIDE, y // TSIDE)) in (PHYSICAL_TILES ^ self.collision_exclusion):
                collisions.append((x // TSIDE, y // TSIDE))
        return collisions


class Game:
    def __init__(self):
        self.screen = screen
        self.game_map = GameMap((80, 80))
        self.player = Player(self, self.game_map.player_position, self.game_map)
        self.camera = Camera(self)
        self.clock = pg.time.Clock()
        self.running = True
        self.level = 0
        self.new_dungeon()

    def pg_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_t:
                    self.new_dungeon(new_level=1)
                elif event.key == pg.K_h:
                    self.camera.b_shadows = not self.camera.b_shadows
                elif event.key == pg.K_f:
                    self.player.getting_key(9)
            self.player.pg_event(event)
            self.game_map.pg_event(event)

    def new_dungeon(self, new_level=1):
        self.level += new_level

        self.camera.reset_game_map()
        self.game_map.__init__((20+10*self.level, 15+10*self.level))
        self.game_map.dungeon_generate()
        self.player.rect.topleft = self.game_map.player_position

    def main(self):
        self.running = True
        while self.running:
            tick = self.clock.tick(FPS)
            pg.display.set_caption(f"FPS: {self.clock.get_fps()}")
            self.pg_events()
            self.player.update(tick)
            self.camera.draw(self.screen)
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
        self.rect = pg.Rect((0, 0), WSIZE)
        self.move_to_player()
        self.display = pg.Surface(WSIZE)
        self.view_tiles = set()
        self.view_rays = []
        self.view_walls = set()
        self.b_shadows = True

    def move_to_player(self):
        self.rect.x = self.player.rect.x - WSIZE[0] // 2
        self.rect.y = self.player.rect.y - WSIZE[1] // 2

    def reset_game_map(self):
        self.view_tiles = set()

    def draw(self, surface):
        self.display.fill("#A3A3A3")
        self.rect.x += (self.player.rect.x - self.rect.x - WSIZE[0] // 2) / 5
        self.rect.y += (self.player.rect.y - self.rect.y - WSIZE[1] // 2) / 5
        tiles, self.view_rays, self.view_walls = self.player.viewed_tiles()
        self.view_tiles |= tiles
        if self.b_shadows:
            self.draw_view_tiles()
            self.draw_shadow()
            self.draw_walls()
        else:
            self.draw_tiles(self.game_map.coords_iterator())
        self.draw_player()
        self.draw_ui()
        surface.blit(self.display, (0, 0))

    def draw_tiles(self, tiles):
        for ix, iy in tiles:
            t = self.game_map.get_tile((ix, iy))
            if t in cell_imgs:
                tx, ty = ix * TSIDE - self.rect.x, iy * TSIDE - self.rect.y
                self.display.blit(cell_imgs[t], (tx, ty))
        pg.draw.rect(self.display, "black", (-self.rect.x, -self.rect.y,
                                             self.game_map.size[0] * TSIDE, self.game_map.size[1] * TSIDE),
                     1)

    def draw_view_tiles(self):
        self.draw_tiles(self.view_tiles)

    def draw_walls(self):
        self.draw_tiles(self.view_walls)

    def draw_player(self):
        px, py = self.player.rect.centerx - self.rect.x, self.player.rect.centery - self.rect.y
        self.player.set_screen_position((px, py))
        pos_2 = px + math.sin(self.player.rotation) * 10, \
                py + math.cos(self.player.rotation) * 10
        pg.draw.circle(self.display, "white", (px, py), self.player.rect.w // 2)

        pg.draw.line(self.display, "black", (px, py), pos_2, 1)

    def draw_shadow(self):
        pvec = Vector2(self.player.rect.centerx - self.rect.x, self.player.rect.centery - self.rect.y)
        # for vec in self.view_rays:
        #     pg.draw.line(self.display, "orange", pvec, pvec + vec * TSIDE)

        sur = pg.Surface(self.rect.size)
        sur.fill("#44403C")
        points = [pvec + vec * TSIDE for vec in self.view_rays] + [pvec]
        pg.draw.polygon(sur, "white", points)
        sur.set_colorkey("white")
        self.display.blit(sur, (0, 0))

    def draw_ui(self):
        text = font.render(f"Level: {self.game.level}", True, "white")
        self.display.blit(text, (5, 5))


def main():
    return Game().main()
