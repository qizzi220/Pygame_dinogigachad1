import random
import sys

import cv2
import pygame

import classes_game
from classes_game import *

BLOCKS = {'┌': 1, '─': 2, '┐': 3, '┤': 4, '┘': 5, '_': 6, '└': 7, '├': 8, '┳': 9,
          '|': 10, '┻': 11, '[': 12, '=': 13, ']': 14, '▄': 15, '╦': 16, '│': 17,
          '╩': 18, '╔': 19, '╤': 20, '╗': 21, '⌜': 22, '⌝': 23, '⌟': 24, '⌞': 25, '~': 0}

BACKGROUND = {'▄': 0, 'V': 1, '▼': 2, 'v': 3, '▽': 4, '√': 5, '▇': 6, '▆': 7, '▃': 8, '▂': 9,
              '█': 10, '╰': 11, '╯': 12, '╥': 13, '║': 14, '╌': 15, 'E': 16}

#rice_with_cutlet
def open_level(name):
    global level_rows
    file = open(f'game_levels/{name}', mode='r', encoding='utf-8')
    lines = file.readlines()
    lvl = []
    level_rows = len(lines)
    for line in lines:
        lvl.append(line)
    return lvl


def start():
    global entities, platforms, thorns, coins_list, hero, left, right, up, dagger, coins, all_sprites, num_coins, live
    if not mixer.music.get_busy():
        mixer.music.unpause()
    end_channel.stop()
    left = right = up = False
    live = 1
    dagger = 0
    coins = 0
    entities = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    platforms = []
    thorns = []
    coins_list = []
    x = y = 0
    for row in level_bkg:
        for col in row:
            if col in BACKGROUND:
                image = Background(x, y, BACKGROUND[col])
                entities.add(image)
                all_sprites.add(image)
            x += pl_WD
        y += pl_HG
        x = 0
    x = y = 0
    for row in level:
        for col in row:
            if col in BLOCKS:
                pf = Platform(x, y, BLOCKS[col])
                entities.add(pf)
                platforms.append(pf)
                all_sprites.add(pf)
            if col == '^':
                th = Thorns(x, y, 0)
                thorns.append(th)
                entities.add(th)
                all_sprites.add(th)
            if col == '<':
                th = Thorns(x, y, 90)
                thorns.append(th)
                entities.add(th)
                all_sprites.add(th)
            if col == 'V':
                th = Thorns(x, y, 180)
                thorns.append(th)
                entities.add(th)
                all_sprites.add(th)
            if col == '>':
                th = Thorns(x, y, 270)
                thorns.append(th)
                entities.add(th)
                all_sprites.add(th)
            if col == '@':
                hero = Hero(x, y)
                entities.add(hero)
                all_sprites.add(hero)
            if col == 'O':
                coin = Coin(x + 16, y + 16)
                coins_list.append(coin)
                entities.add(coin)
                all_sprites.add(coin)
            if col == 'E':
                end = End(x + 60, y + 60)
                entities.add(end)
                thorns.append(end)
                all_sprites.add(end)
            x += pl_WD
        y += pl_HG
        x = 0
    num_coins = len(coins_list)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    global left, right, up, hero, level_num, level, level_bkg, level_rows
    menu_channel.play(mixer.Sound('sounds/menu.mp3'), -1)
    screen.fill((0, 0, 0))
    left = right = up = False
    quit_rect = Button('Выйти', 20, 50, width, height, screen, 0)
    level_rects = []
    rects = [quit_rect]
    x = 0
    for i in range(1, 4):
        btn = Button(f'{i}', -30 + x, 150, width, height, screen, 0)
        level_rects.append(btn)
        rects.append(btn)
        x += 50
    MYEVENTTYPE1 = USEREVENT + 1
    time.set_timer(MYEVENTTYPE1, 20)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in level_rects:
                    if btn.rect.collidepoint(event.pos):
                        menu_channel.stop()
                        channel_sounds.play(mixer.Sound('sounds/button.mp3'))
                        level_num = int(btn.txt)
                        level = open_level(f'{level_num}_lvl.txt')
                        level_bkg = open_level(f'{level_num}_bkg.txt')
                        if live == 1:
                            mixer.music.unpause()
                        start()
                        return
                if quit_rect.rect.collidepoint(event.pos):
                    terminate()
            if event.type == MYEVENTTYPE1:
                for anim in animation_list:
                    anim.animation()
                coin1.animation()
                coin2.animation()
                for rect in rects:
                    rect.change_color()
            screen.blit(bg, (0, 0))
            for rect in rects:
                rect.draw(screen, 0)
            animation_list.draw(screen)
        pygame.display.flip()


