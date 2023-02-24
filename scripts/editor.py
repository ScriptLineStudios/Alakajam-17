import pygame
from assets import Assets
import pickle

class SerialisableTile:
    def __init__(self, name, rect):
        self.rect = rect
        self.name = name

class Tile:
    def __init__(self, image, rect):
        self.rect = rect
        self.image = image

class Editor:
    def __init__(self):
        self.display = pygame.display.set_mode((800, 800))
        self.clock = pygame.time.Clock()
        self.assets = Assets("assets")
        self.tiles = []
        with open("map.bin", "rb") as f:
            self.tiles = [Tile(self.assets.load_image(tile.name), tile.rect) for tile in pickle.load(f)]
        self.draw = False
        self.erase = False
        self.images = [
            self.assets.load_image("block1"),
            self.assets.load_image("block1"),
        ]

        self.selected = self.images[0]
        self.selected_name = self.images[0]

        self.offset = pygame.math.Vector2(0, 0)

    def serialize_tiles(self):
        return [SerialisableTile(tile.image.name, tile.rect) for tile in self.tiles]

    def update(self):
        while True:
            self.display.fill((0, 0, 0))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    with open("map.bin", "wb") as f:
                        pickle.dump(self.serialize_tiles(), f)
                    raise SystemExit

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.draw = True
                    if event.button == 3:
                        self.erase = True

                if  event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.draw = False
                    if event.button == 3:
                        self.erase = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                self.offset.x -= 2
            if keys[pygame.K_a]:
                self.offset.x += 2
            if keys[pygame.K_s]:
                self.offset.y -= 2
            if keys[pygame.K_w]:
                self.offset.y += 2

            if self.draw:
                pos = list(pygame.mouse.get_pos())
                if pos[1] > 200:
                    pos[0] -= self.offset.x
                    pos[1] -= self.offset.y

                    self.tiles.append(Tile(self.selected, pygame.Rect((pos[0] // 16) * 16, (pos[1] // 16) * 16, 16, 16)))


            for i, tile in enumerate(self.tiles):
                pos = pygame.mouse.get_pos()

                if pygame.Rect((tile.rect.x + self.offset.x, tile.rect.y + self.offset.y, tile.rect.width, tile.rect.height)).collidepoint(pos):
                    if self.erase:
                        self.tiles.remove(tile)

                self.display.blit(tile.image.surf, (tile.rect.x + self.offset.x, tile.rect.y + self.offset.y, tile.rect.width, tile.rect.height))

            pygame.draw.rect(self.display, (100, 100, 100), (0, 0, 800, 200))
            for i, image in enumerate(self.images):
                pos = pygame.mouse.get_pos()

                size = 32
                if pygame.Rect(i * 42, 16, 32, 32).collidepoint(pos):
                    size = 35
                else:
                    size = 32
                self.display.blit(pygame.transform.scale(image.surf, (size, size)), (i * 42, 16))

            pygame.display.update()
            self.clock.tick()

Editor().update()
