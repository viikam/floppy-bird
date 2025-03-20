import pygame
from random import randint

FPS = 60
pygame.init()

clock = pygame.time.Clock()

# Chargement des images
BG = pygame.image.load("assets/background.png")
SCREEN_WIDTH, SCREEN_HEIGHT = BG.get_size()
GROUND = pygame.image.load("assets/floor.png")
GROUND_HEIGHT = GROUND.get_height()
DOUBLE_GROUND = pygame.Surface((2 * SCREEN_WIDTH, GROUND_HEIGHT))
DOUBLE_GROUND.blit(GROUND, (0, 0))
DOUBLE_GROUND.blit(GROUND, (SCREEN_WIDTH, 0))

BIRD = pygame.image.load("assets/redbird-upflap.png")
BIRD1 = pygame.image.load("assets/redbird-midflap.png")
BIRD2 = pygame.image.load("assets/redbird-downflap.png")
BIRDS = [BIRD, BIRD1, BIRD2, BIRD]

BIRD_WIDTH, BIRD_HEIGHT = BIRD.get_size()

JUMP_SOUND = pygame.mixer.Sound("assets/wing.wav")
HIT_SOUND = pygame.mixer.Sound("assets/hit.wav")

TUBE_BELOW = pygame.image.load("assets/pipe-green.png")
TUBE_ABOVE = pygame.image.load("assets/pipe-green-above.png")
TUBE_WIDTH, TUBE_HEIGHT = TUBE_ABOVE.get_size()

# Charger les images des chiffres
DIGITS = [pygame.image.load(f"assets/{i}.png") for i in range(10)]
DIGIT_WIDTH, DIGIT_HEIGHT = DIGITS[0].get_size()  

# Position et vitesse de l'oiseau
bird_x = 0
bird_y = 0
JUMP = -5
G = 0.2
bird_s = 0

# Listes des tubes
tube_list_below = []
tube_list_above = []

# Paramètres des tubes
GATE_HEIGHT = 300
MIN_TUBE_LENGTH = 40
MIN_BELOW_TOP = MIN_TUBE_LENGTH + GATE_HEIGHT
MAX_BELOW_TOP = SCREEN_HEIGHT - GROUND_HEIGHT - MIN_TUBE_LENGTH

# Vitesse de défilement du sol
ground_scroll_speed = 5

# Intervalle entre les tuyaux (en frames)
tube_spawn_delay = 40  

# Score
score = 0

def create_gate():
    """ Crée une nouvelle paire de tuyaux avec la même logique pour le haut et le bas.
        Le nouveau couple est positionné en x en fonction du dernier couple existant,
        pour que le prochain apparaisse exactement tube_spawn_delay frames après le précédent. """
    # Calcul de la position x pour le nouveau couple :
    if tube_list_below:
        new_x = tube_list_below[-1]["rect"].x + ground_scroll_speed * tube_spawn_delay
    else:
        new_x = SCREEN_WIDTH

    # Pour le tube du bas
    tube_below_top = randint(MIN_BELOW_TOP, MAX_BELOW_TOP)
    tube_below_length = SCREEN_HEIGHT - GROUND_HEIGHT - tube_below_top

    # Calcul pour le tube du haut
    min_gap = BIRD_HEIGHT + 50
    max_gap = 150
    gap = randint(min_gap, max_gap)

    tube_above_bottom = tube_below_top - gap  
    tube_above_top = tube_above_bottom - TUBE_HEIGHT  
    tube_above_length = TUBE_HEIGHT 

    # Création des tuyaux avec un attribut "passed"
    tube_below = {
        "rect": pygame.Rect(new_x, tube_below_top, TUBE_WIDTH, tube_below_length),
        "passed": False
    }
    tube_above = {
        "rect": pygame.Rect(new_x, tube_above_top, TUBE_WIDTH, tube_above_length),
        "passed": False
    }

    tube_list_below.append(tube_below)
    tube_list_above.append(tube_above)

