import os
import sys
import pygame
# import heatmap as hm
from pygame.locals import *
from PIL import Image, ImageDraw, ImageFont
from optparse import OptionParser

from parser import Parser
from helpers import Color


def draw_arcs(locations, x_scale=4, y_scale=8):
    pygame.display.init()
    screen = pygame.display.set_mode([100 * x_scale, 100 * y_scale])
    # caption = "HeatMap: #" + str(info['number']) + " " + info['name'] + " (" + info['team'] + ")"
    pygame.display.set_caption('Volleymetrics HeatMap')

    screen.fill(Color.black)

    # Draw court outlines
    outer_boundary = [(0,0), (0, 99), (99, 99), (99, 0)]
    court_boundary = [(10, 10), (10, 90), (90, 90), (90, 10)]
    pygame.draw.lines(screen, Color.white, True, scale_up(outer_boundary, x_scale, y_scale), 3)
    pygame.draw.lines(screen, Color.white, True, scale_up(court_boundary, x_scale, y_scale), 3)
    # Draw net
    pygame.draw.line(screen, Color.white, (10 * x_scale, 50 * y_scale), (90 * x_scale, 50 * y_scale), 7)

    for location in locations:
        start_x, start_y, end_x, end_y = location['arc']
        start = (start_x * x_scale, start_y * y_scale)
        end = (end_x * x_scale, end_y * y_scale)
        color = color_by_rating(location['rating'])
        pygame.draw.line(screen, color, start, end)
        pygame.draw.circle(screen, color, end, 3)

    pygame.display.update()
    output_url = 'data/output_images/output.bmp'
    pygame.image.save(screen, output_url)

    # pygame.display.quit()
    # pygame.quit()

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                pygame.display.iconify()
                running = False

    return output_url


# Disable for now while deploying to Heroku
# def draw_heat_map(locations, x_scale=4, y_scale=8):
#     ends = []
#     for location in locations:
#         start_x, start_y, end_x, end_y = location['arc']
#         end = (end_x * x_scale, end_y * y_scale)
#         ends.append(end)
#     h = hm.Heatmap()
#     area = ((0, 0), (99 * x_scale, 99 * y_scale))
#     h.heatmap(ends, dotsize=50, area=area).save('data/output_images/output.png')


def draw_arcs_pillow(locations, output_url, top_caption=None, bottom_caption=None, x_scale=4, y_scale=8):
    im = Image.open('static/images/base_img.png')

    draw = ImageDraw.Draw(im)
    radius = 3
    for location in locations:
        start_x, start_y, end_x, end_y = location['arc']
        start = (start_x * x_scale, start_y * y_scale)
        end = (end_x * x_scale, end_y * y_scale)
        color = color_by_rating(location['rating'])
        draw.line([start, end], fill=color, width=3)
        draw.ellipse([end[0] - radius, end[1] - radius, end[0] + radius, end[1] + radius], fill=color, outline=color)

    width, height = im.size

    font_size = 10
    font = ImageFont.truetype(font='static/fonts/arial.ttf', size=font_size)
    if top_caption is not None:
        draw.text((20, 20), top_caption, font=font, fill=Color.white)
    if bottom_caption is not None:
        draw.text((20, height - (20 + font_size)), bottom_caption, font=font, fill=Color.white)

    im.save(output_url, 'PNG')
    del draw

    return {'url': output_url, 'width': width, 'height': height}


def scale_up(locations, scale_x, scale_y):
    new_list = []
    for item in locations:
        new_list.append((item[0] * scale_x, item[1] * scale_y))
    return new_list


def color_by_rating(rating):
    if rating == '#':
        return Color.green
    elif rating == '=':
        return Color.red
    else:
        return Color.yellow


def read_commands(argv):
    parser = OptionParser()
    parser.add_option('-f', '--folder', dest='folder_name', help='draw heat map from folder', default='testdata')
    parser.add_option('-n', '--number', dest='player_number', help='playerNumber to analyze')
    parser.add_option('-t', '--team', dest='team_number', help='Volleymetrics teamNumber for team the player is on')
    parser.add_option('-a', '--attacks', dest='attack_combos', help='attackCombos to search for and display', default='all')
    parser.add_option('-k', action='store_true', dest='only_kills', default=False)
    (options, args) = parser.parse_args(argv)
    return options


if __name__ == '__main__':
    print 'Running heat_map.py as standalone script'
    options = read_commands(sys.argv[1:])

    team = int(options.team_number)
    player = int(options.player_number)

    # Allow option of "all" attacks to be displayed
    if options.attack_combos == 'all':
        attacks = ['ALL']
    else:
        attacks = [x.upper() for x in options.attack_combos.split(',')]

    # Allow option of "all" files being passed in
    files = []
    folder = 'data/' + options.folder_name + '/'
    for f in os.listdir(os.getcwd() + '/' + folder):
        if f.endswith('.dvw'):
            files.append(folder + f)

    locations = []
    for file_name in files:
        parser = Parser(file_name)
        locations = parser.get_attack_info(team, player, attacks, locations, options.only_kills)

    draw_arcs_pillow(locations)
