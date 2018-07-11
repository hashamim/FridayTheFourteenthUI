import sys, pygame, socket, select, time

#constants
port = 8500
imgdir = "image assets/"
audiodir = "audio assets/"
blue = 0
red = 1
purple = 2
colors = ["blue","red","purple"]

#test variables
victimpts = 0
killerpts = 0
numblocks = [0,0,0]
victimlives = [0,0,0]
killerlives = 0
doubledamage = [False,False,True]
victimescape = [False,False,False]
pygame.init()
def reset():
    global numblocks
    global victimlives
    global killerlives
    global doubledamage
    global victimescape
    numblocks = [0,0,0]
    victimlives = [0,1,1]
    killerlives = 3
    doubledamage = [False,False,False]
    victimescape = [False,False,False]
    roundsnd.play()

#create font
killerpts = 0
victimpts = 0
scoreboard = pygame.Surface((400,400))
scoreboard.fill((255,255,255))
fontboi = pygame.font.SysFont('papyrus', 60)
#load img files
killerstats = pygame.Surface((300,100))
killerstats.fill((255,255,255))
victimstats = pygame.Surface((300,200))
hearts = []
for color in colors:
    hearts.append(pygame.image.load(imgdir + color + "heart.png"))
emptyheart = pygame.image.load(imgdir + "emptyheart.png")
block = pygame.image.load(imgdir + "block.png")
critrdy = pygame.image.load(imgdir + "doubledamage.png")
escape = pygame.image.load(imgdir + "escape.png")

size = width, height = 800, 600
screen = pygame.display.set_mode(size)
background = pygame.image.load(imgdir + "background.png")

#load audio files
slashsnd = pygame.mixer.Sound(audiodir + "slash.wav")
shootsnd = pygame.mixer.Sound(audiodir + "shoot.wav")
blocksnd = pygame.mixer.Sound(audiodir + "newblock.wav")
blockupsnd = pygame.mixer.Sound(audiodir + "blockup.wav")
healsnd = pygame.mixer.Sound(audiodir + "heal.wav")
escapesnd = pygame.mixer.Sound(audiodir + "escape.wav")
roundsnd = pygame.mixer.Sound(audiodir + "roundend.wav")
def draw():
    print("screen being drawn")
    killerstats.fill((255,255,255))
    victimstats.fill((255,255,255))
    for lives in range(1,4):
        if lives <= killerlives:
            killerstats.blit(hearts[blue],[lives*100-100,0])
        else:
            killerstats.blit(emptyheart,[lives*100-100,0])
    for player in range(1,3):
        if victimescape[player] == True:
            victimstats.blit(escape,[0,player*100-100])
        elif victimlives[player] == 1:
            victimstats.blit(hearts[player],[0,player*100-100])
        else:
            victimstats.blit(emptyheart,[0,player*100-100])
        if numblocks[player] > 0:
            victimstats.blit(block,[100,player*100-100])
        if doubledamage[player] == True:
            victimstats.blit(critrdy,[200,player*100-100])
    killerpoints = fontboi.render(str(killerpts), False, (127,0,0))
    victimpoints = fontboi.render(str(victimpts), False,(127,0,110))
    screen.blit(background,[0,0])
    screen.blit(killerstats,[100,100])
    screen.blit(victimstats,[100,300])
    screen.blit(killerpoints,[260,197])
    screen.blit(victimpoints,[260,490])
    pygame.display.flip()
draw()
#start TCP/IP connection
print("connecting to server")
listensock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listensock.bind(('127.0.0.1',port))
listensock.listen(2)
s,addr = listensock.accept()
print("Connection address: ",addr)
inputs = [s]
outputs =[]
print("starting loop")
while 1:
    #quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            sys.exit()
    #Update game state
    print("selecting inputs")
    readable,writable,exceptional = select.select(inputs,outputs,inputs)
    if exceptional:
        print("server socket exception encountered")

    if readable:
        print("input encountered")
        msg = s.recv(3)
        
        print(msg)
        print(len(msg))
        if len(msg) < 3:
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        action = msg[1]
        player = msg[0]
        target = msg[2]
        if msg == "RES".encode('utf-8'):
            print("resetting")
            reset()
        elif action == 0:
            numblocks[player] = 1
            blockupsnd.play()
        elif action == 1 or action == 3:
            if numblocks[target] == 1:
                numblocks[target] -= 1
                blocksnd.play()
            else:
                if target == 0:
                    if doubledamage[player] == True:
                        killerlives -= 2
                        doubledamage[player] = False
                        slashsnd.play()
                        print("killerlives=%d" % (killerlives))
                    else:
                        killerlives -= 1
                        slashsnd.play()
                    if killerlives <= 0:
                        victimpts += 3
                        reset()
                else:
                    killerpts += 1
                    if killerlives < 3:
                        killerlives += 1
                    victimlives[target] -= 1
                    if action == 1:
                        slashsnd.play()
                    else:
                        shootsnd.play()
                    if 1 not in victimlives:
                        if True not in victimescape:
                            killerpts += 3
                        reset()
        elif action == 4: #revive
            victimlives[target] = 1
            doubledamage[player] = True
            healsnd.play()
        elif action == 2: #escape
            print("player escaped")
            escapesnd.play()
            victimpts += 1
            victimescape[player] = True
            victimlives[player] = 0
            if 1 not in victimlives:
                reset()
            
    #Update Display
    draw()
    
