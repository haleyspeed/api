import requests
import configparser
import json
import pandas as pd
from datetime import datetime

f_config = 'config.ini'
config = configparser.ConfigParser()
config.read(f_config)
blizzard_key = config.get('KEYS', 'blizzard')
blizzard_secret = config.get('KEYS', 'blizzard_secret')

def unpack_json(txt):
    unpacked = json.loads(txt)
    return unpacked

# Get access token
r = requests.post('https://us.battle.net/oauth/token', data={'grant_type': 'client_credentials'},
                  auth=(blizzard_key, blizzard_secret))
unpacked = unpack_json(r.text)
access_token = unpacked['access_token']
print(access_token)

# Get achievement Data
locale = 'en_US'
namespace = 'static-us'

def get_achievement_category(namespace, locale):
    directory = 'data/wow/achievement-category/index'
    url = 'https://us.api.blizzard.com/'+ directory +'?namespace='+ namespace + \
      '&locale=' + locale + '&access_token='+ access_token
    r = requests.get (url)
    unpacked = unpack_json (r.text)
    df = pd.DataFrame()
    for keys, values in unpacked.items():
        tmp = pd.DataFrame()
        for category in values:
            if isinstance(category, dict):
                for keys, values in category.items():
                    tmp[keys] = values
                df = df.append(tmp)
    return df


def get_achievement_list (namespace, locale):
    directory = 'data/wow/achievement/index'
    url = 'https://us.api.blizzard.com/'+ directory +'?namespace='+ namespace + \
      '&locale=' + locale + '&access_token='+ access_token
    r = requests.get (url)
    unpacked = unpack_json (r.text)
    df = pd.DataFrame()
    for keys, values in unpacked.items():
        tmp = pd.DataFrame()
        for category in values:
            if isinstance(category, dict):
                for keys, values in category.items():
                    tmp[keys] = values
                df = df.append(tmp)
    return df

def get_mythic_dungeon_leaderboard_instances (realm_id, namespace, locale):
    """Returns an index of Mythic Keystone Leaderboard dungeon instances for a connected realm"""
    directory = 'data/wow/connected-realm/' + str(realm_id) + '/mythic-leaderboard/index'
    url = 'https://us.api.blizzard.com/' + directory + '?namespace=' + namespace + \
          '&locale=' + locale + '&access_token=' + access_token
    r = requests.get(url)
    unpacked = unpack_json(r.text)
    current_leaderboards = unpacked['current_leaderboards']
    df = pd.DataFrame()
    for leaderboard in current_leaderboards:
        df = df.append(leaderboard, ignore_index=True)
    return df


def get_mythic_keystone_dungeon_leaderboard(realm_id,namespace,locale, instance, period):
    directory = 'data/wow/connected-realm/'
    url = 'https://us.api.blizzard.com/' + directory + str(realm_id) + '/mythic-leaderboard/' + str(instance) + \
          '/period/' + str(period) + '?namespace=' + namespace + \
          '&locale=' + locale + '&access_token=' + access_token
    r = requests.get(url)
    unpacked = unpack_json(r.text)
    features = ['period', 'period_start_timestamp', 'period_end_timestamp', 'map_challenge_mode_id',
               'map_challenge_mode_name', 'map_name', 'map_id', 'connected_realm', 'keystone_affix_names',
               'keystone_affix_ids', 'keystone_affix_starting_level', 'leading_groups_ranking',
               'leading_groups_duration', 'leading_groups_completed_timestamp', 'leading_groups_keystone_level',
               'member_name, member_id', 'member_realm_id', 'member_realm_slug', 'member_faction',
               'member_specialization']
    df = pd.DataFrame()
    values = list(unpacked.values())
    map = values[1]
    period = values[2]
    period_start_timestamp  = values[3]
    period_end_timestamp  = values[4]
    map_challenge_mode_id  = values[8]
    map_challenge_mode_name = values[9]
    map_name = map['name']
    map_id = map['id']

    connected_realm = values[5]
    connected_realm = connected_realm['href']

    keystone_affixes = values[7]
    keystone_affix_names = []
    keystone_affix_ids = []
    keystone_affix_starting_level = []
    for affix in keystone_affixes:
        keystone_affix_names.append(affix['keystone_affix']['name'])
        keystone_affix_ids.append(affix['keystone_affix']['id'])
        keystone_affix_starting_level.append(affix['starting_level'])

    leading_groups = values[6]
    for leading_group in leading_groups:
        leading_groups_ranking = leading_group['ranking']
        leading_groups_duration = leading_group['duration']
        leading_groups_completed_timestamp = leading_group['completed_timestamp']
        leading_groups_keystone_level = leading_group['keystone_level']
        members = leading_group['members']
        for member in members:
            member_name = member['profile']['name']
            member_id = member['profile']['id']
            member_realm_id = member['profile']['realm']['id']
            member_realm_slug =  member['profile']['realm']['slug']
            member_faction = member['faction']['type']
            member_specialization = member['specialization']['id']
            tmp = {'period':period,
                    'period_start_timestamp':period_start_timestamp,
                   'period_end_timestamp':period_end_timestamp,
                   'map_challenge_mode_id':map_challenge_mode_id,
                   'map_challenge_mode_name':map_challenge_mode_name,
                   'map_name':map_name,
                   'map_id':map_id,
                   'connected_realm':connected_realm,
                   'keystone_affix_names':keystone_affix_names,
                   'keystone_affix_ids':keystone_affix_ids,
                   'keystone_affix_starting_level':keystone_affix_starting_level,
                   'leading_groups_ranking':leading_groups_ranking,
                   'leading_groups_duration':leading_groups_duration,
                   'leading_groups_completed_timestamp':leading_groups_completed_timestamp,
                   'leading_groups_keystone_level':leading_groups_keystone_level,
                   'member_name':member_name,
                   'member_id':member_id,
                   'member_realm_id':member_realm_id,
                   'member_realm_slug':member_realm_slug,
                   'member_faction':member_faction,
                   'member_specialization':member_specialization}
        df = df.append(tmp, ignore_index=True)
    return (df)

# Example API calls
#print(get_achievement_category (namespace, locale).head())
#print(get_achievement_list (namespace, locale).head())

# Loop for realm, locale (country), and period to get a full dataset
# Look at how the rankings change over time for players and teams
# Effect of player in certain roles
# Effect of affixes and difficulty on team and individual performance
namespace = 'dynamic-us'
mythic_keystone_dungeon_leaderboard_instances = get_mythic_dungeon_leaderboard_instances (11, namespace, locale)
mythic_keystone_dungeon_leaderboard = get_mythic_keystone_leaderboard(11, namespace, locale, 197, 641)

#TODO: Get player profiles: achievements
#TODO: Mythic raid dataset
#TODO: MDI dataset
#TODO: Esports raid dataset
#TODO: League of Legends Dataset
#TODO: Starcraft2 Dataset
#ToDO: Call of duty dataset
