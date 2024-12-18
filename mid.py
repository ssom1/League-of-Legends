import os
import pandas as pd
import json


def extract_data(df_match, df_timeline, gamer_name, opposite=False):
    gamer_data = []

    for j, match in enumerate(df_match['info'].values):
        if pd.isna(df_match['metadata'][j]):
            continue

        matchId = df_match['metadata'][j]['matchId']

        timelineExist = False
        for k, timeline in enumerate(df_timeline['metadata']):
            if not pd.isna(timeline):
                if timeline['matchId'] == matchId:
                    match_timeline = df_timeline['info'][k]
                    timelineExist = True
                    break

        if not timelineExist:
            continue

        check_gamer_mid = False
        teamid = -1
        oteamid = -1

        for pid, participant in enumerate(match['participants']):
            if participant['riotIdGameName'] == gamer_name:
                if participant['teamPosition'] == "MIDDLE":
                    check_gamer_mid = True
                    teamid = pid
            else:
                if participant['teamPosition'] == "MIDDLE":
                    oteamid = pid

        if opposite:
            tmp = teamid
            teamid = oteamid
            oteamid = tmp

        target_data = {}
        if check_gamer_mid and match['gameDuration'] > 1200:
            match_p = match['participants'][teamid]
            match_o = match['participants'][oteamid]
            target_data["riotIdGameName"] = match_p['riotIdGameName']
            target_data["matchId"] = df_match['metadata'][j]['matchId']
            target_data["gameCreation"] = match['gameCreation']
            target_data["gameDuration"] = match_p['challenges']['gameLength']
            target_data["participantId"] = match_p['participantId']
            target_data["opponentpId"] = match_o['participantId']
            target_data["teamId"] = match_p['teamId']
            target_data["teamPosition"] = match_p['teamPosition']
            target_data["win"] = match_p['win']

            target_data['kda'] = match_p['challenges']['kda']
            target_data['kills'] = match_p['kills']
            target_data['deaths'] = match_p['deaths']
            target_data['assists'] = match_p['assists']

            solo_kill, solo_death = 0, 0
            for frame in match_timeline['frames']:
                for event in frame['events']:
                    if (event['type'] == "CHAMPION_KILL") and ('assistingParticipantIds' not in event):
                        if (event['killerId'] == target_data['participantId']):
                            solo_kill += 1
                        elif (event['victimId'] == target_data['participantId']):
                            solo_death += 1

            target_data['solokills'] = solo_kill
            target_data['solodeaths'] = solo_death

            target_data['totalDamageDealtToChampions'] = match_p['totalDamageDealtToChampions']
            target_data['totalDamageTaken'] = match_p['totalDamageTaken']
            target_data['totalMinionsKilled'] = match_p['totalMinionsKilled']
            target_data['totalCS'] = target_data['totalMinionsKilled'] + match_p['totalEnemyJungleMinionsKilled']
            target_data['goldEarned'] = match_p['goldEarned']
            target_data['totalXP'] = \
            match_timeline['frames'][-1]['participantFrames'][str(target_data['participantId'])]['xp']

            duration = target_data['gameDuration'] / 60
            target_data['dpm'] = target_data['totalDamageDealtToChampions'] / duration
            target_data['dtpm'] = target_data['totalDamageTaken'] / duration
            target_data['mpm'] = target_data['totalMinionsKilled'] / duration
            target_data['cspm'] = target_data['totalCS'] / duration
            target_data['xpm'] = target_data['totalXP'] / duration
            target_data['gpm'] = target_data['goldEarned'] / duration
            target_data['dpd'] = target_data['totalDamageDealtToChampions'] / (
                1 if target_data['deaths'] == 0 else target_data['deaths'])
            target_data['dpg'] = target_data['totalDamageDealtToChampions'] / target_data['goldEarned']

            gamer_data.append(target_data)

    return gamer_data


def save_as_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


# 기본 디렉토리 설정
base_dir = "./solo_rank_30"

final_data = []

for gamer_folder in os.listdir(base_dir):
    gamer_name = gamer_folder.split('#')[0]
    match_file_name = f"{gamer_folder}_matchData.json"
    match_file_path = os.path.join(base_dir, gamer_folder, match_file_name)
    timeline_file_name = f"{gamer_folder}_timelineData.json"
    timeline_file_path = os.path.join(base_dir, gamer_folder, timeline_file_name)

    df_match = pd.read_json(match_file_path)
    df_timeline = pd.read_json(timeline_file_path)

    gamer_data = extract_data(df_match, df_timeline, gamer_name)

    data = {}
    data['gamerName'] = gamer_name
    data['numValidGame'] = len(gamer_data)
    data['match'] = gamer_data
    final_data.append(data)

    print(f"소환사명 : {gamer_name}, 매치 수 : {len(gamer_data)}")

# 데이터를 JSON 형식으로 저장
save_as_json(final_data, 'extracted_midlaner_data.json')
