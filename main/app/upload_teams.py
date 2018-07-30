import os
import datastore
import helpers

engine = helpers.get_db_engine()

team_list = [('main/app/data/ncaam_codes/', 'NCAA Mens'),
             ('main/app/data/ncaaw_codes/teams/', 'NCAA Womens')]

for teams_folder, league in team_list:
    for f in os.listdir(teams_folder):
        team_num = f.split(" ")[0]
        team_name = " ".join(f.split(" ")[1:])[:-3]

        row_dict = {'id': team_num, 'teamname': team_name, 'league': league}

        # datastore.upload_team(engine, row_dict)
        print "Uploaded row", row_dict

