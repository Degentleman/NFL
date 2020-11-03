#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 14:11:27 2020

@author: Degentleman
"""
import pandas as pd
import numpy as np
year = 2020
DB = pd.read_csv('pbp/play_by_play_{year}.csv.gz'.format(year=year), 
                       sep=",", compression='gzip', 
                       header=0, na_filter=False,
                       error_bad_lines=False,
                       low_memory=False)

columns = ['posteam','defteam',
           'yards_gained', 'air_yards',
           'yards_after_catch', 'score_differential',
           'ep', 'epa', 'air_epa', 'yac_epa',
           'air_wpa', 'yac_wpa',
           'pass_attempt', 'pass_touchdown', 'complete_pass',
           'passer_player_name',
           'cp', 'xyac_mean_yardage']

DB[columns] = DB[columns].replace('NA', np.nan).fillna('')

'''

DF = pd.DataFrame()
search_term = 'Possessions Summary'
for f in os.listdir('.'):
    if search_term in f and len (f) == 56:
        print(f)
        x = pd.read_csv(f, converters={'gameID':str,
                                                    'teamID':str,
                                                    'oppID':str})
        DF = pd.concat([DF, x], axis=0, ignore_index=False)
'''
Teams = list(np.unique(DB.posteam))
Teams.remove('')
data = []
for Team in Teams:
    teamDF = DB[((DB.posteam == Team) | (DB.defteam == Team))]

    print(Team, year)

    qb_list = list(np.unique(teamDF[(teamDF.posteam == Team)].passer_player_name))
    if '' in qb_list:
        qb_list.remove('')
    for qb in qb_list:
        print(qb)
        qbDF = teamDF[(teamDF.passer_player_name == qb) & (teamDF.pass_attempt == '1') & (teamDF.cp != '') & (teamDF.xyac_mean_yardage != '')].infer_objects()
        gameIDs = np.unique(qbDF.game_id)
        for game in gameIDs:
            sampleDF = qbDF[(qbDF.game_id == game)]
            attempts = len(sampleDF)
            completions = len(sampleDF[(sampleDF.complete_pass == '1')])
            cp = np.array(sampleDF[['cp']], dtype=float)
            xyac_loc = np.array(sampleDF[['xyac_mean_yardage']], dtype=float)
            cpXyac = cp*xyac_loc
            entry = [year, Team, game, qb, attempts, completions, round(np.sum(cp),3), round(np.sum(xyac_loc),3)
                 , round((np.sum(xyac_loc)/np.sum(cp)),3), round(np.sum(cpXyac),3)]

            data.append(entry)
    print('___')
qb_perf = pd.DataFrame(data, columns=['Season', 'Team', 'gameID', 'QB', 'Att', 'Comps', 'CP_Sum', 'Avg_XYAC_Sum', 'XYACperCP', 'CP*XYAC_Sum'])