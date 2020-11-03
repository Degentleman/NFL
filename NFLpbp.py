#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 04:20:00 2020

@author: Degentleman
"""
import pandas as pd
import numpy as np
# Specify the year of the play-by-play data you want to load. Must be in working directory.
year = 2020
#Create pandas DataFrame from nflfastR data
DB = pd.read_csv('pbp/play_by_play_{year}.csv.gz'.format(year=year), 
                       sep=",", compression='gzip', 
                       header=0, na_filter=False,
                       error_bad_lines=False,
                       low_memory=False)
#Specify columns to fillna values, this example is mainly QB-related columns
columns = ['posteam','defteam', 'drive',
           'yards_gained', 'air_yards',
           'yards_after_catch', 'score_differential',
           'ep', 'epa', 'air_epa', 'yac_epa',
           'air_wpa', 'yac_wpa', 
           'pass_attempt', 'pass_touchdown', 'complete_pass',
           'passer_player_name', 'passer', 'pass',
           'cp', 'xyac_mean_yardage']

DB[columns] = DB[columns].replace('NA', np.nan).fillna('')
# Create a list of all teams in DB object.
Teams = list(np.unique(DB.posteam))
Teams.remove('')
#Create blank list as data object to append as the script parses through the file.
data = []
# Look at each team in the DB and their unique QB data per drive.
for Team in Teams:
    teamDF = DB[((DB.posteam == Team) | (DB.defteam == Team))]

    print(Team, year)

    passer_list = list(np.unique(teamDF[(teamDF.posteam == Team)].passer))
    if '' in passer_list:
        passer_list.remove('')
    for qb in passer_list:
        print(qb)
        qbDF = teamDF[(teamDF.passer == qb) & (teamDF['pass'] == 1) & (teamDF.xyac_mean_yardage != '')].infer_objects()
        gameIDs = np.unique(qbDF.game_id)
        for game in gameIDs:
            print(game)
            gameDF = qbDF[(qbDF.game_id == game) & (qbDF.desc != 'END GAME') & (~qbDF.posteam.isin(['NA','']))]
            Opp = np.unique(gameDF.defteam)
            drives = np.sort(np.array(np.unique(gameDF.drive),dtype=int))
            for drive in drives:
                sampleDF = gameDF[(gameDF.drive == str(drive))]
                attempts = len(sampleDF)
                completions = len(sampleDF[(sampleDF.complete_pass == '1')])
                cp = np.array(sampleDF[['cp']], dtype=float)
                xyac_loc = np.array(sampleDF[['xyac_mean_yardage']], dtype=float)
                cpXyac = cp*xyac_loc
                entry = [year, Team, Opp, game, drive, qb, attempts, completions, round(np.sum(cp),3), round(np.sum(xyac_loc),3)
                 , round((np.sum(xyac_loc)/np.sum(cp)),3), round(np.sum(cpXyac),3)]
                data.append(entry)
    print('___')
qb_perf = pd.DataFrame(data, columns=['Season', 'Team', 'Opp', 'gameID', 'Drive', 'QB', 'Att', 'Comps', 'CP_Sum', 'Avg_XYAC_Sum', 'XYACperCP', 'CP*XYAC_Sum'])
