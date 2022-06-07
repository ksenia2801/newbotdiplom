import logging
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


TUSUR_URL = "https://timetable.tusur.ru"
TIMETABLE_DB_URL = 'http://localhost:8080/set_timetable'


def parse_timetable(html: requests.models.Response):
    if not html:
        return
    soup = BeautifulSoup(html.text, 'lxml')
    tt_div = soup.find('div', {'class': 'timetable_wrapper'})
    _header = tt_div.find('thead')
    _body = tt_div.find('tbody')
    _dates = [list(map(str.strip, x.text.strip().split('\n'))) for x in _header.find_all('th') if x.text.strip()]
    _timetable = {k: [] for k in range(1, 7)}

    for i in range(1, 8):
        table_row = _body.find('tr', {'class': f'lesson_{i}'})
        if not table_row:
            continue
        time_start, time_end = table_row.find('th', {'class': 'time'}).text.strip().split('\n')
        for day_num in range(1, 7):
            cell = table_row.find('td', {'class': re.compile(f'lesson_cell day_{day_num} *')})
            if cell:
                cell_for_print = cell.find('div', {'class': 'hidden for_print'})
                if cell_for_print:
                    note = cell_for_print.find('span', {'class': 'note'})
                    cell = {
                        'date': ''.join(_dates[day_num - 1]),
                        'start_time': time_start,
                        'end_time': time_end,
                        'discipline': cell_for_print.find('span', {'class': 'discipline'}).text.strip(),
                        'kind': cell_for_print.find('span', {'class': 'kind'}).text.strip(),
                        'auditoriums': cell_for_print.find('span', {'class': 'auditoriums'}).text.strip(),
                        'teachers': cell_for_print.find('span', {'class': 'group'}).text.strip(),
                        'note': None if note is None else note.text.strip()
                    }
                    _timetable[day_num].append(cell)
    return _timetable


if __name__ == '__main__':
    faculty_tag = 'rtf'
    group_names = ['111', '111-m1', '121-1', '121-2', '121-3', '141-1', '141-2', '141-3', '141-4']
    week_num = 613
    for group_name in group_names:
        url = urljoin(TUSUR_URL, f'faculties/{faculty_tag}/groups/{group_name}?week_id={week_num}')
        html_page = requests.get(url)
        if html_page.status_code == 200:
            timetable = parse_timetable(html=html_page)
            for day_num, table in timetable.items():
                for time_cell_num, row in enumerate(table, 1):
                    try:
                        headers = {'Content-Type': 'application/json'}
                        data = {
                            'faculty_tag': faculty_tag,
                            'group_name': group_name,
                            'week_num': week_num,
                            'day_num': day_num,
                            'time_cell_num': time_cell_num,
                            'discipline_type': row['kind'],
                            'discipline_name': row['discipline'],
                            'teacher_full_name': row['teachers'],
                            'room_name': row['auditoriums']
                        }
                        response = requests.post(url=TIMETABLE_DB_URL, json=data, headers=headers)
                        print(response.text)
                    except Exception as err:
                        logging.error(f'Error: {faculty_tag}, {group_name}, {week_num}')
        else:
            print(f'Response code for {url} is {html_page.status_code}')
