import pygame, sys, os
from parser import Parser
from optparse import OptionParser
from pygame.locals import *

def drawHeatMap(locations, XSCALE=10, YSCALE=5):
    pygame.init()
    screen = pygame.display.set_mode([100*XSCALE, 100*YSCALE])
    # caption = "HeatMap: #" + str(info['number']) + " " + info['name'] + " (" + info['team'] + ")"
    pygame.display.set_caption('Volleymetrics HeatMap')

    white = 255, 240, 200
    black = 20, 20, 40

    screen.fill(black)

    # Draw court outlines
    outerBoundary = [(0,0), (0, 99), (99, 99), (99, 0)]
    courtBoundary = [(10, 10), (10, 90), (90, 90), (90, 10)]
    pygame.draw.lines(screen, white, True, scaleUp(outerBoundary, XSCALE, YSCALE), 3)
    pygame.draw.lines(screen, white, True, scaleUp(courtBoundary, XSCALE, YSCALE), 3)
    # Draw net
    pygame.draw.line(screen, white, (50*XSCALE, 10*YSCALE), (50*XSCALE, 90*YSCALE), 7)

    for location in locations:
        startx, starty = location[0][0]
        endx, endy = location[0][1]
        start = (startx*XSCALE, starty*YSCALE)
        end = (endx*XSCALE, endy*YSCALE)
        color = colorByRating(location[1])
        pygame.draw.line(screen,color,start,end)

    pygame.display.update()
    pygame.image.save(screen, 'output.bmp')
    pygame.display.quit()
    pygame.quit()

    # while(1):
    #     for e in pygame.event.get():
    #         if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
    #             sys.exit("Leaving because you requested it.")

def scaleUp(list, scaleX, scaleY):
    newlist = []
    for item in list:
        newlist.append((item[0]*scaleX, item[1]*scaleY))
    return newlist

def colorByRating(rating):
    white = 255, 240, 200
    red = 255, 0, 0
    green = 0, 255, 0
    if rating == '#':
        return green
    elif rating == '=':
        return red
    else:
        return white

def readCommands(argv):
    parser = OptionParser()
    parser.add_option("-f", "--files", dest="fileNames",
                  help="draw heat map from FILES (comma separated list)", metavar="FILES")
    parser.add_option("-n", "--number", dest="playerNumber",
                    help="playerNumber to analyze")
    parser.add_option("-t", "--team", dest="teamNumber",
                    help="Volleymetrics teamNumber for team the player is on")
    parser.add_option("-a", "--attacks", dest="attackCombos",
                    help="attackCombos to search for and display")
    (options, args) = parser.parse_args(argv)
    return options

if __name__ == '__main__':
    options = readCommands(sys.argv[1:])

    team = int(options.teamNumber)
    player = int(options.playerNumber)

    # Allow option of "all" attacks to be displayed
    if options.attackCombos == 'all':
        attacks = ['ALL']
    else:
        attacks = [x.upper() for x in options.attackCombos.split(',')]

    # Allow option of "all" files being passed in
    files = []
    if options.fileNames == 'all':
        for f in os.listdir(os.getcwd() + '/data'):
            if f.endswith('.dvw'):
                files.append(f)
    elif options.fileNames == None:
        print "Use -f option to pass in .dvw file(s) to analyze."
    else:
        files = options.fileNames.split(',')

    locations = []
    for fileName in files:
        parser = Parser(fileName)
        locations = parser.getAttackInfo(team, player, attacks, locations)

    drawHeatMap(locations)
