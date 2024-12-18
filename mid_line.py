import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# JSON 파일 로드
file_path = 'extracted_full_data.json'
with open(file_path, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 데이터 처리
columns_to_use = ['gamerName', 'KillAt14', 'cspm_at14', 'KillAf14', 'cspm_af14', 'Win']
data_list = []

for summoner in raw_data:
    gamer_name = summoner['gamerName']
    for match in summoner['match']:
        data_list.append({
            'gamerName': gamer_name,
            'KillAt14': match['at14']['kills'],
            'cspm_at14': match['at14']['cspm'],
            'KillAf14': match['af14']['kills'],
            'cspm_af14': match['af14']['cspm'],
            'Win': int(match['win'])
        })

# 데이터프레임 생성
data = pd.DataFrame(data_list)

# 소환사명 필터링 (필요시 제외 가능)
selected_summoners = [
    "龙宫公主", "너는 나의 자존심", "덕소리", "도파민", "땅굴팀 미드", "리 칠", "리하우급 누누", "마리골드", "무적코털 보보보",
    "베인의 여왕 류하린", "소나기", "소울이강철멘탈1", "쏘 테", "안강최", "우와앙", "위너팀 Mid", "위너팀 미드2",
    "위너팀 주지태", "위너팀 판테온", "으 악", "이쁜 오르트구름", "인스타팔로우좀요", "제우스팀 에코", "제우스팀 제리",
    "쫀 지", "쾌감절정능욕매끈야들가련청순발육", "탈리얌", "포뇨의 눈", "황혼우주자야"
]

# 필터링된 데이터프레임
data = data[data['gamerName'].isin(selected_summoners)]

# 필요한 열들을 숫자형으로 변환 (문자열 값은 NaN 처리)
numeric_columns = ['KillAt14', 'KillAf14', 'cspm_at14', 'cspm_af14']
data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')

# NaN 값 제거 (숫자로 변환할 수 없었던 값)
data = data.dropna(subset=numeric_columns)

# 승리 여부에 따른 라인전 전/후 Kill과 cspm 평균 계산
grouped_data = data.groupby('Win')[numeric_columns].mean()

# 시각화
plt.figure(figsize=(14, 8))

# Kill 비교
plt.subplot(2, 1, 1)
grouped_data[['KillAt14', 'KillAf14']].plot(kind='bar', ax=plt.gca(), color=['#1f77b4', '#ff7f0e'])
plt.title('Comparison of Kills Before and After Lane Phase by Win/Loss')
plt.ylabel('Average Kills')
plt.xticks(ticks=[0, 1], labels=['Loss', 'Win'], rotation=0)
plt.legend(['KillAt14', 'KillAf14'])

# cspm 비교
plt.subplot(2, 1, 2)
grouped_data[['cspm_at14', 'cspm_af14']].plot(kind='bar', ax=plt.gca(), color=['#2ca02c', '#d62728'])
plt.title('Comparison of CSPM Before and After Lane Phase by Win/Loss')
plt.ylabel('Average CSPM')
plt.xticks(ticks=[0, 1], labels=['Loss', 'Win'], rotation=0)
plt.legend(['cspm_at14', 'cspm_af14'])

plt.tight_layout()
plt.show()
