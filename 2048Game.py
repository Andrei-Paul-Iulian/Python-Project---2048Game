import random
import pygame, sys
from pygame.locals import *
import argparse

pygame.init()
frame_rate = pygame.time.Clock()

WIDTH = 600
HEIGHT = 700
WIDTH_TABLE = 400
HEIGHT_TABLE = 400

BLACK = (0,0,0)
GREEN = (0, 255, 0)
GREY = (189, 186, 177)
ANOTHERGREY = (138, 135, 127)
WHITE = (255, 255, 255)

DIMENSIONS = (100, 100)


class Game:

    def __init__(self):     # constructor

        self.window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)   # game window
        pygame.display.set_caption('2048')  # title
        self.running = True    # status
        self.score = 0         # number of points
        self.grid = [[0 for _ in range(4)] for _ in range(4)]   # initializing table
        self.addTile()         # add starting tile
        self.previous = []     # previous table configuration (used for undoing moves)
        self.prev_points = 0   # previous number of points (used for undoing moves)
        for i in range(4):
            self.previous.append(self.grid[i].copy())
        self.highscore = 0     # player's highscore
        self.moves = 0         # number of moves since the beginning of the game
        self.in_game = 0       # 0 - game has not started yet, 1 - game in progress
        self.status = 0        # 0 - game has not ended yet, 1 - winner, -1 - failure
        self.replay = False    # False - in game, True - waiting for replay yes or no
        self.fused = [[False for _ in range(4)] for _ in range(4)]    # True - position where two tiles have been fused
        self.getHighScore()
        self.inp = 'X'         # input value for each frame 


    def run(self):   # keeps the game running

        while self.running:
            self.draw()
            inp = self.input()
            self.update(inp)
            self.inp = 0
            pygame.display.update()




    #########      PRE-GAME FUNCTIONS      #########

    def getHighScore(self):  # reads the highscore from the 'highscore.txt' file

        f = open("highscore.txt", "r")
        self.highscore = int(f.readline())
        f.close()

    
    def start(self):     # starts the game; closes start screen

        self.in_game = 1




    #########      INPUT FUNCTIONS      #########

    def input(self):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.saveHighScore()
                sys.exit()
            if event.type==KEYDOWN:
                if self.replay == False:     # if we're not waiting for an answer 
                    if event.key == K_UP or event.key == K_w:        # moving up
                        return 'A'
                    elif event.key == K_DOWN or event.key == K_s:    # moving down
                        return 'D'
                    elif event.key == K_LEFT or event.key == K_a:    # moving left
                        return 'W'
                    elif event.key == K_RIGHT or event.key == K_d:   # moving right
                        return 'S'
                    elif event.key == K_u:   # undo command

                        pundo_rect = pygame.Rect(418, 135, 30, 30)
                        pundo_image = pygame.image.load("C:/Users/Felicia/python/proiect-python/images/pressed_undo.png")
                        pundo_image = pygame.transform.scale(pundo_image, (30, 30))
                        self.window.blit(pundo_image, pundo_rect)

                        return 'U'

                    elif event.key == K_r:   # replay command

                        preplay_rect = pygame.Rect(460, 135, 30, 30)
                        preplay_image = pygame.image.load("C:/Users/Felicia/python/proiect-python/images/pressed_replay.png")
                        preplay_image = pygame.transform.scale(preplay_image, (30, 30))
                        self.window.blit(preplay_image, preplay_rect)

                        return 'R'

                    elif event.key == K_RETURN:  # start game command

                        return '\n'

                elif event.key == K_y and self.replay == True:   # answer 'yes' to the replaying question

                    return 'Y'

                elif event.key == K_n and self.replay == True:   # answer 'no' to the replaying question

                    self.replay = False

                else:

                    continue




    #########      UPDATING FUNCTIONS      #########

    def update(self, input):

        self.status = self.gameEnds()
            # game ends in a win or a loss, we can undo

        if input == 'U':     # undo
            self.undo()
        elif input == 'R':   # ask the replaying question
            if self.replay == False:
                self.replay = True
        elif input == '\n':  # start game
            self.start()
        elif input == 'Y':   # actually replay
            self.rep()
        else:
            moved = self.move(input)     # move table according to the arrow command
            if moved:
                self.addTile()           # add new tile only if the last move was valid (at least one tile has changed its place)
                self.moves = self.moves + 1      # increment the moves counter


    def addTile(self):

        available = []       # create a list of clear positions (with value 0)
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 0:
                    available.append((i, j))
        if random.randint(0, 9) == 0:    # decide wether the new tile will be a 2 (90% chance) or a 4 (10% chance)
            val = 4
        else:
            val = 2

        if len(available) > 0:
            pos = random.choice(available)
            self.grid[pos[0]][pos[1]] = val      # add the new tile (2 or 4) to a new available position (if any)
            return True     # if the new tile has been added, return True
        else:
            return False    # otherwise return False


    def fuse(self, positionfrom, positionto, alreadyFused):  # fusing two positions together
    
        # Idea: the value from 'positionfrom' and the value from 'positionto' will interact
        # Return value: ([did anything move?], [is the 'positionfrom' tile the result of a previous merger?])

        if positionto[1] > 3 or positionto[0] > 3:      # "tiles" that are outside the table can not move (wtf)
            return (False, alreadyFused)
        if positionto[1] < 0 or positionto[0] < 0:
            return (False, alreadyFused)
        if positionfrom[1] > 3 or positionfrom[0] > 3:
            return (False, alreadyFused)
        if positionfrom[1] < 0 or positionfrom[0] < 0:
            return (False, alreadyFused)
        if self.grid[positionfrom[0]][positionfrom[1]] == 0:     # if the value on the 'positionfrom' is 0, it will not move
            return (False, alreadyFused)
        if self.grid[positionto[0]][positionto[1]] == 0:         # if the value on the 'positionto' is 0, the 'positionfrom' tile will move freely
            self.grid[positionto[0]][positionto[1]] = self.grid[positionfrom[0]][positionfrom[1]]
            self.grid[positionfrom[0]][positionfrom[1]] = 0
            return (True, alreadyFused)
        if self.grid[positionto[0]][positionto[1]] == self.grid[positionfrom[0]][positionfrom[1]]:       # if the values are equal ...
            # ... but at least one of the tiles is the result of a previous merger, the fuse will not take place
            if self.fused[positionfrom[0]][positionfrom[1]] or self.fused[positionto[0]][positionto[1]]: 
                return (False, alreadyFused)
            else: # ... and both of them are at their first merger, fuse them
                self.grid[positionto[0]][positionto[1]] *= 2
                self.grid[positionfrom[0]][positionfrom[1]] = 0
                self.score += self.grid[positionto[0]][positionto[1]]
                self.fused[positionto[0]][positionto[1]] = True
                alreadyFused = True
                return (True, alreadyFused)
        return (False, alreadyFused)     # if no condition has been met, don't fuse




    #########      CHECK FUNCTIONS      #########

    def canMove(self, position, alreadyFused, direction = 'Q'):      # checks if a tile can move in a certain direction (Q = any direction)

        # For the conditions explanation see the 'fuse' function
        # RETURN VALUE:
        #           0 - can not move
        #           1 - can move by merging with the adjacent tile
        #           2 - can move freely in an empty space

        if direction == 'Q':     # can move in any direction?
            if self.canMove(position, alreadyFused, 'W') or self.canMove(position, alreadyFused, 'S') or self.canMove(position, alreadyFused, 'A') or self.canMove(position, alreadyFused, 'D'):
                return 1
            else:
                return 0

        elif direction == 'W':   # can move up?
            if position[1] > 3 or position[0] > 3:
                return 0
            if position[1] < 0 or position[0] < 1:
                return 0
            if self.grid[position[0]][position[1]] == 0:
                return 0
            if self.grid[position[0] - 1][position[1]] == 0:
                return 2
            if self.grid[position[0]][position[1]] == self.grid[position[0] - 1][position[1]]:
                if not alreadyFused:
                    return 1
                else:
                    return 0

        elif direction == 'S':   # can move down?
            if position[1] > 3 or position[0] > 2:
                return 0
            if position[1] < 0 or position[0] < 0:
                return 0
            if self.grid[position[0]][position[1]] == 0:
                return 0
            if self.grid[position[0] + 1][position[1]] == 0:
                return 2
            if self.grid[position[0]][position[1]] == self.grid[position[0] + 1][position[1]]:
                if not alreadyFused:
                    return 1
                else:
                    return 0
            
        elif direction == 'A':   # can move to the left?
            if position[1] > 3 or position[0] > 3:
                return 0
            if position[1] < 1 or position[0] < 0:
                return 0
            if self.grid[position[0]][position[1]] == 0:
                return 0
            if self.grid[position[0]][position[1] - 1] == 0:
                return 2
            if self.grid[position[0]][position[1]] == self.grid[position[0]][position[1] - 1]:
                if not alreadyFused:
                    return 1
                else:
                    return 0

        elif direction == 'D':   # can move to the right?
            if position[1] > 2 or position[0] > 3:
                return 0
            if position[1] < 0 or position[0] < 0:
                return 0
            if self.grid[position[0]][position[1]] == 0:
                return 0
            if self.grid[position[0]][position[1] + 1] == 0:
                return 2
            if self.grid[position[0]][position[1]] == self.grid[position[0]][position[1] + 1]:
                if not alreadyFused:
                    return 1
                else:
                    return 0
        else:
            return 0


    def canMoveSomething(self):  # is there at least one tile on the table which can be moved? ...

        for i in range(4):
            for j in range(4):
                if self.canMove((i, j), False):
                    return True
        return False


    def cantMoveAnything(self): # ... or not?

        return not self.canMoveSomething()


    def gameEnds(self):  # checks if the game has come to an end

        # RETURN VALUE:
        #           0 - game still underway
        #           1 - game ends with a win (2048 on the table)
        #          -1 - game ends with a loss (table full, no moves can be performed)

        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 2048:
                    return 1
        if self.cantMoveAnything():
            return -1
        return 0




    #########      MOVING FUNCTIONS      #########

    def movePlace(self, position, direction):    # moves one tile as far as it can

        moved = False    # False - no moves have been performed (yet), True - something has been moved already
        alreadyFused = False     # False - the tile has not been involved in a merger yet, True - the tile has resulted from a merger
        ret = (False, False)     # return tuple of the 'fuse' function

        if direction == 'W':     # move tile up

            ret = self.fuse(position, (position[0] - 1, position[1]), alreadyFused)
            while ret[0]:    # as long as the tile is moved ...
                alreadyFused = ret[1]    # ... update fusing status ...
                moved = True     # ... update moving status ...
                position = (position[0] - 1, position[1]) # ... update position ...
                ret = self.fuse(position, (position[0] - 1, position[1]), alreadyFused) # ... and try again

        elif direction == 'S':   # move tile down
            ret = self.fuse(position, (position[0] + 1, position[1]), alreadyFused)
            while ret[0]:
                alreadyFused = ret[1]
                moved = True
                position = (position[0] + 1, position[1])
                ret = self.fuse(position, (position[0] + 1, position[1]), alreadyFused)
        
        elif direction == 'A':   # move tile to the left
            ret = self.fuse(position, (position[0], position[1] - 1), alreadyFused)
            while ret[0]:
                alreadyFused = ret[1]
                moved = True
                position = (position[0], position[1] - 1)
                ret = self.fuse(position, (position[0], position[1] - 1), alreadyFused)
        
        elif direction == 'D':   # move tile to the right
            ret = self.fuse(position, (position[0], position[1] + 1), alreadyFused)
            while ret[0]:
                alreadyFused = ret[1]
                moved = True
                position = (position[0], position[1] + 1)
                ret = self.fuse(position, (position[0], position[1] + 1), alreadyFused)
        else:
            moved = False
        return moved
        

    def move(self, direction):   # move the entire table in a certain direction

        for i in range(4):
            for j in range(4):
                self.fused[i][j] = False     # reset the fusing status of all tiles
        moved = False
        auxiliary = []   # save last table configuration
        for i in range(4):
            auxiliary.append(self.grid[i].copy())
        aux = self.score
        if direction == 'W':     # move table up
            for j in range(4):
                for i in range(4):
                    if self.movePlace((i, j), 'W'):
                        moved = True
        elif direction == 'S':   # move table down
            for j in range(4):
                for i in range(3, -1, -1):
                    if self.movePlace((i, j), 'S'):
                        moved = True
        elif direction == 'A':   # move table to the left
            for i in range(4):
                for j in range(4):
                    if self.movePlace((i, j), 'A'):
                        moved = True
        elif direction == 'D':   # move table to the right
            for i in range(4):
                for j in range(3, -1, -1):
                    if self.movePlace((i, j), 'D'):
                        moved = True
        else:
            moved = False
        if moved:    # if anything has been moved, the last configuration is saved
            for i in range(4):
                self.previous[i] = auxiliary[i].copy()
            self.prev_points = aux
                 # otherwise, the previous configuration remains the same

        return moved




    #########      ADMINISTRATIVE FUNCTIONS      #########

    def getPath(self, value):    # path finder for a certain number image

        return "C:/Users/Felicia/python/proiect-python/images/image_2048_" + str(value) + ".png"


    def undo(self):  # undoing function

        if self.grid != self.previous:       # if the previous configuration of the table is different from the current one
            self.moves = self.moves - 1      # reduce the number of moves
            self.score = self.prev_points    # reduce score
        for i in range(4):
            self.grid[i] = self.previous[i].copy()   # copy the previous configuration to the current one
        if self.status != 0:
            self.status = 0     # if the undoing has been performed after the game has ended, the status is reset to 0


    def rep(self):   # replaying function

        # Resets all parameters
        self.replay = False
        self.grid = [[0 for _ in range(4)] for _ in range(4)]
        self.addTile()
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.moves = 0
        self.status = 0
        self.previous = []
        self.prev_points = 0
        for i in range(4):
            self.previous.append(self.grid[i].copy())


    def saveHighScore(self):     # saves highscore to the 'highscore.txt' file

        f = open("highscore.txt", "w")
        if self.score > self.highscore:
            f.write(str(self.score))
        else:
            f.write(str(self.highscore))
        f.close()




    #########      DRAWING FUNCTIONS      #########

    def draw(self):

        if self.in_game == 1:        # if the game has already started ...
            if self.replay == False:     # ... if we're not waiting for an answer ...
                if self.status == 0:     # ... and if the game is still underway ...
                    self.window.fill(GREY)   # ... fill window

                    # ... draw title
                    title_rect = pygame.Rect(174, 10, 250, 100)
                    title_image = pygame.image.load("C:/Users/Felicia/python/proiect-python/images/title.png")
                    title_image = pygame.transform.scale(title_image, (250, 100))
                    self.window.blit(title_image, title_rect)

                    # ... draw table
                    for i in range(4):
                        for j in range(4):
                            tile = pygame.Rect(100 + j * 100, 200 + i * 100, 100, 100)
                            pygame.draw.rect(self.window,ANOTHERGREY,tile,100)
                            self.printTile((j, i))
                    tile = pygame.Rect(96, 196, 408, 408)
                    pygame.draw.rect(self.window,ANOTHERGREY,tile,4)

                    # ... draw counters
                    self.printScore()
                    self.printHighScore()
                    self.printMoves()

                    # ... draw undo button
                    undo_rect = pygame.Rect(418, 135, 30, 30)
                    undo_image = pygame.image.load("C:/Users/Felicia/python/proiect-python/images/undo.png")
                    undo_image = pygame.transform.scale(undo_image, (30, 30))
                    self.window.blit(undo_image, undo_rect)

                    # ... draw replay button
                    replay_rect = pygame.Rect(460, 135, 30, 30)
                    replay_image = pygame.image.load("C:/Users/Felicia/python/proiect-python/images/replay.png")
                    replay_image = pygame.transform.scale(replay_image, (30, 30))
                    self.window.blit(replay_image, replay_rect)

                elif self.status == -1:     # ... and if the game has ended in a loss, draw loss screen
                    lost_rect = pygame.Rect(96, 196, 408, 408)
                    lost_image = pygame.image.load("C:/Users/Felicia/python/proiect-python/images/lost.png")
                    lost_image = pygame.transform.scale(lost_image, (408, 408))
                    self.window.blit(lost_image, lost_rect)

                elif self.status == 1:      # ... and if the game has ended in a win, draw win screen
                    won_rect = pygame.Rect(96, 196, 408, 408)
                    won_image = pygame.image.load("C:/Users/Felicia/python/proiect-python/images/won.png")
                    won_image = pygame.transform.scale(won_image, (408, 408))
                    self.window.blit(won_image, won_rect)

            else:    # ... if we're waiting for an answer to the replaying question, draw the question screen
                ques_replay_rect = pygame.Rect(96, 196, 408, 408)
                ques_image = pygame.image.load("C:/Users/Felicia/python/proiect-python/images/replay_q.png")
                ques_image = pygame.transform.scale(ques_image, (408, 408))
                self.window.blit(ques_image, ques_replay_rect)
        
        else:    # if the game hasn't started yet ...
            self.window.fill(GREY)  # ... fill window
            # ... draw the home screen
            start_rect = pygame.Rect(0, 50, 600, 600)
            start_image = pygame.image.load("C:/Users/Felicia/python/proiect-python/images/hello.png")
            start_image = pygame.transform.scale(start_image, (600, 600))
            self.window.blit(start_image, start_rect)




    #########      PRINTING FUNCTIONS      #########

    def printScore(self):    # printing score rectangle

        background = pygame.Rect(102, 120, 96, 60)
        pygame.draw.rect(self.window, ANOTHERGREY, background, 100)
        font1 = pygame.font.Font('freesansbold.ttf', 12)
        text1 = font1.render("TOTAL POINTS", True, GREY, ANOTHERGREY)
        textRect = text1.get_rect()
        textRect.center = (150, 135)
        font2 = pygame.font.Font('freesansbold.ttf', 20)
        text2 = font2.render(str(self.score), True, WHITE, ANOTHERGREY)
        text2Rect = text2.get_rect()
        text2Rect.center = (150, 160)
        self.window.blit(text1, textRect)
        self.window.blit(text2, text2Rect)


    def printHighScore(self):    # printing highscore rectangle

        background = pygame.Rect(202, 120, 96, 60)
        pygame.draw.rect(self.window, ANOTHERGREY, background, 100)
        font1 = pygame.font.Font('freesansbold.ttf', 12)
        text1 = font1.render("HIGHSCORE", True, GREY, ANOTHERGREY)
        textRect = text1.get_rect()
        textRect.center = (250, 135)
        font2 = pygame.font.Font('freesansbold.ttf', 20)
        text2 = font2.render(str(self.highscore), True, WHITE, ANOTHERGREY)
        text2Rect = text2.get_rect()
        text2Rect.center = (250, 160)
        self.window.blit(text1, textRect)
        self.window.blit(text2, text2Rect)

    def printMoves(self):    # printing moves rectangle

        background = pygame.Rect(302, 120, 96, 60)
        pygame.draw.rect(self.window, ANOTHERGREY, background, 100)
        font1 = pygame.font.Font('freesansbold.ttf', 12)
        text1 = font1.render("MOVES", True, GREY, ANOTHERGREY)
        textRect = text1.get_rect()
        textRect.center = (350, 135)
        font2 = pygame.font.Font('freesansbold.ttf', 20)
        text2 = font2.render(str(self.moves), True, WHITE, ANOTHERGREY)
        text2Rect = text2.get_rect()
        text2Rect.center = (350, 160)
        self.window.blit(text1, textRect)
        self.window.blit(text2, text2Rect)

    def printTile(self, pos):    # printing all the tiles and their values

        position = (200 + pos[0] * 100 + 1, 100 + pos[1] * 100 + 1)
        image = pygame.image.load(self.getPath(self.grid[pos[0]][pos[1]]))
        image = pygame.transform.scale(image, (94, 94))
        self.window.blit(image, (position[0]-100+2,position[1]+100+2))




def main():
    game = Game()    # create game
    game.run()       # run game
    return 0

main()               # call the main function