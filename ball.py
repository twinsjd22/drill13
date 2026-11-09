from pico2d import get_canvas_width, load_image

import game_world

SMALL, BIG = 1, 2
IMAGE_FILES = {SMALL: 'ball21x21.png', BIG: 'ball41x41.png'}


class Ball:
    images = {}

    def __init__(self, x, y, velocity, size=SMALL):
        if size not in Ball.images:
            Ball.images[size] = load_image(IMAGE_FILES[size])
        self.image = Ball.images[size]
        self.x, self.y = x, y
        self.velocity = velocity

    def update(self):
        self.x += self.velocity
        if self.x < 0 or self.x > get_canvas_width():
            game_world.remove_object(self)

    def draw(self):
        self.image.draw(self.x, self.y)
