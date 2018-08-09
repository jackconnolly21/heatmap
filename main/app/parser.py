import csv


class Parser:

    def __init__(self, filename):
        self.file_sections = self.read_file(filename)
        self.home_team, self.away_team = self.get_home_and_away()
        self.home_roster = self.read_roster(self.file_sections['[3PLAYERS-H]'])
        self.away_roster = self.read_roster(self.file_sections['[3PLAYERS-V]'])

    def read_file(self, filename):
        file_sections = {}
        with open(filename, 'rb') as dvwfile:
            reader = csv.reader(dvwfile, delimiter=';', quotechar='|')
            current_section = ''
            for row in reader:
                try:
                    if row[0][0] == '[':
                        file_sections[row[0]] = []
                        current_section = row[0]
                    else:
                        file_sections[current_section].append(row)
                except:
                    file_sections[current_section].append(row)
        return file_sections

    def get_home_and_away(self):
        teams = self.file_sections['[3TEAMS]']
        home_team = (teams[0][0], teams[0][1])
        away_team = (teams[1][0], teams[1][1])
        return home_team, away_team

    def read_roster(self, roster_info):
        roster = {}
        for player in roster_info:
            number = int(player[1])
            first_name = player[10]
            last_name = player[9]
            name = str(first_name) + ' ' + str(last_name)
            roster[number] = name
        return roster

    def read_combos(self):
        combos = self.file_sections['[3ATTACKCOMBINATION]']
        combo_list = {}
        for combo in combos:
            code = combo[0]
            name = combo[4]
            location = combo[7]
            combo_list[code] = (name, location)
        return combo_list

    def get_attack_info(self, team, player, attacks, only_kills=False):
        locations = []
        game_info = self.file_sections['[3SCOUT]']

        if str(team) == self.home_team[0]:
            key = '*'
        elif str(team) == self.away_team[0]:
            key = 'a'
        else:
            return locations

        # pad with a leading zero if single digit number
        key += "%02d" % player
        key += 'A'

        for event in game_info:
            info = event[0]
            if info[:4] == key:
                if info[6:8] in attacks or attacks[0] == 'ALL':
                    start = event[4]
                    end = event[6]
                    rating = info[5]
                    if not only_kills or rating == '#':
                        arc = (100 - int(start[2:]), int(start[:2]), 100 - int(end[2:]), int(end[:2]))
                        locations.append( {'arc': arc, 'rating': rating} )

        return locations

    def get_info(self, team, player):

        if str(team) == self.home_team[0]:
            player_name = self.home_roster[player]
            team_name = self.home_team[1]
        else:
            player_name = self.away_roster[player]
            team_name = self.away_team[1]

        info = {
            'name': player_name,
            'number': player,
            'team': team_name
        }

        return info
