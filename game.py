import pygame
import sys
import math

# --- Colors & Theme ---
COLOR_BG = (10, 10, 18)        
COLOR_SIDEBAR = (25, 25, 35)   
COLOR_WALL = (75, 75, 85)      
COLOR_FIRE = (255, 82, 82)     
COLOR_FIRE_DARK = (180, 40, 40)
COLOR_WATER = (52, 152, 219)   
COLOR_WATER_DARK = (30, 90, 150)
COLOR_GOLD = (241, 196, 15)    
COLOR_WHITE = (236, 240, 241)
COLOR_LAVA = (255, 69, 0)      
COLOR_POOL = (0, 80, 255)       
COLOR_WOOD = (139, 69, 19)      
COLOR_METAL = (100, 100, 110)   
COLOR_LAVA_GLOW = (255, 120, 0)
COLOR_WATER_GLOW = (100, 200, 255)

# --- Constants ---
GAME_WIDTH = 700   
SIDEBAR_WIDTH = 200
SCREEN_WIDTH = GAME_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = 650
FPS = 60

# --- Levels Data ---
LEVELS = [
    {
        'walls': [
            pygame.Rect(0, 600, 700, 50),     
            pygame.Rect(0, 0, 20, 650),       
            pygame.Rect(680, 0, 20, 650),     
            pygame.Rect(20, 510, 330, 20),   
            pygame.Rect(350, 380, 330, 20),   
            pygame.Rect(20, 240, 330, 20),   
        ],
        'lava': [], 'water': [],
        'f_door': pygame.Rect(80, 170, 45, 70),
        'w_door': pygame.Rect(150, 170, 45, 70),
        'gems': [(200, 470, 'Fireboy'), (500, 340, 'Watergirl')],
        'boxes': [(300, 560)], 
        'platforms': [],
        'levers': [(450, 570, pygame.Rect(350, 380, 20, 130))] # Gate blocking access to gems
    },
    {
        'walls': [
            pygame.Rect(0, 600, 700, 50),     
            pygame.Rect(0, 0, 20, 650),       
            pygame.Rect(680, 0, 20, 650),     
            pygame.Rect(20, 480, 280, 20),    
            pygame.Rect(400, 360, 280, 20),   
            pygame.Rect(20, 240, 280, 20),    
            pygame.Rect(400, 120, 280, 20),    
        ],
        'lava': [pygame.Rect(160, 465, 120, 15)], # Lava moved further right on the platform (y=480)
        'water': [pygame.Rect(450, 585, 150, 15)], 
        'f_door': pygame.Rect(600, 50, 45, 70),
        'w_door': pygame.Rect(500, 50, 45, 70),
        'gems': [(600, 320, 'Fireboy'), (100, 440, 'Watergirl'), (600, 80, 'Fireboy')],
        'boxes': [(120, 440)], # Box moved further right on the floor/platform area
        'levers': [(630, 330, pygame.Rect(400, 240, 20, 120))], # Barrier to next floor
        'platforms': [
            (320, 480, 60, 20, 320, 360, 2), 
            (320, 240, 60, 20, 320, 120, 2)  
        ]
    },
    {
        'walls': [
            pygame.Rect(0, 600, 700, 50),     
            pygame.Rect(0, 0, 20, 650),       
            pygame.Rect(680, 0, 20, 650),     
            pygame.Rect(200, 500, 20, 100),   # Obstacle wall
            pygame.Rect(20, 300, 500, 20),    # Mid divider
            pygame.Rect(500, 150, 180, 20),   # Top final
        ],
        'lava': [pygame.Rect(300, 585, 180, 15)], # Lava moved away from spawn
        'water': [pygame.Rect(500, 585, 180, 15)], # Water moved right
        'f_door': pygame.Rect(600, 80, 45, 70),
        'w_door': pygame.Rect(530, 80, 45, 70),
        'gems': [(100, 560, 'Fireboy'), (600, 560, 'Watergirl')],
        'boxes': [(400, 560)], 
        'levers': [(250, 270, pygame.Rect(400, 150, 20, 150))], # Final barrier
        'platforms': [
            (550, 450, 100, 20, 550, 300, 3), # Rising platform
            (50, 300, 100, 20, 50, 150, 2)    # Final ascent
        ]
    }
]

