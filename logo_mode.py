import game_framework
from pico2d import *
import title_mode


def init():
    global image
    global logo_start_time

    image = load_image('tuk_credit.png')
    logo_start_time = get_time()


def finish():
    global image
    del image


def handle_events():
    events = get_events()

def update():
    if get_time() - logo_start_time >= 2.0:
        game_framework.change_mode(title_mode)


def render():
    clear_canvas()
    image.draw(400, 300)
    update_canvas()
