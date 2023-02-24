import pygame
import asyncio

from scripts.engine import Engine
from scripts.assets import Assets
from scripts.entity import Entity, EntityManager

engine = Engine(800, 600, "Game")
assets = Assets("assets")

assets.load_single_images(["block1"])
assets.load_animation("player_run", ["block1", "block2"])

class Player(Entity):
    def __init__(self):
        super().__init__(pygame.Rect(0, 0, 16, 16), assets.player_run)
        self.images = assets.player_run
        
    def pipe_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.movement.x += 1
        if keys[pygame.K_a]:
            self.movement.x -= 1

    def update(self):
        self.move([])
        self.animate()
        print(self.img_index, self.images)
        self.engine.display.blit(self.image, self.rect)

em = EntityManager(engine)
em.push_entity(Player())

async def main():
    while True:
        engine.display.fill((0, 0, 0))

        em.update()
        engine.handle_event_triggers()
        engine.update()
        pygame.display.set_caption(f"{engine.clock.get_fps()}")
        await asyncio.sleep(0)

asyncio.run(main())