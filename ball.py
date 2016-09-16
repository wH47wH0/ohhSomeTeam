import sys, pygame
pygame.init()

size = width, height = 1280, 1024
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ball = pygame.image.load("ball.gif")
ballrect = ball.get_rect()

print(ballrect)

clock = pygame.time.Clock()

dirty_rects = []
dirty_rects.append(ballrect)

game_running = True

while game_running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

    ballrect = ballrect.move(speed)
    dirty_rects.append(ballrect)

    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.update()
