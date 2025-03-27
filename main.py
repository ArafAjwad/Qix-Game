import pygame
import random
import time
import math

pygame.init()

# Screen setup
screen_width, screen_height = 700, 700
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Qix Game")
running = True
clock = pygame.time.Clock()

# Game States
GAME_STATES = {
    'INSTRUCTIONS': 0,
    'INSTRUCTIONS_DETAIL': 3,
    'PLAY': 1,
    'END_GAME': 2,
    'PAUSE': 4  # New pause state
}
current_state = GAME_STATES['INSTRUCTIONS']

# Menu selection
menu_selection = 0
pause_menu_selection = 0

# Initialize game fonts
pygame.font.init()
title_font = pygame.font.Font(None, 64)
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Game Variables (will be reset in reset_game)
push_enabled = False
width, height = 10, 10
xpos, ypos = 0, 0
speed = 5
player_path = []
filled_areas = []
lives = 3
invulnerable = False
invulnerability_start_time = 0
INVULNERABILITY_DURATION = 2
sparx = []
perimeter_path = []
qix = {}
total_area = 0
covered_area = 0
level_passed = False
level_pass_time = 0
LEVEL_PASS_DURATION = 2  # Duration to show level passed message

def calculate_polygon_area(polygon):
    """Calculate the area of a polygon using the shoelace formula"""
    n = len(polygon)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += polygon[i][0] * polygon[j][1]
        area -= polygon[j][0] * polygon[i][1]
    area = abs(area) / 2.0
    return area

def calculate_territory_percentage():
    """Calculate the percentage of territory covered"""
    global total_area, covered_area, level_passed, level_pass_time
    
    # Calculate total game area (excluding border)
    if total_area == 0:
        total_area = (screen_width - 100) * (screen_height - 90)
    
    # Sum up the areas of all filled polygons
    covered_area = sum(calculate_polygon_area(area) for area in filled_areas)
    
    # Calculate percentage
    percentage = (covered_area / total_area) * 100 if total_area > 0 else 0
    
    # Check for level completion
    if percentage >= 20 and not level_passed:
        level_passed = True
        level_pass_time = time.time()
    
    return percentage

def line_intersects_circle(line_start, line_end, circle_center, circle_radius):
    """
    Check if a line segment intersects a circle
    """
    x1, y1 = line_start
    x2, y2 = line_end
    cx, cy = circle_center
    
    # Check if the line segment has zero length
    if x1 == x2 and y1 == y2:
        # If the point is within the circle radius, it's a collision
        dist = math.sqrt((cx - x1)**2 + (cy - y1)**2)
        return dist <= circle_radius + 1  # Add 1 for slight tolerance
    
    # Vector from line start to line end
    line_vec_x = x2 - x1
    line_vec_y = y2 - y1
    
    # Vector from line start to circle center
    circle_vec_x = cx - x1
    circle_vec_y = cy - y1
    
    # Calculate line length squared
    line_length_sq = line_vec_x**2 + line_vec_y**2
    
    # Project circle vector onto line vector
    t = max(0, min(1, (circle_vec_x * line_vec_x + circle_vec_y * line_vec_y) / line_length_sq))
    
    # Closest point on the line segment to the circle center
    closest_x = x1 + t * line_vec_x
    closest_y = y1 + t * line_vec_y
    
    # Distance between closest point and circle center
    dist_x = cx - closest_x
    dist_y = cy - closest_y
    
    # Check if distance is less than circle radius
    return (dist_x**2 + dist_y**2) <= (circle_radius + 1)**2

def reset_player_position():
    """Reset player position to starting point"""
    global xpos, ypos, push_enabled, player_path, invulnerable, invulnerability_start_time
    xpos = screen_width / 2
    ypos = screen_height - height - 50
    push_enabled = False
    player_path = []
    invulnerable = True
    invulnerability_start_time = time.time()

def check_sparx_collision():
    """Check if player collides with Sparx"""
    global lives, invulnerable
    
    # Check if currently invulnerable
    if invulnerable:
        if time.time() - invulnerability_start_time > INVULNERABILITY_DURATION:
            invulnerable = False
        return False

    player_rect = pygame.Rect(xpos, ypos, width, height)
    for s in sparx:
        sparx_rect = pygame.Rect(s['x'] - 7, s['y'] - 7, 14, 14)
        if player_rect.colliderect(sparx_rect):
            # If player is pushing and Sparx is touching the green line, lose a life
            if push_enabled and check_sparx_line_collision():
                lives -= 1
                reset_player_position()
                return True
    return False

