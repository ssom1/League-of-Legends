import pandas as pd
import os
import json

def extract_data(df_match, df_timeline, gamer_name, opposite=False):
    gamer_data =[]

    for j, match in enumerate(df_match['info'].values):
        if pd.isna(df_match['metadata'][j]):
            #print(f"No game in {j+1}th match")
            continue

        matchId = df_match['metadata'][j]['matchId']
        #print(matchId)

        timelineExist = False
        for k, timeline in enumerate(df_timeline['metadata']):
            if not pd.isna(timeline):
                if timeline['matchId'] == matchId:
                    match_timeline = df_timeline['info'][k]
                    timelineExist = True
                    #print(matchId, timeline['matchId'])
                    break

        if not timelineExist:
            #print(f"{matchId} does not exist in timeline data.")
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

        #print(check_gamer_mid, teamid, oteamid)
        if opposite:
            tmp = teamid
            teamid = oteamid
            oteamid = tmp
            #
        # 다한 사람은 solo_rank_30 밑에 있는 gamer_name 추출 코드 작성

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
                    if (event['type'] == "CHAMPION_KILL") and ('assistingParticipantIds' not in event):  # 1 vs 1 구도
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
            target_data['totalXP'] = match_timeline['frames'][-1]['participantFrames'][str(target_data['participantId'])][
                'xp']

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

            at14_target_data = {}
            match_timeline_at14 = match_timeline['frames'][:15]
            at14_kill, at14_death, at14_assist = 0, 0, 0
            at14_solo_kill, at14_solo_death = 0, 0
            for frame in match_timeline_at14:
                for event in frame['events']:
                    if (event['type'] == "CHAMPION_KILL") and ('assistingParticipantIds' not in event):
                        if (event['killerId'] == target_data['participantId']):
                            at14_solo_kill += 1
                            at14_kill += 1
                        elif (event['victimId'] == target_data['participantId']):
                            at14_solo_death += 1
                            at14_death += 1
                    elif (event['type'] == "CHAMPION_KILL"):
                        if target_data['participantId'] in event['assistingParticipantIds']:
                            at14_assist += 1
                        elif event['killerId'] == target_data['participantId']:
                            at14_kill += 1
                        elif event['victimId'] == target_data['participantId']:
                            at14_death += 1
            at14_target_data['kills'] = at14_kill
            at14_target_data['deaths'] = at14_death
            at14_target_data['assists'] = at14_assist
            at14_target_data['solokills'] = at14_solo_kill
            at14_target_data['solodeaths'] = at14_solo_death

            match_timeline_14 = match_timeline['frames'][14]
            match_timeline_14_target = match_timeline_14['participantFrames'][str(target_data['participantId'])]
            at14_target_data['gameDuration'] = match_timeline_14['timestamp'] / 1000
            at14_target_data['totalDamageDealtToChampions'] = match_timeline_14_target['damageStats'][
                'totalDamageDoneToChampions']
            at14_target_data['totalDamageTaken'] = match_timeline_14_target['damageStats']['totalDamageTaken']
            at14_target_data['totalMinionsKilled'] = match_timeline_14_target['minionsKilled']
            at14_target_data['totalCS'] = at14_target_data['totalMinionsKilled'] + match_timeline_14_target[
                'jungleMinionsKilled']
            at14_target_data['totalXP'] = match_timeline_14_target['xp']
            at14_target_data['goldEarned'] = match_timeline_14_target['totalGold']

            at14_duration = at14_target_data['gameDuration'] / 60
            at14_target_data['dpm'] = at14_target_data['totalDamageDealtToChampions'] / at14_duration
            at14_target_data['dtpm'] = at14_target_data['totalDamageTaken'] / at14_duration
            at14_target_data['dpd'] = at14_target_data['totalDamageDealtToChampions'] / (
                1 if at14_target_data['deaths'] == 0 else at14_target_data['deaths'])
            at14_target_data['dpg'] = at14_target_data['totalDamageDealtToChampions'] / at14_target_data['goldEarned']
            at14_target_data['gpm'] = at14_target_data['goldEarned'] / at14_duration
            at14_target_data['xpm'] = at14_target_data['totalXP'] / at14_duration
            at14_target_data['mpm'] = at14_target_data['totalMinionsKilled'] / at14_duration
            at14_target_data['cspm'] = at14_target_data['totalCS'] / at14_duration

            # at14와 동일한 항목으로 af14 채워보기 (힌트 : target_data에서 at14_target_data 항목을 뺀다)
            af14_target_data = {}

            af14_target_data['kills'] = target_data['kills'] - at14_target_data['kills']
            af14_target_data['deaths'] = target_data['deaths'] - at14_target_data['deaths']
            af14_target_data['assists'] = target_data['assists'] - at14_target_data['assists']
            af14_target_data['solokills'] = target_data['solokills'] - at14_target_data['solokills']
            af14_target_data['solodeaths'] = target_data['solodeaths'] - at14_target_data['solodeaths']

            af14_target_data['gameDuration'] = target_data['gameDuration'] - at14_target_data['gameDuration']
            af14_target_data['totalDamageDealtToChampions'] = target_data['totalDamageDealtToChampions'] - at14_target_data[
                'totalDamageDealtToChampions']
            af14_target_data['totalDamageTaken'] = target_data['totalDamageTaken'] - at14_target_data['totalDamageTaken']
            af14_target_data['totalMinionsKilled'] = target_data['totalMinionsKilled'] - at14_target_data[
                'totalMinionsKilled']
            af14_target_data['totalCS'] = target_data['totalCS'] - at14_target_data['totalCS']
            af14_target_data['totalXP'] = target_data['totalXP'] - at14_target_data['totalXP']
            af14_target_data['goldEarned'] = target_data['goldEarned'] - at14_target_data['goldEarned']

            af14_target_data['dpm'] = af14_target_data['totalDamageDealtToChampions'] / (
                        af14_target_data['gameDuration'] / 60)
            af14_target_data['dtpm'] = af14_target_data['totalDamageTaken'] / (af14_target_data['gameDuration'] / 60)
            af14_target_data['dpd'] = af14_target_data['totalDamageDealtToChampions'] / (
                1 if af14_target_data['deaths'] == 0 else af14_target_data['deaths'])
            af14_target_data['dpg'] = af14_target_data['totalDamageDealtToChampions'] / af14_target_data['goldEarned']
            af14_target_data['gpm'] = af14_target_data['goldEarned'] / (af14_target_data['gameDuration'] / 60)
            af14_target_data['xpm'] = af14_target_data['totalXP'] / (af14_target_data['gameDuration'] / 60)
            af14_target_data['cspm'] = af14_target_data['totalCS'] / (af14_target_data['gameDuration'] / 60)
            af14_target_data['mpm'] = af14_target_data['totalMinionsKilled'] / (af14_target_data['gameDuration'] / 60)

            target_data['at14'] = at14_target_data
            target_data['af14'] = af14_target_data
            # print(f"{j+1}번째 게임 데이터\n{target_data}")
            # print()
            gamer_data.append(target_data)
        # else:
        #     print(f"{j+1}번째 게임 제외\n 미드인지의 여부 : {check_gamer_mid}, 게임 시간 : {match['gameDuration']/60} ")

    return gamer_data

