import pygame
import random
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Death Runner")

# Couleurs utilisées
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Ancienne couleur des obstacles
BLUE = (0, 0, 255)  # Ancienne couleur du joueur
PINK = (255, 105, 180)  # Ancienne couleur des bonus
YELLOW = (255, 255, 0)  # Ancienne couleur du bonus d'avance

# Charger les images du personnage (Assurez-vous que les fichiers existent dans "pics/")
player_images = [
    pygame.image.load("pics/puss.webp"),
    pygame.image.load("pics/puss.webp"),
    pygame.image.load("pics/puss.webp"),
    pygame.image.load("pics/chaser.webp"),
]
player_index = 0  # Indice d'animation
player_img = pygame.transform.scale(player_images[player_index], (50, 50))

# Charger l'image du background
background = pygame.image.load("pics/Desert.webp")
background = pygame.transform.scale(background, (1024, 1024))

# Position du background pour le scrolling
bg_y1 = 0
bg_y2 = -background.get_height()
bg_speed = 5

# Charger l'image des obstacles
obstacle_img = pygame.image.load("pics/cactus.webp")
obstacle_img = pygame.transform.scale(obstacle_img, (50, 50))
obstacle_img_bus = pygame.image.load("pics/bus.webp")
obstacle_img_bus = pygame.transform.scale(obstacle_img_bus, (150, 150))

# Charger l'image des bonus
bonus_img = pygame.image.load("pics/coin.webp")
bonus_img = pygame.transform.scale(bonus_img, (50, 50))

# Charger l'image du bonus d'avance
advance_bonus_img = pygame.image.load("pics/advance_bonus.webp")
advance_bonus_img = pygame.transform.scale(advance_bonus_img, (50, 50))

# Variables du joueur
player_width, player_height = 50, 50  # Taille du joueur
player_x, player_y = WIDTH // 2, HEIGHT - player_height - 10  # Position initiale
lane_positions = [WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4]  # Positions des voies
current_lane = 1  # Voie actuelle (milieu)
is_jumping = False  # État du saut
jumping_up = True  # Indique si le joueur monte ou descend
jump_height = 175  # Hauteur maximale du saut
jump_speed = 12  # Vitesse du saut
jump_start_y = player_y  # Position initiale du saut
walk_cycle = 0

# Chaser (poursuivant)
chaser_width, chaser_height = 50, 50
chaser_x = random.choice(lane_positions)
chaser_y = HEIGHT + 3500  # Le chaser commence à partir du bas de l'écran
chaser_speed = 3  # Vitesse initiale du chaser

# Charger l'image du chaser
chaser_img = pygame.image.load("pics/chaser.webp")
chaser_img = pygame.transform.scale(chaser_img, (50, 50))

# Obstacles et bonus
obstacle_width, obstacle_height = 50, 50  # Taille des obstacles
obstacle_speed = 5  # Vitesse des obstacles
obstacles = []  # Liste des obstacles
obstacle_spawn_rate = 30  # Fréquence d'apparition des obstacles
bonus_width, bonus_height = 50, 50  # Taille des tuiles bonus
bonus_tiles = []  # Liste des tuiles bonus
advance_bonus_tiles = []  # Liste des tuiles bonus d'avance
bonus_spawn_rate = 200  # Fréquence d'apparition des bonus
advance_bonus_spawn_rate = 500  # Fréquence d'apparition du bonus d'avance
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

