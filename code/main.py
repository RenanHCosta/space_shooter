import pygame
from random import randint, uniform
from os.path import join

class Player(pygame.sprite.Sprite):
  def __init__(self, groups):
    super().__init__(groups)
    self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
    self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    self.dir = pygame.math.Vector2()
    self.speed = 300
    
    # cooldown
    self.can_shoot = True
    self.laser_shoot_time = 0
    self.cooldown_duration = 400

    
  def laser_timer(self):
    if not self.can_shoot:
      current_time = pygame.time.get_ticks()
      if current_time - self.laser_shoot_time >= self.cooldown_duration:
        self.can_shoot = True
    
  def update(self, dt):
    keys = pygame.key.get_pressed()
    self.dir.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
    self.dir.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
    self.dir = self.dir.normalize() if self.dir else self.dir
    self.rect.center += self.dir * self.speed * dt
    
    recent_keys = pygame.key.get_just_pressed()
    if recent_keys[pygame.K_SPACE] and self.can_shoot:
      Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
      self.can_shoot = False
      self.laser_shoot_time = pygame.time.get_ticks()
      laser_sound.play()
      
    self.laser_timer()
       
class Star(pygame.sprite.Sprite):
  def __init__(self, groups, surf):
    super().__init__(groups)
    self.image = surf
    self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
  def __init__(self, surf, pos, groups):
    super().__init__(groups)
    self.image = surf
    self.rect = self.image.get_frect(midbottom = pos)
    
  def update(self, dt):
    self.rect.centery -= 400 * dt
    if self.rect.bottom < 0:
      self.kill()    

class Meteor(pygame.sprite.Sprite):
  def __init__(self, surf, pos, groups):
    super().__init__(groups)
    self.original_surf = surf
    self.image = surf
    self.rect = self.image.get_frect(center = pos)
    self.start_time = pygame.time.get_ticks()
    self.lifetime = 3000
    self.dir = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
    self.speed = randint(400, 500)
    self.rotation_speed = randint(40, 80)
    self.rotation = 0

  def update(self, dt):
    self.rect.center += self.dir * self.speed * dt
    if pygame.time.get_ticks() - self.start_time >= self.lifetime:
      self.kill()
    
    self.rotation += self.rotation_speed * dt
    self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
    self.rect = self.image.get_frect(center = self.rect.center)
    
class AnimatedExplosion(pygame.sprite.Sprite):
  def __init__(self, frames, pos, groups):
    super().__init__(groups)
    self.frames = frames
    self.frame_index = 0
    self.image = self.frames[self.frame_index]
    self.rect = self.image.get_frect(center = pos)
    
  def update(self, dt):
    self.frame_index += 20 * dt
    if self.frame_index < len(self.frames):
      self.image = self.frames[int(self.frame_index) % len(self.frames)] 
    else:
      self.kill()

def collisions():
  global game_paused, score
  
  collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
  if collision_sprites:
    game_paused = True
    
  for laser in laser_sprites:
    collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
    if collided_sprites:
      laser.kill()
      AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
      explosion_sound.play()
      score += 200
    
def display_score():
  global score
  score += 0.01
  text_surf = font.render(str(int(score)), True, (240, 240, 240))
  text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
  display_surface.blit(text_surf, text_rect)
  pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10)
  
def game_over():
  text_surf = font.render('GAME OVER', True, (240, 240, 240))
  text_rect = text_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
  display_surface.blit(text_surf, text_rect)
  pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10)
  
  text_surf = font.render('Press space to restart', True, (240, 240, 240))
  text_rect = text_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50))
  display_surface.blit(text_surf, text_rect)

def start_game():
  global score, player, game_paused
  game_paused = False
  score = 0
  for i in range(20):
    Star(all_sprites, star_surf)
  player = Player(all_sprites)
    
# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Shooter')
running = True
clock = pygame.time.Clock()
game_paused = False
score = 0

# import
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.3)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.1)

game_music.play(loops = -1)

all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

# custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

start_game()

while running:
  dt = clock.tick() / 1000
  # print(clock.get_fps())
  
  # event loop
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == meteor_event:
      x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
      Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE and game_paused:
        all_sprites.empty()
        start_game()
  
  if not game_paused:
    # update the game
    all_sprites.update(dt)
    collisions()
        
    # draw the game
    display_surface.fill('#3a2e3f')
    display_score()
    all_sprites.draw(display_surface)
  else:
    game_over()
    
  
  pygame.display.update()
      
pygame.quit()