class Box:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel_y = 0
        self.gravity = 0.8
        self.is_grounded = False

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_WOOD, self.rect, border_radius=4)
        pygame.draw.rect(surface, (100, 50, 10), self.rect, 3, border_radius=4) # Border
        # Cross pattern for "wooden crate" look
        pygame.draw.line(surface, (100, 50, 10), self.rect.topleft, self.rect.bottomright, 2)
        pygame.draw.line(surface, (100, 50, 10), self.rect.topright, self.rect.bottomleft, 2)

    def update(self, walls, other_boxes):
        # Gravity
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        
        self.is_grounded = False
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel_y > 0:
                    self.rect.bottom = wall.top
                    self.vel_y = 0
                    self.is_grounded = True
                elif self.vel_y < 0:
                    self.rect.top = wall.bottom
                    self.vel_y = 0
        
        for box in other_boxes:
            if box != self and self.rect.colliderect(box.rect):
                if self.vel_y > 0:
                    self.rect.bottom = box.rect.top
                    self.vel_y = 0
                    self.is_grounded = True

class MovingPlatform:
    def __init__(self, x, y, width, height, target_x, target_y, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.start_pos = (x, y)
        self.target_pos = (target_x, target_y)
        self.speed = speed
        self.direction = 1 # 1 for moving to target, -1 for moving to start
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        # Calculate destination
        dest = self.target_pos if self.direction == 1 else self.start_pos
        dx = dest[0] - self.rect.x
        dy = dest[1] - self.rect.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist < self.speed:
            self.rect.x, self.rect.y = dest
            self.direction *= -1
            self.vel_x, self.vel_y = 0, 0
        else:
            self.vel_x = (dx / dist) * self.speed
            self.vel_y = (dy / dist) * self.speed
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_METAL, self.rect, border_radius=2)
        pygame.draw.rect(surface, (60, 60, 70), self.rect, 2, border_radius=2)

class Lever:
    def __init__(self, x, y, gate_rect):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.gate_rect = gate_rect # original rect
        self.current_gate = pygame.Rect(gate_rect) # active rect
        self.active = False
        self.cooldown = 0 # Prevent rapid toggling

    def update(self, players):
        if self.cooldown > 0: self.cooldown -= 1
        
        collision = False
        for p in players:
            if self.rect.colliderect(p.rect):
                collision = True
                break
        
        if collision and self.cooldown == 0:
            self.active = not self.active
            self.cooldown = 30 # Half second cooldown
            
        # If active, the gate "disappears" (move it way off screen)
        if self.active:
            self.current_gate.y = -1000
        else:
            self.current_gate.y = self.gate_rect.y

    def draw(self, surface):
        # Base
        pygame.draw.rect(surface, (50, 50, 50), (self.rect.x, self.rect.bottom-5, 30, 5))
        # Stick
        color = (0, 255, 0) if self.active else (255, 0, 0)
        angle = 45 if self.active else -45
        end_x = self.rect.centerx + math.sin(math.radians(angle)) * 20
        end_y = self.rect.centery - math.cos(math.radians(angle)) * 20
        pygame.draw.line(surface, (150, 150, 150), self.rect.center, (end_x, end_y), 4)
        pygame.draw.circle(surface, color, (int(end_x), int(end_y)), 5)
        
        # Draw the target Gate if it's currently blocking (not active)
        if not self.active:
            pygame.draw.rect(surface, COLOR_METAL, self.current_gate, border_radius=3)
            pygame.draw.rect(surface, (40, 40, 50), self.current_gate, 2, border_radius=3)

class Particle:
    def __init__(self, x, y, color, vel_x, vel_y, life):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = int((self.life / self.max_life) * 255)
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (2, 2), 2)
        surface.blit(s, (int(self.x), int(self.y)))

