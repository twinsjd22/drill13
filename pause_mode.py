import game_framework
import game_world
from pico2d import *


def init():
    pass


def finish():
    pass


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            game_framework.pop_mode()


def update():
    pass  # 월드를 업데이트하지 않으므로 화면이 멈춘다


def render():
    clear_canvas()
    game_world.render()  # 멈춘 play 화면을 그대로 그린다
    draw_rectangle(300, 250, 500, 350)  # 일시 정지 표시
    update_canvas()
