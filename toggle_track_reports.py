# -*- coding: utf-8 -*-

import csv
from collections import defaultdict
from datetime import datetime, timedelta
import argparse
import calendar

parser = argparse.ArgumentParser(
    description='Parse a CSV file and group the results')
parser.add_argument('csv_files', nargs='+', type=str,
                    help='paths to the input CSV files')
args = parser.parse_args()


DAY_NAMES = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье'
}

MONTH_NAMES = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря'
}

tasks_by_day = defaultdict(lambda: defaultdict(float))
total_duration = 0.0

for csv_file in args.csv_files:
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_time = datetime.strptime(
                row['Start date'] + row['Start time'], '%Y-%m-%d%H:%M:%S')
            end_time = datetime.strptime(
                row['End date'] + row['End time'], '%Y-%m-%d%H:%M:%S')
            duration = (end_time - start_time).total_seconds() / \
                3600  # calculate in hours
            day = start_time.date()
            task = (row['Project'], row['Description'])
            tasks_by_day[day][task] += duration
            total_duration += duration

current_week = None
week_tasks = []
week_start = week_end = None
for day, tasks in sorted(tasks_by_day.items()):
    week_number = day.isocalendar()[1]
    if week_number != current_week:
        if current_week is not None:
            week_total = sum(task[1] for task in week_tasks)
            print("**Неделя {0} ({1}—{2} {3})** `{4:.1f}h`\n".format(current_week, week_start.day,
                                                                     week_end.day, MONTH_NAMES[week_start.month], round(week_total, 1)))
            print("___________________\n")
        week_tasks = []
        current_week = week_number
        week_start = day

    week_end = day
    week_tasks.extend(tasks.items())

    day_total = sum(tasks.values())
    day_name = DAY_NAMES[day.weekday()]
    month_name = MONTH_NAMES[day.month]
    print("📆 **{0}, {1} {2}** - `{3:.1f}h`".format(day_name,
                                                   day.day, month_name, round(day_total, 1)))
    for (project, task), duration in sorted(tasks.items(), key=lambda x: x[1], reverse=True):
        print(
            "- #{0}: {1}: `{2:.1f}h`".format(project, task, round(duration, 1)))
    print("\n")  # New line after each day


week_total = sum(duration for _, duration in week_tasks)
print("**Неделя {0} ({1}—{2} {3})** `{4:.1f}h`\n".format(current_week, week_start.day,
                                                         week_end.day, MONTH_NAMES[week_start.month], round(week_total, 1)))
print("___________________")
print("📊 **Общее время:** `{0:.1f}h`".format(round(total_duration, 1)))
