from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import os

# pandas 이용해서 json파일로 데이터 저장하게 변경

# 1. 처음에 일단 json 읽어오기
# 2. 읽어온걸로 데이터 구성 및 체크 유무에 따른 초기화 알고리즘 실행

# json 정보 구성은?
#     일정 이름, 체크 유무, 마지막 체크 시간, 초기화 알고리즘 종류, 초기화 알고리즘 변수 등

# 메모
# 실시간 저장? (하는 쪽으로 갈 듯?)
# 1회성 일정, 반복 일정?
# 알고리즘 계산에 쓰인 변수에 할당된 메모리 삭제 필요? 자동 삭제되나? 확인 필요...

def load_data(app):
    file_path = 'todo-data.json'
    if os.path.exists(file_path):
        df = pd.read_json(file_path, orient='records')
        app.add_todo(df.loc[0][0])


def save_data(app):
    file_path = 'todo-data.json'
    data = [['test name', 0, '2025-01-27 11:30:21', 0, 300]]

    df = pd.DataFrame(data, columns=['name', 'checked', 'lastchecktime', 'reset', 'resetparam0'])
    df.to_json(file_path, orient='records')


#     1. 시간별(daily), 요일별(weekly), 매 달 ~일 등(monthly)
#         현재 시간 기준으로 초기화 주기에 따른 지난번 초기화 시간을 계산하고, 마지막 체크 시간이 지난번 초기화 시간 이전이라면 체크 해제

#         패러미터 구성
#             daily - 시간 (분) + 마지막 체크 시간, 2개
#             weekly - 요일 + 시간 + 마지막 체크 시간, 3개
#             monthly - 일자 + 시간 + 마지막 체크 시간, 3개

# reset_time_input : 분 단위(0-1439), lastcheck_str : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21
def daily_reset(reset_time_input, lastcheck_str): 
    now = datetime.now()
    reset_time = time(reset_time_input // 60, reset_time_input % 60, 0)

    # 현재 시간과 초기화 시간을 비교하여 지난번 초기화 시간 계산
    if now.time() < reset_time: 
        pre_reset_time = datetime.combine(now.date() - timedelta(days = 1), reset_time)
    else:
        pre_reset_time = datetime.combine(now.date(), reset_time)

    # 마지막 체크 시간이 지난번 초기화 시간 이전인지 확인
    # 지난번 초기화 시간 이후면 유지(0), 지난번 초기화 시간 이전이면 체크 해제(1)
    lastcheck = datetime.strptime(lastcheck_str, '%Y-%m-%d %H:%M:%S')
    if pre_reset_time <= lastcheck: 
        return 0
    else:
        return 1

# weekday : 요일(0-6), reset_time_input : 분 단위(0-1439), lastcheck_str : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21
def weekly_reset(reset_time_input, lastcheck_str, weekday):
    now = datetime.now()
    reset_time = time(reset_time_input // 60, reset_time_input % 60, 0)

    # 선택한 요일에서 현재 요일까지의 차이 계산
    days_since_weekday = now.weekday() - weekday + 7
    
    # 다른 요일
    if days_since_weekday < 7: 
        pre_reset_time = datetime.combine(now.date() - timedelta(days = days_since_weekday), reset_time)

    # 같은 요일
    else:
        if now.time() < reset_time: 
            pre_reset_time = datetime.combine(now.date() - timedelta(days = 7), reset_time)
        else:
            pre_reset_time = datetime.combine(now.date(), reset_time)

    lastcheck = datetime.strptime(lastcheck_str, '%Y-%m-%d %H:%M:%S')
    if pre_reset_time <= lastcheck: 
        return 0
    else:
        return 1

# reset_day : 일자(1-31), reset_time_input : 분 단위(0-1439), lastcheck_str : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21
def monthly_reset(reset_time_input, lastcheck_str, reset_day):
    now = datetime.now()
    reset_time = time(reset_time_input // 60, reset_time_input % 60, 0)

    if now.day < reset_day: # 이번달 초기화 일자를 지나지 않은 경우
        pre_reset_time = datetime.combine((now.date() - relativedelta(months = 1)).replace(day = reset_day), reset_time)
    elif now.day == reset_day: # 초기화 당일
        if now.time() < reset_time: 
            pre_reset_time = datetime.combine(now.date() - relativedelta(months = 1), reset_time)
        else:
            pre_reset_time = datetime.combine(now.date(), reset_time)
    else: # 이번달 초기화 일자를 지난 경우
        pre_reset_time = datetime.combine(now.date().replace(day = reset_day), reset_time)

    lastcheck = datetime.strptime(lastcheck_str, '%Y-%m-%d %H:%M:%S')
    if pre_reset_time <= lastcheck: 
        return 0, pre_reset_time
    else:
        return 1, pre_reset_time

#     2. 주기별(기준 시간 정하고, 그 시간 기준으로 주기 설정, 초기화시 기준 시간 변경)
#         1. 현재 시간이 기준 시간과 초기화 시간 사이라면 유지.
#         2. 아니라면 초기화 하고 기준 시간을 초기화 시간으로 변경
#         3. 변경된 기준 시간으로 새로운 초기화 시간을 계산하고, 1번으로
        
#         패러미터 구성
#             기준 날짜, 기준 시간, 초기화 주기 + 마지막 체크 시간 4개

#         분 단위로 구현
#         주기별 알고리즘으로 daily weekly 구현도 가능하나, 복잡도상 살짝 손해