def update_tube_bas():
    """ Déplace et affiche les tuyaux du bas """
    for tube in tube_list_below:
        tube["rect"].move_ip(-ground_scroll_speed, 0)
        screen.blit(TUBE_BELOW, (tube["rect"].left, tube["rect"].top))
    # Supprime le premier tuyau s'il est hors écran
    if tube_list_below and tube_list_below[0]["rect"].right < 0:
        tube_list_below.pop(0)

def update_tube_haut():
    """ Déplace et affiche les tuyaux du haut """
    for tube in tube_list_above:
        tube["rect"].move_ip(-ground_scroll_speed, 0)
        screen.blit(TUBE_ABOVE, (tube["rect"].left, tube["rect"].top))
    # Supprime le premier tuyau s'il est hors écran
    if tube_list_above and tube_list_above[0]["rect"].right < 0:
        tube_list_above.pop(0)

def restart():
    """ Réinitialise le jeu """
    global bird_y, bird_x, bird_s, tube_list_below, tube_list_above, tube_timer, score
    bird_x = (SCREEN_WIDTH - BIRD_WIDTH) // 2
    bird_y = (SCREEN_HEIGHT - GROUND_HEIGHT) // 2
    bird_s = 0
    tube_list_below = []
    tube_list_above = []
    tube_timer = 0
    score = 0
    create_gate()

ground_pos = 0
frame_counter = 0
duration = 20

def update_ground():
    """ Met à jour et affiche le sol """
    global ground_pos
    ground_pos -= ground_scroll_speed
    if ground_pos < -SCREEN_WIDTH:
        ground_pos = 0
    screen.blit(DOUBLE_GROUND, (ground_pos, SCREEN_HEIGHT - GROUND_HEIGHT))

def update_bird():
    """ Met à jour la position et l'affichage de l'oiseau """
    global bird_x, bird_y, bird_s, frame_counter
    bird_s += G
    bird_y += bird_s

    frame_counter = (frame_counter + 1) % duration
    screen.blit(BIRDS[frame_counter // (duration // len(BIRDS))], (bird_x, bird_y))

def check_alive():
    """ Vérifie si l'oiseau est encore en vie """
    global score
    bird_rect = pygame.Rect(bird_x, bird_y, BIRD_WIDTH, BIRD_HEIGHT)

    if bird_y + BIRD_HEIGHT >= SCREEN_HEIGHT - GROUND_HEIGHT:
        HIT_SOUND.play()
        return False

    for tube in tube_list_below + tube_list_above:
        if bird_rect.colliderect(tube["rect"]):
            HIT_SOUND.play()
            return False

    # Vérifie si l'oiseau a passé une gate
    for tube in tube_list_below:
        if tube["rect"].right < bird_x and not tube["passed"]:
            tube["passed"] = True
            score += 1

    return True

def draw_score():
    """ Affiche le score à l'écran en utilisant les images des chiffres """
    score_str = str(score)  
    total_width = len(score_str) * DIGIT_WIDTH  

    # Position de départ pour afficher le score (centré en haut de l'écran)
    start_x = (SCREEN_WIDTH - total_width) // 2
    start_y = 50

    # Afficher chaque chiffre
    for i, digit_char in enumerate(score_str):
        digit_image = DIGITS[int(digit_char)] 
        screen.blit(digit_image, (start_x + i * DIGIT_WIDTH, start_y))

# Création de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
alive = True
go = True

restart()

# Initialisation du timer de génération
tube_timer = 0

while go:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            go = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if alive:
                    bird_s = JUMP
                    JUMP_SOUND.play()
                else:
                    restart()
                    alive = True

    if alive:
        screen.blit(BG, (0, 0))
        update_ground()
        update_bird()
        update_tube_bas()
        update_tube_haut()

        # Incrément du timer et génération du nouveau couple toutes les 40 images
        tube_timer += 1
        if tube_timer >= tube_spawn_delay:
            create_gate()
            tube_timer = 0

        alive = check_alive()
        draw_score()  # Affiche le score
        pygame.display.update()

    clock.tick(FPS)

pygame.quit()
