import pygame
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')

tile_width = tile_height = 50


class Grass(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(grass_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Boxes(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(boxes_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move_left(self):
        self.rect = self.rect.move(-50, 0)
        if pygame.sprite.spritecollideany(self, boxes_group) or not pygame.sprite.spritecollideany(self, grass_group):
            self.rect = self.rect.move(50, 0)

    def move_right(self):
        self.rect = self.rect.move(50, 0)
        if pygame.sprite.spritecollideany(self, boxes_group) or not pygame.sprite.spritecollideany(self, grass_group):
            self.rect = self.rect.move(-50, 0)

    def move_up(self):
        self.rect = self.rect.move(0, -50)
        if pygame.sprite.spritecollideany(self, boxes_group) or not pygame.sprite.spritecollideany(self, grass_group):
            self.rect = self.rect.move(0, 50)

    def move_down(self):
        self.rect = self.rect.move(0, 50)
        if pygame.sprite.spritecollideany(self, boxes_group) or not pygame.sprite.spritecollideany(self, grass_group):
            self.rect = self.rect.move(0, -50)


# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
grass_group = pygame.sprite.Group()
boxes_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Grass('empty', x, y)
            elif level[y][x] == '#':
                Boxes('wall', x, y)
            elif level[y][x] == '@':
                Grass('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    if not filename:
        print('Введите название карты')
        terminate()
    filename = "data/" + filename + ".txt"
    # читаем уровень, убирая символы перевода строки
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
    except FileNotFoundError:
        print(f'Карты {filename[5:]} не существует')
        terminate()
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def start_screen():
    intro_text = ["МАРИО", "", "Чтобы начать нажмите любую клавишу"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (1280, 720))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


pygame.init()
player, level_x, level_y = generate_level(load_level(input()))
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Перемещение героя. Дополнительные уровни')
clock = pygame.time.Clock()
FPS = 60
start_screen()
camera = Camera()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.move_left()
            elif event.key == pygame.K_RIGHT:
                player.move_right()
            elif event.key == pygame.K_UP:
                player.move_up()
            elif event.key == pygame.K_DOWN:
                player.move_down()
    screen.fill((0, 0, 0))
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    boxes_group.draw(screen)
    grass_group.draw(screen)
    player_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
