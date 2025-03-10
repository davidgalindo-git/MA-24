import pygame
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu Subway Surfer Amélioré")

# Couleurs utilisées
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Couleur des obstacles
BLUE = (0, 0, 255)  # Couleur du joueur
PINK = (255, 105, 180)  # Couleur des bonus

# Variables du joueur
player_width, player_height = 50, 50  # Taille du joueur
player_x, player_y = WIDTH // 2, HEIGHT - player_height - 10  # Position initiale
lane_positions = [WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4]  # Positions des voies
current_lane = 1  # Voie actuelle (milieu)
is_jumping = False  # État du saut
jumping_up = True  # Indique si le joueur monte ou descend
jump_height = 150  # Hauteur maximale du saut
jump_speed = 15  # Vitesse du saut
jump_start_y = player_y  # Position initiale du saut

# Obstacles et bonus
obstacle_width, obstacle_height = 50, 50  # Taille des obstacles
obstacle_speed = 5  # Vitesse des obstacles
obstacles = []  # Liste des obstacles
obstacle_spawn_rate = 30  # Fréquence d'apparition des obstacles
bonus_width, bonus_height = 50, 50  # Taille des tuiles bonus
bonus_tiles = []  # Liste des tuiles bonus
bonus_spawn_rate = 200  # Fréquence d'apparition des bonus
score_multiplier = 1  # Multiplicateur de score
multiplier_timer = 0  # Durée actuelle de l'effet bonus
multiplier_duration = 30000  # Durée de l'effet bonus (30 sec)

# Variables de score
score = 0  # Score actuel
best_score = 0  # Meilleur score enregistré
font = pygame.font.Font(None, 36)  # Police d'affichage du score

# Variables pour la difficulté
difficulty_timer = 0  # Temps écoulé pour l'augmentation de difficulté
difficulty_interval = 5000  # Temps avant augmentation de la difficulté (5 sec)

# Contrôle du changement de voie
last_lane_change = 0  # Temps depuis le dernier changement de voie
lane_change_delay = 200  # Délai minimal entre deux changements (200ms)

# Gestion du temps
clock = pygame.time.Clock()
FPS = 60  # Nombre d'images par seconde


# Fonction pour générer un obstacle ou un bonus
def generate_object(obj_list, spawn_rate, color):
    """Ajoute un objet à la liste si un spawn est déclenché."""
    if random.randint(1, spawn_rate) == 1:
        lane = random.choice([0, 1, 2])  # Sélectionne une voie aléatoire
        obj_list.append([lane_positions[lane], -obstacle_height, color])  # Ajoute l'objet


# Fonction pour mettre à jour la position des objets
def update_objects(obj_list):
    """Fait descendre les objets et supprime ceux qui sortent de l'écran."""
    for obj in obj_list:
        obj[1] += obstacle_speed  # Déplace l'objet vers le bas
    return [obj for obj in obj_list if obj[1] < HEIGHT]  # Garde uniquement les objets visibles


# Fonction pour gérer les collisions
def check_collisions():
    """Vérifie les collisions avec les obstacles et les bonus."""
    global score, best_score, score_multiplier, multiplier_timer, obstacles, bonus_tiles
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    # Vérifie la collision avec les obstacles
    for obj in obstacles:
        if player_rect.colliderect(pygame.Rect(obj[0], obj[1], obstacle_width, obstacle_height)):
            if player_y + player_height > obj[1] + 10 and not is_jumping:
                if score > best_score:
                    best_score = score  # Met à jour le meilleur score
                reset_game()  # Réinitialise le jeu

    # Vérifie la collision avec les bonus
    for obj in bonus_tiles:
        if player_rect.colliderect(pygame.Rect(obj[0], obj[1], bonus_width, bonus_height)):
            score_multiplier = 2  # Active le multiplicateur de score
            multiplier_timer = 0  # Réinitialise le compteur de durée
            bonus_tiles.remove(obj)  # Supprime le bonus collecté


# Fonction pour réinitialiser le jeu
def reset_game():
    """Réinitialise toutes les variables de jeu après une collision."""
    global score, obstacle_speed, obstacle_spawn_rate, obstacles, bonus_tiles, current_lane, player_y, score_multiplier, multiplier_timer
    score = 0
    obstacle_speed = 5
    obstacle_spawn_rate = 50
    obstacles.clear()
    bonus_tiles.clear()
    current_lane = 1
    player_y = HEIGHT - player_height - 10
    score_multiplier = 1
    multiplier_timer = 0


# Boucle principale du jeu
def main_loop():
    global player_x, player_y, current_lane, is_jumping, jumping_up, jump_start_y, difficulty_timer, multiplier_timer, score_multiplier, last_lane_change, score
    running = True
    while running:
        elapsed_time = clock.tick(FPS)
        difficulty_timer += elapsed_time
        last_lane_change += elapsed_time
        score += 3 * score_multiplier  # Ajoute l'effet du multiplicateur

        if score_multiplier > 1:
            multiplier_timer += elapsed_time
            if multiplier_timer >= multiplier_duration:
                score_multiplier = 1
                multiplier_timer = 0

        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and current_lane > 0 and last_lane_change > lane_change_delay:
            current_lane -= 1
            last_lane_change = 0
        if keys[pygame.K_RIGHT] and current_lane < 2 and last_lane_change > lane_change_delay:
            current_lane += 1
            last_lane_change = 0
        if keys[pygame.K_UP] and not is_jumping:
            is_jumping = True
            jumping_up = True
            jump_start_y = player_y
        if is_jumping:
            if jumping_up:
                player_y -= jump_speed
                if player_y <= jump_start_y - jump_height:
                    jumping_up = False
            else:
                player_y += jump_speed
                if player_y >= HEIGHT - player_height - 10:
                    player_y = HEIGHT - player_height - 10
                    is_jumping = False

        player_x = lane_positions[current_lane]
        generate_object(obstacles, obstacle_spawn_rate, RED)
        generate_object(bonus_tiles, bonus_spawn_rate, PINK)
        obstacles[:] = update_objects(obstacles)
        bonus_tiles[:] = update_objects(bonus_tiles)
        check_collisions()

        # Dessiner le joueur
        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))
        for obj in obstacles:
            pygame.draw.rect(screen, RED, (obj[0], obj[1], obstacle_width, obstacle_height))
        for obj in bonus_tiles:
            pygame.draw.rect(screen, PINK, (obj[0], obj[1], bonus_width, bonus_height))
        screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Best Score: {best_score}", True, BLACK), (10, 50))
        pygame.display.flip()
    pygame.quit()


main_loop()