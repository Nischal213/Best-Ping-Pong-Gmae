import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
INITIAL_PADDLE_SPEED = 8
INITIAL_BALL_SPEED = 6
PADDLE_WIDTH = 20
INITIAL_PADDLE_HEIGHT = 100
SPEED_INCREMENT = 0.03
SIZE_DECREMENT = 0.5
MIN_PADDLE_HEIGHT = 70
BALL_SIZE = 20
PLAYER1_COLOR = (255, 0, 0)  # Red (RGB)
PLAYER2_COLOR = (0, 255, 255)  # Cyan (RGB)
BOT_COLOR = (0, 255, 255)  # Cyan (same as player 2)
BALL_COLOR = (200, 200, 200)  # Keep original grey
CURVE_COLOR = (0, 128, 128)  # Teal (RGB: 0,128,128)
POWER_COLOR = (0, 0, 139)  # DarkBlue (RGB: 0,0,139)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CURVE_ACTIVATION_DISTANCE = 150
POWER_ACTIVATION_DISTANCE = 200
MAX_SPIN = 2.0
POWER_SPEED_MULTIPLIER = 1.1
PROGRESSION_INCREASE = 1.005

# Initialize sound
pygame.mixer.init()
curve_sound = pygame.mixer.Sound("curve_shot.wav")
power_sound = pygame.mixer.Sound("direct_shoot.wav")

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Pong")

clock = pygame.time.Clock()

# Game objects
player1 = pygame.Rect(
    50, HEIGHT // 2 - INITIAL_PADDLE_HEIGHT // 2, PADDLE_WIDTH, INITIAL_PADDLE_HEIGHT
)
player2 = pygame.Rect(
    WIDTH - 50 - PADDLE_WIDTH,
    HEIGHT // 2 - INITIAL_PADDLE_HEIGHT // 2,
    PADDLE_WIDTH,
    INITIAL_PADDLE_HEIGHT,
)
ball = pygame.Rect(
    WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE
)

# Game variables
game_mode = 1
game_state = "menu"
dx = dy = spin = 0
player1_score = 0
player2_score = 0
player1_speed = INITIAL_PADDLE_SPEED
player2_speed = INITIAL_PADDLE_SPEED
curve_activated = False
power_activated = False

font = pygame.font.Font(None, 74)
menu_font = pygame.font.Font(None, 50)


