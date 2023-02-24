import pygame

class Image:
    def __init__(self, surf, path, name):
        self.surf = surf
        self.path = path
        self.name = name

    def __repr__(self):
        return self.path

class Assets:
    def __init__(self, asset_path):
        self.asset_path = asset_path
        self.images = {}
        self.animations = {}

    def load_image(self, filename):
        path = f"{self.asset_path}/images/{filename}.png"
        image = pygame.image.load(path).convert()
        image.set_colorkey((255, 255, 255))
        return Image(image, path, f"{filename}")

    def load_images(self, images):
        return {image: self.load_image(image) for image in images}

    def load_single_images(self, images):
        self.images = self.load_images(images)

    def load_animation(self, name, images):
        self.animations[name] = [image for image in self.load_images(images).values()]

    def __getattr__(self, name):
        if self.images.get(name, False):
            return self.images.get(name)
        return self.animations.get(name, None)


