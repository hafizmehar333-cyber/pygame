import pygame
import random
import sys
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Rush - Cyberpunk Runner")

# Colors (Neon Cyberpunk Palette)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_GREEN = (0, 255, 0)
NEON_YELLOW = (255, 255, 0)
NEON_PURPLE = (128, 0, 255)
DARK_BLUE = (0, 0, 50)

# Game variables
clock = pygame.time.Clock()
FPS = 60
game_speed = 8
gravity = 0.8
jump_strength = -15
score = 0
high_score = 0
game_active = False
font = pygame.font.SysFont('Arial', 30)
big_font = pygame.font.SysFont('Arial', 60)

# Player properties
player_width = 40
player_height = 60
player_x = WIDTH // 4
player_y = HEIGHT - player_height - 100
player_vel_y = 0
player_jumping = False
player_sliding = False
slide_timer = 0
player_lane = 1  # 0: left, 1: middle, 2: right
lane_positions = [WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4]

# Obstacle properties
obstacle_width = 50
obstacle_height = 50
obstacles = []
obstacle_timer = 0

# Coin properties
coin_radius = 15
coins = []
coin_timer = 0

# Particle effects
particles = []

# Background elements
buildings = []
for i in range(5):
    buildings.append({
        'x': random.randint(0, WIDTH),
        'width': random.randint(100, 300),
        'height': random.randint(200, 500),
        'speed': random.uniform(0.5, 2)
    })

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-3, -1)
        self.life = random.randint(20, 40)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.speed_y += 0.1
        
    def draw(self):
        alpha = min(255, self.life * 10)
        gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.size, (*self.color, alpha))
        gfxdraw.aacircle(screen, int(self.x), int(self.y), self.size, (*self.color, alpha))

def create_particles(x, y, color, count=10):
    for _ in range(count):
        particles.append(Particle(x, y, color))

def draw_neon_rect(x, y, width, height, color, thickness=2):
    # Draw neon glow effect
    for i in range(thickness, 0, -1):
        alpha = 150 - i * 30
        s = pygame.Surface((width + i*2, height + i*2), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, width + i*2, height + i*2), border_radius=8)
        screen.blit(s, (x - i, y - i))
    
    # Draw main rectangle
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=8)
    
    # Draw inner highlight
    pygame.draw.rect(screen, WHITE, (x + 5, y + 5, width - 10, height - 10), 1, border_radius=5)

def draw_neon_circle(x, y, radius, color):
    # Draw neon glow effect
    for i in range(3, 0, -1):
        alpha = 150 - i * 40
        gfxdraw.filled_circle(screen, x, y, radius + i*3, (*color, alpha))
    
    # Draw main circle
    gfxdraw.filled_circle(screen, x, y, radius, color)
    gfxdraw.aacircle(screen, x, y, radius, color)
    
    # Draw inner highlight
    gfxdraw.aacircle(screen, x, y, radius - 5, WHITE)

