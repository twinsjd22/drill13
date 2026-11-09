from pico2d import *
import game_framework
import game_world
import play_mode

ITEM_KEYS = {SDLK_0: 0, SDLK_1: 1, SDLK_2: 2}  # 볼 없음, 작은 볼, 큰 볼


def init():
    global image
    image = load_image('item_select.png')
    play_mode.boy.stop()  # 인벤토리 동안 캐릭터는 움직일 수 없다


def finish():
    global image
    del image


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key in (SDLK_i, SDLK_ESCAPE):
                game_framework.pop_mode()
            elif event.key in ITEM_KEYS:
                play_mode.boy.item = ITEM_KEYS[event.key]
                game_framework.pop_mode()


def update():
    game_world.update()  # 게임은 계속 진행된다


def render():
    clear_canvas()
    game_world.render()
    image.draw(400, 300)  # 화면 중앙에 인벤토리 표시
    update_canvas()


def pause():
    pass


def resume():
    pass
