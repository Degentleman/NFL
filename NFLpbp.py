#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 04:20:00 2020

@author: Degentleman
"""
import pandas as pd
import numpy as np
# Create pandas DataFrame which will be used to append data to.
sampleDB = pd.DataFrame()
# Specify the range of dates to use in the sample, the files must be in your working directory.
for year in range(2020,2021):
    DB = pd.read_csv('pbp/play_by_play_{year}.csv.gz'.format(year=year), 
                           sep=",", compression='gzip', 
                           header=0, na_filter=False,
                           error_bad_lines=False,
                           low_memory=False)
    # Below is a list of columns to pass if you want the NA values changed to blanks.
    na_cols_to_check = ['posteam','defteam', 'drive',
                        'air_yards', 'yards_after_catch', 'yards_gained',
                       'cp', 'cpoe', 'ep', 'epa', 'air_epa', 
                       'yac_epa', 'comp_air_epa', 'comp_yac_epa',
                       'air_wpa', 'yac_wpa', 'comp_air_wpa', 'comp_yac_wpa',
                       'qb_epa', 'xyac_epa', 'xyac_mean_yardage', 'xyac_median_yardage', 
                       'wp', 'wpa', 'def_wp', 
                       'vegas_wp', 'home_wp', 'away_wp',
                       'score_differential', 'pass_attempt', 
                       'pass_touchdown', 'complete_pass',
                       'passer_player_name', 'passer', 'pass']
    
    DB[na_cols_to_check] = DB[na_cols_to_check].replace('NA', np.nan).fillna('')
    # All teams will be included in the sample unless you pass a list of specific teams below.
    Teams = list(np.unique(DB.posteam))
    Teams.remove('')
    
    data = []
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
                drives = np.sort(np.array(np.unique(gameDF.fixed_drive)))
                #Count unique drives per team rather than drive number in game.
                drive_counter = 1
                for drive in drives:
                    sampleDF = gameDF[(gameDF.fixed_drive == drive)]
                    attempts = len(sampleDF)
                    completions = len(sampleDF[(sampleDF.complete_pass == '1')])
                    cp = np.array(sampleDF[['cp']], dtype=float)
                    air_yards = np.array(sampleDF[['air_yards']], dtype=float)
                    yards_gained = np.array(sampleDF[['yards_gained']], dtype=float)
                    xyac_loc = np.array(sampleDF[['xyac_mean_yardage']], dtype=float)
                    cpXyac = cp*xyac_loc
                    entry = [year, Team, Opp[0], game, drive_counter, qb, attempts, completions, round(np.sum(cp),3), 
                             round(np.sum(air_yards),1),round(np.sum(yards_gained),1), round(np.sum(xyac_loc),3)
                     , round((np.sum(xyac_loc)/np.sum(cp)),3), round(np.sum(cpXyac),3)]
                    data.append(entry)
                    drive_counter += 1
                    sampleDB = pd.concat([sampleDB, sampleDF])
        print('___')
qb_perf = pd.DataFrame(data, columns=['Season', 'Team', 'Opp', 'gameID', 'Drive', 'QB', 
                                      'Att', 'Comps', 'CP_Sum', 'AirYards_Sum', 'YardsGained_Sum', 'Avg_XYAC_Sum', 'XYACperCP', 'CP*XYAC_Sum'])
# Below is a list of columns to use for output and can be changed manually to increase readability and decrease file size.
columns_to_use = ['season', 'week', 'game_id', 'game_date', 'start_time',
       'time_of_day', 'stadium_id', 'home_team', 'away_team', 'div_game',
       'play_id', 'time', 'end_clock_time', 'play_clock', 'posteam',
       'posteam_type', 'defteam', 'game_half', 'qtr', 'down', 'ydstogo',
       'yardline_100', 'goal_to_go', 'desc', 'fixed_drive', 'fixed_drive_result', 
       'drive_game_clock_start', 'drive_game_clock_end', 'series',
       'series_success', 'series_result', 'quarter_seconds_remaining',
       'half_seconds_remaining', 'game_seconds_remaining', 'pass_length',
       'pass_location', 'qb_hit', 'sack', 'complete_pass',
       'incomplete_pass', 'air_yards', 'yards_after_catch', 'yards_gained',
       'cp', 'cpoe', 'ep', 'epa', 'air_epa', 
       'yac_epa', 'comp_air_epa', 'comp_yac_epa',
       'air_wpa', 'yac_wpa', 'comp_air_wpa', 'comp_yac_wpa',
       'wp', 'wpa', 'def_wp', 'vegas_wp', 'home_wp', 'away_wp',
       'home_timeouts_remaining', 'away_timeouts_remaining',
       'total_home_score', 'total_away_score', 'posteam_score',
       'defteam_score', 'score_differential', 
       'shotgun', 'no_huddle', 'qb_dropback', 'qb_kneel', 'qb_spike', 'qb_scramble', 
       'first_down', 'third_down_converted', 'third_down_failed', 
       'fourth_down_converted', 'fourth_down_failed', 
       'no_score_prob', 'fg_prob', 'safety_prob', 'td_prob', 
       'opp_fg_prob', 'opp_safety_prob', 'opp_td_prob',
       'home_wp_post', 'away_wp_post', 'vegas_home_wp',
       'total_home_pass_epa', 'total_away_pass_epa',
       'total_home_comp_air_epa', 'total_away_comp_air_epa', 
       'total_home_comp_yac_epa', 'total_away_comp_yac_epa', 
       'total_home_raw_air_epa', 'total_away_raw_air_epa', 
       'total_home_raw_yac_epa', 'total_away_raw_yac_epa', 
       'total_home_pass_wpa', 'total_away_pass_wpa', 
       'total_home_comp_air_wpa', 'total_away_comp_air_wpa', 
       'total_home_comp_yac_wpa', 'total_away_comp_yac_wpa', 
       'total_home_raw_air_wpa', 'total_away_raw_air_wpa', 
       'total_home_raw_yac_wpa', 'total_away_raw_yac_wpa', 
       'interception', 'safety', 'penalty',
       'penalty_type', 'penalty_yards',
       'penalty_team', 'penalty_player_name',
       'touchdown', 'pass_touchdown', 'two_point_attempt', 
       'tackled_for_loss', 'solo_tackle',
       'assist_tackle', 'lateral_reception', 
       'passer_player_name', 'receiver_player_name', 'interception_player_name',
       'tackle_for_loss_1_player_name', 'tackle_for_loss_2_player_name',
       'qb_hit_1_player_name', 'qb_hit_2_player_name',
       'fumble', 'fumble_forced',
       'fumble_not_forced', 'fumble_out_of_bounds', 'fumble_lost',
       'forced_fumble_player_1_team', 'forced_fumble_player_2_team',
       'solo_tackle_1_team', 'solo_tackle_2_team',
       'assist_tackle_1_team', 'assist_tackle_2_team', 
       'assist_tackle_3_team', 'assist_tackle_4_team', 
       'pass_defense_1_player_name', 'pass_defense_2_player_name', 
       'fumbled_1_team', 'fumbled_1_player_name', 
       'fumbled_2_team', 'fumbled_2_player_name',
       'fumble_recovery_1_team', 'fumble_recovery_1_yards',
       'fumble_recovery_1_player_name', 'fumble_recovery_2_team',
       'fumble_recovery_2_yards', 'fumble_recovery_2_player_name',
       'replay_or_challenge', 'replay_or_challenge_result', 
       'end_yard_line', 
       'drive_play_count', 'drive_time_of_possession',
       'drive_first_downs', 'drive_inside20', 'drive_ended_with_score',
       'drive_quarter_start', 'drive_quarter_end',
       'drive_yards_penalized', 'drive_start_transition',
       'drive_end_transition', 'drive_start_yard_line',
       'drive_end_yard_line', 'drive_play_id_started',
       'drive_play_id_ended', 'away_score', 'home_score', 'location',
       'result', 'total', 'spread_line', 'total_line', 'passer',
       'passer_jersey_number', 'receiver', 'receiver_jersey_number',
       'qb_epa', 'xyac_epa', 'xyac_mean_yardage', 'xyac_median_yardage',
       'xyac_success', 'xyac_fd', 'home_coach', 'away_coach',
       'game_stadium', 'roof', 'weather']
# Create a new DataFrame using specified columns above.
newDF = sampleDB[columns_to_use].reset_index(drop=True)
# Parse temperature data from new DataFrame if available and convert to integer
temps = []
for i in range(len(newDF)):
    weather = newDF.iloc[i].weather
    if '°' in weather and 'n/a Temp:' not in weather:
        degree_at = weather.find('°')
        temp_at = weather.find(':')
        temp = weather[temp_at+1:degree_at]
        if temp != ' ':
            temp = int(temp)
    else:
        temp = np.nan
    temps.append(temp)
newDF = pd.concat([newDF, pd.Series(data=temps, name='temp_f')], axis=1)
#Convert NA temperature values to blank strings.
newDF.temp_f.fillna('', inplace=True)
