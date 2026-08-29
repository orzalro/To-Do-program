import calendar
import json
import os
from datetime import datetime, time, timedelta

from dateutil.relativedelta import relativedelta

DATA_FILE_PATH = 'data/userdata.json'
BLOCK_DATA_FILE_PATH = 'data/blockdata.json'


def elapsed_time_decorator(func):
    """실행 시간 측정용 데코레이터"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        # 비유니코드 Windows 콘솔에서도 핵심 로직이 로그 출력 때문에 실패하지 않도록 ASCII만 사용한다.
        print(f'[{end_time.hour:02d}:{end_time.minute:02d}] {func.__name__} elapsed: {elapsed_time.total_seconds():.6f}s')
        return result
    return wrapper


def safe_write_text(file_path, text, encoding = 'utf-8'):
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok = True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    temp_path = f'{file_path}.{timestamp}.tmp'
    try:
        with open(temp_path, 'w', encoding = encoding) as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, file_path)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def default_block_name(block_index):
    return f'블럭 {block_index + 1}'


def ensure_block_data(app, total_blocks = None):
    if total_blocks is None:
        total_blocks = app.grid_row * app.grid_col

    if not hasattr(app, 'block_data') or not isinstance(app.block_data, list):
        app.block_data = []

    while len(app.block_data) < total_blocks:
        app.block_data.append({'name': default_block_name(len(app.block_data))})

    for i, block in enumerate(app.block_data):
        if not isinstance(block, dict):
            app.block_data[i] = {'name': default_block_name(i)}
            continue

        name = str(block.get('name', '')).strip()
        if not name:
            block['name'] = default_block_name(i)

    return app.block_data


def load_block_data(app):
    app.block_data = []

    if os.path.exists(BLOCK_DATA_FILE_PATH):
        try:
            with open(BLOCK_DATA_FILE_PATH, 'r', encoding='utf-8') as f:
                block_data = json.load(f)
            if isinstance(block_data, list):
                app.block_data = block_data
        except (json.JSONDecodeError, OSError):
            app.block_data = []

    ensure_block_data(app)


def save_block_data(app):
    ensure_block_data(app)
    block_data_text = json.dumps(app.block_data, ensure_ascii = False, indent = 2)
    safe_write_text(BLOCK_DATA_FILE_PATH, block_data_text)


def formatting_data(resetmethod, resettime, resetparam0, resetparam1):
    method_dict = {'일간': 0, '주간': 1, '월간': 2, '주기': 3}
    resetmethod = method_dict[resetmethod]

    if resetmethod == 0:
        split_timestr = resettime.split(':')
        resettime = int(split_timestr[0]) * 60 + int(split_timestr[1])  # ex) 05:00(%H:%M) -> 300(Minute)
        resetparam0 = -1 # 사용안함
        resetparam1 = -1

    elif resetmethod == 1:
        split_timestr = resettime.split(':')
        resettime = int(split_timestr[0]) * 60 + int(split_timestr[1])  # ex) 05:00(%H:%M) -> 300(Minute)
        resetparam0 = resetparam0 # 초기화 요일
        resetparam1 = -1

    elif resetmethod == 2:
        split_timestr = resettime.split(':')
        resettime = int(split_timestr[0]) * 60 + int(split_timestr[1])  # ex) 05:00(%H:%M) -> 300(Minute)
        resetparam0 = resetparam0[:-1] # 초기화 일자
        resetparam1 = -1

    elif resetmethod == 3: 
        resettime = -1
        resetparam0 = resetparam0 # 초기화 주기
        resetparam1 = resetparam1 # 기준 날짜

    return resetmethod, resettime, resetparam0, resetparam1


def reset_check(checked, lastchecktime, resetmethod, resettime, resetparam0, resetparam1, now = None):
    # 체크가 되어있는 경우
    if checked:
        # 체크박스 초기화 알고리즘 실행
        # 0: daily, 1: weekly, 2: monthly, 3: cycle
        if resetmethod == 0:
            checked = daily_reset(resettime, lastchecktime, now = now)
        if resetmethod == 1:
            checked = weekly_reset(resettime, lastchecktime, resetparam0, now = now)
        if resetmethod == 2:
            checked = monthly_reset(resettime, lastchecktime, resetparam0, now = now)
        if resetmethod == 3:
            checked, resetparam1 = cycle_reset(resetparam0, resetparam1, now = now)
    else:
        if resetmethod == 3:
            checked, resetparam1 = cycle_reset(resetparam0, resetparam1, now = now)
        checked = 0
    return checked, resetparam1


# json 구성
# ['row', 'col', 'name', 'checked', 'reset', 'reset_time_input', 'resetparam0', 'resetparam1']
@elapsed_time_decorator
def load_data(app):
    # json에서 유저 일정 데이터 읽기
    if os.path.exists(DATA_FILE_PATH):
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
            for i in data:
                row = i[0]
                col = i[1]
                todoname = i[2]
                checked = i[3]
                resetmethod = i[4]
                resettime = i[5]
                resetparam0 = i[6]
                resetparam1 = i[7]

                app.todo_list[f'list{row * app.grid_col + col}'].add_todo(todoname, resetmethod, resettime, resetparam0, resetparam1, checked)
            

@elapsed_time_decorator
def apply_due_resets(app, evaluated_at = None):
    """반복 일정의 초기화 여부만 판단하고 화면 상태에 반영한다.

    일정 파일 저장은 호출자가 변경 여부를 확인한 뒤 수행한다.
    """
    from . import config

    evaluated_at = evaluated_at or datetime.now()
    state_changed = False
    for row in range(app.grid_row):
        for col in range(app.grid_col):
            todo_list = app.todo_list[f'list{row * app.grid_col + col}']
            for i in range(todo_list.count()):
                item = todo_list.item(i)
                todo = todo_list.get_todo_payload(item)

                checked, new_resetparam1 = reset_check(
                    todo['checked'],
                    app.lastchecktime,
                    todo['reset_method'],
                    todo['reset_time'],
                    todo['resetparam0'],
                    todo['resetparam1'],
                    now = evaluated_at,
                )
                reset_applied = (
                    todo['checked'] != checked
                    or str(todo['resetparam1']) != str(new_resetparam1)
                )
                if reset_applied:
                    todo_list.update_param(
                        item,
                        todo['reset_method'],
                        todo['reset_time'],
                        todo['resetparam0'],
                        new_resetparam1,
                        checked,
                    )
                    state_changed = True

    # 다음 확인이 이번 평가 구간을 다시 처리하지 않도록 시각을 기록한다.
    config.update_config(app, 'Variables', 'lastchecktime', evaluated_at.strftime('%Y-%m-%d %H:%M:%S'))
    return state_changed


@elapsed_time_decorator
def save_data(app):
    """현재 화면의 일정 상태만 파일에 저장한다."""
    data = []
    for row in range(app.grid_row):
        for col in range(app.grid_col):
            todo_list = app.todo_list[f'list{row * app.grid_col + col}']
            for i in range(todo_list.count()):
                item = todo_list.item(i)
                todo = todo_list.get_todo_payload(item)
                data.append([
                    row,
                    col,
                    todo['title'],
                    todo['checked'],
                    todo['reset_method'],
                    todo['reset_time'],
                    todo['resetparam0'],
                    todo['resetparam1'],
                ])

    data_text = ''.join(json.dumps(item, ensure_ascii=False) + '\n' for item in data)
    safe_write_text(DATA_FILE_PATH, data_text)


#     1. 시간별(daily), 요일별(weekly), 매 달 ~일 등(monthly)
#         현재 시간 기준으로 초기화 주기에 따른 지난번 초기화 시간을 계산하고, 마지막 체크 시간이 지난번 초기화 시간 이전이라면 체크 해제

#         패러미터 구성
#             daily - 시간 (분) + 마지막 체크 시간, 2개
#             weekly - 요일 + 시간 + 마지막 체크 시간, 3개
#             monthly - 일자 + 시간 + 마지막 체크 시간, 3개


# reset_time_input : 분 단위(0-1439), lastchecktime : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21
def daily_reset(reset_time_input, lastchecktime, output = 0, now = None):
    now = now or datetime.now()
    reset_time = time(reset_time_input // 60, reset_time_input % 60, 0)

    # 현재 시간과 초기화 시간을 비교하여 지난번 초기화 시간 계산
    if now.time() < reset_time: 
        pre_reset_time = datetime.combine(now.date() - timedelta(days = 1), reset_time)
    else:
        pre_reset_time = datetime.combine(now.date(), reset_time)

    # 요청시 체크유무대신 다음번 초기화 시간 리턴
    if output == 1:
        return pre_reset_time + timedelta(days = 1)

    # 마지막 체크 시간이 지난번 초기화 시간 이전인지 확인
    # 지난번 초기화 시간 이후후면 체크 해제(0), 지난번 초기화 시간 이전이면 체크 유지(1)
    lastcheck = datetime.strptime(lastchecktime, '%Y-%m-%d %H:%M:%S')
    if lastcheck < pre_reset_time: 
        return 0
    else:
        return 1


# reset_time_input : 분 단위(0-1439), lastchecktime : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21, resetparam0 : 요일(0-6)
def weekly_reset(reset_time_input, lastchecktime, resetparam0, output = 0, now = None):
    now = now or datetime.now()
    reset_time = time(reset_time_input // 60, reset_time_input % 60, 0)
    weekday = list(map(int, str(resetparam0).split()))

    if now.weekday() in weekday:
        if now.time() < reset_time:
            next_reset_day = now.weekday()
            pre_reset_day = weekday[weekday.index(now.weekday()) - 1]
        else:
            next_reset_day = weekday[(weekday.index(now.weekday()) + 1) % len(weekday)]
            pre_reset_day = now.weekday()
    else:
        for i in weekday:
            if i > now.weekday():
                next_reset_day = i
                pre_reset_day = weekday[weekday.index(i) - 1]
                break
            else:
                next_reset_day = weekday[0]
                pre_reset_day = weekday[-1]

    # 다음 초기화 요일에서 현재 요일까지의 차이 계산
    days_since_pre_reset = now.weekday() - pre_reset_day
    
    # 다른 요일
    if days_since_pre_reset > 0: 
        pre_reset_time = datetime.combine(now.date() - timedelta(days = days_since_pre_reset), reset_time)
    elif days_since_pre_reset < 0: 
        pre_reset_time = datetime.combine(now.date() - timedelta(days = 7 + days_since_pre_reset), reset_time)
    # 같은 요일
    else:
        if now.time() < reset_time: 
            pre_reset_time = datetime.combine(now.date() - timedelta(days = 7), reset_time)
        else:
            pre_reset_time = datetime.combine(now.date(), reset_time)

    # 요청시 체크유무대신 다음번 초기화 시간 리턴
    if output == 1:
        pre_to_next = next_reset_day - pre_reset_day
        if pre_to_next < 0:
            pre_to_next += 7
        elif pre_to_next == 0:
            pre_to_next = 7
        return pre_reset_time + timedelta(days = pre_to_next)

    lastcheck = datetime.strptime(lastchecktime, '%Y-%m-%d %H:%M:%S')
    if lastcheck < pre_reset_time: 
        return 0
    else:
        return 1


def normalize_month_day(resetparam0):
    return max(1, min(int(resetparam0), 31))


def _monthly_reset_datetime(year, month, reset_day, reset_time):
    last_day = calendar.monthrange(year, month)[1]
    return datetime.combine(
        datetime(year, month, min(reset_day, last_day)).date(),
        reset_time,
    )


# reset_time_input : 분 단위(0-1439), lastchecktime : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21, resetparam0 : 일자(1-31)
def monthly_reset(reset_time_input, lastchecktime, resetparam0, output = 0, now = None):
    now = now or datetime.now()
    reset_time = time(reset_time_input // 60, reset_time_input % 60, 0)
    reset_day = normalize_month_day(resetparam0)

    current_reset_time = _monthly_reset_datetime(now.year, now.month, reset_day, reset_time)
    if now < current_reset_time:
        pre_month = datetime(now.year, now.month, 1) - relativedelta(months = 1)
        pre_reset_time = _monthly_reset_datetime(pre_month.year, pre_month.month, reset_day, reset_time)
        next_reset_time = current_reset_time
    else:
        next_month = datetime(now.year, now.month, 1) + relativedelta(months = 1)
        pre_reset_time = current_reset_time
        next_reset_time = _monthly_reset_datetime(next_month.year, next_month.month, reset_day, reset_time)

    # 요청시 체크유무대신 다음번 초기화 시간 리턴
    if output == 1:
        return next_reset_time

    lastcheck = datetime.strptime(lastchecktime, '%Y-%m-%d %H:%M:%S')
    if lastcheck < pre_reset_time: 
        return 0
    else:
        return 1


#     2. 주기별(기준 시간 정하고, 그 시간 기준으로 주기 설정, 초기화시 기준 시간 변경)
#         1. 현재 시간이 기준 시간과 초기화 시간 사이라면 유지.
#         2. 아니라면 초기화 하고 기준 시간을 초기화 시간으로 변경
#         3. 변경된 기준 시간으로 새로운 초기화 시간을 계산하고, 1번으로

#         패러미터 구성     
#           초기화 주기, 기준 날짜 2개


# resetparam0 : 분 단위, resetparam1: %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21
def cycle_reset(resetparam0, resetparam1, now = None):
    now = now or datetime.now()
    reset_cycle = int(resetparam0)
    base_datetime = datetime.strptime(resetparam1, '%Y-%m-%d %H:%M:%S')

    next_reset_time = base_datetime + timedelta(minutes = reset_cycle)

    if now < base_datetime:
        return 1, base_datetime.strftime('%Y-%m-%d %H:%M:%S')

    if base_datetime < now < next_reset_time:
        return 1, base_datetime.strftime('%Y-%m-%d %H:%M:%S')
    else:
        # 남은 시간이 항상 양수가 되도록 현재 시각과 같은 초기화 시각도 다음 주기로 넘긴다.
        while next_reset_time <= now:
            base_datetime += timedelta(minutes = reset_cycle)
            next_reset_time = base_datetime + timedelta(minutes = reset_cycle)
        return 0, base_datetime.strftime('%Y-%m-%d %H:%M:%S')
