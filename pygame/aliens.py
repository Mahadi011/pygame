#!/usr/bin/env python
""" pygame.examples.aliens
Shows a mini game where you have to defend against aliens.
What does it show you about pygame?
* pg.sprite, the difference between Sprite and Group.
* dirty rectangle optimization for processing for speed.
* music with pg.mixer.music, including fadeout
* sound effects with pg.Sound
* event processing, keyboard handling, QUIT handling.
* a main loop frame limited with a game clock from pg.time.Clock
* fullscreen switching.
Controls
--------
* Left and right arrows to move.
* Space bar to shoot
* f key to toggle between fullscreen.
"""

import random
import os
from re import S

# import basic pygame modules
import pygame as pg

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


# game constants
MAX_SHOTS = 2  # most player bullets onscreen
ALIEN_ODDS = 22  # chances a new alien appears
BOMB_ODDS = 60  # chances a new bomb will drop
ALIEN_RELOAD = 12  # frames between new aliens
SCREENRECT = pg.Rect(0, 0, 640, 480)
SCORE = 0

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert_alpha()


def load_sound(file):
    """because pygame can be be compiled without mixer."""
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None


# Each type of game object gets an init and an update function.
# The update function is called once per frame, and it is when each object should
# change its current position and state.
#
# The Player object actually gets a "move" function instead of update,
# since it is passed extra information about the keyboard.


class Player(pg.sprite.Sprite):
    """Representing the player as a moon buggy type car."""

    speed = 10
    bounce = 24
    gun_offset = -11
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, direction):
        if direction:
            self.facing = direction
        self.rect.move_ip(direction * self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)

    def gunpos(self):
        pos = self.facing * self.gun_offset + self.rect.centerx
        return pos, self.rect.top


class Balloon(pg.sprite.Sprite):
    """A simple balloon"""
                                                                                                                                                                                                                      
    speed = 4
    animcycle = 100
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.image = pg.transform.scale(self.image, (100, 100))
        self.rect = pg.Rect(10, 10, 100, 100)
        self.facing = random.choice((-1, 1)) * Balloon.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right
             
    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        # self.image = self.images[self.frame // self.animcycle % 3]

  

class Alien(pg.sprite.Sprite):
    """An alien space ship. That slowly moves down the screen."""

    speed = 4
    animcycle = 12
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Alien.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame // self.animcycle % 3]


class Plane(pg.sprite.Sprite):

    speed = 4
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.image = pg.transform.scale(self.image,(90,70))
        self.rect = pg.Rect(10, 10, 90,70)
        #self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Plane.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1

class OtherAlien(Alien):
    images = []
    speed = 4
    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.image = pg.transform.scale(self.image, (80, 71))
        self.rect = pg.Rect(10, 10, 80, 71)
        self.facing = OtherAlien.speed
        self.frame = 0

class Explosion(pg.sprite.Sprite):
    """An explosion. Hopefully the Alien and not the player!"""

    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        """called every time around the game loop.
        Show the explosion surface for 'defaultlife'.
        Every game tick(update), we decrease the 'life'.
        Also we animate the explosion.
        """
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()


class Shot(pg.sprite.Sprite):
    """a bullet the Player sprite fires."""

    speed = -11
    images = []

    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        """called every time around the game loop.
        Every tick we move the shot upwards.
        """
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()


class Bomb(pg.sprite.Sprite):
    """A bomb the aliens drop."""

    speed = 9
    images = []

    def __init__(self, alien):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=alien.rect.move(0, 5).midbottom)

    def update(self):
        """called every time around the game loop.
        Every frame we move the sprite 'rect' down.
        When it reaches the bottom we:
        - make an explosion.
        - remove the Bomb.
        """
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom >= 470:
            Explosion(self)
            self.kill()


class Score(pg.sprite.Sprite):
    """to keep track of the score."""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.font = pg.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = "white"
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 450)

    def update(self):
        """We only update the score in update() when it has changed."""
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)

# class StartKnapp(pg.sprite.Sprite):
#     images = []

#     def __init__(self):
#         pg.sprite.Sprite.__init__(self, self.containers)
#         self.image = self.images[0]
#         self.x = 240
#         self.y = 140
#         self.rect = self.image.get_rect(center=(self.x, self.y))

#     def nedtryckt(self):
#         self.image = self.images[1]

#     def upptryckt(self):
#         self.image = self.images[0]   


# class Quit(pg.sprite.Sprite):
#     images = []
#     def __init__(self):
#         pg.sprite.Sprite.__init__(self, self.containers)
#         self.image = self.images[0]
#         self.x = 240
#         self.y = 210
#         self.rect = self.image.get_rect(center = (self.x, self.y))


