from riotwatcher import LolWatcher
from dotenv import load_dotenv
import os

def setup_env():
    load_dotenv('../../config.env')
    api_key = "RGAPI-b8607081-dd4c-48b7-bc0f-6c6f27544678"
    lol_watcher = LolWatcher(api_key)
    del(api_key)
    return lol_watcher

lol_watcher = setup_env()

# PLAYER PARAMETERS
player_name = 'Sett on me Yuumi'
num_matches_data = 10
player_region = 'NA1'.lower()
player_routing = 'americas'

try:
    summoner = lol_watcher.summoner.by_name(player_region, player_name)
    match_history = lol_watcher.match.matchlist_by_puuid(region=player_routing, puuid=summoner['puuid'],
                                                        queue=420,
                                                        start=0, count=num_matches_data)

    print('Game times=')
    for match_id in match_history:
        match_data = lol_watcher.match.by_id(region=player_routing, match_id=match_id)
        game_time = match_data['info']['gameDuration']
        print(f"Match ID: {match_id}, Game Time: {game_time}")

    print('Total Gold Obtained in Each Game:')
    for match_id in match_history:
        try:
            match_data = lol_watcher.match.by_id(region=player_routing, match_id=match_id)
            print(f"Match ID: {match_id}")
            for participant in match_data['info']['participants']:
                print(f"Participant ID: {participant['participantId']}, Gold Earned: {participant['goldEarned']}")
        except Exception as e:
            print(f"Error fetching data for Match ID: {match_id}, Error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
