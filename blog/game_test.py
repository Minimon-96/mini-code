import pygame
import sys
import time

# 초기 설정
pygame.init()
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Simple Block Game')

# 색상 정의
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)

# 플레이어 설정
player_size = 30
player_velocity = [0, 0]
player_speed = 15
moving = False

# 라운드 별 맵 데이터
rounds = [
    {
        "player_pos": [50, 50],
        "walls": [[100, 100, 100, 30], [200, 200, 100, 30]],  # [x, y, width, height]
        "target": [500, 400, 30, 30],
    },
    {
        "player_pos": [100, 400],
        "walls": [[300, 100, 100, 30], [400, 300, 100, 30]],
        "target": [100, 50, 30, 30],
    }
]

current_round = 0  # 현재 라운드 인덱스

# 라운드 정보를 기반으로 게임 상태 초기화
def setup_round(round_data):
    global player_pos, player_velocity, moving
    player_pos = round_data["player_pos"].copy()
    player_velocity = [0, 0]
    moving = False

wall_pos_size, target_pos_size = setup_round(rounds[current_round])

clock = pygame.time.Clock()

def check_collision(p_pos, obj_pos, obj_size):
    if (p_pos[0] + player_size > obj_pos[0]) and (p_pos[0] < obj_pos[0] + obj_size[0]) and (p_pos[1] + player_size > obj_pos[1]) and (p_pos[1] < obj_pos[1] + obj_size[1]):
        return True
    return False

def check_wall_collision(p_pos, walls):
    for wall in walls:
        if check_collision(p_pos, wall[:2], wall[2:4]):
            return True
    return False

# 게임 메인 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not moving:
            if event.key == pygame.K_LEFT:
                player_velocity = [-player_speed, 0]
                moving = True
            elif event.key == pygame.K_RIGHT:
                player_velocity = [player_speed, 0]
                moving = True
            elif event.key == pygame.K_UP:
                player_velocity = [0, -player_speed]
                moving = True
            elif event.key == pygame.K_DOWN:
                player_velocity = [0, player_speed]
                moving = True

    player_pos[0] += player_velocity[0]
    player_pos[1] += player_velocity[1]


    # 화면 밖으로 나갔는지 체크
    if player_pos[0] < 0 or player_pos[0] + player_size > width or player_pos[1] < 0 or player_pos[1] + player_size > height:
        setup_round(rounds[current_round])  # 현재 라운드 재시작

    # 벽에 부딪혔는지 체크
    if check_wall_collision(player_pos, wall_pos_size):
        setup_round(rounds[current_round])  # 현재 라운드 재시작

    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, (player_pos[0], player_pos[1], player_size, player_size))
    for wall in wall_pos_size:
        pygame.draw.rect(screen, GRAY, wall)
    pygame.draw.rect(screen, BLUE, target_pos_size)

    if check_collision(player_pos, target_pos_size[:2], target_pos_size[2:4]):
        print("You Win!")
        time.sleep(3)
        current_round = (current_round + 1) % len(rounds)  # 다음 라운드로 이동
        setup_round(rounds[current_round])

    pygame.display.update()
    clock.tick(30)

pygame.quit()