def win_screen():
    global level_rows, level, level_num, level_bkg
    screen.fill((0, 0, 0))
    level_rect = Button('Уровень пройден', 20, 200, width, height, screen, 0)
    result_rect = Button(f'Монеты: {coins} из {(coins + len(coins_list))}', 20, 100, width, height, screen, 0)
    menu_rect = Button('Меню', -60, 0, width, height, screen, 0)
    next_rect = Button('Вперёд', 85, 0, width, height, screen, 0)
    rects = [menu_rect, next_rect, level_rect, result_rect]
    MYEVENTTYPE2 = USEREVENT + 1
    time.set_timer(MYEVENTTYPE2, 20)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_rect.rect.collidepoint(event.pos):
                    mixer.music.pause()
                    channel_sounds.play(mixer.Sound('sounds/button.mp3'))
                    start_screen()
                    return
                if next_rect.rect.collidepoint(event.pos):
                    channel_sounds.play(mixer.Sound('sounds/button.mp3'))
                    level_rows = 0
                    level_num += 1
                    if level_num <= 3:
                        level = open_level(f'{level_num}_lvl.txt')
                        level_bkg = open_level(f'{level_num}_bkg.txt')
                        start()
                        return
                    else:
                        start_screen()
                        return 
            if event.type == MYEVENTTYPE2:
                for anim in animation_list:
                    anim.animation()
                coin1.animation()
                coin2.animation()
                menu_rect.change_color()
                next_rect.change_color()
            screen.blit(bg, (0, 0))
            for rect in rects:
                rect.draw(screen, 0)
            animation_list.draw(screen)
        pygame.display.flip()


width, height = 1000, 600

if __name__ == '__main__':
    init()
    pygame.mixer.music.load('sounds/Pixel_chad.wav')
    pygame.mixer.music.play()
    video = cv2.VideoCapture("game_images/Pixel_chad.mp4")
    success, video_image = video.read()
    fps = video.get(cv2.CAP_PROP_FPS)
    display.set_caption('Платформер')
    window = pygame.display.set_mode((740, 660))
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.unicode == ' ':
                run = False
        success, video_image = video.read()
        if success:
            video_surf = pygame.image.frombuffer(
                video_image.tobytes(), video_image.shape[1::-1], "BGR")
        else:
            run = False
        window.blit(video_surf, (0, 0))
        pygame.display.flip()
    quit()

camera = Camera(width, height)
MUSIC_VOLUME = 1

