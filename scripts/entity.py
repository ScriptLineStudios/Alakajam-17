import pygame

class EntityManager:
    def __init__(self, engine):
        self.entities = []
        self.engine = engine

    def push_entity(self, entity):
        entity.engine = self.engine
        self.entities.append(entity)

    def update(self):
        for entity in self.entities:
            entity.update()

class Entity:
    def __init__(self, rect, engine=None, images=[]):
        self.rect = rect
        self.movement = pygame.Vector2(0, 0)
        self.images = images
        self.img_index = 0
        self.anim_time = 15
        self.engine = engine
        self.airtime = 0    
        self.collisions = {"left": False, "right": False}
        self.hoz = 0
        self.released = True

    def animate(self):
        if self.img_index + 1 >= len(self.images) * self.anim_time:
            self.img_index = 0
        self.img_index += 1

    @property
    def image(self):
        return self.images[self.img_index // self.anim_time]

    def pipe_input():
        pass

    def get_collisions(self, tiles):
        return_list = []
        for tile in tiles:
            if tile.rect.colliderect(self.rect) and tile.image.name not in ("bush1", "bush2"):
                return_list.append(tile)

        return return_list

    def move(self, tiles):
        self.collisions = {"left": False, "right": False, "hoz": False}

        self.pipe_input()
        self.rect.x += self.movement.x
        for tile in self.get_collisions(tiles):
            if self.movement.x > 0:
                self.rect.right = tile.rect.left
                self.collisions["right"] = True
                self.collisions["hoz"] = True
                if self.hoz <= 0 and self.released:
                    self.hoz = 12
                    self.released = False

            if self.movement.x < 0:
                self.rect.left = tile.rect.right
                self.collisions["left"] = True
                self.collisions["hoz"] = True
                if self.hoz <= 0 and self.released:
                    self.hoz = 12
                    self.released = False

        self.rect.y += self.movement.y
        for tile in self.get_collisions(tiles):
            if self.movement.y > 0:
                self.rect.bottom = tile.rect.top
                self.airtime = 0

            if self.movement.y < 0:
                self.rect.top = tile.rect.bottom

    def update(self):
        pass