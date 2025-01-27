#     1. 시간별(daily), 요일별(weekly), 매 달 ~일 등(monthly)
#         현재 시간 기준으로 초기화 주기에 따른 지난번 초기화 시간을 계산하고, 마지막 체크 시간이 지난번 초기화 시간 이전이라면 체크 해제

#         패러미터 구성
#             daily - 시간 (분), 1개
#             weekly - 요일 + 시간, 2개
#             monthly - 일자 + 시간, 2개

from datetime import datetime, time, timedelta

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
def weekly_reset(weekday, reset_time_input, lastcheck_str):
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted

# day : 일자(1-31), reset_time_input : 분 단위(0-1439), lastcheck_str : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21
def monthly_reset(day, reset_time_input, lastcheck_str):
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted

#     2. 주기별(기준 시간 정하고, 그 시간 기준으로 주기 설정, 초기화시 기준 시간 변경)
#         1. 현재 시간이 기준 시간과 초기화 시간 사이라면 유지.
#         2. 아니라면 초기화 하고 기준 시간을 초기화 시간으로 변경
#         3. 변경된 기준 시간으로 새로운 초기화 시간을 계산하고, 1번으로
        
#         패러미터 구성
#             기준 날짜, 초기화 주기 2개

#         어느 단위까지 구현할지... 초? 분? 시?
#         주기별 알고리즘으로 daily weekly 구현도 가능하나, 복잡도상 살짝 손해