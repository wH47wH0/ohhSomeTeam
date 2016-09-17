import random
import os
import sge
import time

DATA = os.path.join(os.path.dirname(__file__), "data")
PADDLE_XOFFSET = 96
PADDLE_SPEED = 12
PADDLE_VERTICAL_FORCE = 1 / 4
BALL_START_SPEED = 6
BALL_ACCELERATION = 0.6
BALL_MAX_SPEED = 35
POINTS_TO_WIN = 10
TEXT_OFFSET = 32
DEBUG = True

game_in_progress = True


class Inventory(sge.dsp.Object):

    def __init__(self):
        sprite = sge.gfx.Sprite(width=40, height=40, origin_x=20, origin_y=20)
        sprite.draw_rectangle(0, 0, sprite.width, sprite.height, fill=sge.gfx.Color(self.color))
        super().__init__(0, 0, sprite=sprite, checks_collisions=False)

        # TODO: fix this, to be random at the whole screen
        self.x = random.randint(400, sge.game.width-400)
        self.y = random.randint(50, sge.game.height-50)


class ShrinkPaddleInventory(Inventory):
    color = "red"


class GrowPaddleInventory(Inventory):
    color = "blue"


class MultipleBallInventory(Inventory):
    color = "yellow"


class BallSpeedup(Inventory):
    color = "green"


class DirectionChanger(Inventory):
    color = "#cc6699"


class ScarySht(Inventory):
    color = "#333300"

INVENTORY_CLASSES = [ShrinkPaddleInventory, GrowPaddleInventory, MultipleBallInventory, BallSpeedup, DirectionChanger, ScarySht]


class Game(sge.dsp.Game):
    tm = int(time.time())
    left = 0
    right = 0
    def event_step(self, time_passed, delta_mult):
        curr_time = int(time.time())
        self.project_sprite(hud_sprite, 0, self.width / 2, 0)
        if self.left != 0 and curr_time-self.left < 2:
            rnd = [random.randint(0, 100), random.randint(0, 150)]
            sge.game.current_room.project_sprite(scary_sprite,0,rnd[0],rnd[1],1)
        if self.right != 0 and curr_time-self.right < 2:
            rnd = [random.randint(self.width-630, self.width-530), random.randint(0, 150)]
            sge.game.current_room.project_sprite(scary_sprite,0,rnd[0],rnd[1],1)
        if curr_time-self.tm == 5:
            inventory = random.choice(INVENTORY_CLASSES)()
            sge.game.current_room.add(inventory)
            self.tm = curr_time
        # if sge.joystick.get_pressed(players[0].joystick, 1) and players[0].scare > 0:
        #     if self.right == 0:
        #         scary_sound.play()
        #         self.right = int(time.time())
        #         players[0].scare -= 1
        # if sge.joystick.get_pressed(players[1].joystick, 1) and players[1].scare > 0:
        #     if self.left == 0:
        #         scary_sound.play()
        #         self.left = int(time.time())
        #         players[1].scare -= 1

    def event_key_press(self, key, char):
        global game_in_progress

        if key == 'f8':
            sge.gfx.Sprite.from_screenshot().save('screenshot.jpg')
        elif key == 'f11':
            self.fullscreen = not self.fullscreen
        elif key == 'escape':
            self.event_close()
        elif key in ('p', 'enter'):
            if game_in_progress:
                self.pause()
            else:
                game_in_progress = True
                self.current_room.start()
        elif key == 'a':
            inventory = random.choice(INVENTORY_CLASSES)()
            sge.game.current_room.add(inventory)
        elif key == "u" and players[1].scare > 0:
            self.left = int(time.time())
            scary_sound.play()
            players[1].scare -= 1
        elif key == "j" and players[0].scare > 0:
            self.right = int(time.time())
            scary_sound.play()
            players[0].scare -= 1

    def event_joystick_button_press(self, js_name, js_id, button):
        debug("js_id: " + str(js_id))
        debug("button: " + str(button))
        debug("players[0].scare: " + str(players[0].scare))
        debug("players[1].scare: " + str(players[1].scare))

        global game_in_progress

        if button == 10:
            if game_in_progress:
                self.pause()
            else:
                game_in_progress = True
                self.current_room.start()
        elif button == 11:
            self.fullscreen = not self.fullscreen
        elif button == 2 and players[js_id].scare > 0:
            scary_sound.play()
            if js_id == 0:
                self.right = int(time.time())
            else:
                self.left = int(time.time())
            players[js_id].scare -= 1

    def event_close(self):
        self.end()

    def event_paused_key_press(self, key, char):
        if key == 'escape':
            # This allows the player to still exit while the game is
            # paused, rather than having to unpause first.
            self.event_close()
        else:
            self.unpause()

    def event_paused_close(self):
        # This allows the player to still exit while the game is paused,
        # rather than having to unpause first.
        self.event_close()


