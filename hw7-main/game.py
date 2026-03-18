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
            pygame.Rect(100, 450, 250, 20),   
            pygame.Rect(350, 320, 250, 20),   
            pygame.Rect(50, 180, 250, 20),   
        ],
        'lava': [], 'water': [],
        'f_door': pygame.Rect(80, 110, 45, 70),
        'w_door': pygame.Rect(150, 110, 45, 70),
        'gems': [(200, 410, 'Fireboy'), (500, 280, 'Watergirl')]
    },
    {
        'walls': [
            pygame.Rect(0, 600, 700, 50),     
            pygame.Rect(0, 0, 20, 650),       
            pygame.Rect(680, 0, 20, 650),     
            pygame.Rect(300, 480, 380, 20),   
            pygame.Rect(20, 360, 350, 20),    
            pygame.Rect(350, 240, 330, 20),   
            pygame.Rect(20, 120, 300, 20),    
        ],
        'lava': [pygame.Rect(250, 585, 100, 15)], 
        'water': [pygame.Rect(400, 585, 100, 15)], 
        'f_door': pygame.Rect(60, 50, 45, 70),
        'w_door': pygame.Rect(130, 50, 45, 70),
        'gems': [(600, 440, 'Fireboy'), (100, 320, 'Watergirl'), (600, 200, 'Fireboy')]
    }
]

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

    def draw(self, surface):
        # Update walk timer
        if self.vel_x != 0 and self.is_grounded:
            self.walk_timer += 0.2
        else:
            self.walk_timer = 0

        # Jump Stretch Logic
        # Stretch when moving fast vertically, squash when grounded
        stretch = 0
        if not self.is_grounded:
            stretch = abs(self.vel_y) * 0.8
        
        # 1. Legs (Drawn relative to the bottom of the rect)
        leg_swing = math.sin(self.walk_timer) * 8
        # Left Leg
        pygame.draw.rect(surface, self.dark_color, 
                         (self.rect.x + 6, self.rect.bottom - 12 + (leg_swing if leg_swing > 0 else 0), 8, 12), border_radius=3)
        # Right Leg
        pygame.draw.rect(surface, self.dark_color, 
                         (self.rect.right - 14, self.rect.bottom - 12 + (-leg_swing if leg_swing > 0 else 0), 8, 12), border_radius=3)

        # 2. Main Body (With Stretch effect)
        body_h = 30 + (stretch * 0.5)
        body_y = self.rect.y + 14 - (stretch * 0.2)
        body_rect = pygame.Rect(self.rect.x + 3, body_y, 26, body_h)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=5)
        
        # 3. Head (Follows the body stretch)
        head_center = (self.rect.centerx, body_y - 2)
        pygame.draw.circle(surface, self.color, head_center, 12)
        
        # 4. Eyes
        look_offset = 5 if self.vel_x >= 0 else -5
        pygame.draw.circle(surface, COLOR_WHITE, (head_center[0] + look_offset, head_center[1] - 2), 4)
        pygame.draw.circle(surface, (0, 0, 0), (head_center[0] + look_offset + (1 if self.vel_x >= 0 else -1), head_center[1] - 2), 2)

        # 5. Features
        if self.name == "Fireboy":
            flame_pts = [(head_center[0], head_center[1] - 14), 
                         (head_center[0] - 8, head_center[1] - 4), 
                         (head_center[0] + 8, head_center[1] - 4)]
            pygame.draw.polygon(surface, (255, 165, 0), flame_pts)
        else:
            pygame.draw.circle(surface, (180, 230, 255), (head_center[0], head_center[1] - 10), 5)

    def update(self, walls):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[self.controls['left']]: self.vel_x = -self.speed
        if keys[self.controls['right']]: self.vel_x = self.speed

        # X Movement
        self.rect.x += self.vel_x
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel_x > 0: self.rect.right = wall.left
                if self.vel_x < 0: self.rect.left = wall.right

        # Jump
        if keys[self.controls['up']] and self.is_grounded:
            self.vel_y = self.jump_power
            self.is_grounded = False

        # Gravity & Y Movement
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        
        # Ground Collision (Fixed the Shaking)
        on_floor = False
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel_y > 0: # Falling
                    self.rect.bottom = wall.top
                    self.vel_y = 0
                    on_floor = True
                elif self.vel_y < 0: # Hitting ceiling
                    self.rect.top = wall.bottom
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
        return f, w, g, d['walls'], d['lava'], d['water'], d['f_door'], d['w_door']

    fireboy, watergirl, gems, walls, lava, water, f_door, w_door = setup(lvl_idx)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and state == "GAMEOVER" and event.key == pygame.K_r:
                fireboy, watergirl, gems, walls, lava, water, f_door, w_door = setup(lvl_idx)
                state = "PLAYING"

        if state == "PLAYING":
            fireboy.update(walls)
            watergirl.update(walls)

            for l in lava:
                if watergirl.rect.colliderect(l): state = "GAMEOVER"
            for wt in water:
                if fireboy.rect.colliderect(wt): state = "GAMEOVER"

            for gem in gems[:]:
                if fireboy.rect.colliderect(gem['rect']) and gem['owner'] == 'Fireboy':
                    fireboy.score += 10; gems.remove(gem)
                elif watergirl.rect.colliderect(gem['rect']) and gem['owner'] == 'Watergirl':
                    watergirl.score += 10; gems.remove(gem)

            if fireboy.rect.colliderect(f_door) and watergirl.rect.colliderect(w_door):
                lvl_idx += 1
                if lvl_idx < len(LEVELS):
                    fs, ws = fireboy.score, watergirl.score
                    fireboy, watergirl, gems, walls, lava, water, f_door, w_door = setup(lvl_idx)
                    fireboy.score, watergirl.score = fs, ws
                else: state = "WIN"

        # --- Rendering ---
        screen.fill(COLOR_BG)
        for wl in walls: pygame.draw.rect(screen, COLOR_WALL, wl, border_radius=3)
        for lv in lava: pygame.draw.rect(screen, COLOR_LAVA, lv)
        for wt in water: pygame.draw.rect(screen, COLOR_POOL, wt)
        
        pygame.draw.rect(screen, COLOR_FIRE, f_door, 3, border_radius=5)
        pygame.draw.rect(screen, COLOR_WATER, w_door, 3, border_radius=5)

        for gem in gems:
            c = COLOR_FIRE if gem['owner'] == 'Fireboy' else COLOR_WATER
            pygame.draw.circle(screen, c, gem['rect'].center, 8)

        fireboy.draw(screen)
        watergirl.draw(screen)

        pygame.draw.rect(screen, COLOR_SIDEBAR, (GAME_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        screen.blit(f_stats.render("PLAYER STATS", True, COLOR_GOLD), (GAME_WIDTH + 15, 30))
        screen.blit(f_stats.render(f"F: {fireboy.score}", True, COLOR_FIRE), (GAME_WIDTH + 20, 70))
        screen.blit(f_stats.render(f"W: {watergirl.score}", True, COLOR_WATER), (GAME_WIDTH + 20, 105))
        
        screen.blit(f_stats.render("GUIDE", True, COLOR_GOLD), (GAME_WIDTH + 15, 200))
        guide = ["Fireboy: ARROWS", "Watergirl: WASD", "", "LAVA: Red", "WATER: Blue", "", "F safe in Red", "W safe in Blue", "Goal: Reach The Boxes"]
        for i, line in enumerate(guide):
            screen.blit(f_guide.render(line, True, COLOR_WHITE), (GAME_WIDTH + 20, 240 + (i * 22)))

        if state == "GAMEOVER":
            ov = pygame.Surface((GAME_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,200)); screen.blit(ov, (0,0))
            screen.blit(f_go.render("TRY AGAIN", True, COLOR_LAVA), (GAME_WIDTH//2-140, 250))
            screen.blit(f_guide.render("Press 'R' to Restart Level", True, COLOR_WHITE), (GAME_WIDTH//2-90, 320))

        if state == "WIN":
            screen.blit(f_go.render("VICTORY!", True, COLOR_GOLD), (GAME_WIDTH//2-110, 250))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__": main()