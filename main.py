import pygame
import asyncio
import pickle
import math
import random

pygame.font.init()
pygame.init()

from scripts.engine import Engine
from scripts.assets import Assets
from scripts.entity import Entity, EntityManager

class SerialisableTile:
    def __init__(self, name, rect):
        self.rect = rect
        self.name = name

class Tile:
    def __init__(self, image, rect):
        self.rect = rect
        self.image = image

    def __repr__(self):
        return "Tile"

class Enemy:
    def __init__(self, image, rect):
        self.rect = rect
        self.image = image

    def __repr__(self):
        return "Enemy"

def deserialize(fi, game):
    with open(fi, "rb") as f:
        return [Tile(game.assets.load_image(tile.name), tile.rect) if tile.name not in ("spike") else Enemy(
            game.assets.load_image(tile.name), tile.rect) for tile in pickle.load(f)]

class Player(Entity):
    def __init__(self, game):
        self.game = game
        self.camera = pygame.math.Vector2(0, 0)
        self.vertical_momentum = 0
        self.moving = False
        self.flipped = False
        self.screenskake_amount = 0
        self.landed = True
        self.landcool = 0
        self.rotation = 0
        self.offwall = False
        self.dash = False
        self.speed = 2
        self.dash_cooldown = 0
        self.dash_end_cooldown = 0
        self.dead= False
        self.new_level = False
        super().__init__(pygame.Rect(self.game.start_positions[self.game.current_level][0], self.game.start_positions[self.game.current_level][1], 16, 16), images=self.game.assets.player_idle)

    def pipe_input(self):
        keys = pygame.key.get_pressed()
        if self.alive:
            self.moving = False
            if keys[pygame.K_d]:
                self.movement.x += self.speed
                self.moving = True
                self.flipped = False
            if keys[pygame.K_a]:
                self.movement.x -= self.speed
                self.moving = True
                self.flipped = True

            if keys[pygame.K_LSHIFT]:
                if not self.dash and self.dash_end_cooldown <= 0:
                    self.dash = True
                    self.dash_cooldown = 25
                    self.dash_end_cooldown = 100
                    self.screenshake(10)
                    self.game.circles.append([pygame.Vector2(self.rect.copy().x+4, self.rect.copy().y+16), 255, 2])

            if keys[pygame.K_SPACE]:
                if self.airtime < 4 or self.hoz > 2:
                    self.landed = False
                    if self.hoz > 2:
                        self.offwall = True
                        self.screenshake(2)
                    self.vertical_momentum = -5   

            if self.dash:
                self.dash_cooldown -= 1
                self.speed = 4
            else:
                self.speed = 2        

            if self.dash_end_cooldown > 0:
                self.dash_end_cooldown -= 1

            if self.dash_cooldown <= 0:
                self.dash = False

            if self.airtime < 2 and not self.landed:
                self.anim_time = 2
                self.images = self.game.assets.player_land
                # self.screenshake(1)

            else:
                self.anim_time = 8
                if self.moving:
                    self.images = self.game.assets.player_walk
                else:
                    self.images = self.game.assets.player_idle

            if self.images == self.game.assets.player_land:
                if self.img_index == 13:
                    self.landed = True
                    self.offwall = False

        else:
            if keys[pygame.K_RETURN]:
                self.rect.x, self.rect.y = self.game.start_positions[self.game.current_level]
                self.alive = True
                self.dead = False
    def screenshake(self, amount):
        self.screenskake_amount = amount

    def update(self):
        self.movement = pygame.Vector2(0, 0)
        self.movement.y += self.vertical_momentum
        self.move(self.game.tiles)

        if self.new_level:
            self.game.current_level += 1
            self.game.tiles = deserialize(self.game.maps[self.game.current_level], self.game)
            self.new_level = False
            self.rect.x = self.game.start_positions[self.game.current_level][0]
            self.rect.y = self.game.start_positions[self.game.current_level][1]

        if not self.collisions["hoz"]:
            self.released = True

        if self.hoz > 0:
            self.engine.display.blit(self.game.marker.surf, (self.rect.x - self.camera.x, self.rect.y - self.camera.y - 16))
            self.hoz -= 1

        if self.screenskake_amount > 0:
            self.camera.x += random.randint(-4, 4)
            self.camera.y += random.randint(-4, 4)
            self.screenskake_amount -= 1

        self.vertical_momentum += 0.2
        if self.vertical_momentum > 3:
            self.vertical_momentum = 3

        if self.airtime > 0 and self.offwall and not (self.collisions["left"] or self.collisions["right"]):
            if self.movement.x > 0:
                self.rotation += 10
            else:
                self.rotation -= 10
        else:
            self.rotation = 0

        if self.airtime > 0:
            if self.collisions["left"] or self.collisions["right"]:
                self.images = self.game.assets.player_onwall

        self.airtime +=1
        self.animate()
        self.camera.x += ((self.rect.x - self.camera.x) - 100) / 15
        self.camera.y += ((self.rect.y - self.camera.y) - 80) / 15
        if self.alive:
            self.engine.display.blit(pygame.transform.flip(pygame.transform.rotate(self.image.surf, self.rotation), self.flipped, False), (self.rect.x - self.camera.x, self.rect.y - self.camera.y))

