import game_framework
from pico2d import *
import play_mode


def init():
    global image
    image = load_image('title.png')


def finish():
    global image
    del image


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            game_framework.change_mode(play_mode)


def update():
    pass


def render():
    clear_canvas()
    image.draw(400, 300)
    update_canvas()
