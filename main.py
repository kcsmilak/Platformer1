import pgzrun
import pygame
import random
import helpers

TITLE = "Hello World"

WIDTH = 600
HEIGHT = 350

MAX_PLATFORMS = 3
MAX_BALLS = 0

GRAVITY = 0.3
GRAVITY_MAX = 10
HEIGHT_MIN = -200
JUMP_BOOST = 10

PLAYER_ENTITY = 0
PLATFORM_ENTITY = 1
BALL_ENTITY = 2
BULLET_ENTITY = 3

SHOOT_COOLDOWN = 20

# edge behaviors: STOP, STICK, BOUNCE, DIE, DESTROY

class Entity(Actor):
    def __init__(self, image):
        Actor.__init__(self, image)
        self.xspeed = 0
        self.yspeed = 0
        self.max_right = WIDTH
        self.min_left = 0
        self.min_top = 0
        self.max_bottom = HEIGHT
        self.airborn = False
        self.hit = False
        self.id = random.randint(1,1024)
        self.type = -1
        self.solid = True
        self.shooting = False
        self.edgeBounce = True
        self.shootCooldown = 0


        
    def move(self, player):
        entity = self

        # try to move in x direction
        entity.x += entity.xspeed

        # if hit edge, bounce or die
        if (self.right > self.max_right):
            self.xspeed *= -1
            self.right = self.max_right
        
        elif (self.left < self.min_left):
            self.xspeed *= -1
            self.left = self.min_left
        
        # if hit player, do something
        if entity.colliderect(player):
            # if platform, push the player
            if (PLATFORM_ENTITY == entity.type):
                player.x += entity.xspeed
            # if ball, hurt the player
            elif (BALL_ENTITY == entity.type):
                player.hit = True
                entity.hit = True
    
        entity.y += entity.yspeed

        # if hit edge, bounce
        if (entity.bottom > entity.max_bottom):
            entity.yspeed *= -1
            entity.bottom = entity.max_bottom           
            
        elif (entity.top < entity.min_top):
            entity.yspeed *= -1
            entity.top = entity.min_top

    def draw2(self, screen):
        screen.draw.rect(Rect((self.topleft, (self.width, self.height))), (255,255,255)) 
        self.draw()
        
    

        
class Player(Entity):
    def __init__(self):
        Entity.__init__(self, "alien-left")
        self.type = PLAYER_ENTITY
        self.min_top = -200        

        
    def move(self, obstacles):
        entity = self

        # try to move in x direction
        entity.x += entity.xspeed

        # if hit edge, bounce
        if (entity.right > entity.max_right):
            entity.xspeed *= -1
            entity.right = entity.max_right
        
        elif (entity.left < entity.min_left):
            entity.xspeed *= -1
            entity.left = entity.min_left                
        
        entity.y += entity.yspeed

        # if hit edge, bounce
        if (entity.bottom > entity.max_bottom):
            entity.yspeed *= -1
            entity.bottom = entity.max_bottom

            entity.yspeed = 0
            entity.airborn = False               
            
        elif (entity.top < entity.min_top):
            entity.yspeed *= -1
            entity.top = entity.min_top

        else:
            for obstacle in obstacles:
                if entity.colliderect(obstacle):
                    if (obstacle.solid):
                        entity.y -= entity.yspeed
                        if (entity.yspeed > 0):
                            entity.airborn = False
                        entity.yspeed = 0
                        entity.x += obstacle.xspeed
                        break
            if entity.yspeed > 0:
                entity.airborn = True


class Platform(Entity):
    def __init__(self, i):
        Entity.__init__(self, "platform-rock")
        self.type = PLATFORM_ENTITY
        self.pos = 100 * i + 100, i * 135 + 50
        self.xspeed = random.randint(1, 3)        
        self.max_right = WIDTH * .75
        self.min_left = WIDTH * .25


class Ball(Entity):
    def __init__(self):
        Entity.__init__(self, "bomb")
        self.type = BALL_ENTITY
        self.pos = random.randint(0,WIDTH - self.width), random.randint(0,HEIGHT - self.height)
        self.xspeed = random.randint(1, 3) 
        if (random.randint(0,1)): self.xspeed *= -1
        self.yspeed = random.randint(1, 3) 
        if (random.randint(0,1)): self.yspeed *= -1
        self.solid = True

