# 초기화 알고리즘 여러개 필요
#     1. 시간별(daily), 요일별(weekly), 매 달 ~일 등(monthly)
#         현재 시간 기준으로 초기화 주기에 따른 저번 초기화 시간과 이번 초기화 시간을 계산하고, 마지막 체크 시간이 그 사이인지 확인
#         아니라면 체크 해제

#         패러미터 구성?
#             daily - 시간 (시 or 분? 초단위는 굳이?) 1개
#             weekly - 요일 + 시간 2개
#             monthly - 일자 + 시간 2개

#         패러미터 구성시, 공간 절약과 시간 중 어느쪽을 우선시?
#         일단 공간 절약해보고 시간 차이가 유의미하면 바꿔보는 걸로...

from datetime import datetime

class reset_algorithm():
    def daily_reset(time):
        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted

    def weekly_reset(day, time):
        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted
    
    def monthly_reset(day, time):
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

#     예시. 매일 오전 5시에 초기화하고 싶다 한다면?
#         1. 체크 유무 확인
#         2. 현재 시간 확인
#             1. 현재 시간이 오전 5시 전이라면 저번 초기화 시간이 어제 오전 5시이고, 이번 초기화 시간은 오늘 오전 5시이다.
#             2. 현재 시간이 오전 5시 이후라면 저번 초기화 시간이 오늘 오전 5시이고, 이번 초기화 시간은 내일 오전 5시이다.
#         3. 마지막 체크 시간이 저번 초기화 시간 전이라면 체크를 해제한다.