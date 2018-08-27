import pygame
import random
import time
from pygame.locals import *

size = 48  # minimum 30 unless you want visual glitches 48 is default
count = 16  # squares squared
mines = 32  # mine count recomended: about (square_root(count)/3) should be mines
font_size = 20  # font size, 20 is recomended
bg_color = 150, 150, 150  # revealed block color
bl_color = 120, 120, 120  # grid color
bl_color2 = 175, 175, 175  # block color
mine_color = 255, 0, 0  # mine color
bl_thickness = 2  # grid thickness
caption = 'Minesweeper'  # window caption
fps = 1000  # fps limit, pygame is limited to 1000
window_size = size * count, size * count  # window size
mine_path = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # search path for the numbers on revealed blocks
clear_path = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # the path which the auto-reveal works in


class Block:
    def __init__(self, x, y):
        self.number = None
        self.revealed = False
        self.mine = False
        self.flagged = False
        self.color = bl_color2
        self.rect = pygame.Rect(x * size, y * size, size, size)

    def reveal(self):
        self.revealed = True
        if not self.mine:
            self.color = bg_color
            return
        self.color = mine_color

    def flag(self):
        self.flagged = True

    def unflag(self):
        self.flagged = False


def generate_board():
    blocks = {}
    for x in range(count):
        for y in range(count):
            blocks[x, y] = Block(x, y)
    return blocks


def generate_mines(block):
    if mines >= count**2:
        raise ValueError('Mine count too high.')
        return
    mine_list = []
    for i in range(mines):
        while True:
            tmp = random.choice(list(board.values()))
            if not tmp.mine and not block == tmp:
                tmp.mine = True
                mine_list.append(tmp)
                break
    return mine_list


def stop():
    pygame.quit()
    quit()


def press(cord):
    if board[cord].flagged:
        return
    board[cord].reveal()
    if not board[cord].number:
        clear_from(cord)


def flag(cord):
    if not board[cord].revealed:
        if not board[cord].flagged:
            board[cord].flag()
            return
        board[cord].unflag()


def clear_from(cord):
    dx, dy = cord
    for x, y in clear_path:
        try:
            if not board[x + dx, y + dy].revealed and not board[x + dx, y + dy].mine:
                press((x + dx, y + dy))
        except KeyError:
            pass


def get_number(cord):
    _sum = 0
    dx, dy = cord
    for x, y in mine_path:
        try:
            if board[x + dx, y + dy].mine:
                _sum += 1
        except KeyError:
            pass
    return _sum


def lose():
    print('rip')
    for block in board.values():
        if not block.mine and not block.flagged:
            block.reveal()
        elif block.mine:
            block.reveal()


def win():
    for block in board.values():
        if block.mine and not block.flagged:
            block.flag()
        elif not block.mine:
            block.reveal()
    print('win')
    screen.fill(bg_color)
    tmp = pygame.font.Font(pygame.font.get_default_font(), 50).render('You won!', 1, bg_color)
    pygame.display.set_mode((tmp.get_rect().w, tmp.get_rect().h))
    while True:
        screen.fill(bl_color2)
        screen.blit(tmp, (0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                stop()


def checks():
    for block in board.values():
        if block.mine and block.revealed:
            lose()
            return False

    if all([block.flagged and block.mine for block in mine_list]) and mine_list:
        tmp = []
        tmp2 = []
        for block in board.values():
            if not block.mine and block.revealed:
                tmp.append(block)
            if not block.mine:
                tmp2.append(block)
            if tmp == tmp2:
                win()
                return False
    return True


def draw_grid():
    for x in range(count):
        x *= size
        for y in range(count):
            y *= size
            pygame.draw.line(screen, bl_color, (0, x), (size * count, x), bl_thickness)
            pygame.draw.line(screen, bl_color, (y, 0), (y, size * count), bl_thickness)


def draw():
    screen.fill(bg_color)
    for x in range(count):
        for y in range(count):
            pygame.draw.rect(screen, board[x, y].color, board[x, y])
            tmp = font.render(f'{board[x,y].number}', 1, (255, 255, 255))
            if board[x, y].revealed and board[x, y].number and not board[x, y].mine:
                screen.blit(tmp, tmp.get_rect(center=(x * size + (size / 2), y * size + (size / 2 + 2))))
            if board[x, y].flagged and not board[x, y].revealed:
                screen.blit(flag_texture, flag_texture.get_rect(center=(x * size + (size / 2 + 2), y * size + (size / 2 + 2))))
            if board[x, y].mine and board[x, y].revealed:
                if board[x, y].flagged:
                    board[x, y].color = bg_color
                screen.blit(mine_texture, mine_texture.get_rect(center=(x * size + (size / 2 + 1), y * size + (size / 2 + 1))))
    draw_grid()


pygame.init()
screen = pygame.display.set_mode(window_size)
clock = pygame.time.Clock()
font = pygame.font.Font(pygame.font.get_default_font(), font_size)
flag_texture = pygame.image.load('flag.png')
mine_texture = pygame.image.load('mine.png')
has_generated_mines = False
checking = True
mine_list = []
board = generate_board()
while True:
    time.delta_time = clock.tick(fps) / 1000
    pygame.display.set_caption(f'{caption} - FPS {int(clock.get_fps())}')
    keys = pygame.key.get_pressed()
    b1, b2, b3 = (bool(button) for button in pygame.mouse.get_pressed())
    mx, my = pygame.mouse.get_pos()
    draw()
    if checking:
        checking = checks()
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == QUIT:
            stop()
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if not has_generated_mines:
                    mine_list = generate_mines(board[mx // size, my // size])
                    has_generated_mines = True
                    for x, y in board.keys():
                        board[x, y].number = get_number((x, y))
                try:
                    press((mx // size, my // size))
                except KeyError:
                    pass
            elif event.button == 3:
                flag((mx // size, my // size))