# Fonction pour générer un objet (obstacle ou bonus)
def generate_object(obj_list, spawn_rate, img, is_advance=False):
    """Ajoute un objet à la liste si un spawn est déclenché."""
    global obstacles
    if random.randint(1, spawn_rate) == 1:
        lane = random.choice([0, 1, 2])
        if is_advance:
            obj_list.append([lane_positions[lane], -bonus_height, img])  # Utiliser une image
        else:
            obj_list.append([lane_positions[lane], -obstacle_height, img])  # Utiliser une image
        cactus_count = sum(1 for obj in obstacles if len(obj) > 2 and obj[2] == obstacle_img)
        bus_count = sum(1 for obj in obstacles if len(obj) > 2 and obj[2] == obstacle_img_bus)
        # Liste des obstacles possibles en fonction des limites
        possible_objects = []
        if cactus_count < 6:
            possible_objects.append("cactus")
        if bus_count < 3:
            possible_objects.append("bus")
        # Vérifier qu'il y a encore de la place pour un nouvel obstacle
        if possible_objects and random.randint(1, obstacle_spawn_rate) == 1:
            lane = random.choice([0, 1, 2])  # Sélectionne une voie aléatoire
            object_type = random.choice(possible_objects)  # Choisit un type parmi ceux encore disponibles
            # Ajouter l'obstacle choisi
            if object_type == "cactus":
                obstacles.append([lane_positions[lane], -obstacle_height, obstacle_img])
                another_one = random.choice([0, 1, 2, 3])
                gift = 0
                while another_one > gift:
                    obstacles.append([lane_positions[lane], -obstacle_height, obstacle_img])
                    gift += 1
            elif object_type == "bus":
                obstacles.append([lane_positions[lane], -obstacle_height - 200, obstacle_img_bus])
                another_one = random.choice([0,1])
                if another_one == 1:
                    obstacles.append([lane_positions[lane], -obstacle_height - 200, obstacle_img_bus])

# Fonction pour mettre à jour la position des objets
def update_objects(obj_list):
    """Fait descendre les objets et supprime ceux qui sortent de l'écran."""
    for obj in obj_list:
        obj[1] += obstacle_speed  # Déplace l'objet vers le bas
    return [obj for obj in obj_list if obj[1] < HEIGHT]  # Garde uniquement les objets visibles

# Fonction pour gérer les collisions
def check_collisions():
    """Vérifie les collisions avec les obstacles, les bonus classiques et les bonus multiplicateurs."""
    global player_y, chaser_x, chaser_y, score, best_score, obstacles, bonus_tiles, advance_bonus_tiles, score_multiplier, multiplier_timer
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    # Vérifie la collision avec les obstacles
    for obj in obstacles:
        if obj[2] == obstacle_img:  # Cactus
            obj_rect = pygame.Rect(obj[0], obj[1], obstacle_width, obstacle_height)
            if player_rect.colliderect(obj_rect):
                if is_jumping and (player_y + player_height > obj[1]-15):  # Ajuster la marge de sécurité
                    continue  # Ignore la collision si le joueur est clairement au-dessus du cactus
                if score > best_score:
                    best_score = score
                reset_game()
        # Vérifie la collision avec les obstacles (bus)
    for obj in obstacles:
        if obj[2] == obstacle_img_bus:  # Bus
            bus_height = 150
            if player_rect.colliderect(pygame.Rect(obj[0], obj[1], obstacle_width, bus_height)):
                if score > best_score:
                    best_score = score
                reset_game()

    # Vérifie la collision avec le chaser
    chaser_rect = pygame.Rect(chaser_x, chaser_y, chaser_width, chaser_height)
    if player_rect.colliderect(chaser_rect):
        if score > best_score:
            best_score = score
        reset_game()

    # Vérifie la collision avec le bonus d'avance
    for obj in advance_bonus_tiles:
        if player_rect.colliderect(pygame.Rect(obj[0], obj[1], bonus_width, bonus_height)):
            # Le joueur obtient un boost d'avance
            advance_bonus_tiles.remove(obj)
            chaser_y += 1000  # Le chaser recule de 250 pixels

    # Vérifie la collision avec le bonus multiplicateur
    for obj in bonus_tiles:
        if player_rect.colliderect(pygame.Rect(obj[0], obj[1], bonus_width, bonus_height)):
            # Le multiplicateur est activé lors de la collecte du bonus
            score_multiplier = 2  # Active le multiplicateur de score
            multiplier_timer = 0  # Réinitialise le compteur de durée
            bonus_tiles.remove(obj)  # Supprime le bonus collecté

