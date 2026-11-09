# PRD: 인벤토리 모드 추가

## 1. 개요

플레이 중 `I` 키로 인벤토리 화면을 띄워, 캐릭터(Boy)가 발사할 공의 종류(볼 없음 / 작은 볼 / 큰 볼)를 고를 수 있게 한다.
인벤토리가 열려 있어도 게임 월드는 계속 진행되며, 캐릭터만 조작할 수 없다.

- 원본 요구사항: [PRE_PRD.md](PRE_PRD.md)
- 대상 프로젝트: pico2d 기반 2D 게임 (`logo_mode → title_mode → play_mode`, `pause_mode`)

## 2. 현재 구조 요약

| 파일 | 역할 | 이번 작업과의 관계 |
|---|---|---|
| [game_framework.py](game_framework.py) | 모드 스택 관리 (`change_mode`, `push_mode`, `pop_mode`) | `push_mode`/`pop_mode`로 인벤토리를 띄우고 닫는다 |
| [game_world.py](game_world.py) | 3개 레이어(배경/오브젝트/UI)의 update·render | 인벤토리 모드에서도 `update()`를 호출해 게임을 진행시킨다 |
| [play_mode.py](play_mode.py) | 메인 플레이. `boy`를 모듈 전역으로 가짐 | `I` 키 처리 추가 |
| [pause_mode.py](pause_mode.py) | `P` 키 일시정지. `update()`를 하지 않아 화면이 멈춤 | 인벤토리 모드의 참고 구현 (차이점: 인벤토리는 update를 **한다**) |
| [boy.py](boy.py) | 상태 머신(IDLE / SLEEP / RUN), `SPACE`로 공 발사, IDLE 5초 후 SLEEP | 선택된 공 종류 보관, 발사 로직 변경, 조작 차단 시 상태 정리 |
| [ball.py](ball.py) | `ball21x21.png`로 고정된 공 | 크기(이미지) 선택 가능하도록 변경 |
| `item_select.png` | 272×215 인벤토리 UI 이미지 ("Press '0' to Clear / '1' for 작은 공 / '2' for 큰 공") | 인벤토리 화면 배경으로 사용 |
| `ball21x21.png`, `ball41x41.png` | 작은 볼 / 큰 볼 이미지 | 공 종류별 이미지 |

## 3. 기능 요구사항

### FR-1. 인벤토리 열기 / 닫기
- 플레이 모드에서 `I` 키를 누르면 `game_framework.push_mode(inventory_mode)`로 인벤토리 모드에 진입한다.
- 인벤토리 모드에서 다음 경우 `game_framework.pop_mode()`로 플레이 모드로 돌아간다.
  - `0`, `1`, `2` 중 하나로 공을 선택했을 때 (선택 즉시 적용 후 닫힘)
  - `I` 키 또는 `ESC` 키를 눌렀을 때 (선택 변경 없이 닫힘)
- 인벤토리 모드에서 `ESC`는 타이틀로 가지 않고 인벤토리만 닫는다.
- 창 닫기(`SDL_QUIT`)는 어느 모드에서든 게임을 종료한다.

### FR-2. 인벤토리 화면 표시
- 매 프레임 `clear_canvas()` → `game_world.render()` → 인벤토리 이미지 → `update_canvas()` 순으로 그린다.
- 인벤토리 이미지(`item_select.png`)는 화면 중앙 `(400, 300)`에 직사각형으로 그려, 주변에 게임 화면이 계속 보이게 한다.
- 이미지 로드는 인벤토리 모드의 `init()`에서 하고 `finish()`에서 해제한다 (`title_mode`, `logo_mode`와 동일 패턴).

### FR-3. 공 종류 선택
| 키 | 선택 | 발사 시 동작 |
|---|---|---|
| `0` | 볼 없음 | `SPACE`를 눌러도 공이 발사되지 않는다 |
| `1` | 작은 볼 | `ball21x21.png` 공 발사 |
| `2` | 큰 볼 | `ball41x41.png` 공 발사 |

- 게임 시작 시 기본값은 **작은 볼(1)** 로 하여 기존 동작을 유지한다.
- 선택 값은 `Boy` 인스턴스가 보관한다 (예: `boy.item`). 인벤토리 모드는 `play_mode.boy`를 통해 값을 바꾼다.
- 선택은 **이후 발사되는 공에만** 적용되고, 이미 날아가는 공은 바뀌지 않는다.
- 볼 없음 상태에서도 SLEEP 상태의 캐릭터를 `SPACE`로 깨우는 동작은 그대로 유지한다.

### FR-4. 인벤토리 중 게임 진행 / 캐릭터 조작 차단
- 인벤토리 모드의 `update()`는 `game_world.update()`를 호출한다. 따라서:
  - 이미 발사된 공은 계속 날아가고 화면 밖으로 나가면 제거된다.
  - 캐릭터의 IDLE 타이머가 계속 흘러, 5초가 지나면 SLEEP(눕기) 상태로 바뀐다.
- 인벤토리 모드는 키 이벤트를 `boy.handle_event()`로 넘기지 않는다. 방향키·`SPACE` 입력은 캐릭터에 영향을 주지 않는다.
- **RUN 중 인벤토리 진입 처리**: 달리는 중에 `I`를 누르면 update가 계속되므로 캐릭터가 계속 달려 버린다. 이를 막기 위해 인벤토리 진입 시 캐릭터를 정지시킨다.
  - `pressed_keys`를 비우고 `dir = 0`으로 만든다.
  - 상태가 RUN이면 `stop_run()`으로 IDLE로 전환한다 (IDLE 타이머가 이 시점부터 시작되어 5초 후 눕는다).
  - 이 처리는 `Boy`에 메서드(예: `boy.stop()`)로 두고 인벤토리 모드 `init()`에서 호출한다.
