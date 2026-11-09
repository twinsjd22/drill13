from pico2d import *
import game_framework
import game_world
import title_mode
import pause_mode
import inventory_mode
from boy import Boy
from grass import Grass


def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            game_framework.push_mode(pause_mode)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            game_framework.push_mode(inventory_mode)
        else:
            boy.handle_event(event)


def init():
    global boy

    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)


def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()


def pause():
    # 다른 모드가 위에 쌓이면 키 입력(KEYUP 포함)이 캐릭터에 전달되지 않으므로
    # 눌린 키 상태를 비우고 멈춰 세운다 (일시정지·인벤토리 공통)
    boy.stop()


def resume():
    pass
