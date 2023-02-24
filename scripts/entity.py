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
            if tile.rect.colliderect(self.rect):
                return_list.append(tile)

        return return_list

    def move(self, tiles):
        self.movement = pygame.Vector2(0, 0)
        self.pipe_input()
        self.rect.x += self.movement.x
        for tile in self.get_collisions(tiles):
            if self.movement.x > 0:
                self.rect.right = tile.left

            if self.movement < 0:
                self.rect.left = tile.right

        self.rect.y += self.movement.y
        for tile in self.get_collisions(tiles):
            if self.movement.y > 0:
                self.rect.bottom = tile.top

            if self.movement < 0:
                self.rect.top = tile.bottom

    def update(self):
        pass