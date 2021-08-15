import math
import time

import pygame as pygame

win = pygame.display.set_mode((500, 500))

clock = pygame.time.Clock()

map_size = pygame.math.Vector2(30, 30)
tile_size = pygame.math.Vector2(win.get_width() / map_size.x, win.get_height() / map_size.y)
game_map = {}
for y in range(int(map_size.y)):
    for x in range(int(map_size.x)):
        game_map[(x, y)] = True

for y in range(1, int(map_size.y) - 1):
    for x in range(1, int(map_size.x) - 1):
        game_map[(x, y)] = False


class Player:
    def __init__(self, x, y, vel=1, fov=math.pi / 2, angle=0, angle_change=math.pi / 2):
        self.pos = pygame.math.Vector2(x, y)
        self.fov = fov
        self.angle = angle
        self.angle_change = angle_change

        self.new_pos = pygame.math.Vector2(0, 0)
        self.new_angle = 0

        self.move_distance = vel


player = Player(map_size.x / 2, map_size.y / 2, vel=10, fov=math.pi / 2, angle=0, angle_change=math.pi / 2)

rays = 90
rad = 10

distances = []


for d in range(rays):
    distances.append(player.pos)

def dda_ray_casting(rays, radius, distances):
    start_pos = player.pos
    for ray in range(rays):
        ray_angle = (player.angle - player.fov / 2) + (ray / rays) * player.fov
        x_end = math.cos(ray_angle) * radius
        y_end = math.sin(ray_angle) * radius
        end_pos_norm = (pygame.math.Vector2(x_end, y_end)).normalize()

        if end_pos_norm.x == 0 or end_pos_norm.y == 0:
            distances[ray] = pygame.math.Vector2(start_pos)
            continue

        step_size = pygame.math.Vector2(math.sqrt(1 + (end_pos_norm.y / end_pos_norm.x) ** 2),
                                        math.sqrt(1 + (end_pos_norm.x / end_pos_norm.y) ** 2))

        map_coords = pygame.math.Vector2(int(start_pos.x), int(start_pos.y))
        ray_len = pygame.math.Vector2()
        step = pygame.math.Vector2()
        if end_pos_norm.x < 0:
            step.x = -1
            ray_len.x = (start_pos.x - map_coords.x) * step_size.x
        else:
            step.x = 1
            ray_len.x = ((map_coords.x + 1) - start_pos.x) * step_size.x

        if end_pos_norm.y < 0:
            step.y = -1
            ray_len.y = (start_pos.y - map_coords.y) * step_size.y
        else:
            step.y = 1
            ray_len.y = ((map_coords.y + 1) - start_pos.y) * step_size.y

        hit_tile = False
        distance = 0
        while (not hit_tile) and (distance < radius):
            if ray_len.x < ray_len.y:
                map_coords.x += step.x
                distance = ray_len.x
                ray_len.x += step_size.x
            else:
                map_coords.y += step.y
                distance = ray_len.y
                ray_len.y += step_size.y

            if 0 <= map_coords.x < map_size.x and 0 <= map_coords.y < map_size.y:
                if game_map.get((map_coords.x, map_coords.y)):
                    hit_tile = True

        if hit_tile:
            distances[ray] = pygame.math.Vector2(start_pos + end_pos_norm * distance)
        else:
            distances[ray] = pygame.math.Vector2(start_pos)


    return distances

def draw_on_update(distances):
    # win.fill((0, 0, 0))

    # for coords, tile in game_map.items():
    #     if tile:
    #         x = coords[0] * tile_size.x
    #         y = coords[1] * tile_size.y
    #         pygame.draw.rect(win, (255, 255, 255), pygame.Rect((x, y), tile_size))

    for distance in distances:
        pygame.draw.line(win,
                         (0, 255, 0),
                         (player.pos.x * tile_size.x, player.pos.y * tile_size.y),
                         (distance.x * tile_size.x, distance.y * tile_size.y))

    pygame.draw.rect(win, (255, 0, 0), pygame.Rect((player.pos.x * tile_size.x - tile_size.x / 2,
                                                    player.pos.y * tile_size.y - tile_size.y / 2),
                                                   tile_size))

    pygame.draw.line(win,
                     (0, 255, 0),
                     (player.pos.x * tile_size.x, player.pos.y * tile_size.y),
                     (int((player.pos.x * tile_size.x + 20 * math.cos(player.angle))),
                      int((player.pos.y * tile_size.y + 20 * math.sin(player.angle)))))

    pygame.display.set_caption('X: {:.2f} Y: {:.2f} - Angle: {:.0f} FPS: {:.2f}'
                               .format(player.pos.x,
                                       player.pos.y,
                                       abs(math.degrees(player.angle) % 360),
                                       clock.get_fps()))

    pygame.display.update()


class DeltaTime:
    def __init__(self):
        self.dt = 0
        self.prev_time = time.time()
        self.now = 0

    def new_dt(self):
        self.now = time.time()
        self.dt = self.now - self.prev_time
        self.prev_time = self.now


dt = DeltaTime()


def events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False

    player.new_pos.x = 0
    player.new_pos.y = 0
    player.new_angle = 0

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player.new_pos.x = math.cos(player.angle) * player.move_distance * dt.dt
        player.new_pos.y = math.sin(player.angle) * player.move_distance * dt.dt
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player.new_pos.x = -math.cos(player.angle) * player.move_distance * dt.dt
        player.new_pos.y = -math.sin(player.angle) * player.move_distance * dt.dt
    if keys[pygame.K_a]:
        player.new_pos.x = math.cos(player.angle - math.pi / 2) * player.move_distance * dt.dt
        player.new_pos.y = math.sin(player.angle - math.pi / 2) * player.move_distance * dt.dt
    if keys[pygame.K_d]:
        player.new_pos.x = math.cos(player.angle + math.pi / 2) * player.move_distance * dt.dt
        player.new_pos.y = math.sin(player.angle + math.pi / 2) * player.move_distance * dt.dt

    if keys[pygame.K_LEFT]:
        player.new_angle -= player.angle_change * dt.dt * 2
    if keys[pygame.K_RIGHT]:
        player.new_angle += player.angle_change * dt.dt * 2

    game_map_tile = game_map.get((int(player.pos.x + player.new_pos.x), int(player.pos.y + player.new_pos.y)))
    if game_map_tile is not None and not game_map_tile:
        player.pos += player.new_pos

    player.angle += player.new_angle

    return True

game_on = True
while game_on:
    clock.tick(60)

    dt.new_dt()

    game_on = events()

    win.fill((0, 0, 0))

    for coords, tile in game_map.items():
        if tile:
            x = coords[0] * tile_size.x
            y = coords[1] * tile_size.y
            pygame.draw.rect(win, (255, 255, 255), pygame.Rect((x, y), (math.ceil(tile_size.x), math.ceil(tile_size.y))))

    distances = dda_ray_casting(rays, rad, distances)

    draw_on_update(distances)

