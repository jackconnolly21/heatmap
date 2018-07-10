import pygame, sys, os, time
from pygame.locals import *
from timeit import default_timer as timer
from PIL import Image, ImageDraw
from optparse import OptionParser

from parser import Parser
import heatmap as hm

def drawArcs(locations, XSCALE=4, YSCALE=8):
    pygame.display.init()
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
    pygame.draw.line(screen, white, (10*XSCALE, 50*YSCALE), (90*XSCALE, 50*YSCALE), 7)

    for location in locations:
        startx, starty = location[0][0]
        endx, endy = location[0][1]
        start = (startx*XSCALE, starty*YSCALE)
        end = (endx*XSCALE, endy*YSCALE)
        color = colorByRating(location[1])
        pygame.draw.line(screen,color,start,end)
        pygame.draw.circle(screen,color,end,3)

    pygame.display.update()
    output_url = 'static/images/output.bmp'
    pygame.image.save(screen, output_url)

    # pygame.display.quit()
    # pygame.quit()

    running = True
    while(running):
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                pygame.display.iconify()
                running = False

    return output_url

def drawHeatMap(locations, XSCALE=4, YSCALE=8):
    ends = []
    for location in locations:
        endx, endy = location[0][1]
        end = (endx*XSCALE, endy*YSCALE)
        ends.append(end)
    h = hm.Heatmap()
    area = ((0, 0), (99*XSCALE, 99*YSCALE))
    h.heatmap(ends, dotsize=50, area=area).save("heatmap.png")

def drawArcsPillow(locations, XSCALE=4, YSCALE=8):
    im = Image.open("static/images/base_img.png")

    draw = ImageDraw.Draw(im)
    radius = 3
    for location in locations:
        startx, starty = location[0][0]
        endx, endy = location[0][1]
        start = (startx*XSCALE, starty*YSCALE)
        end = (endx*XSCALE, endy*YSCALE)
        color = colorByRating(location[1])
        draw.line([start, end], fill=color, width=3)
        draw.ellipse([end[0] - radius, end[1] - radius, end[0] + radius, end[1] + radius], fill=color, outline=color)

    # write to output
    del draw
    
    output_url = "static/images/output.png"
    im.save(output_url, "PNG")
    return output_url

def scaleUp(list, scaleX, scaleY):
    newlist = []
    for item in list:
        newlist.append((item[0]*scaleX, item[1]*scaleY))
    return newlist

def colorByRating(rating):
    white = 255, 240, 200
    red = 255, 0, 0
    green = 0, 255, 0
    yellow = 255, 255, 0
    if rating == '#':
        return green
    elif rating == '=':
        return red
    else:
        return yellow

def readCommands(argv):
    parser = OptionParser()
    parser.add_option("-f", "--folder", dest="folderName",
                  help="draw heat map from folder", default="testdata")
    parser.add_option("-n", "--number", dest="playerNumber",
                    help="playerNumber to analyze")
    parser.add_option("-t", "--team", dest="teamNumber",
                    help="Volleymetrics teamNumber for team the player is on")
    parser.add_option("-a", "--attacks", dest="attackCombos",
                    help="attackCombos to search for and display", default="all")
    parser.add_option("-k", action="store_true", dest="onlyKills", default=False)
    (options, args) = parser.parse_args(argv)
    return options

if __name__ == '__main__':
    print "Running heatMap.py as standalone script"
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
    folder = 'data/' + options.folderName + '/'
    for f in os.listdir(os.getcwd() + '/' + folder):
        if f.endswith('.dvw'):
            files.append(folder + f)

    locations = []
    for fileName in files:
        parser = Parser(fileName)
        locations = parser.getAttackInfo(team, player, attacks, locations, options.onlyKills)

    drawArcsPillow(locations)
