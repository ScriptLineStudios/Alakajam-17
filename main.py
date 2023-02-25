import pygame
import asyncio
import pickle
import math
import random

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

def deserialize(fi, game):
    with open(fi, "rb") as f:
        return [Tile(game.assets.load_image(tile.name), tile.rect) for tile in pickle.load(f)]

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
        super().__init__(pygame.Rect(18, 250, 14, 16), images=self.game.assets.player_idle)

    def pipe_input(self):
        self.moving = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.movement.x += 2
            self.moving = True
            self.flipped = False
        if keys[pygame.K_a]:
            self.movement.x -= 2
            self.moving = True
            self.flipped = True

        if keys[pygame.K_SPACE]:
            if self.airtime < 4 or self.hoz > 2:
                self.landed = False
                if self.hoz > 2:
                    self.offwall = True
                    self.screenshake(2)
                self.vertical_momentum = -5   

        if self.airtime < 2 and not self.landed:
            self.anim_time = 2
            self.images = self.game.assets.player_land

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


    def screenshake(self, amount):
        self.screenskake_amount = amount

    def update(self):
        self.movement = pygame.Vector2(0, 0)
        self.movement.y += self.vertical_momentum
        self.move(self.game.tiles)

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
        self.engine.display.blit(pygame.transform.flip(pygame.transform.rotate(self.image.surf, self.rotation), self.flipped, False), (self.rect.x - self.camera.x, self.rect.y - self.camera.y))

class Game:
    def __init__(self):
        self.engine = Engine(800, 600, "Game")
        self.assets = Assets("assets")

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
        self.assets.load_animation("player_onwall",  ["player_onwall"])

        self.em = EntityManager(self.engine)
        self.player = Player(self)
        self.em.push_entity(self.player)

        self.tiles = deserialize("map.bin", self)

        self.background = self.assets.load_image("background")
        self.mountain = self.assets.load_image("mountain")
        self.marker = self.assets.load_image("maker")
        self.cloud = self.assets.load_image("cloud")

        self.clouds = []
        self.particles = []
        self.global_time = 0
        
    async def main(self):
        while True:
            self.global_time += 1
            self.engine.display.fill((104, 194, 211))
            self.engine.display.blit(self.background.surf, (0, 50))
            self.engine.display.blit(self.mountain.surf, (-10-self.player.camera.x * 0.2, 50-self.player.camera.y * 0.2))

            if random.randrange(0, 100) == 10:
                self.clouds.append([-50, random.randrange(0,  200)])

            for cloud in self.clouds:
                cloud[0] += 1
                self.engine.display.blit(self.cloud.surf, (cloud[0]-self.player.camera.x * 0.1 , cloud[1]-self.player.camera.y * 0.1))

            for tile in self.tiles:
                if math.dist([tile.rect.x, tile.rect.y], [self.player.rect.x, self.player.rect.y]) < 200:
                    self.engine.display.blit(tile.image.surf, (tile.rect.x - self.player.camera.x, tile.rect.y - self.player.camera.y))

                if tile.image.name in ("bush1", "bush2"):
                    if random.randrange(0, 1000) == 2:
                        self.particles.append([
                            pygame.Vector2(tile.rect.copy().x + random.randrange(0, 10), tile.rect.copy().y + random.randrange(0, 10)), 100
                        ])

            for particle in self.particles:
                if self.global_time % 2 == 0:
                    particle[0].x += math.sin(self.global_time / 50) * 2
                    particle[0].y += 1

                particle[1] -= 1

                if (particle[1]) < 0:
                    self.particles.remove(particle)

                pygame.draw.rect(self.engine.display, (86, 123, 121), (particle[0].x - self.player.camera.x, particle[0].y - self.player.camera.y, 2, 2))



            self.em.update()
            self.engine.handle_event_triggers()
            self.engine.update()
            pygame.display.set_caption(f"{self.engine.clock.get_fps()}")
            await asyncio.sleep(0)

asyncio.run(Game().main())