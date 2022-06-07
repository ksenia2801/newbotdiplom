import os
import csv
import json
import requests
from http import HTTPStatus

URL = 'http://127.0.0.1:8080/set_timetable'
HEADERS = {
    'Content-Type': 'application/json'
}
keys = [
    "faculty_tag",
    "group_name",
    "week_num",
    "day_num",
    "time_cell_num",
    "discipline_type",
    "discipline_name",
    "teacher_full_name",
    "room_name"
]
DATA_FILE = 'data.csv'


if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), DATA_FILE), newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            data = {}
            for i, key in enumerate(keys):
                data.update({key: row[i]})
            response = requests.post(url=URL, data=json.dumps(data), headers=HEADERS)
            print(response.status_code, response.text)