class Player(sge.dsp.Object):

    score = 0

    def __init__(self, player):
        y = sge.game.height / 2
        self.speed_duration = 100
        self.dir_change = 3
        self.scare = 1
        if player == 1:
            self.joystick = 0
            self.up_key = "w"
            self.down_key = "s"
            x = PADDLE_XOFFSET
            self.hit_direction = 1
        else:
            self.joystick = 1
            self.up_key = "up"
            self.down_key = "down"
            x = sge.game.width - PADDLE_XOFFSET
            self.hit_direction = -1
        sprite = sge.gfx.Sprite(width=24, height=144, origin_x=12, origin_y=72)
        sprite.draw_rectangle(0, 0, sprite.width, sprite.height, fill=sge.gfx.Color("white"))

        super().__init__(x, y, sprite=sprite, checks_collisions=False)

    def event_create(self):
        self.score = 0
        refresh_hud()
        self.trackball_motion = 0

    def event_step(self, time_passed, delta_mult):
        # Movement
        key_motion = (sge.keyboard.get_pressed(self.down_key) -
                      sge.keyboard.get_pressed(self.up_key))
        axis_motion = sge.joystick.get_axis(self.joystick, 1)

        if (abs(axis_motion) > abs(key_motion) and
                abs(axis_motion) > abs(self.trackball_motion)):
            self.yvelocity = axis_motion * PADDLE_SPEED
        elif abs(self.trackball_motion) > abs(key_motion):
            self.yvelocity = self.trackball_motion * PADDLE_SPEED
        else:
            self.yvelocity = key_motion * PADDLE_SPEED

        self.trackball_motion = 0

        # Keep the paddle inside the window
        if self.bbox_top < 0:
            self.bbox_top = 0
        elif self.bbox_bottom > sge.game.current_room.height:
            self.bbox_bottom = sge.game.current_room.height

    def event_joystick_trackball_move(self, joystick, ball, x, y):
        if joystick == self.joystick:
            self.trackball_motion += y