class Game:
    def __init__(self):
        self.engine = Engine(800, 600, "Game")
        self.assets = Assets("assets")

        self.current_level = 0
        self.maps = ["map1.bin", "map2.bin", "map3.bin", "map4.bin"]
        self.start_positions = [(0, 400), (28, 400), (28, 400), (28, 400)]

        self.assets.load_animation("player_idle",  ["player_idle1",
                                                    "player_idle2",
                                                    "player_idle3",
                                                    "player_idle4",
                                                    "player_idle5",
                                                    "player_idle6",
                                                    "player_idle7"])

        self.assets.load_animation("player_walk",  ["player_walk1",
                                                    "player_walk2",
                                                    "player_walk3",
                                                    "player_walk4"])
        self.assets.load_animation("player_land",  ["player_land1",
                                                    "player_land2",
                                                    "player_land3",
                                                    "player_land4",
                                                    "player_land5",
                                                    "player_land6",
                                                    "player_land7"])
        self.assets.load_animation("bug_flap",  ["bug1",
                                                    "bug2",
                                                    "bug3",
                                                    "bug4",
                                                    "bug5",
                                                    "bug6",
                                                    "bug7"])
        self.assets.load_animation("player_onwall",  ["player_onwall"])

        self.em = EntityManager(self.engine)
        self.player = Player(self)
        self.em.push_entity(self.player)

        self.tiles = deserialize(self.maps[self.current_level], self)

        self.background = self.assets.load_image("background")
        self.mountain = self.assets.load_image("mountain")
        self.mountain_bg = self.assets.load_image("mountain_bg")
        self.marker = self.assets.load_image("maker")
        self.cloud = self.assets.load_image("cloud")
        self.dash_img = self.assets.load_image("player_dash")

        self.clouds = []
        self.particles = []
        self.global_time = 0

        self.dash = []

        self.font = pygame.font.Font("assets/font.ttf", 32)
        self.dead_text = self.font.render("You Died!", False, (255, 255, 255))
        self.small_font = pygame.font.Font("assets/font.ttf", 16)
        self.restart_text = self.small_font.render("Enter to restart...", False, (255, 255, 255))

        self.dead_particles = []
        self.explosions = []
        self.circles = []

        self.bug_index = 0

        self.bullets = []
        self.bug_pattern_1 = [
            [1, 1],
            [1, -1],

            [-1, 1],
            [-1, -1],
        ]
        
    async def main(self):
        while True:
            if self.bug_index + 1 >= len(self.assets.bug_flap) * 5:
                self.bug_index = 0
            self.bug_index += 1

            self.global_time += 1
            self.engine.display.fill((104, 194, 211))
            self.engine.display.blit(self.background.surf, (0, 50))
            # self.engine.display.blit(self.mountain_bg.surf, (-10-self.player.camera.x * 0.2, 50-self.player.camera.y * 0.2))
            self.engine.display.blit(self.mountain.surf, (-20-self.player.camera.x * 0.4, 80-self.player.camera.y * 0.4))

            if random.randrange(0, 100) == 10:
                self.clouds.append([-50, random.randrange(0,  200)])

            if self.player.dash:
                if self.global_time % 2 == 0:
                    self.dash.append([self.player.rect.copy(), 255])

            for d in self.dash:
                img = self.dash_img.surf
                img.set_alpha(d[1])
                d[1] -= 5
                self.engine.display.blit(img, (d[0].x - self.player.camera.x, d[0].y - self.player.camera.y))

            for cloud in self.clouds:
                cloud[0] += 1
                self.engine.display.blit(self.cloud.surf, (cloud[0]-self.player.camera.x * 0.1 , cloud[1]-self.player.camera.y * 0.1))

            for tile in self.tiles:
                if math.dist([tile.rect.x, tile.rect.y], [self.player.rect.x, self.player.rect.y]) < 200:
                    if tile.image.name != "bug1":
                        self.engine.display.blit(tile.image.surf, (tile.rect.x - self.player.camera.x, tile.rect.y - self.player.camera.y))
                    
                    else:
                        if self.global_time % 60 == 0:
                            for bul in self.bug_pattern_1:
                                self.bullets.append([pygame.Vector2(*tile.rect.center), pygame.Vector2(bul[0] * math.sin(self.global_time / 100) * 2, bul[1])])
                        self.engine.display.blit(self.assets.bug_flap[self.bug_index // 5].surf, (tile.rect.x - self.player.camera.x, tile.rect.y - self.player.camera.y))

                if tile.image.name in ("bush1", "bush2"):
                    if random.randrange(0, 1000) == 2:
                        self.particles.append([
                            pygame.Vector2(tile.rect.copy().x + random.randrange(0, 10), tile.rect.copy().y + random.randrange(0, 10)), 100
                        ])

            if random.randrange(0, 2500) == 2:
                self.particles.append([
                    pygame.Vector2(random.randrange(0, 1000), -500), 1000
                ])

            for particle in self.particles:
                if self.global_time % 2 == 0:
                    particle[0].x += math.sin(self.global_time / 50) * 2
                    particle[0].y += 1

                particle[1] -= 1

                if (particle[1]) < 0:
                    self.particles.remove(particle)

                pygame.draw.rect(self.engine.display, (86, 123, 121), (particle[0].x - self.player.camera.x, particle[0].y - self.player.camera.y, 2, 2))

            if not self.player.alive:
                if not self.player.dead:
                    self.player.screenshake(10)
                    self.player.dead = True
                    for i in range(20):
                        self.explosions.append([pygame.Vector2(self.player.rect.copy().x+random.randrange(1, 10), self.player.rect.copy().y+random.randrange(2, 10)), pygame.Vector2(random.randrange(-10, 10), random.randrange(5, 10)), 255, 10])

                self.engine.display.blit(self.dead_text, (30, 50))
                self.engine.display.blit(self.restart_text, (30, 84))


            for e in self.explosions:
                e[0].x += e[1].x
                e[0].y -= e[1].y

                e[1].y -= .6

                e[2] -= 4
                e[3] += 1

                if e[2] < 10:
                    self.explosions.remove(e)

                self.player.screenshake(e[2] / 40)
                
                pygame.draw.circle(self.engine.display, (167, 123, 91, e[2]), (int(e[0].x - self.player.camera.x), int(e[0].y - self.player.camera.y)), e[3], 1)
                pygame.draw.circle(self.engine.display, (167, 123, 91, e[2]), (int(e[0].x - self.player.camera.x), int(e[0].y - self.player.camera.y)), 5)
                self.dead_particles.append([int(e[0].x), int(e[0].y), 2])

            for p in self.dead_particles:
                p[2] -= 0.1
                if p[2] > 0.1:
                    pygame.draw.circle(self.engine.display, (167, 123, 91), (int(p[0] - self.player.camera.x), int(p[1] - self.player.camera.y)), int(p[2]))

            for circle in self.circles:
                circle[2] += 1
                circle[1] -= 10
                if  circle[1] < 10:
                    self.circles.remove(circle)

                pygame.draw.circle(self.engine.display, (255, 255, 255, circle[1]), (int(circle[0].x - self.player.camera.x), int(circle[0].y - self.player.camera.y)), circle[2], 1)

            if self.current_level == 0:
                text = self.small_font.render("WASD + Space", False, (255, 255, 255))
                self.engine.display.blit(text, (-65-self.player.camera.x, 400-self.player.camera.y))

                text = self.small_font.render("Jump tp climb walls", False, (255, 255, 255))
                self.engine.display.blit(text, (-85-self.player.camera.x, 300-self.player.camera.y))

                text = self.small_font.render("Shift to dash", False, (255, 255, 255))
                self.engine.display.blit(text, (-85-self.player.camera.x, 0-self.player.camera.y))

            for bullet in self.bullets:
                bullet[0].x += bullet[1].x
                bullet[0].y += bullet[1].y

                if pygame.Rect(bullet[0].x, bullet[0].y, 2, 2).colliderect(self.player.rect):
                    self.player.alive = False

                pygame.draw.circle(self.engine.display, (255, 0, 0, 100), (int(bullet[0].x - self.player.camera.x), int(bullet[0].y - self.player.camera.y)), 6)
                pygame.draw.circle(self.engine.display, (255, 0, 0), (int(bullet[0].x - self.player.camera.x), int(bullet[0].y - self.player.camera.y)), 2)

            self.em.update()
            self.engine.handle_event_triggers()
            self.engine.update()
            pygame.display.set_caption(f"{self.engine.clock.get_fps()}")
            await asyncio.sleep(0)

asyncio.run(Game().main())