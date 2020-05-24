import blizzard_api_caller as bapi
import configparser
import wget
import os
import gzip
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup, SoupStrainer
import httplib2
import xlrd
import csv
import glob
from datetime import datetime


# Import keys and tokens
f_config = 'config.ini'
config = configparser.ConfigParser()
config.read(f_config)
blizzard_key = config.get('KEYS', 'blizzard')
blizzard_secret = config.get('KEYS', 'blizzard_secret')
access_token = bapi.get_access_token (blizzard_key, blizzard_secret)


# Get achievement Data
locale = 'en_US'
namespace = 'static-us'


# Get Blizzard Achievements
#wow_achievements = bapi.get_wow_achievement_list (namespace, locale)
#wow_achievements.to_csv('wow_achievements.csv')

#starcraft_achievements = bapi.get_starcraft_achievements (locale, access_token)
#starcraft_achievements = bapi.unpack_json(starcraft_achievements)
#starcraft_achievements = bapi.explore_starcraft_achievements(starcraft_achievements)
#starcraft_achievements.to_csv('starcraft_achievements.csv')


# Get player ranks

dir_save = 'wowprogress_reports'

def get_wowprogress_rank_list(rank_list_name, locale, base_url,df):
    """Downloads guild rankings for each realm provided"""
    url = base_url + rank_list_name
    tar_file = wget.download(url)


def unpack_wowprogress_guild_ranks():
    """Reads all the .gz files in the current working directory and extracts the
    data as JSON. Data is parsed and collated into a single dataframe."""
    files = os.listdir()
    df = pd.DataFrame()
    for tarfile in files:
        print("reading: " + tarfile)
        try:
            splits = tarfile.split('_tier')
            realm = splits[0]
            tier = splits[1].split('.json')[0]
            tmp = pd.DataFrame()
            with gzip.open(tarfile, 'rb') as f:
                json_text = f.read()
            unpacked = bapi.unpack_json(json_text)
            for guild in unpacked:
                tmp = tmp.append(guild, ignore_index=True)
                tmp['tier'] = tier
                tmp['region'] = locale
                tmp['realm'] = realm
                df = df.append(tmp, ignore_index=True)
        except:
            print('Could not read: ' + tarfile + '. Moving on...')
            continue
    df.to_csv('wow_guild_rankings.csv')
    #os.remove(tarfile)
    return df


def get_wowprogress_by_realm (locale, namespace,base_url):
    """Gets the realm list from the Blizzard API then scrapes the wowprogress.com website
    for guild rankings"""
    namespace = 'dynamic-us'
    realm_names, realm_ids, realm_slugs = bapi.get_wow_realms_list(namespace, locale)
    http = httplib2.Http()
    status, response = http.request(base_url)
    df = pd.DataFrame()
    for link in BeautifulSoup(response, parse_only=SoupStrainer('a'), features="lxml"):
        if link.has_attr('href'):
            link = str(link).split('="')[1].split('">')[0]
            for realm in realm_slugs:
                if realm in link and 'us_' in link[:3]:
                    print('Downloading: ' + link)
                    get_wowprogress_rank_list(link, locale, base_url,df)

base_url = 'https://www.wowprogress.com/export/ranks/'
os.chdir('wowprogress_reports')

#get_wowprogress_by_realm(locale, namespace, base_url)
#wow_guilds = unpack_wowprogress_guild_ranks()
#wow_players = bapi.get_wow_guild_rosters('wow_guild_rankings.csv')


def xlsx_to_csv (dir_xlsx):
    os.chdir(dir_xlsx)
    files = os.listdir()
    xlsx_files = glob.glob('*.{}'.format('xlsx'))
    for f in xlsx_files:
        wb = xlrd.open_workbook(f)
        sh = wb.sheet_by_name('Sheet1')
        csv_name = f.replace('xlsx','csv')
        f_csv = open(csv_name, 'w', encoding='utf8')
        wr = csv.writer(f_csv, quoting=csv.QUOTE_ALL)
        for rownum in range(sh.nrows):
            wr.writerow(sh.row_values(rownum))
        f_csv.close()
#lsx_to_csv (dir_dataset)

def dataforazeroth (dir_dataset):
    date_cols = []
    os.chdir(dir_dataset)
    files = os.listdir()
    csv_files = glob.glob('*.{}'.format('csv'))
    df = pd.DataFrame()
    for f in csv_files:
        temp = pd.read_csv(f)
        temp.columns = ['ranking','leaderboard','player','guild','realm','score']
        temp.leaderboard = f.split('wow_')[1].split('.csv')[0]
        df = df.append(temp[['ranking','leaderboard','player','guild','realm']], ignore_index=True)
    df.to_csv('../dataforazeroth_complete_dataset.csv')
    return df

dir_dataset = '/Users/haleyspeed/Docs/insight/datasets/dataforazeroth_datasets'
dataforazeroth_set = dataforazeroth (dir_dataset)




#TODO: Steam Achievements
#TODO: Xbox Achievements
#TODO: Classify based on play type
#TODO: Sentiment Analysis of Achievement
#TODO: Leaderboard Achievements