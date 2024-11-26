import pygame
import random
import sys
import ctypes

# pygameの初期化
pygame.init()

# ウィンドウサイズの設定
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# フォントの設定
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)

# タイトルの設定
pygame.display.set_caption("インベーダーゲーム")

# FPSの設定
clock = pygame.time.Clock()
FPS = 60

# スコアの初期化
score_value = 0
high_score = 0

def show_score():
    score = font.render(f"Score: {score_value}", True, (255, 255, 255))
    screen.blit(score, (10, 10))

def show_high_score():
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (600, 10))

# プレイヤーの設定
player_width = 60
player_height = 40
playerX = (screen_width - player_width) / 2
playerY = screen_height - player_height - 10
player_speed = 5

def player(x, y, color=(0, 255, 0)):
    pygame.draw.rect(screen, color, (x, y, player_width, player_height))

# シールドの設定
shields = []
shield_width = 80
shield_height = 60
shield_color = (0, 255, 0)
shield_health = 10
num_of_shields = 4
for i in range(num_of_shields):
    x = 100 + i * 175
    y = playerY - shield_height - 20
    shields.append({"rect": pygame.Rect(x, y, shield_width, shield_height), "health": shield_health})

def draw_shields():
    for shield in shields:
        if shield["health"] > 0:
            pygame.draw.rect(screen, shield_color, shield["rect"])

# 敵の設定
enemy_rows = 5
enemy_cols = 11
enemy_width = 40
enemy_height = 30
enemy_padding = 10
enemy_offset_x = (screen_width - (enemy_cols * (enemy_width + enemy_padding))) / 2
enemy_offset_y = 50
enemy_list = []
enemy_speed = 1
enemy_direction = 1  # 1:右移動, -1:左移動

def create_enemies():
    for row in range(enemy_rows):
        for col in range(enemy_cols):
            x = enemy_offset_x + col * (enemy_width + enemy_padding)
            y = enemy_offset_y + row * (enemy_height + enemy_padding)
            rect = pygame.Rect(x, y, enemy_width, enemy_height)
            enemy_list.append({"rect": rect, "row": row})

def draw_enemies():
    for enemy in enemy_list:
        if enemy["row"] == 0:
            color = (255, 0, 0)  # 上段の敵
        elif enemy["row"] == 1 or enemy["row"] == 2:
            color = (255, 165, 0)  # 中段の敵
        else:
            color = (255, 255, 0)  # 下段の敵
        pygame.draw.rect(screen, color, enemy["rect"])

create_enemies()

# 敵の弾の設定
enemy_bullets = []
enemy_bullet_width = 4
enemy_bullet_height = 20
enemy_bullet_speed = 4

# プレイヤーの弾の設定
bullet_width = 4
bullet_height = 20
bullet_speed = 7
bullet_state = "ready"  # "ready" または "fire"
bullet_list = []  # 複数の弾を管理

active_powerups = []
powerup_start_times = {}
powerup_duration = 10000  # パワーアップの持続時間（ミリ秒）

# パワーアップアイテムの設定
powerups = []
powerup_types = ["spread", "bounce"]
def create_powerup(x, y):
    powerup = {
        "rect": pygame.Rect(x, y, 30, 30),
        "type": random.choice(powerup_types),
        "speed": 2,
        "active": True
    }
    powerups.append(powerup)

def draw_powerups():
    for powerup in powerups:
        if powerup["type"] == "spread":
            color = (0, 0, 255)
        elif powerup["type"] == "bounce":
            color = (0, 255, 255)
        pygame.draw.rect(screen, color, powerup["rect"])

# UFOの設定
ufo_active = False
ufo_width = 60
ufo_height = 30
ufoX = 0
ufoY = 50
ufo_speed = 2

def draw_ufo(x, y):
    pygame.draw.rect(screen, (255, 0, 255), (x, y, ufo_width, ufo_height))

# 効果音の設定（Windowsのシステムサウンドを使用）
def play_sound(sound_name):
    if sound_name == "shoot":
        ctypes.windll.winmm.mciSendStringW('play SystemAsterisk', None, 0, None)
    elif sound_name == "explosion":
        ctypes.windll.winmm.mciSendStringW('play SystemExclamation', None, 0, None)
    elif sound_name == "powerup":
        ctypes.windll.winmm.mciSendStringW('play SystemNotification', None, 0, None)
    elif sound_name == "ufo":
        ctypes.windll.winmm.mciSendStringW('play SystemHand', None, 0, None)