def draw_player():
    global player_y, player_vel_y, player_jumping, player_sliding, slide_timer
    
    # Handle gravity
    if player_jumping:
        player_vel_y += gravity
        player_y += player_vel_y
        
        # Landing
        if player_y >= HEIGHT - player_height - 100:
            player_y = HEIGHT - player_height - 100
            player_jumping = False
            player_vel_y = 0
    
    # Handle sliding
    if player_sliding:
        slide_timer -= 1
        if slide_timer <= 0:
            player_sliding = False
    
    # Draw player with neon effect
    lane_x = lane_positions[player_lane]
    
    if player_sliding:
        # Draw sliding player
        draw_neon_rect(lane_x - player_width//2, player_y + player_height//2, 
                       player_width, player_height//2, NEON_BLUE)
    else:
        # Draw standing player
        draw_neon_rect(lane_x - player_width//2, player_y, 
                       player_width, player_height, NEON_BLUE)
    
    # Draw player trail
    for i in range(5):
        alpha = 100 - i * 20
        trail_x = lane_x - player_vel_y * i * 0.5
        trail_y = player_y + player_height // 2
        trail_size = 5 - i
        if trail_size > 0:
            gfxdraw.filled_circle(screen, int(trail_x), int(trail_y), trail_size, (*NEON_BLUE, alpha))

def draw_obstacles():
    global obstacles, obstacle_timer
    
    # Create new obstacles
    obstacle_timer += 1
    if obstacle_timer > random.randint(30, 90):
        lane = random.randint(0, 2)
        obstacle_type = random.choice(['block', 'spike'])
        obstacles.append({
            'x': WIDTH,
            'y': HEIGHT - obstacle_height - 100 if obstacle_type == 'block' else HEIGHT - obstacle_height - 50,
            'width': obstacle_width,
            'height': obstacle_height,
            'lane': lane,
            'type': obstacle_type
        })
        obstacle_timer = 0
    
    # Update and draw obstacles
    for obstacle in obstacles[:]:
        obstacle['x'] -= game_speed
        
        # Draw obstacle with neon effect
        lane_x = lane_positions[obstacle['lane']]
        
        if obstacle['type'] == 'block':
            draw_neon_rect(lane_x - obstacle['width']//2, obstacle['y'], 
                           obstacle['width'], obstacle['height'], NEON_PINK)
        else:  # spike
            points = [
                (lane_x, obstacle['y']),
                (lane_x - obstacle['width']//2, obstacle['y'] + obstacle['height']),
                (lane_x + obstacle['width']//2, obstacle['y'] + obstacle['height'])
            ]
            pygame.draw.polygon(screen, NEON_PINK, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Remove off-screen obstacles
        if obstacle['x'] < -obstacle['width']:
            obstacles.remove(obstacle)

def draw_coins():
    global coins, coin_timer
    
    # Create new coins
    coin_timer += 1
    if coin_timer > random.randint(40, 100):
        lane = random.randint(0, 2)
        coins.append({
            'x': WIDTH,
            'y': HEIGHT - 150 - random.randint(0, 100),
            'lane': lane,
            'collected': False
        })
        coin_timer = 0
    
    # Update and draw coins
    for coin in coins[:]:
        coin['x'] -= game_speed
        
        # Draw coin with neon effect
        lane_x = lane_positions[coin['lane']]
        draw_neon_circle(lane_x, coin['y'], coin_radius, NEON_YELLOW)
        
        # Remove off-screen coins
        if coin['x'] < -coin_radius * 2:
            coins.remove(coin)

def check_collisions():
    global player_lane, player_y, player_height, player_sliding, game_active, score
    
    player_rect = pygame.Rect(
        lane_positions[player_lane] - player_width//2,
        player_y if not player_sliding else player_y + player_height//2,
        player_width,
        player_height//2 if player_sliding else player_height
    )
    
    # Check obstacle collisions
    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(
            lane_positions[obstacle['lane']] - obstacle['width']//2,
            obstacle['y'],
            obstacle['width'],
            obstacle['height']
        )
        
        if player_rect.colliderect(obstacle_rect):
            create_particles(lane_positions[player_lane], player_y + player_height//2, NEON_PINK, 20)
            game_active = False
            return
    
    # Check coin collisions
    for coin in coins[:]:
        coin_rect = pygame.Rect(
            lane_positions[coin['lane']] - coin_radius,
            coin['y'] - coin_radius,
            coin_radius * 2,
            coin_radius * 2
        )
        
        if player_rect.colliderect(coin_rect) and not coin['collected']:
            coin['collected'] = True
            score += 10
            create_particles(lane_positions[coin['lane']], coin['y'], NEON_YELLOW, 15)
            coins.remove(coin)

def draw_background():
    # Fill background with dark blue
    screen.fill(DARK_BLUE)
    
    # Draw moving buildings
    for building in buildings:
        building['x'] -= building['speed']
        if building['x'] < -building['width']:
            building['x'] = WIDTH
            building['width'] = random.randint(100, 300)
            building['height'] = random.randint(200, 500)
        
        # Draw building with neon effect
        draw_neon_rect(building['x'], HEIGHT - building['height'], 
                       building['width'], building['height'], NEON_PURPLE, 3)
        
        # Draw windows
        for i in range(5, building['height'] - 10, 20):
            for j in range(10, building['width'] - 10, 20):
                if random.random() > 0.3:  # Randomly light windows
                    pygame.draw.rect(screen, NEON_YELLOW, 
                                    (building['x'] + j, HEIGHT - building['height'] + i, 10, 10))
    
    # Draw road
    pygame.draw.rect(screen, (30, 30, 40), (0, HEIGHT - 100, WIDTH, 100))
    
    # Draw road markings
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, WHITE, (i, HEIGHT - 50, 20, 5))

def draw_ui():
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))
    
    # Draw high score
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(high_score_text, (20, 60))
    
    # Draw game over screen
    if not game_active:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_text = big_font.render("GAME OVER", True, NEON_PINK)
        restart_text = font.render("Press SPACE to Restart", True, WHITE)
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

def reset_game():
    global player_y, player_vel_y, player_jumping, player_sliding, slide_timer
    global player_lane, obstacles, coins, particles, score, game_active, game_speed
    
    player_y = HEIGHT - player_height - 100
    player_vel_y = 0
    player_jumping = False
    player_sliding = False
    slide_timer = 0
    player_lane = 1
    obstacles = []
    coins = []
    particles = []
    score = 0
    game_active = True
    game_speed = 8

def main():
    global game_active, score, high_score, game_speed
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_active:
                        reset_game()
                    elif not player_jumping and not player_sliding:
                        player_jumping = True
                        player_vel_y = jump_strength
                        create_particles(lane_positions[player_lane], player_y + player_height, NEON_BLUE, 10)
                
                if event.key == pygame.K_DOWN and not player_sliding and not player_jumping:
                    player_sliding = True
                    slide_timer = 30
                    create_particles(lane_positions[player_lane], player_y + player_height, NEON_BLUE, 10)
                
                if event.key == pygame.K_LEFT and player_lane > 0:
                    player_lane -= 1
                    create_particles(lane_positions[player_lane], player_y + player_height//2, NEON_BLUE, 5)
                
                if event.key == pygame.K_RIGHT and player_lane < 2:
                    player_lane += 1
                    create_particles(lane_positions[player_lane], player_y + player_height//2, NEON_BLUE, 5)
        
        if game_active:
            # Increase game speed gradually
            game_speed += 0.002
            score += 1
            
            # Update high score
            if score > high_score:
                high_score = score
            
            # Update particles
            for particle in particles[:]:
                particle.update()
                if particle.life <= 0:
                    particles.remove(particle)
            
            # Draw everything
            draw_background()
            draw_player()
            draw_obstacles()
            draw_coins()
            check_collisions()
            
            # Draw particles
            for particle in particles:
                particle.draw()
        
        draw_ui()
        pygame.display.update()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
