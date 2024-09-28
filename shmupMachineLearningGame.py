import pygame
import random
import math
from shmupNN import *
from shmupSettings import *

from pygame.sprite import Group

def rect_distance(rect1, rect2):
    distance = math.sqrt((rect1.centerx - rect2.centerx) ** 2 + (rect1.centery - rect2.centery) ** 2) 
    return distance

class Player(pygame.sprite.Sprite):
    def __init__(self, gene, game):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((14, 14))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.radius = PLAYER_RADIUS
        pygame.draw.circle(self.image, GREEN, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shoot_timer = 0
        self.shoot_times = 0
        self.score = 0
        self.life = True
        self.game = game
        self.gene = gene.copy()
        self.nn = Net(N_INPUT, N_HIDDEN1, N_HIDDEN2, N_OUTPUT, self.gene)

    def update(self):
        self.shoot()
        self.speedx = 0
        action = self.nn.predict(self.get_state())
        if action == 1:
            self.speedx = -10
            self.score += 10
        if action == 2:
            self.speedx = 10
            self.score += 10
        self.rect.x += self.speedx
        if self.rect.right > WIDTH - 50:
            self.rect.right = WIDTH - 50
        if self.rect.left < 50:
            self.rect.left = 50

    def get_state(self):
        state = []
        state.append(self.rect.centerx)
        for mob in self.game.mobs:
            state.append(mob.rect.centerx)
            state.append(mob.rect.centery)
        return state
    
    def shoot(self):
        self.shoot_timer += 1
        if self.shoot_timer / 9 >= 1:
            self.shoot_times += 1
            self.shoot_timer %= 9
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((100, 100))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.radius = BOSS_RADIUS
        pygame.draw.circle(self.image, WHITE, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.centery = 120

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.radius = MOB_RADIUS
        pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(6, 12)
        self.speedx = random.randrange(-4, 4)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(6, 12)
            self.speedx = random.randrange(-4, 4)
        if self.rect.right < 0:
            self.speedx = -self.speedx
        if self.rect.left > WIDTH:
            self.speedx = -self.speedx

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((5, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Game:
    def __init__(self):
        #Initialize and create window
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(CAPION)
        self.clock = pygame.time.Clock()

        self.all_sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.players = pygame.sprite.Group()

        self.running = True
        self.playing = False
        self.current_generation = 0
        self.record = dict()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
        if not self.running:
            return
        #Evolve later

    def reset(self, gene_list):
        for s in self.all_sprites:
            s.kill()
            self.record.clear()
        boss = Boss()
        self.all_sprites.add(boss)
        for i in range(8):
            mob = Mob()
            self.all_sprites.add(mob)
            self.mobs.add(mob)
        for i in range(10):
            player = Player(gene_list[i], self)
            self.all_sprites.add(player)
            self.players.add(player)
        
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.playing = False

    def _update(self):
        self.all_sprites.update()
        if not self.players:
            self.playing = False
            return
        for player in self.players:
            if player.rect.centerx >= 190 and player.rect.centerx <= 290:
                player.score += 16
            elif player.rect.centerx >= 120 and player.rect.centerx <= 360:
                player.score += 4
            elif player.rect.centerx >= 50 and player.rect.centerx <= WIDTH - 50:
                player.score *= 0.98
            for mob in self.mobs:
                distance = rect_distance(player.rect, mob.rect)
                if distance < 19:
                    player.score /= (player.shoot_times ** 0.6)
                    player.score = int(player.score)
                    while player.score in self.record:
                        player.score += 1
                    self.record[player.score] = player.gene
                    player.kill()
                elif distance < 27:
                    if player.rect.centerx >= 140 and player.rect.centerx <= 340:
                        player.score += 30
    
    def _draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()