class BackgroundKlass(pg.sprite.Sprite):

    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.image = pg.transform.scale(self.image, (SCREENRECT.width, SCREENRECT.height*2))
        self.rect = pg.Rect(0, 0, SCREENRECT.width, SCREENRECT.height*2)

    def update(self):
        self.rect.move_ip(0, 3)
        if(self.rect.y > 0):
            self.rect.y = -self.rect.height//2
    

#button class
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pg.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pg.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pg.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action   




def main(winstyle=0):
    # Initialize pygame
    menu_state = "main"
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    img = load_image("player1.gif")
    Player.images = [img, pg.transform.flip(img, 1, 0)]
    img = load_image("explosion1.gif")
    Explosion.images = [img, pg.transform.flip(img, 1, 1)]
    Alien.images = [load_image(im) for im in ("alien1.gif", "alien2.gif", "alien3.gif")]
    Balloon.images = [load_image("plane.png")]
    OtherAlien.images = [load_image(im) for im in ("alienny2.png", "alienny2.png", "alienny2.png")]
    Bomb.images = [load_image("bomb.gif")]
    Shot.images = [load_image("shot.gif")]
    Plane.images = [load_image(i) for i in ("plane4.png", "plane4.png")]
    # StartKnapp.images = [load_image("Menu_Green_01.png"), load_image("Menu_Red_03.png")]
    # Quit.images = [load_image("Menu_Green_04.png")]
    BackgroundKlass.images = [load_image("background4.png")]


    #load button images
    resume_img = load_image("button_resume.png").convert_alpha()
    options_img = load_image("button_options.png").convert_alpha()
    quit_img = load_image("button_quit.png").convert_alpha()
    back_img = load_image("button_back.png").convert_alpha()
    plane_img = load_image("plane4.png").convert_alpha()
    plane_img = pg.transform.scale(plane_img, (100,100))
    baloon_img = load_image("plane.png").convert_alpha()
    baloon_img = pg.transform.scale(baloon_img, (100,100))
    otheralien_img = load_image("alienny2.png").convert_alpha()
    

    #create button instances
    resume_button = Button(240, 100, resume_img, 1)
    options_button = Button(240, 200, options_img, 1)
    quit_button = Button(240, 300, quit_img, 1)
    back_button = Button(240, 370, back_img, 1)
    plane_button = Button(50, 50, plane_img, 1)
    baloon_button = Button(50, 200, baloon_img, 1)
    otheralien_button = Button(50, 350,otheralien_img,1)


    
    
    # decorate the game window
    icon = pg.transform.scale(Alien.images[0], (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("Pygame Aliens")
    pg.mouse.set_visible(True)

    # create the background, tile the bgd image
    bgdtile = pg.transform.scale(load_image("background3.gif"),(640,480))
    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()

    # load the sound effects
    boom_sound = load_sound("boom.wav")
    shoot_sound = load_sound("car_door.wav")
    punch_sound = load_sound("punch.wav")
    if pg.mixer:
        music = os.path.join(main_dir, "data", "house_lo.wav")
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)

    # Initialize Game Groups
    aliens = pg.sprite.Group()
    balloons = pg.sprite.Group()
    shots = pg.sprite.Group()
    bombs = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()
    lastalien = pg.sprite.GroupSingle()
    lastballoon = pg.sprite.GroupSingle()
    planes = pg.sprite.Group()
    last_palne = pg.sprite.GroupSingle()
    menu = pg.sprite.Group()
    


    # assign default groups to each sprite class
    Player.containers = all
    Alien.containers = aliens, all, lastalien
    Balloon.containers = balloons, all, lastballoon
    OtherAlien.containers = aliens, all
    Plane.containers = planes, all, last_palne
    Shot.containers = shots, all
    Bomb.containers = bombs, all
    Explosion.containers = all
    Score.containers = all
    # StartKnapp.containers = menu
    # Quit.containers = menu
    BackgroundKlass.containers = all

    # Create Some Starting Values
    global score
    alienreload = ALIEN_RELOAD
    clock = pg.time.Clock()

    # initialize our starting sprites
    global SCORE
    # start_knapp = StartKnapp()
    BackgroundKlass()
    player = Player()
    
    
    # Alien()  # note, this 'lives' because it goes into a sprite group
    # OtherAlien()
    # Balloon()
    # Quit()
    # Plane()
    
    if pg.font:
        all.add(Score())
    plane1 = False
    alien1 = False
    baloon1 = False
    menu_state = False
    start_game = False
    while not start_game:
        screen.blit(background, (0, 0))
        if menu_state == False:  # When it is in the main menu
            if resume_button.draw(screen):
                start_game= True
                pg.display.flip()
                dirty = menu.draw(screen)
                pg.display.update(dirty)
                pg.mouse.set_visible(False)
                # game_paused = False
            if options_button.draw(screen):
                menu_state = True
            if quit_button.draw(screen):
                pg.quit()
        elif menu_state == True: # when it will be in the option menu
                       
            if plane_button.draw(screen):
                

                Plane()
                plane1 = True
                start_game= True
                   
                

            if baloon_button.draw(screen):
                Balloon()
                baloon1 = True
                start_game= True
                
            if otheralien_button.draw(screen):
                Alien()
                alien1 = True
                start_game= True

            if back_button.draw(screen):
                menu_state = False
                
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                pass
            if event.type == pg.QUIT:
                return




        # for event in pg.event.get():
        #     if event.type == pg.KEYDOWN:
        #         start_game = True
        #     elif event.type == pg.MOUSEBUTTONDOWN:
        #         if(Quit().rect.collidepoint(pg.mouse.get_pos())):
        #             pg.quit()
                    
        #     elif event.type == pg.MOUSEBUTTONDOWN:
        #         if(start_knapp.rect.collidepoint(pg.mouse.get_pos())):
        #             start_knapp.nedtryckt()
                    
        #     elif event.type == pg.MOUSEBUTTONUP:
        #             if(start_knapp.rect.collidepoint(pg.mouse.get_pos())):
        #                 start_knapp.upptryckt()
        #                 start_game = True
                    
                    
                


        pg.display.flip()
        dirty = menu.draw(screen)
        pg.display.update(dirty)
    pg.mouse.set_visible(False)    

    # Run our main loop whilst the player is alive.
    while player.alive():

        # get input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_f:
                    if not fullscreen:
                        print("Changing to FULLSCREEN")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    else:
                        print("Changing to windowed mode")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    pg.display.flip()
                    fullscreen = not fullscreen

        keystate = pg.key.get_pressed()

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # handle player input
        direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
        player.move(direction)
        firing = keystate[pg.K_SPACE]
        if not player.reloading and firing and len(shots) < MAX_SHOTS:
            Shot(player.gunpos())
            if pg.mixer:
                shoot_sound.play()
        player.reloading = firing

        # Create new alien
        if alienreload:
            alienreload = alienreload - 1
        elif not int(random.random() * ALIEN_ODDS):
            if plane1 == True:

                if(random.randint(0, 1) == 0):
                    # Alien()
                    Plane()
                # else:
                #     OtherAlien()
                #     Balloon()
                alienreload = ALIEN_RELOAD
            elif baloon1 == True :

                if(random.randint(0, 1) == 0):
                   Balloon()
               
                alienreload = ALIEN_RELOAD
            elif alien1 == True:

                if(random.randint(0, 1) == 0):
                    Alien()
                
                alienreload = ALIEN_RELOAD

        # Drop bombs
        if last_palne and not int(random.random()* BOMB_ODDS):
            Bomb(last_palne.sprite)
        if lastalien and not int(random.random() * BOMB_ODDS):
            Bomb(lastalien.sprite)

        # Detect collisions between aliens and players.
        for plane in pg.sprite.spritecollide(player,planes,1):
            if pg.mixer:
                boom_sound.play()
            Explosion(plane)
            Explosion(player)
            SCORE = SCORE + 1
            player.kill()
        
        for alien in pg.sprite.spritecollide(player, aliens, 1):
            if pg.mixer:
                boom_sound.play()
            Explosion(alien)
            Explosion(player)
            SCORE = SCORE + 1
            player.kill()

        # Detect collisions between balloon and player.
        for balloon in pg.sprite.spritecollide(player, balloons, 1):
            if pg.mixer:
                punch_sound.play()
            Explosion(balloon)
            Explosion(player)
            SCORE = SCORE + 1
            player.kill()


        # See if shots hit the aliens.
        for plane in pg.sprite.groupcollide(planes, shots, 1,1).keys():
            if pg.mixer:
                boom_sound.play()
            Explosion(plane)
            SCORE = SCORE + 1
        for alien in pg.sprite.groupcollide(aliens, shots, 1, 1).keys():
            if pg.mixer:
                boom_sound.play()
            Explosion(alien)
            SCORE = SCORE + 1

        #Shots hitting balloon
        for balloon in pg.sprite.groupcollide(balloons, shots, 1, 1).keys():
            if pg.mixer:
                punch_sound.play()
            Explosion(balloon)
            SCORE = SCORE + 1

        # See if alien boms hit the player.
        for bomb in pg.sprite.spritecollide(player, bombs, 1):
            if pg.mixer:
                boom_sound.play()
            Explosion(player)
            Explosion(bomb)
            player.kill()

        # draw the scene
        dirty = all.draw(screen)
        pg.display.update(dirty)

        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
        clock.tick(40)

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)


# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
