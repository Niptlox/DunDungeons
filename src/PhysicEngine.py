from pygame import Vector2, Rect


def physic_colliding_circle_square(circle_center, radius, rect, sx=1, sy=1):
    # 1 -top 2-bottom 4-left 8-right
    side = 0
    rx, ry, rw, rh = rect
    rx2, ry2 = rx + rw, ry + rh
    center: Vector2 = Vector2(rx + rw // 2, ry + rh // 2)
    position = Vector2(circle_center)
    new_x, new_y = position.xy
    vec_rect_circle = position - center
    vec_rect_r = Vector2(rx2, ry) - Vector2(rx, ry2)
    vec_rect_l = Vector2(rx, ry) - Vector2(rx2, ry2)
    dot_r = vec_rect_r.dot(vec_rect_circle)
    dot_l = vec_rect_l.dot(vec_rect_circle)
    
    if dot_r > 0:
        if dot_l > 0:
            side = 1  # top
        elif dot_l < 0:
            side = 8  # right
        else:
            side = 1 + 8  # topright
    elif dot_r < 0:
        if dot_l > 0:
            side = 4  # left
        elif dot_l < 0:
            side = 2  # bottom
        else:
            side = 4 + 2  # topright
    else:
        if dot_l > 0:
            side = 1 + 4  # topleft
        elif dot_l < 0:
            side = 2 + 8  # bottomright

    r = radius
    if side & 2:
        sy *= -1
        new_y = ry2 + r  # под
    elif side & 1:
        new_y = ry - r  # над
        sy *= -1
    if side & 8:
        sx *= -1
        new_x = rx2 + r  # справа
    elif side & 4:
        sx *= -1
        new_x = rx - r  # слева

    return new_x, new_y


def physic_colliding_circle_circle(circle_center, radius, circle_center_2, radius_2):
    # Есили один шар в нутри другого
    H: Vector2 = (circle_center_2 - circle_center)
    dist = (radius + radius_2)
    if H.length_squared() == 0:
        return circle_center
    elif H.length_squared() < dist ** 2:
        my_new_pos = circle_center_2 - (H.normalize() * (dist+0.5))
        return my_new_pos
    return circle_center

# import pygame
# import pygame as pg
# from pygame import Vector2
#
#
# def draw_obj(surface, obj, pos_on_screen):
#     center_screen = Vector2(500, 500)
#     if isinstance(obj, Circle):
#         pg.draw.circle(surface, obj.color, obj.position+center_screen, obj.radius, 1)
#         print(isinstance(obj, Circle), obj.position+center_screen)
#     elif isinstance(obj, Point):
#         pg.draw.circle(surface, obj.color, obj.position+center_screen, 2)
#
#
#
# class Point:
#     color = "red"
#
#     def __init__(self, scene, position):
#         self.scene = scene
#         self.position = Vector2(position)
#
#
# class Collider:
#     def __init__(self, gameObject):
#         self.gameObject = gameObject
#
#     @property
#     def position(self):
#         return self.gameObject.position
#
#     @position.setter
#     def position(self, value):
#         self.gameObject.position = value
#
#     # check colliding for list GameObjects
#     def collisions(self, objs):
#         return []
#
#
# class CircleCollider(Collider):
#     def __init__(self, gameObject, radius=10):
#         super().__init__(gameObject)
#         self.radius = radius
#
#     # check colliding for list GameObjects
#     def collisions(self, objs):
#         # my position
#         mx, my = self.position.xy
#         # столкновения Collider
#         collisions = []
#         for obj in objs:
#             coll = obj.collider
#             if coll is self:
#                 continue
#             if type(coll) is CircleCollider:
#                 px, py = coll.position.xy
#                 # проверяем соприклсновение кругов
#                 summ_r_2 = (self.radius + coll.radius) ** 2
#                 dist_2 = abs(px - mx) ** 2 + abs(py - my) ** 2
#                 if dist_2 <= summ_r_2:
#                     collisions.append(coll)
#         return collisions
#
#
# class Physbody:
#     def __init__(self, gameObject, speed=Vector2()):
#         self.gameObject = gameObject
#         self.speed = speed
#         # в текущий такт происходила ли проверка физики объекта
#         self.is_update_collisions = False
#
#     @property
#     def position(self):
#         return self.gameObject.position
#
#     @position.setter
#     def position(self, value):
#         self.gameObject.position = value
#
#     @property
#     def collider(self):
#         return self.gameObject.collider
#
#     # обновление координаты от скорости
#     def update(self):
#         self.is_update_collisions = False
#         mx, my = self.position.xy
#         self.position.xy = mx + self.speed.x, my + self.speed.y
#         return self.position.xy
#
#         # вычисление столкновений
#
#     def collisions(self, collisions):
#
#         my_pos = self.position
#         sx, sy = self.speed.xy
#         if type(self.collider) is CircleCollider:
#             for coll in collisions:
#                 if type(coll) is CircleCollider:
#                     coll_physbody = coll.gameObject.physbody
#                     coll_pos = coll.position
#                     # вектор между кругами
#                     H = (coll_pos - my_pos)
#                     if H.length_squared() == 0:
#                         continue
#
#                     if coll_physbody:
#                         sx2, sy2 = coll_physbody.speed.xy
#                     else:
#                         sx2, sy2 = 0, 0
#
#                     hx, hy = H.xy
#                     a = sx * hx + sy * hy - sx2 * hx - sy2 * hy
#                     a /= H.length_squared()
#                     my_speed = Vector2(sx - a * hx, sy - a * hy)
#                     if coll_physbody:
#                         other_speed = Vector2(sx2 + a * hx, sy2 + a * hy)
#                         coll_physbody.speed = other_speed
#                         coll_physbody.is_update_collisions = True
#                     sx, sy = my_speed.xy
#         self.speed.xy = sx, sy
#
#
# class GameObject:
#     def __init__(self, position: Vector2, cls_collider=None, cls_physbody=Physbody, speed=Vector2(), name="GameObject"):
#         self.position = position
#         self.collider = cls_collider(self)
#         self.physbody = cls_physbody(self, speed=speed)
#         self.name = name
#
#     @property
#     def xy(self):
#         return self.position.xy
#
#     @xy.setter
#     def xy(self, value):
#         self.position.xy = value
#
#     def __str__(self):
#         return f"<{self.name}>{self.position}"
#
#
# class Circle(GameObject):
#     color = "red"
#
#     def __init__(self, position: Vector2, cls_collider=CircleCollider, cls_physbody=Physbody, radius=10, speed=Vector2(),
#                  name="Circle"):
#         super().__init__(position, cls_collider, cls_physbody, speed, name)
#         self.radius = radius
#         self.collider.radius = radius
#
#
# class Player(Circle):
#     color = "green"
#
#     def __init__(self, position: Vector2, speed=Vector2(), name="Player"):
#         super().__init__(position, speed=speed, name=name)
#         self.collider.radius = 1
#         self.max_speed = 1
#         # ускорение
#         self.acceleration = 0.2
#
#     def handle_event(self, event):
#         speed = self.physbody.speed.copy()
#
#         if event.type == pygame.KEYDOWN:
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_LEFT:
#                     speed.x = min(-self.max_speed, speed.x - self.acceleration)
#                 if event.key == pygame.K_RIGHT:
#                     speed.x = max(self.max_speed, speed.x + self.acceleration)
#                 if event.key == pygame.K_UP:
#                     speed.y = min(-self.max_speed, speed.y - self.acceleration)
#                 if event.key == pygame.K_DOWN:
#                     speed.y = max(self.max_speed, speed.y + self.acceleration)
#         mod = speed.length()
#         if mod > 0:
#             speed.x = speed.x / mod * abs(speed.x)
#             speed.y = speed.y / mod * abs(speed.y)
#
#
# class Space:
#     def __init__(self, size, objs: dict):
#         self.width, self.height = size
#         self.objs = objs
#         if objs:
#             self.max_obj_id = max(objs.keys())
#         else:
#             self.max_obj_id = 0
#
#     def append(self, obj):
#         new_id = self.max_obj_id + 1
#         self.objs[new_id] = obj
#         self.max_obj_id = new_id
#         return new_id
#
#     def pop(self, obj_id):
#         return self.objs.pop(obj_id)
#
#     def update(self):
#         lst_objs = self.objs.values()
#         for obj in lst_objs:
#             if obj.physbody:
#                 obj.physbody.update()
#         for obj_id, obj in self.objs.items():
#             if obj.physbody:
#                 if not obj.physbody.is_update_collisions:
#                     collisions = obj.collider.collisions(lst_objs)
#                     obj.physbody.collisions(collisions)
#                 print(obj_id, obj.position, obj.physbody.speed)
#                 # input("Letter...")
#
#     def main(self):
#         while True:
#             self.update()
#
#
# class Camera:
#     def __init__(self, space, screen, player):
#         self.space = space
#         self.screen = screen
#         self.player = player
#
#     def main(self):
#         clock = pygame.time.Clock()
#         running = True
#         fps = FPS
#         while running:
#             self.screen.fill("black")
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     running = False
#                 self.player.handle_event(event)
#             self.space.update()
#             for obj in self.space.objs.values():
#                 draw_obj(self.screen, obj, obj.position)
#             clock.tick(fps)
#             pygame.display.flip()
#         pygame.quit()
#
#
# if __name__ == "__main__":
#     SX, SY = 1000, 1000
#     FPS = 30
#
#     objs = {
#         1: Circle(Vector2(-50, 0), speed=Vector2(1, 0)),
#         2: Circle(Vector2(60, 50), speed=Vector2(-1, 0)),
#         3: Circle(Vector2(40, 30), speed=Vector2(-1, -1)),
#         4: Circle(Vector2(40, 40), speed=Vector2(-1, -1)),
#         5: Circle(Vector2(50, 50), speed=Vector2(-1, -1)),
#         6: Circle(Vector2(40, 60), speed=Vector2(-1, -1)),
#         7: Circle(Vector2(40, 60), speed=Vector2(-1, -1)),
#         8: Circle(Vector2(40, 60), speed=Vector2(-1, -1)),
#         9: Circle(Vector2(40, 60), speed=Vector2(-1, -1)),
#     }
#     space = Space((100, 100), objs)
#     player = Player(Vector2(-5, 15))
#     space.append(player)
#     # for x in range(-20, 20, 2):
#     #     for y in range(-4, 4, 2):
#     #         obj = GameObject(Vector2(x, y), Collider=CircleCollider,
#     #                         Physbody=Physbody, speed=Vector2(y / 5, x / 25))
#     #         space.append(obj)
#     pygame.init()
#     pygame.display.set_caption('Board')
#     size = SX, SY
#     screen = pygame.display.set_mode(size)
#
#     camera = Camera(space, screen, player)
#     camera.main()
