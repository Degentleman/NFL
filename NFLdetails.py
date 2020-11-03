#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 04:20:00 2020

@author: Degentleman
"""
import pandas as pd
import numpy as np
for year in range(2020,2021):
    SCORES = pd.DataFrame()
    print('____')
    print(year)
    DB = pd.read_csv('pbp/play_by_play_{year}.csv.gz'.format(year=year), 
                           sep=",", compression='gzip', 
                           header=0, na_filter=False,
                           error_bad_lines=False,
                           low_memory=False)
    # Add the columns you would like to include from the original play-by-play file in the details list below.
    details = ['season', 'game_id', 'week',
        'home_team', 'away_team', 'div_game', 'qtr', 'drive',
        'game_seconds_remaining', 'yardline_100',
        'posteam', 'posteam_type', 'defteam',
        'posteam_score', 'defteam_score', 'score_differential',
        'total_home_score', 'total_away_score', 'ha_differential', 'curr_total',
        'home_score', 'away_score', 'result', 'total',
    'spread_line','total_line', 'desc']
    # Fill NA values in scoring with zeros, which assumes NA value is because no scoring has occured.
    columns = ['posteam_score', 'defteam_score', 'score_differential']
    DB[columns] = DB[columns].replace('NA', np.nan).fillna(0)
    gameIDs = np.unique(DB.game_id)
    #For each game where the team with the ball is known, take the first play of the drive and evaluate current score.
    for game in gameIDs:
        print(game)
        gameDF = DB[(DB.game_id == game) & (DB.desc != 'END GAME') & (~DB.posteam.isin(['NA','']))]
        drives = np.unique(gameDF.drive)
        for drive in drives:
            first_play = np.min(gameDF[(gameDF.drive == drive)].play_id)
            row = gameDF[(gameDF.play_id == first_play)]
            row = row.assign(curr_total = lambda x: row.total_home_score + row.total_away_score)
            row = row.assign(ha_differential = lambda x: row.total_home_score - row.total_away_score)
            # Using list selection to return first instance of duplicate play id
            SCORES = pd.concat([SCORES, row.iloc[[0]][details]])
    print('Results from '+str(year)+' are done!')
    # Save CSV of details to current working directory.
    SCORES.to_csv('NFL '+str(year)+' Quarter and Drive Scoring DF.csv', index=False)