- 인벤토리 중에 놓은 방향키의 `KEYUP`은 캐릭터에 전달되지 않으므로, 위와 같이 `pressed_keys`를 비워 복귀 후 키가 눌린 채로 남는 문제를 방지한다.

## 4. 구현 설계

### 4.1 `ball.py`
- 생성자에 크기 인자를 추가한다. 예: `Ball(x, y, velocity, size)` (`size`: 1 = 작은 볼, 2 = 큰 볼).
- 이미지는 크기별로 클래스 변수에 한 번만 로드해 캐싱한다 (예: `Ball.images = {1: ..., 2: ...}`).

### 4.2 `boy.py`
- `self.item = 1` 속성 추가 (0: 없음, 1: 작은 볼, 2: 큰 볼).
- `fire_ball()`: `self.item == 0`이면 아무것도 하지 않고, 그 외에는 `Ball(self.x, self.y, self.face_dir * 10, self.item)` 생성.
- `stop()` 메서드 추가: `pressed_keys` 초기화, `dir = 0`, RUN이면 `stop_run()`.

### 4.3 `inventory_mode.py` (신규)
```python
from pico2d import *
import game_framework
import game_world
import play_mode


def init():
    global image
    image = load_image('item_select.png')
    play_mode.boy.stop()


def finish():
    global image
    del image


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key in (SDLK_i, SDLK_ESCAPE):
                game_framework.pop_mode()
            elif event.key in (SDLK_0, SDLK_1, SDLK_2):
                play_mode.boy.item = event.key - SDLK_0
                game_framework.pop_mode()


def update():
    game_world.update()          # 게임은 계속 진행


def render():
    clear_canvas()
    game_world.render()
    image.draw(400, 300)         # 화면 중앙 인벤토리
    update_canvas()


def pause(): pass
def resume(): pass
```

### 4.4 `play_mode.py`
- `handle_events()`에 `SDL_KEYDOWN and event.key == SDLK_i` → `game_framework.push_mode(inventory_mode)` 분기 추가.
- `import inventory_mode` 추가 (`inventory_mode`가 `play_mode`를 import하는 순환 import는 함수 안에서만 참조하므로 문제 없음 — 기존 `title_mode ↔ play_mode`와 같은 구조).

## 5. 범위 밖 (Non-Goals)
- 인벤토리 안에서 마우스 조작, 커서 하이라이트 등 추가 UI
- 공의 속도·궤적·충돌 변경
- 선택한 공 종류의 저장(재시작 후 유지)
- `pause_mode` 동작 변경

## 6. 수용 기준 (테스트 시나리오)

| # | 시나리오 | 기대 결과 |
|---|---|---|
| 1 | 플레이 중 `I` | 화면 중앙에 인벤토리가 뜨고, 뒤로 잔디·캐릭터가 보인다 |
| 2 | 인벤토리에서 `I` 또는 `ESC` | 인벤토리가 닫히고 플레이로 복귀, 공 종류 변화 없음 |
| 3 | 인벤토리에서 `2` → `SPACE` | 큰 볼이 발사된다 |
| 4 | 인벤토리에서 `1` → `SPACE` | 작은 볼이 발사된다 |
| 5 | 인벤토리에서 `0` → `SPACE` | 공이 발사되지 않는다 |
| 6 | 볼 없음 상태에서 캐릭터가 잠든 뒤 `SPACE` | 캐릭터가 깨어난다 |
| 7 | `SPACE`로 공 발사 직후 `I` | 공은 계속 날아가 화면 밖에서 사라진다 |
| 8 | 인벤토리를 연 채 5초 대기 | 캐릭터가 눕는다(SLEEP) |
| 9 | 인벤토리 중 방향키 / `SPACE` | 캐릭터가 움직이거나 공을 쏘지 않는다 |
| 10 | 방향키로 달리는 중 `I` | 캐릭터가 즉시 멈추고, 5초 후 눕는다 |
| 11 | 달리는 중 `I` → 인벤토리에서 방향키 떼기 → 닫기 | 복귀 후 캐릭터가 저절로 달리지 않는다 |
| 12 | 인벤토리 중 창 닫기 | 게임이 정상 종료된다 |
| 13 | 시작 직후 아무 선택 없이 `SPACE` | 기존처럼 작은 볼이 발사된다 |

## 7. 작업 및 커밋 계획

커밋은 기능 단위로 나누고, 메시지는 한글로 작성한다. 각 커밋 시점에 게임이 실행 가능한 상태를 유지한다.

| 순서 | 작업 | 커밋 메시지(예시) |
|---|---|---|
| 1 | PRE_PRD.md, PRD.md 추가 | `인벤토리 모드 요구사항 및 PRD 문서 추가` |
| 2 | `Ball`에 크기 인자 및 이미지 캐싱 추가 (기본 동작은 작은 볼) | `공 크기 선택 기능 추가` |
| 3 | `Boy`에 `item` 속성, 볼 없음 처리, `stop()` 메서드 추가 | `캐릭터에 공 종류 선택 상태와 정지 기능 추가` |
| 4 | `inventory_mode.py` 신규 작성 | `인벤토리 모드 추가` |
| 5 | `play_mode`에서 `I` 키로 인벤토리 진입 연결 | `플레이 모드에서 I 키로 인벤토리 열기 연결` |
| 6 | 수용 기준 점검 후 필요한 수정 | `인벤토리 모드 동작 수정` (필요 시) |
