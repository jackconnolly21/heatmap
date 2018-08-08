import os
import datastore
import helpers

engine = helpers.get_db_engine(mode='prod')

team_list = [
    ('main/app/data/ncaam_codes/', 'NCAA Mens'),
    ('main/app/data/ncaaw_codes/teams/', 'NCAA Womens')
    ]

all_ids = set([row['id'] for row in datastore.get_all_teams(engine)])

for teams_folder, league in team_list:
    for f in os.listdir(teams_folder):
        team_num = int(f.split(" ")[0])
        team_name = " ".join(f.split(" ")[1:])[:-3]

        row_dict = {'id': team_num, 'teamname': team_name, 'league': league}

        if team_num in all_ids:
            print "Duplicate ID:", team_num
        else:
            datastore.upload_team(engine, row_dict)
            print "Uploaded row", row_dict
            all_ids.add(team_num)