def update_score():
    """Mise à jour du score en fonction du multiplicateur."""
    global score, score_multiplier, multiplier_timer, multiplier_duration

    # Ajoute des points au score actuel en fonction du multiplicateur
    score += 1 + 10 * score_multiplier  # Ajoute 10 points * multiplicateur par image

    # Si le multiplicateur est actif, vérifie le timer
    if score_multiplier > 1:
        multiplier_timer += 1  # Incrémente le timer pour suivre le temps
        if multiplier_timer >= multiplier_duration:  # Si la durée du multiplicateur est dépassée
            score_multiplier = 1  # Réinitialise le multiplicateur
            multiplier_timer = 0  # Réinitialise le timer
    else:
        score_multiplier = 0  # Réinitialise si le multiplicateur n'est pas actif

def animation_player():
    """Anime légèrement le joueur pour donner une impression de marche."""
    global walk_cycle, player_y

    if not is_jumping:  # Seulement quand le joueur est au sol
        walk_cycle += 1
        player_y_offset = int(2 * math.sin(walk_cycle * 0.3))  # Oscillation légère
        player_y = HEIGHT - player_height - 10 + player_y_offset

# Fonction pour mettre à jour le chaser
def update_chaser():
    """Fait en sorte que le chaser suive le joueur et le rattrape efficacement."""
    global chaser_x, chaser_y, chaser_speed
    # Augmenter progressivement la vitesse du chaser pour éviter qu'il reste trop loin
    chaser_speed = min(chaser_speed + 0.000000000000000000000001, 10)  # Augmentation progressive, max 10
    # Faire en sorte que le chaser suive immédiatement la voie du joueur
    target_x = lane_positions[current_lane]  # La lane actuelle du joueur

    # Déplacement horizontal : si le chaser est trop à gauche, va à droite, et inversement
    if chaser_x < target_x:
        chaser_x += min(10, target_x - chaser_x)  # Déplacement plus rapide en X
    elif chaser_x > target_x:
        chaser_x -= min(10, chaser_x - target_x)

    # Déplacement vertical pour rattraper le joueur
    if chaser_y < player_y:
        chaser_y += min(chaser_speed, player_y - chaser_y)  # Monte vers le joueur
    elif chaser_y > player_y:
        chaser_y -= min(chaser_speed, chaser_y - player_y)  # Descend (si nécessaire)

    # Vérifier si le chaser attrape le joueur
    chaser_rect = pygame.Rect(chaser_x, chaser_y, chaser_width, chaser_height)
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    if chaser_rect.colliderect(player_rect):
        reset_game()  # Fin du jeu si le chaser touche le joueur

def reset_chaser():
    """Réinitialise la position du chaser hors de l'écran."""
    global chaser_x, chaser_y, chaser_speed
    chaser_x = random.choice(lane_positions)
    chaser_y = HEIGHT+3500  # Commence encore plus loin hors de l'écran
    chaser_speed = 3

# Fonction pour gérer les entrées du joueur
def def_movement():
    """Vérifie les touches pressées et effectue l'action correspondante."""
    global current_lane, is_jumping, jumping_up, jump_start_y, last_lane_change
    # Récupère les touches pressées
    keys = pygame.key.get_pressed()
    # Changer de voie vers la gauche
    if keys[pygame.K_LEFT] and current_lane > 0 and last_lane_change > lane_change_delay:
        current_lane -= 1
        last_lane_change = 0
    # Changer de voie vers la droite
    if keys[pygame.K_RIGHT] and current_lane < 2 and last_lane_change > lane_change_delay:
        current_lane += 1
        last_lane_change = 0
    # Sauter si le joueur n'est pas déjà en train de sauter
    if keys[pygame.K_UP] and not is_jumping:
        is_jumping = True
        jumping_up = True
        jump_start_y = player_y