class Ball(sge.dsp.Object):

    @staticmethod
    def ball_count_in_room():
        return len([x for x in sge.game.current_room.objects if isinstance(x, Ball)])

    def __init__(self, sprite):
        x = sge.game.width / 2
        y = sge.game.height / 2
        self.reset_speed = False
        super().__init__(x, y, sprite=sprite)

    def event_create(self):
        self.serve()

    def event_joystick_button_press(self, js_name, js_id, button):
        if button == 1:
            if players[js_id].dir_change > 0:
                if (js_id == 0 and self.xvelocity > 0 and self.yvelocity != 0) or (js_id == 1 and self.xvelocity < 0 and self.yvelocity != 0):
                        dirchange_sound.play()
                        self.yvelocity = 0-self.yvelocity
                        players[js_id].dir_change -= 1

    def event_key_press(self, key, char):
        if key == "c" and players[0].dir_change > 0:
            if self.xvelocity < 0 and self.yvelocity != 0:
                dirchange_sound.play()
                self.yvelocity = 0-self.yvelocity
                players[0].dir_change -= 1
        if key == "3" and players[1].dir_change > 0:
            if self.xvelocity > 0 and self.yvelocity != 0:
                dirchange_sound.play()
                self.yvelocity = 0-self.yvelocity
                players[1].dir_change -= 1

    def event_step(self, time_passed, delta_mult):
        # Scoring
        if self.bbox_right < 0:
            players[1].score += 1
            refresh_hud()
            score_sound.play()
            if self.ball_count_in_room() > 1:
                self.destroy()
            else:
                self.serve(-1)
        elif self.bbox_left > sge.game.current_room.width:
            players[0].score += 1
            refresh_hud()
            score_sound.play()
            if self.ball_count_in_room() > 1:
                self.destroy()
            else:
                self.serve(1)

        # Bouncing off of the edges
        if self.bbox_bottom > sge.game.current_room.height:
            self.bbox_bottom = sge.game.current_room.height
            self.yvelocity = -abs(self.yvelocity)
            bounce_wall_sound.play()
        elif self.bbox_top < 0:
            self.bbox_top = 0
            self.yvelocity = abs(self.yvelocity)
            bounce_wall_sound.play()

        # Speedup the ball
        if sge.joystick.get_pressed(players[0].joystick, 0) and players[0].speed_duration > 0:
            if not self.reset_speed:
                if self.xvelocity > 0:
                    self.xvelocity = BALL_MAX_SPEED
                else:
                    self.xvelocity = 0-BALL_MAX_SPEED
                self.reset_speed = True
            speed_sound.play()
            players[0].speed_duration -= 1
        elif sge.joystick.get_pressed(players[1].joystick, 0) and players[1].speed_duration > 0:
            if not self.reset_speed:
                if self.xvelocity > 0:
                    self.xvelocity = BALL_MAX_SPEED
                else:
                    self.xvelocity = 0-BALL_MAX_SPEED
                self.reset_speed = True
            players[1].speed_duration -= 1
            speed_sound.play()
        else:
            if self.reset_speed:
                if self.xvelocity > 0:
                    self.xvelocity = BALL_START_SPEED
                else:
                    self.xvelocity = 0-BALL_START_SPEED
                self.reset_speed = False

    def event_collision(self, other, xdirection, ydirection):
        if isinstance(other, Player):
            if other.hit_direction == 1:
                self.bbox_left = other.bbox_right + 1
            else:
                self.bbox_right = other.bbox_left - 1

            self.xvelocity = min(abs(self.xvelocity) + BALL_ACCELERATION,
                                 BALL_MAX_SPEED) * other.hit_direction
            self.yvelocity += (self.y - other.y) * PADDLE_VERTICAL_FORCE * (48/other.bbox_height)
            bounce_sound.play()
        elif isinstance(other, ShrinkPaddleInventory):
            shrink_sound.play()
            if self.xvelocity < 0:
                indx = 1
            elif self.xvelocity > 0:
                indx = 0
            if players[indx].bbox_height > 45:
                players[indx].sprite.height -= 45
                players[indx].bbox_height -= 45
            else:
                players[indx].sprite.height, players[indx].bbox_height = 1, 1
            other.destroy()
        elif isinstance(other, GrowPaddleInventory):
            grow_sound.play()
            if self.xvelocity < 0:
                indx = 0
            elif self.xvelocity > 0:
                indx = 1
            players[indx].sprite.height += 45
            players[indx].bbox_height += 45
            other.destroy()
        elif isinstance(other, MultipleBallInventory):
            multi_sound.play()
            for i in range(0, 2):
                sge.game.current_room.add(Ball(ball_sprite))
            other.destroy()
        elif isinstance(other, BallSpeedup):
            bounce_sound.play()
            if self.xvelocity < 0:
                players[0].speed_duration += 100
            else:
                players[1].speed_duration += 100
            other.destroy()
        elif isinstance(other, DirectionChanger):
            bounce_sound.play()
            if self.xvelocity < 0:
                players[0].dir_change += 1
            else:
                players[1].dir_change += 1
            other.destroy()
        elif isinstance(other, ScarySht):
            bounce_sound.play()
            if self.xvelocity < 0:
                players[0].scare += 1
            else:
                players[1].scare += 1
            other.destroy()

    def serve(self, direction=None):
        global game_in_progress

        if direction is None:
            direction = random.choice([-1, 1])

        self.x = self.xstart
        self.y = random.randint(0, sge.game.current_room.height)

        if (players[0].score < POINTS_TO_WIN and
                players[1].score < POINTS_TO_WIN):
            # Next round
            self.xvelocity = BALL_START_SPEED * direction
            self.yvelocity = 0
        else:
            # Game Over!
            win_sound.play()
            self.xvelocity = 0
            self.yvelocity = 0
            hud_sprite.draw_clear()
            x = hud_sprite.width / 2
            p1text = "WIN" if players[0].score > players[1].score else "LOSE"
            p2text = "WIN" if players[1].score > players[0].score else "LOSE"
            hud_sprite.draw_text(hud_font, p1text, x - TEXT_OFFSET,
                                 TEXT_OFFSET, color=sge.gfx.Color("white"),
                                 halign="right", valign="top")
            hud_sprite.draw_text(hud_font, p2text, x + TEXT_OFFSET,
                                 TEXT_OFFSET, color=sge.gfx.Color("white"),
                                 halign="left", valign="top")
            game_in_progress = False