class Player:
    def __init__(self, x, y, color, dark_color, controls, name):
        self.start_pos = (x, y)
        self.rect = pygame.Rect(x, y, 32, 54) # Physics hitbox
        self.color = color
        self.dark_color = dark_color
        self.controls = controls
        self.name = name
        
        self.vel_y = 0
        self.vel_x = 0
        self.speed = 5           
        self.jump_power = -17   
        self.gravity = 0.8       
        self.is_grounded = False
        self.score = 0
        self.walk_timer = 0
        
        # Visual squash/stretch
        self.anim_offset_y = 0

    def draw(self, surface, alpha=255):
        # Update walk timer
        if self.vel_x != 0 and self.is_grounded:
            self.walk_timer += 0.2
        else:
            self.walk_timer = 0

        # Jump Stretch Logic
        stretch = 0
        if not self.is_grounded:
            stretch = abs(self.vel_y) * 0.8
        
        # Draw on a temporary surface to apply global alpha
        temp = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
        # Center coordinates for drawing on the temp surface
        cx, cy = (self.rect.width // 2) + 10, (self.rect.height // 2) + 10
        rx, ry = 10, 10 # rect-relative top-left
        
        # 1. Legs
        leg_swing = math.sin(self.walk_timer) * 8
        pygame.draw.rect(temp, (*self.dark_color, alpha), 
                         (rx + 6, ry + self.rect.height - 12 + (leg_swing if leg_swing > 0 else 0), 8, 12), border_radius=3)
        pygame.draw.rect(temp, (*self.dark_color, alpha), 
                         (rx + self.rect.width - 14, ry + self.rect.height - 12 + (-leg_swing if leg_swing > 0 else 0), 8, 12), border_radius=3)

        # 2. Main Body
        body_h = 30 + (stretch * 0.5)
        body_y = ry + 14 - (stretch * 0.2)
        body_rect = pygame.Rect(rx + 3, body_y, 26, body_h)
        pygame.draw.rect(temp, (*self.color, alpha), body_rect, border_radius=5)
        
        # 3. Head
        head_center = (rx + self.rect.width // 2, body_y - 2)
        pygame.draw.circle(temp, (*self.color, alpha), head_center, 12)
        
        # 4. Eyes
        look_offset = 5 if self.vel_x >= 0 else -5
        pygame.draw.circle(temp, (255, 255, 255, alpha), (head_center[0] + look_offset, head_center[1] - 2), 4)
        pygame.draw.circle(temp, (0, 0, 0, alpha), (head_center[0] + look_offset + (1 if self.vel_x >= 0 else -1), head_center[1] - 2), 2)

        # 5. Features
        if self.name == "Fireboy":
            flame_pts = [(head_center[0], head_center[1] - 14), 
                         (head_center[0] - 8, head_center[1] - 4), 
                         (head_center[0] + 8, head_center[1] - 4)]
            pygame.draw.polygon(temp, (255, 165, 0, alpha), flame_pts)
        else:
            pygame.draw.circle(temp, (180, 230, 255, alpha), (head_center[0], head_center[1] - 10), 5)

        surface.blit(temp, (self.rect.x - 10, self.rect.y - 10))

    def update(self, walls, boxes, platforms, levers):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[self.controls['left']]: self.vel_x = -self.speed
        if keys[self.controls['right']]: self.vel_x = self.speed

        # Gates (levers)
        all_walls = walls + [l.current_gate for l in levers if not l.active]

        # X Movement
        self.rect.x += self.vel_x
        for wall in all_walls:
            if self.rect.colliderect(wall):
                if self.vel_x > 0: self.rect.right = wall.left
                if self.vel_x < 0: self.rect.left = wall.right
        
        for box in boxes:
            if self.rect.colliderect(box.rect):
                if self.vel_x > 0:
                    box.rect.x += self.vel_x
                    # Check box against walls
                    for wall in all_walls:
                        if box.rect.colliderect(wall): box.rect.right = wall.left
                    self.rect.right = box.rect.left
                elif self.vel_x < 0:
                    box.rect.x += self.vel_x
                    for wall in all_walls:
                        if box.rect.colliderect(wall): box.rect.left = wall.right
                    self.rect.left = box.rect.right

        # Jump
        if keys[self.controls['up']] and self.is_grounded:
            self.vel_y = self.jump_power
            self.is_grounded = False

        # Gravity & Y Movement
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        
        # Ground Collision (Fixed the Shaking)
        on_floor = False
        all_ground = all_walls + [b.rect for b in boxes] + [p.rect for p in platforms]
        
        for platform in platforms:
             if self.rect.colliderect(platform.rect) and self.vel_y >= 0:
                 if self.rect.bottom <= platform.rect.top + 10:
                     self.rect.bottom = platform.rect.top
                     self.rect.x += platform.vel_x
                     self.rect.y += platform.vel_y
                     self.vel_y = 0
                     on_floor = True

        for wall in all_walls:
            if self.rect.colliderect(wall):
                if self.vel_y > 0: # Falling
                    self.rect.bottom = wall.top
                    self.vel_y = 0
                    on_floor = True
                elif self.vel_y < 0: # Hitting ceiling
                    self.rect.top = wall.bottom
                    self.vel_y = 0
                    
        for box in boxes:
            if self.rect.colliderect(box.rect):
                if self.vel_y > 0:
                    self.rect.bottom = box.rect.top
                    self.vel_y = 0
                    on_floor = True
                elif self.vel_y < 0:
                    self.rect.top = box.rect.bottom
                    self.vel_y = 0
                    
        self.is_grounded = on_floor

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fireboy and Watergirl")
    clock = pygame.time.Clock()
    
    f_stats = pygame.font.SysFont("Verdana", 20, bold=True)
    f_guide = pygame.font.SysFont("Verdana", 14)
    f_go = pygame.font.SysFont("Verdana", 50, bold=True)

    lvl_idx = 0
    state = "PLAYING"
    
    def setup(i):
        d = LEVELS[i]
        f = Player(40, 540, COLOR_FIRE, COLOR_FIRE_DARK, {'up': pygame.K_UP, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}, "Fireboy")
        w = Player(100, 540, COLOR_WATER, COLOR_WATER_DARK, {'up': pygame.K_w, 'left': pygame.K_a, 'right': pygame.K_d}, "Watergirl")
        g = [{'rect': pygame.Rect(x, y, 16, 16), 'owner': owner} for x, y, owner in d['gems']]
        b = [Box(bx, by) for bx, by in d.get('boxes', [])]
        p = [MovingPlatform(px, py, pw, ph, tx, ty, s) for px, py, pw, ph, tx, ty, s in d.get('platforms', [])]
        l = [Lever(lx, ly, gr) for lx, ly, gr in d.get('levers', [])]
        pt = [] # Main particle list
        return f, w, g, d['walls'], d['lava'], d['water'], d['f_door'], d['w_door'], b, p, l, pt

    fireboy, watergirl, gems, walls, lava, water, f_door, w_door, boxes, platforms, levers, particles = setup(lvl_idx)
    death_timer = 0
    win_timer = 0 # Delay for level transition
    shake_timer = 0 # Screen shake effect

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if state == "GAMEOVER" and event.key == pygame.K_r:
                    fireboy, watergirl, gems, walls, lava, water, f_door, w_door, boxes, platforms, levers, particles = setup(lvl_idx)
                    state = "PLAYING"
                    death_timer = 0
                    win_timer = 0
                # Level Skip (Cheat Code: N for Next)
                if event.key == pygame.K_n and state == "PLAYING":
                    lvl_idx += 1
                    if lvl_idx < len(LEVELS):
                        fireboy, watergirl, gems, walls, lava, water, f_door, w_door, boxes, platforms, levers, particles = setup(lvl_idx)
                    else: state = "WIN"

        if state == "PLAYING":
            fireboy.update(walls, boxes, platforms, levers)
            watergirl.update(walls, boxes, platforms, levers)
            for plat in platforms: plat.update()
            for box in boxes: box.update(walls, boxes)
            for lev in levers: lev.update([fireboy, watergirl])
            
            # --- Character Effects ---
            if abs(fireboy.vel_x) > 0 and random.random() < 0.2:
                particles.append(Particle(fireboy.rect.centerx, fireboy.rect.bottom - 5, COLOR_FIRE, random.uniform(-1, 1), -1, 30))
            
            if abs(watergirl.vel_x) > 0 and random.random() < 0.2:
                particles.append(Particle(watergirl.rect.centerx, watergirl.rect.bottom - 5, COLOR_WATER, random.uniform(-1, 1), -1, 30))

            # Watergirl bubbles near water
            for wt in water:
                if watergirl.rect.inflate(40, 40).colliderect(wt) and random.random() < 0.1:
                    particles.append(Particle(watergirl.rect.centerx, watergirl.rect.centery, COLOR_WATER_GLOW, random.uniform(-0.5, 0.5), -1.5, 40))

            # --- Move Particles ---
            particles[:] = [p for p in particles if p.update()]
            
            # --- Spawn Liquid Particles ---
            import random
            for lv in lava:
                if random.random() < 0.15:
                    particles.append(Particle(random.randint(lv.left, lv.right), lv.top, 
                                            COLOR_LAVA_GLOW, random.uniform(-0.5, 0.5), random.uniform(-2, -0.5), 40))
            for wt in water:
                if random.random() < 0.15:
                    particles.append(Particle(random.randint(wt.left, wt.right), wt.top, 
                                            COLOR_WATER_GLOW, random.uniform(-0.3, 0.3), random.uniform(-1.5, -0.5), 50))

            # Hazard Check
            dead_player = None
            for l in lava:
                if watergirl.rect.colliderect(l): dead_player = watergirl
            for wt in water:
                if fireboy.rect.colliderect(wt): dead_player = fireboy
            
            if dead_player:
                state = "DEATH_ANIM"
                death_timer = 40
                shake_timer = 15 # Trigger shake on death
                for _ in range(30):
                    particles.append(Particle(dead_player.rect.centerx, dead_player.rect.centery,
                                            dead_player.color, random.uniform(-3, 3), random.uniform(-5, -1), 60))

            for gem in gems[:]:
                if fireboy.rect.colliderect(gem['rect']) and gem['owner'] == 'Fireboy':
                    fireboy.score += 10; gems.remove(gem)
                elif watergirl.rect.colliderect(gem['rect']) and gem['owner'] == 'Watergirl':
                    watergirl.score += 10; gems.remove(gem)

            if fireboy.rect.colliderect(f_door) and watergirl.rect.colliderect(w_door):
                state = "LEVEL_COMPLETE"
                win_timer = 60 # 1 second delay at 60 FPS

        elif state == "LEVEL_COMPLETE":
            win_timer -= 1
            particles[:] = [p for p in particles if p.update()]
            # Visual reward: spawn some gold/yellow particles
            if win_timer > 30 and random.random() < 0.5:
                px = random.randint(f_door.left, w_door.right)
                py = random.randint(f_door.top, f_door.bottom)
                particles.append(Particle(px, py, COLOR_GOLD, 0, -2, 40))
                
            if win_timer <= 0:
                lvl_idx += 1
                if lvl_idx < len(LEVELS):
                    fs, ws = fireboy.score, watergirl.score
                    fireboy, watergirl, gems, walls, lava, water, f_door, w_door, boxes, platforms, levers, particles = setup(lvl_idx)
                    fireboy.score, watergirl.score = fs, ws
                    state = "PLAYING"
                else: state = "WIN"

        elif state == "DEATH_ANIM":
            particles[:] = [p for p in particles if p.update()]
            for plat in platforms: plat.update()
            death_timer -= 1
            if death_timer <= 0:
                state = "GAMEOVER"

        # --- Rendering ---
        render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        render_surface.fill(COLOR_BG)
        
        # Shake Offset
        offset = (0, 0)
        if shake_timer > 0:
            import random
            offset = (random.randint(-5, 5), random.randint(-5, 5))
            shake_timer -= 1
            
        for wl in walls: pygame.draw.rect(render_surface, COLOR_WALL, wl, border_radius=3)
        for lv in lava: 
            pygame.draw.rect(render_surface, COLOR_LAVA, lv)
            # Surface glisten/glow line
            pygame.draw.line(render_surface, COLOR_LAVA_GLOW, lv.topleft, lv.topright, 2)
        for wt in water: 
            pygame.draw.rect(render_surface, COLOR_POOL, wt)
            pygame.draw.line(render_surface, COLOR_WATER_GLOW, wt.topleft, wt.topright, 2)
        
        # Draw doors (glow if players are nearby)
        f_active = fireboy.rect.colliderect(f_door)
        w_active = watergirl.rect.colliderect(w_door)
        
        def draw_door(rect, base_color, active, name, full_active):
            # Outer frame
            pygame.draw.rect(render_surface, base_color, rect, 3, border_radius=5)
            
            # Glow logic
            glow_color = COLOR_GOLD if full_active else base_color
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5 # 0 to 1
            
            if full_active:
                # Pulsing internal aura when winning
                alpha = int(40 + pulse * 60)
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                s.fill((*glow_color, alpha))
                render_surface.blit(s, rect.topleft)
                
                # Fill animation
                fill_h = int(rect.height * (1.0 - (win_timer / 60.0)))
                fill_rect = pygame.Rect(rect.left, rect.bottom - fill_h, rect.width, fill_h)
                pygame.draw.rect(render_surface, COLOR_GOLD, fill_rect, 0, border_radius=2)
            elif active:
                # Slight border glow when one player is standing there (but not both)
                alpha = int(20 + pulse * 30)
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                s.fill((*base_color, alpha))
                render_surface.blit(s, rect.topleft)
        
        is_win = (state == "LEVEL_COMPLETE")
        draw_door(f_door, COLOR_FIRE, f_active, "F", is_win)
        draw_door(w_door, COLOR_WATER, w_active, "W", is_win)

        for p in particles: p.draw(render_surface)
        for plat in platforms: plat.draw(render_surface)
        for lev in levers: lev.draw(render_surface)
        for box in boxes: box.draw(render_surface)
        
        for gem in gems:
            c = COLOR_FIRE if gem['owner'] == 'Fireboy' else COLOR_WATER
            glow_c = COLOR_LAVA_GLOW if gem['owner'] == 'Fireboy' else COLOR_WATER_GLOW
            center = gem['rect'].center
            # Glow effect
            s = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(s, (*glow_c, 80), (16, 16), 14)
            render_surface.blit(s, (center[0]-16, center[1]-16))
            # Gem shape
            pts = [(center[0], center[1]-8), (center[0]+8, center[1]), 
                   (center[0], center[1]+8), (center[0]-8, center[1])]
            pygame.draw.polygon(render_surface, c, pts)
            pygame.draw.polygon(render_surface, COLOR_WHITE, pts, 1)

        if state != "DEATH_ANIM" or death_timer > 20:
            # If door is filling, fade players
            alpha = 255
            if state == "LEVEL_COMPLETE":
                alpha = max(0, int(255 * (win_timer / 60.0)))
            
            fireboy.draw(render_surface, alpha)
            watergirl.draw(render_surface, alpha)

        pygame.draw.rect(render_surface, COLOR_SIDEBAR, (GAME_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        render_surface.blit(f_stats.render("PLAYER STATS", True, COLOR_GOLD), (GAME_WIDTH + 15, 30))
        render_surface.blit(f_stats.render(f"Fireboy: {fireboy.score}", True, COLOR_FIRE), (GAME_WIDTH + 20, 70))
        render_surface.blit(f_stats.render(f"Watergirl: {watergirl.score}", True, COLOR_WATER), (GAME_WIDTH + 20, 105))
        
        render_surface.blit(f_stats.render("GUIDE", True, COLOR_GOLD), (GAME_WIDTH + 15, 200))
        guide = ["Fireboy: ARROWS", "Watergirl: WASD", "", "LAVA: Red", "WATER: Blue", "", "Fireboy safe in Red", "Watergirl safe in Blue", "Goal: Reach The Doors!"]
        for i, line in enumerate(guide):
            render_surface.blit(f_guide.render(line, True, COLOR_WHITE), (GAME_WIDTH + 20, 240 + (i * 22)))

        if state == "GAMEOVER":
            ov = pygame.Surface((GAME_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,200)); render_surface.blit(ov, (0,0))
            render_surface.blit(f_go.render("TRY AGAIN", True, COLOR_LAVA), (GAME_WIDTH//2-140, 250))
            render_surface.blit(f_guide.render("Press 'R' to Restart Level", True, COLOR_WHITE), (GAME_WIDTH//2-90, 320))

        if state == "WIN":
            render_surface.blit(f_go.render("VICTORY!", True, COLOR_GOLD), (GAME_WIDTH//2-110, 250))

        # Final Blit with Shake offset
        screen.blit(render_surface, offset)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__": main()