def check_sparx_line_collision():
    """Check if Sparx touches the green push line and player is in contact"""
    # Only check when push is enabled and there's a path
    if not push_enabled or len(player_path) < 2:
        return False
    
    # Check each Sparx against the entire player path
    for s in sparx:
        # Check if Sparx is touching the green line path
        for i in range(len(player_path) - 1):
            if line_intersects_circle(player_path[i], player_path[i+1], (s['x'], s['y']), 7):
                return True
    return False

def draw_instructions():
    """Draw game instructions screen"""
    global menu_selection
    screen.fill("black")  # Black background
    
    # If we're in the main menu
    if current_state == GAME_STATES['INSTRUCTIONS']:
        # MQIX Title
        title = title_font.render("MQIX", True, (255, 255, 255))  # White text
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 200))
        
        # Menu options
        menu_options = [
            ("Start", (255, 255, 255)),    # White
            ("Instructions", (255, 255, 255)),  # Yellow
            ("Exit", (255, 255, 255))      # White
        ]
        
        for i, (option, color) in enumerate(menu_options):
            # Change color of selected option
            if i == menu_selection:
                color = (255, 255, 0)  # Yellow for selected
            
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(screen_width // 2, 300 + i * 50))
            screen.blit(text, text_rect)
    
    # If we're in the instructions screen
    elif current_state == GAME_STATES['INSTRUCTIONS_DETAIL']:
        # Instructions Title
        title = title_font.render("How to Play", True, (255, 255, 255))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 50))
        
        # Detailed instructions
        instructions = [
            "Objective: Cover at least 20% of the screen",
            "",
            "Controls:",
            "- Arrow Keys: Move around the border or when not pushing",
            "- Spacebar: Start/Stop pushing to draw lines",
            "- ESC: Pause Game",
            "",
            "Gameplay:",
            "- Move along the border to start pushing",
            "- Create territories by drawing closed paths",
            "- Avoid Sparx (orange circles) and Qix (purple circle)",
            "- Don't get caught while pushing!",
            "",
            "Enemies:",
            "- Sparx: Patrol the border",
            "- Qix: Moves freely inside the play area",
            "",
            "Tips:",
            "- Be strategic in your territory claims",
            "- Watch out for enemy movements",
            "",
            "Press ESC to Return to Menu"
        ]
        
        for i, line in enumerate(instructions):
            color = (255, 255, 255)  # White text
            # Highlight section headers
            if line.endswith(":"):
                color = (255, 255, 0)  # Yellow for headers
            
            text = small_font.render(line, True, color)
            screen.blit(text, (50, 150 + i * 30))

