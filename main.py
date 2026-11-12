import pygame
import random
import math
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boids Flocking Simulation & Swarm Intelligence")
clock = pygame.time.Clock()

# Couleurs (Thème Cyber / Néon Sombre)
DARK_BG = (12, 15, 22)
BOID_COLOR = (0, 210, 255)      # Cyan néon pour l'essaim
LEADER_COLOR = (255, 105, 180)  # Rose néon pour la souris / cible
OBSTACLE_COLOR = (50, 65, 85)
TEXT_COLOR = (240, 245, 255)
GRAY = (120, 130, 150)

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 14)

class Boid:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.0, 4.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.max_speed = 3.5
        self.max_force = 0.12

    def update(self):
        self.x += self.vx
        self.y += self.vy

        # Gestion des bords (effet tore / passage traversant)
        if self.x < 0: self.x = WIDTH
        elif self.x > WIDTH: self.x = 0
        if self.y < 80: self.y = HEIGHT
        elif self.y > HEIGHT: self.y = 80

    def apply_behavior(self, boids, mouse_pos):
        # 1. Règles des Boids (Séparation, Alignement, Cohésion)
        sep_x, sep_y = 0, 0
        align_vx, align_vy = 0, 0
        cohere_x, cohere_y = 0, 0
        
        neighbor_dist = 50
        count = 0

        for other in boids:
            if other != self:
                dist = math.hypot(self.x - other.x, self.y - other.y)
                if dist < neighbor_dist:
                    # Séparation (éviter la collision)
                    if dist > 0:
                        sep_x += (self.x - other.x) / dist
                        sep_y += (self.y - other.y) / dist
                    # Alignement (partager la même direction)
                    align_vx += other.vx
                    align_vy += other.vy
                    # Cohésion (rester groupés)
                    cohere_x += other.x
                    cohere_y += other.y
                    count += 1

        fx, fy = 0, 0

        if count > 0:
            # Alignement
            align_vx /= count
            align_vy /= count
            # Cohésion
            cohere_x /= count
            cohere_y /= count
            cohere_dx = cohere_x - self.x
            cohere_dy = cohere_y - self.y

            fx += sep_x * 1.5 + align_vx * 0.5 + cohere_dx * 0.03

        # 2. Interaction avec la souris (Attraction si clic, ou fuite légère)
        if mouse_pos[1] > 80:
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist_mouse = math.hypot(dx, dy)
            if dist_mouse < 200 and dist_mouse > 10:
                # Suivre doucement le curseur
                fx += (dx / dist_mouse) * 0.4

        # Appliquer les forces à la vitesse
        self.vx += fx
        self.vy += fy

        # Limiter la vitesse maximale
        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed

    def draw(self, surface):
        # Dessiner le boid sous forme de petit triangle orienté
        angle = math.atan2(self.vy, self.vx)
        tip_x = self.x + math.cos(angle) * 8
        tip_y = self.y + math.sin(angle) * 8
        left_x = self.x + math.cos(angle + 2.5) * 5
        left_y = self.y + math.sin(angle + 2.5) * 5
        right_x = self.x + math.cos(angle - 2.5) * 5
        right_y = self.y + math.sin(angle - 2.5) * 5

        pygame.draw.polygon(surface, BOID_COLOR, [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])

# Initialiser la population (150 oiseaux / boids)
boids = [Boid(random.randint(100, WIDTH - 100), random.randint(150, HEIGHT - 100)) for _ in range(150)]

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                boids = [Boid(random.randint(100, WIDTH - 100), random.randint(150, HEIGHT - 100)) for _ in range(150)]
            elif event.key == pygame.K_SPACE:
                # Ajouter de nouveaux boids au clic espace
                for _ in range(25):
                    boids.append(Boid(mouse_pos[0] if mouse_pos[1] > 80 else WIDTH//2, mouse_pos[1] if mouse_pos[1] > 80 else HEIGHT//2))

    # Mettre à jour tous les boids
    for boid in boids:
        boid.apply_behavior(boids, mouse_pos)
        boid.update()

    # --- RENDU GRAPHIQUE ---
    screen.fill(DARK_BG)

    # Dessiner un indicateur de la position de la souris (leader de l'essaim)
    if mouse_pos[1] > 80:
        pygame.draw.circle(screen, LEADER_COLOR, mouse_pos, 8, 2)
        pygame.draw.circle(screen, LEADER_COLOR, mouse_pos, 2)

    # Dessiner tous les boids
    for boid in boids:
        boid.draw(screen)

    # --- HUD ET INSTRUCTIONS ---
    title_txt = font_medium.render("BOIDS FLOCKING SIMULATION — INTELLIGENCE EN ESSAIM", True, TEXT_COLOR)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 12))

    stats_txt = font_small.render(f"Oiseaux dans l'essaim : {len(boids)}", True, BOID_COLOR)
    screen.blit(stats_txt, (40, 42))

    inst_txt = font_small.render("SOURIS : Attirer l'essaim | ESPACE : Ajouter des boids | R : Reset", True, GRAY)
    screen.blit(inst_txt, (WIDTH - inst_txt.get_width() - 40, 42))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()