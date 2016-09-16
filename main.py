import sys
import pygame

def game_loop():
    pygame.init()

    display_width = 1280
    display_height = 1024

    size = width, height = 320, 240
    speed = [2, 2]
    black = 0, 0, 0

    screen = pygame.display.set_mode((display_width,display_height))

    ball = pygame.image.load("ball.png")
    ballrect = ball.get_rect()

    pygame.display.set_caption('Pong')
    clock = pygame.time.Clock()

    game_exit = False

    while not game_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit = True

        print(event)

        ballrect = ballrect.move(speed)
        if ballrect.left < 0 or ballrect.right > width:
            speed[0] = -speed[0]
        if ballrect.top < 0 or ballrect.bottom > height:
            speed[1] = -speed[1]

        screen.fill(black)
        screen.blit(ball, ballrect)
        pygame.display.flip()

        pygame.display.update()
        clock.tick(60)

game_loop()
pygame.quit()
quit()
