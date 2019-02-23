#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_gpa(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features='lxml')
    headers = [header_child.find_parent() for header_child in soup.find_all('th', text='課別')]
    columns = [th.text for th in headers[0].find_all('th')]

    list_of_courses_plus_comment = [header.find_next_siblings() for header in headers]
    courses = [course for courses_plus_comment in list_of_courses_plus_comment for course in courses_plus_comment[:-1]]
    courses_text = [[td.text.strip() for td in course.find_all('td')] for course in courses]

    df = pd.DataFrame.from_records(courses_text, columns=columns)
    df.drop(['課別', '課號', '班次', '備註'], axis=1, inplace=True)

    grade2point = {
        'A+': 4.3, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'F': 0.0, '(F )': 0.0, 'X': 0.0
        # 'F' is kept here in case the system changes '(F )' to 'F' in the future...
    }

    grade2point_std = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'F': 0.0, '(F )': 0.0, 'X': 0.0
        # 'F' is kept here in case the system changes '(F )' to 'F' in the future...
        # ref: https://pages.collegeboard.org/how-to-convert-gpa-4.0-scale
    }

    df = df.loc[df['成績'].isin(grade2point)]
    df.loc[:, '學分'] = pd.to_numeric(df.loc[:, '學分'])
    df.loc[:, 'GP'] = df.loc[:, '成績'].apply(lambda s: grade2point[s])
    df.loc[:, 'GP_std'] = df.loc[:, '成績'].apply(lambda s: grade2point_std[s])

    def is_major(code):
        return code == '725 U3500' or any([code.startswith(cs) for cs in ['902', '922', '944']])

    df_major = df[df['課程識別碼'].apply(is_major)]

    def calc_GPA(df):
        sum_GP = sum(df.apply(lambda row: row['學分'] * row['GP'], axis=1))
        sum_GP_std = sum(df.apply(lambda row: row['學分'] * row['GP_std'], axis=1))
        sum_credits = sum(df['學分'])
        return sum_GP / sum_credits, sum_GP_std / sum_credits

    gpa_overall, gpa_overall_std = calc_GPA(df)
    gpa_major, gpa_major_std = calc_GPA(df_major)
    return gpa_overall, gpa_major, gpa_overall_std, gpa_major_std

def main():
    import sys
    print(get_gpa(sys.argv[1]))

if __name__ == '__main__':
    main()
