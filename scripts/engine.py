import pygame
import collections
event_triggers = collections.defaultdict(set)

def called_by(*args):
    def inner(func):
        for arg in args:
            event_triggers[arg].add(func)

    return inner

class Engine:
    def __init__(self, width, height, title, zoom=4, fps=60):
        self.width = width
        self.height = height
        self.title = title
        self.zoom = zoom

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.display = pygame.Surface((self.width / self.zoom, self.height / self.zoom))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.events = None

    def called_by(*args):
        def inner(func):
            for arg in args:
               event_triggers[arg].add(func)

        return inner

    @called_by(pygame.QUIT)
    def stop(event):
        raise SystemExit

    def handle_event_triggers(self):
        self.events = pygame.event.get()
        for event in self.events:
            if event_triggers.get(event.type) is not None:
                for function in event_triggers.get(event.type):
                    function(event)

    def update(self):
        self.screen.blit(pygame.transform.scale(self.display, (self.width, self.height)), (0, 0))
        pygame.display.update()
        self.clock.tick(self.fps)