# ゲームオーバーフラグ
game_over = False

# メインループ
running = True
while running:
    dt = clock.tick(FPS)
    screen.fill((0, 0, 0))
    show_score()
    show_high_score()
    draw_shields()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # キー入力処理
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_move_left = True
            if event.key == pygame.K_RIGHT:
                player_move_right = True
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready":
                    play_sound("shoot")
                    bullet_state = "fire"
                    positions = [playerX + player_width / 2 - bullet_width / 2]
                    if "spread" in active_powerups:
                        positions = [playerX + 10, playerX + player_width / 2 - bullet_width / 2, playerX + player_width - 10]
                    for pos in positions:
                        bullet = {
                            "rect": pygame.Rect(pos, playerY, bullet_width, bullet_height),
                            "speed": bullet_speed,
                            "state": "normal"
                        }
                        if "bounce" in active_powerups:
                            bullet["state"] = "bounce"
                        bullet_list.append(bullet)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                player_move_left = False
            if event.key == pygame.K_RIGHT:
                player_move_right = False

    # プレイヤーの移動
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        playerX -= player_speed
    if keys[pygame.K_RIGHT]:
        playerX += player_speed
    playerX = max(0, min(playerX, screen_width - player_width))

    # パワーアップ効果の時間管理
    current_time = pygame.time.get_ticks()
    for p_type in list(active_powerups):
        if current_time - powerup_start_times[p_type] > powerup_duration:
            active_powerups.remove(p_type)
            del powerup_start_times[p_type]

    # プレイヤーの描画（パワーアップに応じて色を変更）
    if not active_powerups:
        player_color = (0, 255, 0)
    else:
        colors = []
        if "spread" in active_powerups:
            colors.append((0, 0, 255))
        if "bounce" in active_powerups:
            colors.append((0, 255, 255))
        avg_color = tuple(sum(c) // len(c) for c in zip(*colors))
        player_color = avg_color
    player(playerX, playerY, player_color)

    # プレイヤーの弾の移動
    if bullet_list:
        for bullet in bullet_list[:]:
            pygame.draw.rect(screen, (255, 255, 255), bullet["rect"])
            bullet["rect"].y -= bullet["speed"]
            if bullet["rect"].y < 0:
                if bullet["state"] == "bounce":
                    bullet["speed"] = -bullet["speed"]
                else:
                    bullet_list.remove(bullet)
                    if not bullet_list:
                        bullet_state = "ready"
            elif bullet["rect"].y > screen_height:
                if bullet["state"] == "bounce":
                    bullet["speed"] = -bullet["speed"]
                else:
                    bullet_list.remove(bullet)
                    if not bullet_list:
                        bullet_state = "ready"
            else:
                # 弾と敵の衝突判定
                for enemy in enemy_list[:]:
                    if bullet["rect"].colliderect(enemy["rect"]):
                        play_sound("explosion")
                        bullet_list.remove(bullet)
                        if not bullet_list:
                            bullet_state = "ready"
                        score_value += (5 - enemy["row"]) * 10  # 上段の敵ほど高得点
                        enemy_list.remove(enemy)
                        # 敵の数が減ると速度が上がる
                        enemy_speed = 1 + (1 - len(enemy_list) / (enemy_rows * enemy_cols)) * 2
                        # 敵が全滅した場合
                        if not enemy_list:
                            # 次のラウンドを開始
                            enemy_list = []
                            enemy_speed = 1
                            create_enemies()
                        break
                # 弾とシールドの衝突判定
                for shield in shields:
                    if shield["health"] > 0 and bullet["rect"].colliderect(shield["rect"]):
                        shield["health"] -= 1
                        bullet_list.remove(bullet)
                        if not bullet_list:
                            bullet_state = "ready"
                        break
                # 弾とUFOの衝突判定
                if ufo_active and bullet["rect"].colliderect(pygame.Rect(ufoX, ufoY, ufo_width, ufo_height)):
                    play_sound("explosion")
                    bullet_list.remove(bullet)
                    if not bullet_list:
                        bullet_state = "ready"
                    score_value += random.choice([50, 100, 150])  # ランダムな高得点
                    ufo_active = False

    # 敵の移動
    move_down = False
    for enemy in enemy_list:
        enemy["rect"].x += enemy_direction * enemy_speed
        if enemy["rect"].x <= 0 or enemy["rect"].x >= screen_width - enemy_width:
            move_down = True
    if move_down:
        enemy_direction *= -1
        for enemy in enemy_list:
            enemy["rect"].y += enemy_height
            # 敵が画面下部に到達した場合
            if enemy["rect"].y + enemy_height >= playerY:
                game_over = True

    # 敵の描画
    draw_enemies()

    # 敵の弾の発射
    if random.randint(0, 1000) > 995 and enemy_list:
        shooting_enemy = random.choice(enemy_list)
        bullet = pygame.Rect(shooting_enemy["rect"].x + enemy_width / 2, shooting_enemy["rect"].y + enemy_height, enemy_bullet_width, enemy_bullet_height)
        enemy_bullets.append(bullet)

    # 敵の弾の移動
    for bullet in enemy_bullets[:]:
        pygame.draw.rect(screen, (255, 255, 255), bullet)
        bullet.y += enemy_bullet_speed
        if bullet.y > screen_height:
            enemy_bullets.remove(bullet)
        else:
            # 弾とシールドの衝突判定
            for shield in shields:
                if shield["health"] > 0 and bullet.colliderect(shield["rect"]):
                    shield["health"] -= 1
                    enemy_bullets.remove(bullet)
                    break
            else:
                # 弾とプレイヤーの衝突判定
                if bullet.colliderect(pygame.Rect(playerX, playerY, player_width, player_height)):
                    play_sound("explosion")
                    game_over = True
                    enemy_bullets.remove(bullet)

    # パワーアップアイテムの出現
    if random.randint(0, 1000) > 998:
        create_powerup(random.randint(0, screen_width - 30), 0)

    # パワーアップアイテムの移動と描画
    for powerup in powerups[:]:
        if powerup["active"]:
            powerup["rect"].y += powerup["speed"]
            draw_powerups()
            if powerup["rect"].colliderect(pygame.Rect(playerX, playerY, player_width, player_height)):
                play_sound("powerup")
                active_powerups.append(powerup["type"])
                powerup_start_times[powerup["type"]] = current_time
                powerups.remove(powerup)
            elif powerup["rect"].y > screen_height:
                powerups.remove(powerup)

    # UFOの出現
    if not ufo_active and random.randint(0, 1000) > 998:
        ufo_active = True
        ufoX = 0 if random.choice([True, False]) else screen_width - ufo_width
        ufo_direction = 1 if ufoX == 0 else -1
        play_sound("ufo")

    if ufo_active:
        draw_ufo(ufoX, ufoY)
        ufoX += ufo_speed * ufo_direction
        if ufoX < -ufo_width or ufoX > screen_width:
            ufo_active = False

    # ゲームオーバー処理
    if game_over:
        if score_value > high_score:
            high_score = score_value
        game_over_text = game_over_font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(game_over_text, (screen_width / 2 - 150, screen_height / 2 - 50))
        restart_text = font.render("Press Enter to Restart", True, (255, 255, 255))
        screen.blit(restart_text, (screen_width / 2 - 130, screen_height / 2))
        pygame.display.update()
        # ゲームオーバー後の入力待ち
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # ゲームのリセット
                        playerX = (screen_width - player_width) / 2
                        playerY = screen_height - player_height - 10
                        bullet_state = "ready"
                        bullet_list = []
                        enemy_list = []
                        enemy_bullets = []
                        enemy_speed = 1
                        create_enemies()
                        shields = []
                        for i in range(num_of_shields):
                            x = 100 + i * 175
                            y = playerY - shield_height - 20
                            shields.append({"rect": pygame.Rect(x, y, shield_width, shield_height), "health": shield_health})
                        score_value = 0
                        ufo_active = False
                        active_powerups = []
                        powerup_start_times = {}
                        powerups = []
                        game_over = False
                        waiting = False
            clock.tick(FPS)
        continue

    pygame.display.update()

pygame.quit()
sys.exit()