def create_room():
    global players
    players = [Player(0), Player(1)]
    ball = Ball(ball_sprite)
    return sge.dsp.Room([players[0], players[1], ball], background=background)


def refresh_hud():
    # This fixes the HUD sprite so that it displays the correct score.
    hud_sprite.draw_clear()
    x = hud_sprite.width / 2
    hud_sprite.draw_text(hud_font, str(players[0].score), x - TEXT_OFFSET,
                         TEXT_OFFSET, color=sge.gfx.Color("white"),
                         halign="right", valign="top")
    hud_sprite.draw_text(hud_font, str(players[1].score), x + TEXT_OFFSET,
                         TEXT_OFFSET, color=sge.gfx.Color("white"),
                         halign="left", valign="top")

def debug(message):
    if DEBUG is True:
        print(message)

# Create Game object
Game(width=1280, height=1024, fps=120, window_text="Pong")

# Load sprites
paddle_sprite = sge.gfx.Sprite(width=8, height=48, origin_x=4, origin_y=24)
ball_sprite = sge.gfx.Sprite(width=16, height=16, origin_x=8, origin_y=8)
scary_sprite = sge.gfx.Sprite("scary", "data")
paddle_sprite.draw_rectangle(0, 0, paddle_sprite.width, paddle_sprite.height,
                             fill=sge.gfx.Color("white"))
ball_sprite.draw_rectangle(0, 0, ball_sprite.width, ball_sprite.height,
                           fill=sge.gfx.Color("white"))
hud_sprite = sge.gfx.Sprite(width=320, height=120, origin_x=160, origin_y=0)

# Load backgrounds
layers = [sge.gfx.BackgroundLayer(paddle_sprite, sge.game.width / 2, 0, -10000,
                                  repeat_up=True, repeat_down=True)]
background = sge.gfx.Background(layers, sge.gfx.Color("black"))

# Load fonts
hud_font = sge.gfx.Font("Droid Sans Mono", size=48)

# Load sounds
bounce_sound = sge.snd.Sound(os.path.join(DATA, 'bounce.wav'))
bounce_wall_sound = sge.snd.Sound(os.path.join(DATA, 'bounce_wall.wav'))
score_sound = sge.snd.Sound(os.path.join(DATA, 'score.wav'))
scary_sound = sge.snd.Sound(os.path.join(DATA, 'scream.wav'))
speed_sound = sge.snd.Sound(os.path.join(DATA, 'buzzaway.wav'))
multi_sound = sge.snd.Sound(os.path.join(DATA, 'multi.wav'))
shrink_sound = sge.snd.Sound(os.path.join(DATA, 'shrink.wav'))
dirchange_sound = sge.snd.Sound(os.path.join(DATA, 'dirchange.wav'))
grow_sound = sge.snd.Sound(os.path.join(DATA, 'grow.wav'))
win_sound = sge.snd.Sound(os.path.join(DATA, 'win.wav'))

# Create rooms
sge.game.start_room = create_room()

sge.game.mouse.visible = False


if __name__ == '__main__':
    sge.game.start()
