import pygame
import math

import math
import random

pygame.init()

# Screen set up
screen_width = 500
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))

BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)

GREEN = (0, 255, 0)

# For fire particles
RED = (255, 0, 0)
ORANGE = (255, 128, 0)
YELLOW = (255, 255, 0)

# Background color
TOP_COLOR = (0, 29, 40)
BOTTOM_COLOR = (135, 206, 250)
MINIMAP_BLUE = (135 - 10, 206 - 10, 250 - 10)  # A shade darker

font = pygame.font.SysFont("Monospace", 20)

class Rocket:
    def __init__(self, width, height, pad, angle, mouse_x, mouse_y, gravity, thrust_power, mass):
        self.width = width
        self.height = height

        self.mode = "taking_off"

        x = int(screen_width / 2)
        y = screen_height - pad.height

        # Initialize start with 0
        self.vx = 0
        self.vy = 0

        self.mass = mass
        

        self.x = x
        self.y = y

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.angle = angle

        self.gravity = gravity
        self.thrust_power = thrust_power

        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

        self.original_image = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        raw_image = pygame.image.load("VSACapstoneRocket.png").convert_alpha()
        real_area = raw_image.get_bounding_rect()  # Removes the area around the png

        cropped_image = raw_image.subsurface(real_area)
        self.image = pygame.transform.scale(cropped_image, (self.width, self.height))

        self.original_image = self.image # For the rotation section of the code

        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def draw(self):
        # pygame.draw.rect(screen, (0, 255, 0), self.rect, 1)  # The green hitbox
        screen.blit(self.image, self.rect)

    def thrust(self, angle):  # For thrust and tilt --> based on mouse position
        downward_force = self.gravity * self.mass

        on_ground = self.rect.bottom >= pad.rect.top

        # Ensure active_power is always defined to avoid use-before-assignment
        active_power = 0

       
        if on_ground and pygame.mouse.get_pressed()[0]:
            active_power = downward_force * 3.0  # Kick-Start

        if pygame.key.get_pressed()[pygame.K_l]:
            self.mode = "landing" 

        if self.mode == "landing":
            if pygame.mouse.get_pressed()[0]:
                if self.vy > 2.0:
                    active_power = downward_force * 5.0
                elif self.vy > 0:
                    active_power = downward_force * 0.95 # Gradual descent --> allows user to focus solely on angle, instead of both thrust and angle --> triggered by pressing "L"
                else:
                    active_power = self.thrust_power
            else:
                active_power = 0

        elif self.mode == "taking_off":
            if self.vy > 2.0:  # Fast descent!
                active_power = downward_force * 5.0  # Hover slam
            else:
                active_power = self.thrust_power  # Else --> lifting off or going up

        self.vy += downward_force # GRAVITY!

        if pygame.mouse.get_pressed()[0]:
            rads = math.radians(90 - self.angle)

            thrust_x = math.cos(rads) * active_power
            thrust_y = math.sin(rads) * active_power 

            self.vx += thrust_x
            self.vy -= thrust_y

        # movement
        self.x += self.vx
        self.y += self.vy

        # reduce sidesways sliding
        #self.x *= 0.98

        max_speed = 6
        if self.vy < - max_speed:
            self.vy = - max_speed

        self.rect.center = (int(self.x), int(self.y))

        # Only snap to floor if moving downwards
        if self.rect.bottom > pad.rect.top and self.vy > 0:  # Touching launchpad
            self.rect.bottom = pad.rect.top
            self.y = self.rect.centery
            self.vx = 0
            self.vy = 0
            self.thrust_power = self.thrust_power
            self.mode = "taking_off"


    def tilt(self):
        in_air = self.rect.bottom < pad.rect.top

        if in_air and pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rel_x = mouse_x - self.rect.centerx

            target_angle = rel_x * 0.06
            target_angle = max(-35, min(35, target_angle))
        else:
            target_angle = 0

        # smooth rotation toward target_angle
        smoothness = 0.08
        self.angle += (target_angle - self.angle) * smoothness

        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
            
    def reset_tilt(self):
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, 0)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def reset_rocket_pos(self, x, y):
        if pygame.key.get_pressed()[pygame.K_r]:
            self.x = x
            self.y = y

class LaunchPad:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = screen_width / 2 - self.width / 2
        self.y = screen_height - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        pygame.draw.rect(screen, BLACK, self.rect)


class RocketParticle:
    def __init__(self, x, y, radius, rocket, speed, pad):
        color_list = [RED, ORANGE, YELLOW]
        self.color = random.choice(color_list)

        # self.x = x
        # self.y = y
        # Distance from rocket center to engine
        offset = rocket.height / 2

        # Convert rocket angle
        rads = math.radians(90 - rocket.angle)

        # Engine pos
        self.x = rocket.rect.centerx - math.cos(rads) * offset
        self.y = rocket.rect.centery + math.sin(rads) * offset

        self.radius = radius
        self.rocket = rocket

        self.angle = math.radians(
            270 - rocket.angle + random.randint(-10, 10)
        )

        self.speed = speed

        blast_distance = 10

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y -= self.speed * math.sin(self.angle)

        circle_rect = pygame.Rect(self.x, self.y, self.radius, self.radius)

# Instances
pad = LaunchPad(
    width=150,
    height=10,
)

rocket = Rocket(
    width=15,
    height=200,
    pad=pad,
    angle=0,
    mouse_x=pygame.mouse.get_pos()[0],
    mouse_y=pygame.mouse.get_pos()[1],
    gravity=0.16,  # 0.16
    thrust_power=0.149,  # 0.149
    mass=0.7  # 0.7
)

particle = []

def draw_vert_gradient(width, height, top_color, bottom_color): #draw background
    gradient = pygame.Surface((width, height))

    for y in range(height):
        ratio = y / height

        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)

        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    
    return gradient

background = draw_vert_gradient(
    screen_width, 
    screen_height, 
    TOP_COLOR, 
    BOTTOM_COLOR
)

clock = pygame.time.Clock()
# Game loop
while True:
    clock.tick(90)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pos = pygame.mouse.get_pos()

        keys = pygame.key.get_pressed()

    screen.blit(background,(0, 0))


    # Launchpad
    pad.draw()

    # Particle
    if pygame.mouse.get_pressed()[0]:
        for _ in range(15):
            particle.append(
                RocketParticle(
                    rocket.rect.centerx,
                    rocket.rect.bottom,
                    2,
                    rocket,
                    random.uniform(3, 10),
                    pad
                )
            )

    for p in particle[:]:
        p.move()

        circle_rect = pygame.Rect(p.x, p.y, p.radius * 2, p.radius * 2)

        if circle_rect.colliderect(pad.rect):
            particle.remove(p)
            continue

        p.draw()  # Underneath rocket

    # Rocket
    rocket.tilt()
    rocket.thrust(rocket.angle)
    rocket.draw()

    rocket.reset_rocket_pos(int(screen_width//2), screen_height - pad.height)

    pygame.display.flip()

pygame.quit()
