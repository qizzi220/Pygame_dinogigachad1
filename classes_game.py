from pygame import *
import pygame
import os

speed = 6
dagger_speed = 11
dagger_way = 400
jump_speed = 16
wall_jump_speed = 4
wall_jump_frames = 5
max_fall_speed = 15
fall_speed = 1
animation_frames = 6
animation_frames_coin = 12
animation_frames_fireball = 3

pl_WD = 64
pl_HG = 64
pl_CL = (255, 0, 0)
th_WD = 64
th_HG = 32

win = False


def load_image(name, colorkey=None):
    fullname = os.path.join('game_images', name)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Hero(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.attack = False
        self.move_x = 0
        self.move_y = 0
        self.dx = 1
        self.f = -1
        self.double = 0
        self.check = 0
        self.wall_frame = 0
        self.wall_jump = False
        self.wall_jump_direction = False
        self.live = 1
        self.frame_count = 0
        self.start_x = x
        self.start_y = y
        self.left = False
        self.right = False
        self.wall = False
        self.ground = False
        self.air = True
        self.frames = {'afk': [load_image(f'дино\дино афк\{i}.png', -1) for i in range(1, 5)],
                       'run': [load_image(f'дино\дино ран\{i}.png', -1) for i in range(1, 7)],
                       'attack': [load_image(f'дино\дино атак\{i}.png', -1) for i in range(1, 3)],
                       'up': [load_image(f'дино\дино ап.png', -1)],
                       'down': [load_image(f'дино\дино даун.png', -1)]}
        self.animation()
        self.rect = self.image.get_rect(left=x, bottom=y)

    def update(self, left, right, up, platforms, thorns):
        global fall_speed
        if self.wall_jump:
            if self.wall_jump_direction == 1:
                self.left = False
            else:
                self.left = True
            self.wall_frame += 1
        if self.wall_frame >= 20:
            self.wall_frame = 0
            self.wall_jump_direction = False
            self.wall_jump = False
        if left and not self.wall_jump:
            self.move_x = -speed
            self.left = True
            self.right = False
        if right and not self.wall_jump:
            self.move_x = speed
            self.left = False
            self.right = True
        if up:
            if self.wall:
                self.wall_jump_direction = 1 if left else 2
                self.wall_jump = True
                self.move_x = wall_jump_speed if self.wall_jump_direction == 1 else -wall_jump_speed
                self.move_y = -jump_speed
            elif not self.air:
                self.move_y = -jump_speed
        if self.double == 1 and self.air and self.check == 0:
            self.double = 0
            self.check = 1
            self.move_y = -jump_speed
        if not (left or right):
            self.move_x = 0
        if not self.ground and self.move_y <= max_fall_speed and fall_speed != 0:
            self.move_y += fall_speed
        if self.move_x != 0:
            self.dx = 1 if self.move_x > 0 else 0
        if self.air or self.ground:
            fall_speed = 1
            self.wall = False
        self.air = True if not self.ground else False
        self.ground = False
        self.rect.x += self.move_x
        self.collide(self.move_x, 0, platforms, thorns)
        self.rect.y += self.move_y
        self.collide(0, self.move_y, platforms, thorns)
        self.animation()

    def collide(self, move_x, move_y, platforms, thorns):
        global fall_speed, coins, win
        for t in thorns:
            if sprite.collide_mask(self, t):
                if type(t) == End:
                    win = True
                else:
                    self.live = 0
        for p in platforms:
            if sprite.collide_rect(self, p):
                if move_x > 0:
                    self.rect.right = p.rect.left
                    self.wall = True
                if move_x < 0:
                    self.rect.left = p.rect.right
                    self.wall = True
                if move_y < 0:
                    self.wall = False
                    self.rect.top = p.rect.bottom
                    self.move_y = 0
                if move_y > 0:
                    self.rect.bottom = p.rect.top
                    self.ground = True
                    self.air = False
                    self.wall = False
                    self.check = 0
                    self.double = 0
                    self.move_y = 0
                if self.air and self.wall and self.move_y >= 0:
                    self.ground = False
                    self.air = False
                    self.move_y = 2
                    fall_speed = 0
                    self.check = 0

    def animation(self):
        if self.attack:
            self.attack = False
            self.f = len(self.frames['attack']) * animation_frames

        if self.move_x == 0 and self.move_y == 0 and self.f < 0:
            anim = 'afk'
        elif self.move_y > 0 and self.f < 0:
            anim = 'down'
        elif self.move_y < 0 and self.f < 0:
            anim = 'up'
        elif self.move_x != 0 and self.f < 0:
            anim = 'run'
        else:
            anim = 'attack'
        self.f -= 1
        self.frame_count += 1
        if self.frame_count >= len(self.frames[anim]) * animation_frames:
            self.frame_count = 0
        image = self.frames[anim][self.frame_count // animation_frames]
        if self.left:
            image = pygame.transform.flip(image, True, False)
        self.image = image


class Platform(sprite.Sprite):
    def __init__(self, x, y, sym):
        sprite.Sprite.__init__(self)
        self.image = load_image(f'blocks\walls\{sym}.png', (255, 255, 255, 255))
        self.rect = Rect(x, y, pl_WD, pl_HG)


class Background(sprite.Sprite):
    def __init__(self, x, y, sym):
        sprite.Sprite.__init__(self)
        self.image = load_image(f'blocks/background\{sym}.png', (255, 255, 255, 255))
        self.rect = Rect(x, y, pl_WD, pl_HG)


class Dagger(sprite.Sprite):
    def __init__(self, dx, x, y):
        super().__init__()
        self.dx = dx
        self.check = 0
        self.move_x = 0
        self.start_x = x
        self.image = load_image('dagger.png', -1)
        self.image = pygame.transform.flip(self.image, False if dx else True, False)
        if dx:
            self.rect = self.image.get_rect(left=x, centery=y)
        else:
            self.rect = self.image.get_rect(right=x, centery=y)
        self.frames = [load_image(f'fireball\{i}.png', -1) for i in range(0, 5)]
        self.frame_count = 0

    def update(self, platforms):
        self.rect.x += dagger_speed if self.dx else -dagger_speed
        self.move_x += dagger_speed
        self.collide(platforms)
        self.way()
        self.animation()

    def collide(self, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):
                if self.dx == 1:
                    self.rect.right = p.rect.left
                if self.dx == 0:
                    self.rect.left = p.rect.right
                self.check = 1

    def way(self):
        if self.move_x >= dagger_way:
            self.check = 1

    def animation(self):
        self.frame_count += 1
        if self.frame_count >= len(self.frames) * animation_frames_fireball:
            self.frame_count = 0
        self.image = self.frames[self.frame_count // animation_frames_fireball]
        self.image = pygame.transform.flip(self.image, False if self.dx else True, False)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, width, height):
        self.dx = 0
        self.dy = 0
        self.width = width
        self.height = height

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - self.width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - self.height // 2)


class Thorns(sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = load_image('blocks/spikes.png', -1)
        self.image = transform.rotate(self.image, angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(left=x, top=y)


class Coin(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image('спин койн/1.png', -1)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(centerx=x + 19, top=y)
        self.frames = [load_image(f'спин койн\{i}.png', -1) for i in range(1, 9)]
        self.frame_count = 0

    def animation(self):
        self.frame_count += 1
        if self.frame_count >= len(self.frames) * animation_frames_coin:
            self.frame_count = 0
        self.image = self.frames[self.frame_count // animation_frames_coin]


class End(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image('end.png')
        self.rect = self.image.get_rect(centerx=x + 3, top=y)


class AnimationHero(sprite.Sprite):
    def __init__(self, x, y, name, numbers, trans=False):
        super().__init__()
        self.image = load_image(f'{name}/0.png', -1)
        self.mask = pygame.mask.from_surface(self.image)
        self.trans = trans
        self.rect = self.image.get_rect(centerx=x, top=y)
        self.frames = [load_image(f'{name}/{i}.png', -1) for i in numbers]
        self.frame_count = 0

    def animation(self):
        self.frame_count += 1
        if self.frame_count >= len(self.frames) * animation_frames:
            self.frame_count = 0
        self.image = self.frames[self.frame_count // animation_frames]
        self.image = transform.flip(self.image, self.trans, False)


class Button:
    def __init__(self, txt, dx, dy, width, height, screen, wd):
        self.btn_color = (216, 23, 23)
        self.text_color = (0, 0, 0)
        self.rect = 0
        self.dx = dx
        self.dy = dy
        self.txt = txt
        font = pygame.font.Font(None, 50)
        self.text = font.render(self.txt, True, self.text_color)
        self.text_x = width // 2 - self.text.get_width() // 2 + self.dx
        self.text_y = height // 2 - self.text.get_height() // 2 - self.dy
        text_w = self.text.get_width()
        text_h = self.text.get_height()
        self.rect = Rect((self.text_x - 10, self.text_y - 10, text_w + 20, text_h + 20))
        pygame.draw.rect(screen, self.btn_color, self.rect, wd)
        screen.blit(self.text, (self.text_x, self.text_y))

    def change_color(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.btn_color = (212, 60, 60)
        else:
            self.btn_color = (216, 23, 23)

    def draw(self, screen, wd):
        pygame.draw.rect(screen, self.btn_color, self.rect, wd)
        screen.blit(self.text, (self.text_x, self.text_y))

