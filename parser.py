import csv

class Parser:

    def __init__(self, filename='CU-PENN.dvw'):
        self.fileSections = self.readFile(filename)
        self.homeTeam, self.awayTeam = self.getHomeAndAway()
        self.homeRoster = self.readRoster(self.fileSections['[3PLAYERS-H]'])
        self.awayRoster = self.readRoster(self.fileSections['[3PLAYERS-V]'])

    def readFile(self, filename='CU-PENN.dvw'):
        fileSections = {}
        with open('data/' + filename, 'rb') as dvwfile:
            reader = csv.reader(dvwfile, delimiter=';', quotechar='|')
            currentSection = ''
            for row in reader:
                try:
                    if row[0][0] == '[':
                        fileSections[row[0]] = []
                        currentSection = row[0]
                    else:
                        fileSections[currentSection].append(row)
                except:
                    fileSections[currentSection].append(row)
        return fileSections

    def getHomeAndAway(self):
        teams = self.fileSections['[3TEAMS]']
        homeTeam = (teams[0][0], teams[0][1])
        awayTeam = (teams[1][0], teams[1][1])
        return (homeTeam, awayTeam)

    def readRoster(self, rosterInfo):
        roster = {}
        for player in rosterInfo:
            number = int(player[1])
            firstName = player[10]
            lastName = player[9]
            name = str(firstName) + ' ' + str(lastName)
            roster[number] = name
        return roster

    def readCombos(self):
        combos = self.fileSections['[3ATTACKCOMBINATION]']
        comboList = {}
        for combo in combos:
            code = combo[0]
            name = combo[4]
            location = combo[7]
            comboList[code] = (name, location)
        return comboList

    def getAttackInfo(self, team, player, attacks, list):

        gameInfo = self.fileSections['[3SCOUT]']

        if str(team) == self.homeTeam[0]:
            key = '*'
        elif str(team) == self.awayTeam[0]:
            key = 'a'
        else:
            return list

        key += str(player)
        key += 'A'

        for event in gameInfo:
            info = event[0]
            if info[:4] == key:
                if info[6:8] in attacks or attacks[0] == 'ALL':
                    start = event[4]
                    end = event[6]
                    rating = info[5]
                    arc = ((int(start[:2]), int(start[2:])), (int(end[:2]), int(end[2:])))
                    list.append((arc, rating))

        return list

    def getInfo(self, team, player):

        if str(team) == self.homeTeam[0]:
            playerName = self.homeRoster[player]
            teamName = self.homeTeam[1]
        else:
            playerName = self.awayRoster[player]
            teamName = self.awayTeam[1]

        info = {
            'name': playerName,
            'number': player,
            'team': teamName
        }

        return info