def draw_pause_menu():
    """Draw pause menu screen"""
    global pause_menu_selection
    screen.fill("black")  # Black background
    
    # Pause Title
    pause_title = title_font.render("PAUSED", True, (255, 255, 255))
    screen.blit(pause_title, (screen_width // 2 - pause_title.get_width() // 2, 200))
    
    # Pause menu options
    pause_options = [
        ("Resume", (255, 255, 255)),    # White
        ("Main Menu", (255, 255, 255)), # White
        ("Exit Game", (255, 255, 255))  # White
    ]
    
    for i, (option, color) in enumerate(pause_options):
        # Change color of selected option
        if i == pause_menu_selection:
            color = (255, 255, 0)  # Yellow for selected
        
        text = font.render(option, True, color)
        text_rect = text.get_rect(center=(screen_width // 2, 300 + i * 50))
        screen.blit(text, text_rect)

def reset_game():
    """Reset all game variables to initial state"""
    global push_enabled, width, height, xpos, ypos, speed
    global player_path, filled_areas, lives, invulnerable
    global invulnerability_start_time, sparx, qix, current_state, perimeter_path
    global total_area, covered_area, level_passed, level_pass_time
    
    push_enabled = False
    width, height = 10, 10
    xpos, ypos = screen_width / 2, screen_height - height - 50
    speed = 5

    player_path = []
    filled_areas = []

    # Area tracking
    total_area = (screen_width - 100) * (screen_height - 90)
    covered_area = 0

    # Level pass tracking
    level_passed = False
    level_pass_time = 0

    # Lives and Invulnerability
    lives = 3
    invulnerable = False
    invulnerability_start_time = 0

    # Sparx
    sparx = [{'x': 50, 'y': 20, 'dx': 5, 'dy': 0, 'path_index': 0}]
    perimeter_path = [(50, 20), (screen_width - 50, 20), (screen_width - 50, screen_height - 50), (50, screen_height - 50)]

    # Qix
    qix = {'x': screen_width / 2, 'y': screen_height / 2, 'dx': random.choice([-3, 3]), 'dy': random.choice([-3, 3])}
    
    current_state = GAME_STATES['PLAY']

def draw_game_over():
    """Draw game over screen"""
    screen.fill("white")
    
    # Game Over Title
    game_over_text = title_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 200))
    
    # Percentage covered
    percentage = calculate_territory_percentage()
    covered_text = font.render(f"Territory Covered: {percentage:.2f}%", True, (0, 0, 0))
    screen.blit(covered_text, (screen_width // 2 - covered_text.get_width() // 2, 250))
    
    # Instructions
    restart_text = font.render("Press ENTER to Restart", True, (0, 0, 0))
    quit_text = font.render("Press ESC to Quit", True, (0, 0, 0))
    screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, 300))
    screen.blit(quit_text, (screen_width // 2 - quit_text.get_width() // 2, 350))

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if current_state == GAME_STATES['INSTRUCTIONS']:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu_selection = (menu_selection - 1) % 3
                elif event.key == pygame.K_DOWN:
                    menu_selection = (menu_selection + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if menu_selection == 0:  # Start
                        reset_game()
                    elif menu_selection == 1:  # Instructions
                        current_state = GAME_STATES['INSTRUCTIONS_DETAIL']
                    elif menu_selection == 2:  # Exit
                        running = False
        
        elif current_state == GAME_STATES['INSTRUCTIONS_DETAIL']:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = GAME_STATES['INSTRUCTIONS']
        
        elif current_state == GAME_STATES['PAUSE']:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    pause_menu_selection = (pause_menu_selection - 1) % 3
                elif event.key == pygame.K_DOWN:
                    pause_menu_selection = (pause_menu_selection + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if pause_menu_selection == 0:  # Resume
                        current_state = GAME_STATES['PLAY']
                    elif pause_menu_selection == 1:  # Main Menu
                        current_state = GAME_STATES['INSTRUCTIONS']
                    elif pause_menu_selection == 2:  # Exit Game
                        running = False
                elif event.key == pygame.K_ESCAPE:
                    current_state = GAME_STATES['PLAY']
        
        elif current_state == GAME_STATES['PLAY']:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Pause the game when ESC is pressed
                    current_state = GAME_STATES['PAUSE']
                    pause_menu_selection = 0
                
                if event.key == pygame.K_SPACE:
                    if push_enabled and len(player_path) >= 3:
                        filled_areas.append(player_path[:])  # Save the path as a polygon
                    push_enabled = not push_enabled
                    player_path = []  # Reset the path
        
        elif current_state == GAME_STATES['END_GAME']:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False

    # State-based rendering
    if current_state == GAME_STATES['INSTRUCTIONS'] or current_state == GAME_STATES['INSTRUCTIONS_DETAIL']:
        draw_instructions()
    
    elif current_state == GAME_STATES['PAUSE']:
        draw_pause_menu()
    
    elif current_state == GAME_STATES['PLAY']:
        # Game over check
        if lives <= 0:
            current_state = GAME_STATES['END_GAME']
            continue

        # Level passed check - return to instructions after showing message
        if level_passed and time.time() - level_pass_time >= LEVEL_PASS_DURATION:
            current_state = GAME_STATES['INSTRUCTIONS']
            continue

        screen.fill("white")
        
        # Draw claimed territories
        for area in filled_areas:
            pygame.draw.polygon(screen, (173, 216, 230), area)  # Light blue
        
        # Draw border
        pygame.draw.rect(screen, "black", (50, 20, screen_width - 100, screen_height - 70), 10)
        
        # Draw current path
        if push_enabled and len(player_path) > 1:
            pygame.draw.lines(screen, "green", False, player_path, 3)
        
        # Draw player
        player_color = "red"
        if invulnerable:
            # Blinking effect during invulnerability
            if int(time.time() * 10) % 2 == 0:
                player_color = "gray"
        pygame.draw.rect(screen, player_color, (xpos, ypos, width, height))
        
        # Draw UI Panel
        panel_width = 200
        panel_height = 150  # Increased height to accommodate territory percentage
        panel_x = screen_width - panel_width - 20
        panel_y = 20
        
        # Create a semi-transparent background for the panel
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (200, 200, 200, 180), panel_surface.get_rect(), border_radius=10)
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw lives
        lives_text = font.render(f"Lives:", True, (0, 0, 0))
        lives_value = title_font.render(str(lives), True, (255, 0, 0))
        screen.blit(lives_text, (panel_x + 20, panel_y + 20))
        screen.blit(lives_value, (panel_x + 120, panel_y + 20))
        
        # Draw territory percentage
        percentage = calculate_territory_percentage()
        territory_text = font.render("Territory:", True, (0, 0, 0))
        territory_value = font.render(f"{percentage:.2f}%", True, (0, 128, 0))
        screen.blit(territory_text, (panel_x + 20, panel_y + 70))
        screen.blit(territory_value, (panel_x + 120, panel_y + 70))
        
        # Draw invulnerability timer if active
        if invulnerable:
            remaining_time = max(0, 2 - (time.time() - invulnerability_start_time))
            vulnerable_text = font.render("Vulnerable in:", True, (0, 0, 0))
            vulnerable_time = font.render(f"{remaining_time:.1f}s", True, (255, 0, 0))
            screen.blit(vulnerable_text, (panel_x + 20, panel_y + 110))
            screen.blit(vulnerable_time, (panel_x + 120, panel_y + 110))
        
        # Display Level Passed message
        if level_passed and time.time() - level_pass_time < LEVEL_PASS_DURATION:
            level_pass_text = title_font.render("Congrats! Level Passed!", True, (0, 255, 0))
            text_width = level_pass_text.get_width()
            screen.blit(level_pass_text, (screen_width // 2 - text_width // 2, screen_height // 2 - 50))
        
        # Movement and game logic for player and enemies (same as before)
        keys = pygame.key.get_pressed()
        if push_enabled:
            # Prevent diagonal movement by prioritizing one direction
            if keys[pygame.K_LEFT] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
                xpos -= speed
                if xpos < 50:
                    xpos = 50
                player_path.append((xpos + width // 2, ypos + height // 2))  # Track path

            elif keys[pygame.K_RIGHT] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
                xpos += speed
                if xpos > screen_width - width - 50:
                    xpos = screen_width - width - 50
                player_path.append((xpos + width // 2, ypos + height // 2))  # Track path

            elif keys[pygame.K_UP] and not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                ypos -= speed
                if ypos < 20:
                    ypos = 20
                player_path.append((xpos + width // 2, ypos + height // 2))  # Track path

            elif keys[pygame.K_DOWN] and not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                ypos += speed
                if ypos > screen_height - height - 50:
                    ypos = screen_height - height - 50
                player_path.append((xpos + width // 2, ypos + height // 2))  # Track path
        else:
            if keys[pygame.K_LEFT] and ypos in [20, screen_height - height - 50]:
                xpos = max(50, xpos - speed)
            elif keys[pygame.K_RIGHT] and ypos in [20, screen_height - height - 50]:
                xpos = min(screen_width - width - 50, xpos + speed)
            elif keys[pygame.K_UP] and xpos in [50, screen_width - width - 50]:
                ypos = max(20, ypos - speed)
            elif keys[pygame.K_DOWN] and xpos in [50, screen_width - width - 50]:
                ypos = min(screen_height - height - 50, ypos + speed)
        
        # Update Sparx
        for s in sparx:
            target_x, target_y = perimeter_path[s['path_index']]
            if (s['x'], s['y']) == (target_x, target_y):
                s['path_index'] = (s['path_index'] + 1) % len(perimeter_path)
            
            if s['x'] < target_x: s['x'] += 5
            elif s['x'] > target_x: s['x'] -= 5
            if s['y'] < target_y: s['y'] += 5
            elif s['y'] > target_y: s['y'] -= 5
            
            pygame.draw.circle(screen, "orange", (s['x'], s['y']), 7)
        
        # Check Sparx collision
        check_sparx_collision()
        
        # Update Qix movement
        qix['x'] += qix['dx']
        qix['y'] += qix['dy']
        if qix['x'] <= 50 or qix['x'] >= screen_width - 50:
            qix['dx'] = -qix['dx']
        if qix['y'] <= 20 or qix['y'] >= screen_height - 50:
            qix['dy'] = -qix['dy']
        pygame.draw.circle(screen, "purple", (int(qix['x']), int(qix['y'])), 14)
    
    elif current_state == GAME_STATES['END_GAME']:
        draw_game_over()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()