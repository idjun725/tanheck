import asyncio
import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")

font_path = "NanumGothic.ttf"
font = pygame.font.Font(font_path, 36)
background_img = pygame.image.load("background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
player_img = pygame.image.load("player.png").convert_alpha()
enemy_base_img = pygame.image.load("enemy.png").convert_alpha()

player_size = 50
player_img = pygame.transform.scale(player_img, (player_size, player_size))
player = pygame.Rect(400, 500, player_size, player_size)
player_speed = 5

def draw_text(text, x, y, color=(255,255,255)):
    img = font.render(text, True, color)
    win.blit(img, (x, y))

def title_screen():
    while True:
        win.blit(background_img, (0, 0))
        draw_text("탄핵 피하기!", WIDTH//2-80, HEIGHT//2-100)
        draw_text("Press SPACE to Start", WIDTH//2-150, HEIGHT//2)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: return
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

def game_over_screen(score):
    button_rect = pygame.Rect(WIDTH//2-80, HEIGHT//2+40, 160, 50)
    while True:
        win.blit(background_img, (0, 0))
        draw_text("Game Over!", WIDTH//2-80, HEIGHT//2-60, (255,0,0))
        draw_text(f"Score: {score}", WIDTH//2-60, HEIGHT//2-10)
        pygame.draw.rect(win, (0, 128, 255), button_rect)
        draw_text("Restart", WIDTH//2-40, HEIGHT//2+50)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos): return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: return
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

def game_clear_screen(score):
    button_rect = pygame.Rect(WIDTH//2-80, HEIGHT//2+40, 160, 50)
    while True:
        win.blit(background_img, (0, 0))
        draw_text("탄핵을 피했습니다!", WIDTH//2-100, HEIGHT//2-60, (0,255,255))
        draw_text(f"Score: {score}", WIDTH//2-60, HEIGHT//2-10)
        pygame.draw.rect(win, (0, 128, 255), button_rect)
        draw_text("Restart", WIDTH//2-40, HEIGHT//2+50)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos): return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: return
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

async def main():
    global player
    while True:
        title_screen()
        score = await main_game()
        if score >= 100:
            game_clear_screen(score)
        else:
            game_over_screen(score)

async def main_game():
    global player
    bullets, enemies = [], []
    bullets_to_remove, enemies_to_remove = [], []
    bullet_speed, last_shot_time, cooldown = 7, 0, 300
    ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(ENEMY_SPAWN_EVENT, 1000)
    score, running = 0, True
    clock = pygame.time.Clock()

    while running:
        win.blit(background_img, (0, 0))
        clock.tick(60)
        if score >= 100: break

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == ENEMY_SPAWN_EVENT:
                while True:
                    esize = random.randint(40, 60)
                    x, y = random.randint(0, WIDTH - esize), random.randint(0, HEIGHT - esize)
                    ex, ey = x + esize//2, y + esize//2
                    if ((ex - player.centerx)**2 + (ey - player.centery)**2)**0.5 < 100: continue
                    speed = random.randint(1, 4)
                    img = pygame.transform.scale(enemy_base_img, (esize, esize))
                    enemies.append({'rect': pygame.Rect(x, y, esize, esize), 'speed': speed, 'img': img})
                    cooldown = max(100, cooldown - 10)
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.time.get_ticks() - last_shot_time > cooldown:
                    last_shot_time = pygame.time.get_ticks()
                    mx, my = pygame.mouse.get_pos()
                    dx, dy = mx - player.centerx, my - player.centery
                    dist = (dx**2 + dy**2) ** 0.5
                    direction = (dx / dist, dy / dist)
                    bullets.append({'rect': pygame.Rect(player.centerx, player.centery, 5, 5), 'dir': direction})

        for bullet in bullets[:]:
            bullet['rect'].x += bullet_speed * bullet['dir'][0]
            bullet['rect'].y += bullet_speed * bullet['dir'][1]
            pygame.draw.rect(win, (255, 255, 0), bullet['rect'])
            if not win.get_rect().colliderect(bullet['rect']): bullets.remove(bullet)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.left > 0: player.x -= player_speed
        if keys[pygame.K_d] and player.right < WIDTH: player.x += player_speed
        if keys[pygame.K_w] and player.top > 0: player.y -= player_speed
        if keys[pygame.K_s] and player.bottom < HEIGHT: player.y += player_speed

        for enemy in enemies[:]:
            dx, dy = player.centerx - enemy['rect'].centerx, player.centery - enemy['rect'].centery
            dist = (dx**2 + dy**2) ** 0.5
            dirx, diry = (dx / dist, dy / dist) if dist else (0, 0)
            mx = max(1, abs(enemy['speed'] * dirx)) * (1 if dirx > 0 else -1) if dirx else 0
            my = max(1, abs(enemy['speed'] * diry)) * (1 if diry > 0 else -1) if diry else 0
            enemy['rect'].x += int(mx)
            enemy['rect'].y += int(my)
            win.blit(enemy['img'], enemy['rect'])
            if not win.get_rect().colliderect(enemy['rect']): enemies.remove(enemy)

        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet['rect'].colliderect(enemy['rect']):
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
                    score += 1

        for bullet in bullets_to_remove:
            if bullet in bullets: bullets.remove(bullet)
        bullets_to_remove.clear()
        for enemy in enemies_to_remove:
            if enemy in enemies: enemies.remove(enemy)
        enemies_to_remove.clear()

        for enemy in enemies:
            dx, dy = player.centerx - enemy['rect'].centerx, player.centery - enemy['rect'].centery
            if (dx**2 + dy**2) ** 0.5 < 10 or player.colliderect(enemy['rect']):
                running = False; break

        draw_text(f"Score: {score}", 10, 10)
        win.blit(player_img, player)
        pygame.display.update()
        await asyncio.sleep(0)

    pygame.time.delay(1000)
    return score

asyncio.run(main())