def reset_ball(direction):
    global dx, dy, spin, curve_activated, power_activated
    ball.center = (WIDTH // 2, HEIGHT // 2)
    dx = direction * INITIAL_BALL_SPEED
    dy = random.uniform(-INITIAL_BALL_SPEED, INITIAL_BALL_SPEED)
    spin = 0
    curve_activated = False
    power_activated = False

    # Reset paddle parameters
    player1_speed = INITIAL_PADDLE_SPEED
    player2_speed = INITIAL_PADDLE_SPEED
    player1.height = INITIAL_PADDLE_HEIGHT
    player2.height = INITIAL_PADDLE_HEIGHT


def draw_menu():
    screen.fill(BLACK)
    title = menu_font.render("Select Game Mode", True, WHITE)
    p1 = menu_font.render("1 Player (Press 1)", True, WHITE)
    p2 = menu_font.render("2 Players (Press 2)", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(p1, (WIDTH // 2 - p1.get_width() // 2, HEIGHT // 2))
    screen.blit(p2, (WIDTH // 2 - p2.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_1:
                    game_mode = 1
                    game_state = "playing"
                    reset_ball(random.choice([-1, 1]))
                elif event.key == pygame.K_2:
                    game_mode = 2
                    game_state = "playing"
                    reset_ball(random.choice([-1, 1]))

    if game_state == "menu":
        draw_menu()
        continue

    keys = pygame.key.get_pressed()

    # Player 1 controls
    if keys[pygame.K_w]:
        player1.y -= player1_speed
    if keys[pygame.K_s]:
        player1.y += player1_speed

    # Player 2/AI controls
    if game_mode == 1:
        if dx > 0:
            time_to_reach = (player2.left - ball.right) / abs(dx)
            projected_y = ball.centery + (dy + spin) * time_to_reach
            while projected_y < 0 or projected_y > HEIGHT:
                projected_y = (
                    2 * HEIGHT - projected_y if projected_y > HEIGHT else -projected_y
                )
            target_y = projected_y - player2.height // 2
            target_y = max(0, min(target_y, HEIGHT - player2.height))
            if player2.centery < projected_y:
                player2.y += min(player2_speed, projected_y - player2.centery)
            else:
                player2.y -= min(player2_speed, player2.centery - projected_y)
    else:
        if keys[pygame.K_UP]:
            player2.y -= player2_speed
        if keys[pygame.K_DOWN]:
            player2.y += player2_speed

    player1.y = max(0, min(player1.y, HEIGHT - player1.height))
    player2.y = max(0, min(player2.y, HEIGHT - player2.height))

    ball.x += dx
    ball.y += dy + spin * 1.1
    dy += spin * 0.03

    if ball.top <= 0 or ball.bottom >= HEIGHT:
        dy = -dy
        spin *= 0.7
        if ball.top <= 0:
            ball.top = 1
        else:
            ball.bottom = HEIGHT - 1

    if ball.colliderect(player1) and dx < 0:
        # Stop sounds when ball is returned
        curve_sound.stop()
        power_sound.stop()
        ball.left = player1.right
        curve_activated = False
        power_activated = False

        power_ready = abs(ball.centerx - player1.centerx) < POWER_ACTIVATION_DISTANCE
        curve_ready = abs(ball.centerx - player1.centerx) < CURVE_ACTIVATION_DISTANCE

        if power_ready and keys[pygame.K_d] and not keys[pygame.K_a]:
            current_speed = abs(dx)
            dx = POWER_SPEED_MULTIPLIER * current_speed
            dy = 0
            spin = 0
            power_activated = True
            power_sound.play()
        elif curve_ready and keys[pygame.K_a] and not keys[pygame.K_d]:
            offset = (ball.centery - player1.centery) / (player1.height / 2)
            offset = max(-1.0, min(1.0, offset))
            spin = MAX_SPIN * offset
            dx *= (
                -PROGRESSION_INCREASE
            )  # Change dx and dy to have a lower speed per rebound
            dy *= PROGRESSION_INCREASE
            curve_activated = True
            curve_sound.play()
        else:
            dx *= -PROGRESSION_INCREASE
            dy *= PROGRESSION_INCREASE

        player1_speed += SPEED_INCREMENT
        original_center = player1.centery
        player1.height = max(player1.height - SIZE_DECREMENT, MIN_PADDLE_HEIGHT)
        player1.centery = original_center

    elif ball.colliderect(player2) and dx > 0:
        # Stop sounds when ball is returned
        curve_sound.stop()
        power_sound.stop()
        ball.right = player2.left
        curve_activated = False
        power_activated = False

        power_ready = abs(ball.centerx - player2.centerx) < POWER_ACTIVATION_DISTANCE
        curve_ready = abs(ball.centerx - player2.centerx) < CURVE_ACTIVATION_DISTANCE

        if power_ready and keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            current_speed = abs(dx)
            dx = -POWER_SPEED_MULTIPLIER * current_speed
            dy = 0
            spin = 0
            power_activated = True
            power_sound.play()
        elif curve_ready and keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            offset = (ball.centery - player2.centery) / (player2.height / 2)
            offset = max(-1.0, min(1.0, offset))
            spin = MAX_SPIN * offset
            dx *= -PROGRESSION_INCREASE
            dy *= PROGRESSION_INCREASE
            curve_activated = True
            curve_sound.play()
        else:
            dx *= -PROGRESSION_INCREASE
            dy *= PROGRESSION_INCREASE

        player2_speed += SPEED_INCREMENT
        original_center = player2.centery
        player2.height = max(player2.height - SIZE_DECREMENT, MIN_PADDLE_HEIGHT)
        player2.centery = original_center

    if ball.right < 0 or ball.left > WIDTH:
        if ball.right < 0:
            player2_score += 1
        else:
            player1_score += 1

        if player1_score >= 5 or player2_score >= 5:
            winner = "Player 1 Wins!" if player1_score >= 5 else "Player 2/AI Wins!"
            text = font.render(winner, True, WHITE)
            screen.fill(BLACK)
            screen.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    HEIGHT // 2 - text.get_height() // 2,
                ),
            )
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
        else:
            reset_ball(1 if ball.right < 0 else -1)

    screen.fill(BLACK)
    pygame.draw.rect(screen, PLAYER1_COLOR, player1)
    pygame.draw.rect(screen, BOT_COLOR if game_mode == 1 else PLAYER2_COLOR, player2)

    ball_color = (
        POWER_COLOR
        if power_activated
        else CURVE_COLOR if curve_activated else BALL_COLOR
    )
    pygame.draw.ellipse(screen, ball_color, ball)

    p1_text = font.render(str(player1_score), True, WHITE)
    p2_text = font.render(str(player2_score), True, WHITE)
    screen.blit(p1_text, (WIDTH // 4, 20))
    screen.blit(p2_text, (3 * WIDTH // 4 - p2_text.get_width(), 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
