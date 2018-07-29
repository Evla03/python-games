from pygame.locals import *
import pygame
import random
import time


def game(retried=False):
    # Settings
    acceleration = 1
    show_fps = True
    hide_cursor = False
    score = 0                        # Starting score
    ticks = 60                       # Updates per second
    window_size = 800, 600           # The size of the window
    window_name = 'Game'             # The title of the pygame window
    show_hitboxes = False            # Change if hitboxed will be drawed
    skip_title_screen = False        # Skip the title and loading screen
    debug = False                    # Change if debugging prints will be seen (not recommended)
    bullets = []                     # Initsalize the bullets list
    meteors = []                     # Initsalize the meteors list
    files = {                        # Dict of all filenames
        'background': 'background.png',
        'player': 'player.png',
        'bullet': 'bullet.png',
        'meteor': 'meteor.png',
        'background_music': 'music.mp3',
        'icon': 'icon.png',
        'energy': 'energy.png',
        'logo': ['logo.png', 'keys.png', 'defend.png']
    }

    stations = []
    for i in range(6):
        stations.append(f'station{i}.png')

    stations += stations[::-1]

    tips = [
        'It takes longer time to regenerate energy if you have no left.',
        'Steer using A and D or the arrow keys, press space to fire.',
        'Defend your spaceship from meteors.',
        'Loading...'
    ]

    try:
        with open("scores.dat", "r") as file:
            for line in file:
                if debug:
                    print(file.redline(line))
    except FileNotFoundError:
        with open("scores.dat", "w") as file:
            file.write("[Scores]")

    class Energy(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            others_group.add(self)
            self.x = 10
            self.y = 560
            self.energy = 10
            self.last_shot = 0
            self.blinking = False
            self.surface = pygame.image.load(files['energy'])
            #self.blend = BLEND_MULT

        def update(self):
            pygame.draw.rect(window, (255, 200, 0), pygame.Rect(self.x, self.y, 75 * self.energy / 10, 30))
            if not self.blinking:
                pass
                pygame.draw.rect(window, (50, 50, 50), pygame.Rect(self.x, self.y, 75, 30), 3)
            else:
                pass
                pygame.draw.rect(window, (255, 50, 50), pygame.Rect(self.x, self.y, 75, 30), 3)
            window.blit(self.surface, (self.x, self.y + 5))
            self.last_shot += 1
            if debug:
                print(self.last_shot)
            if self.energy != 0 and self.energy != 1:
                if self.energy < 10 and self.last_shot > 100 / (self.energy**1.1) * 5 and self.energy != 0:
                    self.energy += 1
                    self.blinking = False
            else:
                if self.energy < 10 and self.last_shot > 230:
                    self.energy += 1
            # if self.energy < 10:
            #   self.energy += 1

        def shot(self):
            self.energy -= 1
            self.last_shot = 0

    class Station(pygame.sprite.Sprite):  # The space station class
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            others_group.add(self)
            self.x = 550
            self.y = -50
            self.surface = pygame.image.load(stations[0])
            self.rect = self.surface.get_rect()
            self.hp = 100
            self.animator = 0
            self.index = 0

        def update(self):
            if show_hitboxes:
                pygame.draw.rect(self.surface, (255, 0, 0), self.rect, 1)
            self.rect.topleft = (self.x, self.y)
            window.blit(self.surface, (self.x, self.y))
            pygame.draw.rect(window, (50, 100, 50), pygame.Rect(self.x, self.y + 300, self.rect.w * self.hp / 100, 25))
            pygame.draw.rect(window, (200, 200, 200), pygame.Rect(self.x, self.y + 300, self.rect.w, 25), 3)
            if self.hp <= 0:
                pygame.event.post(game_over_event)

            self.surface = pygame.image.load(stations[(self.animator % (len(stations) * 10)) // 10])
            self.animator += 1

        def take_damage(self, meteor):
            self.hp -= 10

        def check_collide(self, meteors):
            for meteor in meteors:
                if self.rect.contains(meteor):
                    if debug:
                        print(meteor, 'did damage to me')
                    meteor.kill()
                    meteors.pop(meteors.index(meteor))
                    self.take_damage(meteor)

    class Player(pygame.sprite.Sprite):  # The controllable player class
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            others_group.add(self)
            self.x = 350
            self.y = 500
            self.surface = pygame.image.load(files['player'])
            self.rect = self.surface.get_rect()

        def update(self):
            if show_hitboxes:
                pygame.draw.rect(self.surface, (255, 0, 0), self.rect, 1)
            self.rect.topleft = (self.x, self.y)
            window.blit(self.surface, (self.x, self.y))

        def move(self, x=0, y=0):
            self.x += x
            self.y += y

    class Bullet(pygame.sprite.Sprite):  # The bullet class (shot by player)
        def __init__(self, player):
            pygame.sprite.Sprite.__init__(self)
            bullet_group.add(self)
            self.x = player.x + player.rect.w // 2 - 10
            self.y = player.y
            self.surface = pygame.image.load(files['bullet'])
            self.rect = self.surface.get_rect()
            #print(self, 'I got created')

        def update(self):
            # print(self.x,self.y)
            if show_hitboxes:
                pygame.draw.rect(self.surface, (255, 0, 0), self.rect, 1)
            #self.rect.topleft = (self.x, self.y)
            self.y -= 10 * acceleration
            self.rect.x = self.x
            self.rect.y = self.y
            window.blit(self.surface, (self.x, self.y))
            self.rect = self.surface.get_rect()

    class Meteor(pygame.sprite.Sprite):  # The meteor class
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            meteor_group.add(self)
            self.x = -100
            self.y = random.randint(0, 200)
            self.surface = pygame.image.load(files['meteor'])
            self.rect = self.surface.get_rect()
            self.speed = float(random.randint(100, 200) / 100)

        def update(self):
            if show_hitboxes:
                pygame.draw.rect(self.surface, (255, 0, 0), self.rect, 1)
            if show_hitboxes:
                pygame.draw.rect(window, (0, 0, 255), pygame.Rect(self.x, self.y, 5, 5), 5)
            self.rect.x = self.x
            self.rect.y = self.y
            window.blit(self.surface, (self.x, self.y))
            self.x += self.speed
            self.speed = self.speed * acceleration

        def check_collide(self, bullets):
            for bullet in bullets:
                distance = x, y = ((self.x + 50 - bullet.x), (self.y + 25 - bullet.y))
                if (distance[0] > 0) and distance[0] < self.rect.h:
                    if (distance[1] > 0) and distance[1] < self.rect.w:
                        if debug:
                            print(clock.get_time(), (self.x, self.y), distance, 'I got hit')
                        # bullets.pop(bullets.index(bullet))
                        self.kill()
                        # bullet.kill()
                        if debug:
                            print('Score is now:', score)
                        return bullet
            return False

    pygame.init()
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption(window_name)
    background = pygame.image.load(files['background'])
    icon = pygame.image.load(files['icon'])
    pygame.display.set_icon(icon)

    if not retried:
        pygame.mixer.music.load(files['background_music'])
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.25)

    clock = pygame.time.Clock()
    if hide_cursor:
        pygame.mouse.set_visible(False)
    font = pygame.font.SysFont(pygame.font.get_default_font(), 30)
    big_font = pygame.font.SysFont(pygame.font.get_default_font(), 180)

    if not skip_title_screen and not retried:
        for t in tips:
            window.blit(background, (0, 0))
            try:
                window.blit(pygame.image.load(files['logo'][tips.index(t)]), (0, 0))
            except IndexError:
                pass
            tip = t
            window.blit(font.render(tip, True, (255, 255, 255)), (20, 570))
            pygame.display.flip()
            pygame.time.wait(3000)

    font = pygame.font.SysFont(pygame.font.get_default_font(), 40)
    big_font = pygame.font.SysFont(pygame.font.get_default_font(), 180)
    game_over_event = pygame.event.Event(2, {'GAMEOVER': '2'})
    bullet_group = pygame.sprite.Group()
    meteor_group = pygame.sprite.Group()
    others_group = pygame.sprite.Group()
    shoot_ticker = 0
    pygame.time.set_timer(1, 1000)
    player = Player()
    energy_bar = Energy()
    station = Station()

    while True:
        bullet_group.update()
        meteor_group.update()
        others_group.update()
        if show_fps:
            window.blit(font.render(str(int(clock.get_fps())), True, (255, 255, 100)), (2, 27))
        window.blit(font.render(str(score), True, (255, 255, 255)), (2, 2))
        pygame.display.flip()
        shoot_ticker += 1
        clock.tick(ticks)
        pressed_keys = pygame.key.get_pressed()
        window.blit(background, (0, 0))

        # Controls
        if (pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]) and player.x >= 0:
            if debug:
                print('Event LEFT')
            player.move(-8)

        elif (pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]) and player.x <= window_size[0] - player.rect.w:
            if debug:
                print('Event RIGHT')
            player.move(8)

        if pressed_keys[pygame.K_ESCAPE]:
            window.fill((255, 255, 255, 100))
            stop = False
            while not stop:
                pygame.mouse.set_visible(True)
                pygame.mixer.music.set_volume(0.10)
                quit_button = pygame.Rect(500, 450, 100, 40)
                window.blit(big_font.render('Paused', True, (0, 0, 0)), (40, 200))

                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        if score:
                            with open("scores.dat", "a") as file:
                                file.write(f'\nTime: {str(int(time.time()))} - Score: {str(score)}')
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                            stop = True

                pos = pygame.mouse.get_pos()
                press = pygame.mouse.get_pressed()
                if quit_button.contains(pygame.Rect(pos[0], pos[1], 1, 1)):
                    quit_button = pygame.draw.rect(window, (100, 255, 100), pygame.Rect(500, 450, 160, 40))
                    window.blit(font.render(f'Continue', True, (100, 100, 100)), (518, 457))
                    pygame.display.flip()

                    if press[0]:
                        pygame.mixer.music.set_volume(0.25)
                        break
                else:
                    quit_button = pygame.draw.rect(window, (0, 255, 0), pygame.Rect(500, 450, 160, 40))
                    window.blit(font.render(f'Continue', True, (0, 0, 0)), (518, 457))
                    pygame.display.flip()

        if pressed_keys[pygame.K_SPACE]:
            if shoot_ticker >= 15 and energy_bar.energy > 0:
                bullets.append(Bullet(player))
                shoot_ticker = 0
                energy_bar.shot()

            elif energy_bar.energy <= 0:
                energy_bar.blinking = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                if debug:
                    print('Event QUIT')
                if score:
                    with open("scores.dat", "a") as file:
                        file.write(f'\nTime: {str(int(time.time()))} - Score: {str(score)}')
                quit()

            elif event.type == 1:
                meteors.append(Meteor())
                if debug:
                    print('Spawning meteor')

                if acceleration < 1.2:
                    pass

            elif event == game_over_event:
                window.fill((255, 255, 255))

                if score:
                    with open("scores.dat", "a") as file:
                        file.write(f'\nTime: {str(int(time.time()))} - Score: {str(score)}')

                while True:
                    pygame.mouse.set_visible(True)
                    quit_button = pygame.Rect(500, 450, 100, 40)
                    retry_button = pygame.Rect(500, 500, 100, 40)
                    window.blit(big_font.render('Game over!!', True, (0, 0, 0)), (40, 200))
                    window.blit(font.render(f'Score: {score}', True, (100, 100, 100)), (100, 350))
                    pygame.display.flip()
                    acceleration = 0.1
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            quit()

                    pos = pygame.mouse.get_pos()
                    press = pygame.mouse.get_pressed()
                    if quit_button.contains(pygame.Rect(pos[0], pos[1], 1, 1)):
                        quit_button = pygame.draw.rect(window, (255, 100, 100), pygame.Rect(500, 450, 100, 40))
                        window.blit(font.render(f'Quit', True, (100, 100, 100)), (518, 457))
                        pygame.display.flip()

                        if press[0]:
                            quit()

                    else:
                        quit_button = pygame.draw.rect(window, (255, 0, 0), pygame.Rect(500, 450, 100, 40))
                        window.blit(font.render(f'Quit', True, (0, 0, 0)), (518, 457))
                        pygame.display.flip()

                    if retry_button.contains(pygame.Rect(pos[0], pos[1], 1, 1)):
                        retry_button = pygame.draw.rect(window, (100, 255, 100), pygame.Rect(500, 500, 100, 40))
                        window.blit(font.render(f'Retry', True, (100, 100, 100)), (518, 507))
                        pygame.display.flip()

                        if press[0]:
                            pygame.event.clear()
                            game(True)

                    else:
                        retry_button = pygame.draw.rect(window, (0, 255, 0), pygame.Rect(500, 500, 100, 40))
                        window.blit(font.render(f'Retry', True, (0, 0, 0)), (518, 507))
                        pygame.display.flip()

        for bullet in bullets:
            if bullet.y < -50:
                bullet.kill()
                bullets.pop(bullets.index(bullet))

        for meteor in meteors:
            if meteor.x > 800:
                meteors.pop(meteors.index(meteor))
            if meteor.check_collide(bullets):
                meteors.pop(meteors.index(meteor))
                score += 1

        station.check_collide(meteors)


game()