def show_game_over():
    """Affiche un écran Game Over avec un bouton pour recommencer."""
    button_width, button_height = 200, 50
    button_x, button_y = WIDTH // 2 - button_width // 2, HEIGHT // 2 + 50
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    waiting = True
    while waiting:
        screen.fill(BLACK)
        # Affichage du texte "Game Over"
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 2 - 50))
        # Dessiner le bouton "Recommencer"
        pygame.draw.rect(screen, WHITE, button_rect)
        restart_text = font.render("Recommencer", True, BLACK)
        screen.blit(restart_text, (button_x + 20, button_y + 10))
        pygame.display.flip()
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()  # Quitter complètement le jeu
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):  # Vérifie si le bouton est cliqué
                    waiting = False  # Sort de la boucle pour recommencer la partie


# Fonction pour réinitialiser le jeu
def reset_game():
    """Réinitialise toutes les variables de jeu après une collision."""
    global score, obstacle_speed, obstacle_spawn_rate, obstacles, bonus_tiles, advance_bonus_tiles, current_lane, player_y, score_multiplier, multiplier_timer
    show_game_over()
    score = 0
    obstacle_speed = 5
    obstacle_spawn_rate = 50
    obstacles.clear()
    bonus_tiles.clear()
    advance_bonus_tiles.clear()
    current_lane = 1
    player_y = HEIGHT - player_height - 10
    score_multiplier = 1
    multiplier_timer = 0
    reset_chaser()

# Boucle principale du jeu
def main_loop():
    global player_x, player_y, current_lane, is_jumping, jumping_up, jump_start_y, difficulty_timer, multiplier_timer, score_multiplier, last_lane_change, score, bg_y1, bg_y2
    running = True
    while running:
        elapsed_time = clock.tick(FPS)
        difficulty_timer += elapsed_time
        last_lane_change += elapsed_time
        # Appel de la fonction update_score pour gérer le score et le multiplicateur
        update_score()
        # Appel à la fonction def_movement pour gérer les actions basées sur les touches pressées
        def_movement()
        animation_player()
        bg_y1 += bg_speed
        bg_y2 += bg_speed
        # Réinitialiser la position quand une image sort de l'écran
        if bg_y1 >= HEIGHT:
            bg_y1 = -background.get_height()
        if bg_y2 >= HEIGHT:
            bg_y2 = -background.get_height()
        screen.blit(background, (0, bg_y1))
        screen.blit(background, (0, bg_y2))
        update_chaser()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
        generate_object(obstacles, obstacle_spawn_rate, obstacle_img)
        generate_object(bonus_tiles, bonus_spawn_rate, bonus_img)
        generate_object(advance_bonus_tiles, advance_bonus_spawn_rate, advance_bonus_img, is_advance=True)
        obstacles[:] = update_objects(obstacles)
        bonus_tiles[:] = update_objects(bonus_tiles)
        advance_bonus_tiles[:] = update_objects(advance_bonus_tiles)
        check_collisions()

        # Dessiner le joueur
        screen.blit(player_img, (player_x, player_y))

        # Dessiner les obstacles
        for obj in obstacles:
            screen.blit(obj[2], (obj[0], obj[1]))  # Utilise l'image correcte stockée dans l'objet

        # Dessiner les bonus classiques
        for obj in bonus_tiles:
            screen.blit(bonus_img, (obj[0], obj[1]))

        # Dessiner les bonus d'avance
        for obj in advance_bonus_tiles:
            screen.blit(advance_bonus_img, (obj[0], obj[1]))

        # Dessiner le chaser
        screen.blit(chaser_img, (chaser_x, chaser_y))

        # Affichage du score
        screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Best Score: {best_score}", True, BLACK), (10, 50))

        # Afficher la distance entre le joueur et le chaser
        distance = chaser_y - player_y
        screen.blit(font.render(f"Distance: {distance} m", True, BLACK), (10, 90))

        pygame.display.flip()

    pygame.quit()

main_loop()