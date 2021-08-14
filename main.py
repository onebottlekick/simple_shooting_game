import pygame
import os
import random

# window parameters
pygame.font.init()
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('shoot enemies')

# objects
BC = pygame.image.load(os.path.join('assets', 'bc.png'))
HS = pygame.image.load(os.path.join('assets', 'hs.png'))
BH = pygame.image.load(os.path.join('assets', 'bh.png'))
YH = pygame.image.load(os.path.join('assets', 'yh.png'))

# weapons 
BC_WEAPON = pygame.image.load(os.path.join('assets', 'weapon2.png'))
YH_WEAPON = pygame.image.load(os.path.join('assets', 'weapon1.png'))
HS_WEAPON = pygame.image.load(os.path.join('assets', 'weapon3.png'))
BH_WEAPON = pygame.image.load(os.path.join('assets', 'weapon4.png'))

# background
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-black.png')), (WIDTH, HEIGHT))

class Objects:
    COOLDOWN = 30

    def __init__(self, x, y, hp=100):
        self.x = x
        self.y = y
        self.hp = hp
        self.obj_img = None
        self.weapon_img = None
        self.weapons = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.obj_img, (self.x, self.y))
        for weapon in self.weapons:
            weapon.draw(window)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def move_weapons(self, vel, obj):
        self.cooldown()
        for weapon in self.weapons:
            weapon.move(vel)
            if weapon.off_screen(HEIGHT):
                self.weapons.remove(weapon)
            elif weapon.collision(obj):
                self.weapons.remove(weapon)

    def shoot(self):
        if self.cool_down_counter == 0:
            weapon = Weapon(self.x, self.y, self.weapon_img)
            self.weapons.append(weapon)
            self.cool_down_counter = 1

    def get_width(self):
        return self.obj_img.get_width()

    def get_height(self):
        return self.obj_img.get_height()

class Weapon:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # velocity
    def move(self, vel):
        self.y += vel

    # set weapon show off condition
    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Player(Objects):
    def __init__(self, x, y, hp=100):
        super().__init__(x, y, hp)
        self.obj_img = BC
        self.weapon_img = BC_WEAPON
        self.mask = pygame.mask.from_surface(self.obj_img)
        self.max_hp = hp

    def move_weapons(self, vel, objs):
        self.cooldown()
        for weapon in self.weapons:
            weapon.move(vel)
            if weapon.off_screen(HEIGHT):
                self.weapons.remove(weapon)
            else:
                for obj in objs:
                    if weapon.collision(obj):
                        objs.remove(obj)
                        self.weapons.remove(weapon)

    def hp_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.obj_img.get_height() + 10, self.obj_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.obj_img.get_height() + 10, self.obj_img.get_width() * (self.hp)/self.max_hp, 10))
    
    def draw(self, window):
        super().draw(window)
        self.hp_bar(window)

class Enemy(Objects):
    OBJ_MAP = {
        'hs' : (HS, HS_WEAPON),
        'bh' : (BH, BH_WEAPON),
        'yh' : (YH, YH_WEAPON)
    }

    def __init__(self, x, y, name, hp=100):
        super().__init__(x, y, hp)
        self.obj_img, self.weapon_img = self.OBJ_MAP[name]
        self.mask = pygame.mask.from_surface(self.obj_img)
    
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            weapon = Weapon(self.x, self.y, self.weapon_img)
            self.weapons.append(weapon)
            self.cool_down_counter = 1

# if objects overlaps each other, collide and disappear
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    # main setting parameters
    run = True
    lost = False
    lost_count = 0
    lost_wait_key = 3
    FPS = 60
    level = 0
    lives = 5
    weapon_vel = 5
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont('NanumPen', 50)
    lost_font = pygame.font.SysFont('NanumPen', 60)

    # enemy parameters
    enemies = []
    wave_length = 5
    enemy_vel = 1

    # player parameters
    player = Player(300, 630)
    player_vel = 5

    def refresh_window():
        WIN.blit(BG, (0, 0))

        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))

        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        player.draw(WIN)

        for enemy in enemies:
            enemy.draw(WIN)
        
        if lost:
            lost_label1 = lost_font.render('you lost', 1, (255, 255, 255))
            WIN.blit(lost_label1, (WIDTH/2 - lost_label1.get_width()/2, 350))
            lost_label2 = lost_font.render(f'press any key to play again in {lost_wait_key}seconds...', 1, (255, 255, 255))
            WIN.blit(lost_label2, (WIDTH/2 - lost_label2.get_width()/2, 410))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        refresh_window()

        if lives <= 0 or player.hp <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * lost_wait_key:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        main_menu()
                quit()
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(['hs', 'bh', 'yh']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # player controller
        keys = pygame.key.get_pressed()
        # move
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        # shoot weapon
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_weapons(weapon_vel, player)

            if random.randrange(0, 2 * FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.hp -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_weapons(-weapon_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont('NanumPen', 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render('press any key to start...', 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

main_menu()