class Bullet(Entity):
    def __init__(self, x, y, dx, dy):
        Entity.__init__(self, "bullet")
        self.angle = -90
        self.type = BULLET_ENTITY
        self.pos = x, y
        self.xspeed = dx 
        self.yspeed = dy 
        self.solid = True
        self.max_right = self.max_left = 100


class World():
    def __init__(self):
        self.all_entities = []
        self.player = 0
        self.reset()

    def reset(self):
        self.all_entities.clear()

        self.player = Player()
        #self.all_entities.append(self.player)
    
        for i in range(0, MAX_PLATFORMS):
            self.all_entities.append(Platform(i))    

        for i in range(0, MAX_BALLS):
            self.all_entities.append(Ball()) 

        #self.all_entities.append(Bullet(100,100,2,0))
    
    def update(self):
        player = self.player
        entities = self.all_entities
        
        self.handleInput()
        
        # move entities
        for entity in entities:          
            entity.move(player)

        # move player
        player.move(entities)

        # remove hit entities
        for entity in entities:
            if (entity.hit):
                entities.remove(entity)

        # handle hit Player
        if (player.hit):
            player.hit = False
            print("ouch!")

    def handleInput(self):
        if (keyboard.r):
            self.reset()
            return

        player = self.player


        if (keyboard.b):
            self.all_entities.append(Ball())    
        
        if (keyboard.d):
            player.image = "alien-right"
        if (keyboard.a):
            player.image = "alien-left"
    
        if (keyboard.d):
            player.xspeed = 5 
        elif (keyboard.a):
            player.xspeed = -5 
        else:
            player.xspeed = 0
            pass

        if (keyboard.space) and not player.shooting:
            # shoot
            player.shooting = True
            player.shootCooldown = SHOOT_COOLDOWN
            self.all_entities.append(Bullet(player.x,player.y,2,0))
        elif player.shootCooldown > 0: # add cooldown here
            player.shootCooldown -= 1
        else:
            player.shooting = False
    
        if keyboard.w and not player.airborn:
            player.yspeed -= JUMP_BOOST
            player.airborn = True
    
        player.yspeed += GRAVITY

    def draw(self,screen):

        self.player.draw()
        
        for entity in self.all_entities:
            entity.draw()
       


def update():
    global world
    world.update()

def draw():
    global world
    screen.clear()
    screen.draw.rect(Rect(((0,0), (WIDTH, HEIGHT))), (55,55,55)) 
    
    world.draw(screen)

world = World()
pgzrun.go()











def space():
    pass
    '''
    for i in range(0, len(all_entities)):
        for j in range (i+1, len(all_entities)):
            entity1 = all_entities[i];
            entity2 = all_entities[j];

            if entity1.colliderect(entity2):
                print("collision")
    '''
    
    '''        
    for i in range(1, len(all_entities)):
        entity = all_entities[i]
        if player.colliderect(entity):
            print("collision")
            obj1 = player
            obj2 = entity

            v1 = pygame.math.Vector2(obj1.x, obj1.y)
            v2 = pygame.math.Vector2(obj2.x, obj2.y)

            nv = v2 - v1
            m1 = pygame.math.Vector2(obj1.xspeed, obj1.yspeed).reflect(nv)
            m2 = pygame.math.Vector2(obj2.xspeed, obj2.yspeed).reflect(nv)

            obj1.x -= obj1.xspeed
            obj1.y -= obj1.yspeed
            
            obj1.xspeed, obj1.yspeed = m1.x, m1.y
    '''


    '''
    def move2(self, obstacles):
        entity = self
        entity.x += entity.xspeed
        
        if (entity.right > entity.max_right):
            entity.xspeed *= -1
            entity.right = entity.max_right
            
        if (entity.left < entity.min_left):
            entity.xspeed *= -1
            entity.left = entity.min_left

        entity.y += entity.yspeed
        
        if (entity.bottom > entity.max_bottom):
            entity.yspeed *= -1
            entity.bottom = entity.max_bottom

            if (PLAYER_ENTITY == entity.type):
                entity.yspeed = 0
                entity.airborn = False
                
            
        if (entity.top < entity.min_top):
            entity.yspeed *= -1
            entity.top = entity.min_top    
    '''