if __name__ == '__main__':
    init()

    fon_music = ['sounds/fon1.mp3', 'sounds/fon2.mp3', 'sounds/fon3.mp3', 'sounds/fon4.mp3']
    random.shuffle(fon_music)

    pygame.mixer.music.load(fon_music[3])
    song_index = 0
    pygame.mixer.music.queue(fon_music[0])
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play()
    pygame.mixer.music.pause()

    channel_sounds = mixer.Channel(1)
    jump_channel = mixer.Channel(2)
    dagger_channel = mixer.Channel(4)
    end_channel = mixer.Channel(3)
    menu_channel = pygame.mixer.Channel(5)
    menu_channel.play(mixer.Sound('sounds/menu.mp3'), -1)
    menu_channel.stop()

    live = 1

    display.set_caption('Платформер')
    size = width, height
    screen = display.set_mode(size)

    hero1 = AnimationHero(150, 472, 'диносы афка в меню/красный', [0, 1, 2, 3])
    hero2 = AnimationHero(250, 472, 'диносы афка в меню/синий', [2, 3, 0, 1])
    hero3 = AnimationHero(width - 150, 472, 'диносы афка в меню/зелёный', [1, 2, 3, 0], trans=True)
    hero4 = AnimationHero(width - 250, 472, 'диносы афка в меню/желтый', [3, 0, 1, 2], trans=True)
    coin1 = Coin(200, 270)
    coin2 = Coin(780, 150)
    animation_list = pygame.sprite.Group()
    animation_list.add(hero1)
    animation_list.add(hero2)
    animation_list.add(hero3)
    animation_list.add(hero4)
    animation_list.add(coin1)
    animation_list.add(coin2)
    bg = load_image('fon1.png')
    bg = transform.scale(bg, (width, height))

    level_num = 1
    level_rows = 0
    level = 0
    level_bkg = 0

    start_screen()
    screen.fill((0, 0, 0))

    left = right = up = dagger = coins = all_sprites = 0
    entities = platforms = thorns = coins_list = hero = num_coins = 0
    start()

    MYEVENTTYPE = USEREVENT + 1
    time.set_timer(MYEVENTTYPE, 20)

    SONG_END = pygame.USEREVENT
    pygame.mixer.music.set_endevent(SONG_END)

    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.mixer.music.stop()
                running = False
            if ev.type == SONG_END:
                song_index += 1
                if song_index > 3:
                    song_index = 0
                pygame.mixer.music.queue(fon_music[song_index])
            if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                pygame.mixer.music.pause()
                start_screen()
            if ev.type == KEYDOWN and ev.key == K_a:
                left = True
            if ev.type == KEYDOWN and ev.key == K_d:
                right = True
            if ev.type == KEYDOWN and ev.key == K_r:
                start()
            if ev.type == KEYDOWN and ev.key in [K_w, K_SPACE]:
                if hero.live == 1:
                    if hero.air and hero.double == 0:
                        if hero.check == 0:
                            jump_channel.play(mixer.Sound('sounds/jump.mp3'))
                        hero.double = 1
                    else:
                        up = True
                    if not hero.air:
                        hero.double = 0
                        jump_channel.play(mixer.Sound('sounds/jump.mp3'))
            if ev.type == KEYUP and ev.key == K_d:
                right = False
            if ev.type == KEYUP and ev.key == K_a:
                left = False
            if ev.type == KEYDOWN and ev.key == K_l:
                if hero in entities:
                    if not dagger:
                        dagger = Dagger(hero.dx,
                                        hero.rect.right if hero.dx == 1 else hero.rect.left, hero.rect.centery)
                        dagger_channel.play(mixer.Sound('sounds/dagger_drop.mp3'))
                        entities.add(dagger)
                        hero.attack = True
                    else:
                        dagger_channel.play(mixer.Sound('sounds/dagger_tp.mp3'))
                        hero.rect.x = dagger.rect.x
                        hero.rect.centery = dagger.rect.centery
                        dagger.check = 1
                        hero.move_y = 0
            if ev.type == MYEVENTTYPE:
                if hero.live == 0:
                    mixer.music.pause()
                    channel_sounds.play(mixer.Sound('sounds/dead.mp3'))
                    hero.move_y = hero.move_x = 0
                    entities.remove(hero)
                    all_sprites.remove(hero)
                    entities.remove(dagger)
                    dagger = 0
                    live = 0
                    hero.live = -1
                if hero in entities:
                    for coin in coins_list:
                        coin.animation()
                        if hero.rect.colliderect(coin):
                            channel_sounds.play(mixer.Sound('sounds/coin.mp3'))
                            entities.remove(coin)
                            all_sprites.remove(coin)
                            coins_list.remove(coin)
                            coins += 1
                    if classes_game.win:
                        mixer.music.pause()
                        channel_sounds.set_volume(0.5)
                        channel_sounds.play(mixer.Sound('sounds/end_level_2.mp3'))
                        channel_sounds.set_volume(1)
                        entities.remove(hero)
                        all_sprites.remove(hero)
                        entities.remove(dagger)
                        dagger = 0
                        classes_game.win = False
                        win_screen()
                    else:
                        hero.update(left, right, up, platforms, thorns)
                        up = False
                        if dagger:
                            dagger.update(platforms)
                            if dagger.check == 1:
                                entities.remove(dagger)
                                dagger = 0
        screen.fill((25, 29, 49))
        if hero in entities:
            camera.update(hero)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        if dagger:
            dagger.rect.centery += camera.dy
            dagger.rect.x += camera.dx
        entities.draw(screen)
        display.flip()
    quit()
