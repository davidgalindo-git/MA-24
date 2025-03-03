import pygame
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu Subway Surfer Amélioré")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Variables du joueur
player_width, player_height = 50, 50
player_x, player_y = WIDTH // 2, HEIGHT - player_height - 10
player_speed = 10
lane_positions = [WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4]
current_lane = 1  # Milieu
is_jumping = False
jumping_up = True
jump_height = 150
jump_speed = 15
jump_start_y = player_y

# Variables des obstacles
obstacle_width, obstacle_height = 50, 50
obstacle_speed = 5
obstacles = []
obstacle_spawn_rate = 30  # Plus ce nombre est bas, plus il y a d'obstacles

# Temps
clock = pygame.time.Clock()
FPS = 60

# Scores
score = 0
best_score = 0
font = pygame.font.Font(None, 36)

# Temps pour augmenter la difficulté
difficulty_timer = 0
difficulty_interval = 5000  # Augmente la vitesse toutes les 5 secondes

# Contrôle du délai entre les changements de voie
last_lane_change = 0
lane_change_delay = 200  # Délai minimum en millisecondes

# Fonction pour générer un obstacle
def generate_obstacle():
    lane = random.choice([0, 1, 2])
    obstacle_x = lane_positions[lane]
    obstacle_y = -obstacle_height
    return [obstacle_x, obstacle_y]

# Boucle principale du jeu
running = True
while running:
    elapsed_time = clock.tick(FPS)  # Temps écoulé en millisecondes
    difficulty_timer += elapsed_time
    last_lane_change += elapsed_time

    # Remplir l'écran
    screen.fill(WHITE)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Gestion des touches
    keys = pygame.key.get_pressed()

    # Gestion des déplacements gauche/droite (avec délai)
    if keys[pygame.K_LEFT] and current_lane > 0 and last_lane_change > lane_change_delay:
        current_lane -= 1
        last_lane_change = 0
    if keys[pygame.K_RIGHT] and current_lane < 2 and last_lane_change > lane_change_delay:
        current_lane += 1
        last_lane_change = 0

    # Gestion du saut
    if keys[pygame.K_UP] and not is_jumping:
        is_jumping = True
        jumping_up = True  # On commence par monter
        jump_start_y = player_y

    # Animation du saut
    if is_jumping:
        if jumping_up:  # Montée
            player_y -= jump_speed
            if player_y <= jump_start_y - jump_height:
                jumping_up = False  # Inverser pour descendre
        else:  # Descente
            player_y += jump_speed
            if player_y >= HEIGHT - player_height - 10:
                player_y = HEIGHT - player_height - 10
                is_jumping = False  # Fin du saut

    # Mise à jour de la position du joueur
    player_x = lane_positions[current_lane]

    # Génération des obstacles (fréquence ajustée au score)
    if random.randint(1, obstacle_spawn_rate) == 1:
        obstacles.append(generate_obstacle())

    # Mise à jour des obstacles
    for obstacle in obstacles:
        obstacle[1] += obstacle_speed

    # Supprimer les obstacles hors de l'écran
    obstacles = [ob for ob in obstacles if ob[1] < HEIGHT]

    # Détection des collisions (prise en compte du saut)
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], obstacle_width, obstacle_height)
        # Vérifie si le joueur est en contact avec un obstacle
        if player_rect.colliderect(obstacle_rect):
            # Collision seulement si le joueur est au niveau de l'obstacle (pas au-dessus)
            if player_y + player_height > obstacle[1] + 10 and not is_jumping:  # Tolérance de 10 pixels
                print(f"Game Over! Score: {score}")
                if score > best_score:
                    best_score = score  # Met à jour le meilleur score
                score = 0  # Réinitialise le score
                obstacle_speed = 5  # Réinitialise la vitesse
                obstacle_spawn_rate = 50  # Réinitialise la fréquence des obstacles
                obstacles = []  # Supprime les obstacles
                current_lane = 1  # Réinitialise la position du joueur
                player_y = HEIGHT - player_height - 10  # Réinitialise la position verticale

    # Augmenter la vitesse des obstacles et la fréquence au fil du temps
    if difficulty_timer >= difficulty_interval:
        obstacle_speed += 1
        if obstacle_spawn_rate > 20:  # Réduit la fréquence jusqu'à un minimum
            obstacle_spawn_rate -= 2
        difficulty_timer = 0

    # Dessiner le joueur
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))

    # Dessiner les obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen, RED, (obstacle[0], obstacle[1], obstacle_width, obstacle_height))

    # Affichage du score
    score += 1
    score_text = font.render(f"Score: {score}", True, BLACK)
    best_score_text = font.render(f"Best Score: {best_score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(best_score_text, (10, 50))

    # Mise à jour de l'affichage
    pygame.display.flip()

pygame.quit()