base_dir = "./solo_rank_30"

final_data = []
final_data_o = []

for gamer_folder in os.listdir(base_dir):
    #print(gamer_folder)
    gamer_name = gamer_folder.split('#')[0]
    print(gamer_name)

    match_file_name = f"{gamer_folder}_matchData.json"
    match_file_path = os.path.join(base_dir, gamer_folder, match_file_name)
    print(match_file_path)

    timeline_file_name = f"{gamer_folder}_timelineData.json"
    timeline_file_path = os.path.join(base_dir, gamer_folder, timeline_file_name)
    print(timeline_file_path)

    df_match = pd.read_json(match_file_path)
    df_timeline = pd.read_json(timeline_file_path)

    gamer_data   = extract_data(df_match, df_timeline, gamer_name)
    gamer_data_o = extract_data(df_match, df_timeline, gamer_name, opposite=True)

    data   = {}
    data_o = {}

    data['gamerName'] = gamer_name
    data['numValidGame'] = len(gamer_data)
    data['match'] = gamer_data
    final_data.append(data)

    data_o['gamerName'] = gamer_name
    data_o['numValidGame'] = len(gamer_data_o)
    data_o['match'] = gamer_data_o
    final_data_o.append(data_o)
    print(f"소환사명 : {gamer_name}, 매치 수 : {len(gamer_data)}, 상대방 매치 수 : {len(gamer_data_o)} ")

with open('extracted_full_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)

with open('extracted_full_data_o.json', 'w', encoding='utf-8') as f:
    json.dump(final_data_o, f, ensure_ascii=False, indent=4)