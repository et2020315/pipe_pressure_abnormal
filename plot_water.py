'''
Temporary python file to analyze data given as csv files.
'''

import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import *

TIME_WINDOW = 10
TIME_OFFSET = 3
pd.set_option('display.max_columns', 15)

def string_to_date(date_as_str):
    split_str = date_as_str.split('-')
    return date(int(split_str[0]), int(split_str[1]), int(split_str[2]))

# helper functions
def isNumber(val):
    try:
        new_float = float(val)
        return True
    except:
        return False


def get_file_name(water_type, data_type):
    return "data/ap2" + water_type + "-" + data_type + ".csv"


def get_headers_mapping(filename):
    with open(filename, "r") as csvfile:
        points_to_building_nums = {}
        reader = csv.reader(csvfile)
        for index, item in enumerate(reader):
            # ignore header
            if index == 0: continue
            if "Point" in item[0]:
                # assign point num to building num and remove ":" character
                points_to_building_nums[item[0][:len(item[0]) - 1]] = item[1]
            else:
                break

    return points_to_building_nums


def get_refined_df(filename, headers_mapping):
    dtf = pd.read_csv(filename, skiprows=len(headers_mapping) + 5)
    dtf = dtf.rename(headers_mapping, axis=1)

    # filter out string values
    cols = list(headers_mapping.values())
    dtf[cols] = dtf[cols].applymap(lambda x: x if isNumber(x) else np.nan)
    # convert to float
    dtf[cols] = dtf[cols].astype(np.float16)

    # convert time to timeseries objects
    dtf['new_time'] = dtf['<>Date'] + " " + dtf['Time']
    dtf = dtf.drop(['<>Date','Time'], axis=1)
    dtf['new_time'] = pd.to_datetime(dtf['new_time'])
    dtf.set_index('new_time')

    return dtf


def get_df(water_type, data_type):
    filename = get_file_name(water_type, data_type)
    headers_mapping = get_headers_mapping(filename)
    df = get_refined_df(filename, headers_mapping)

    return df, headers_mapping.values()


def plot_water(water_type, data_type, start_date, end_date, selected_buildings, ylim=[], dynamic_size=False):
    df, buildings = get_df(water_type, data_type)

    fig = plt.figure()

    if dynamic_size:
        # set the width by number of days:
        d0 = string_to_date(start_date)
        d1 = string_to_date(end_date)
        delta = d1 - d0
        fig.set_figwidth(8 * delta.days)
    ax1 = fig.add_subplot()

    # filter by date
    df = df[(df['new_time'] > start_date) & (df['new_time'] < end_date)]

    for building in buildings:
        if not building in selected_buildings:
            continue
        # only plots buildings who have data

        if len(df[building].dropna()):
            ax1.scatter(df["new_time"], df[building], s=0.7, label=building)

    if ylim and len(ylim): ax1.set_ylim(ylim)
    ax1.legend()
    ax1.figure.show()

def get_HDW_for_building(file_dir, building, time_period):
    df = pd.read_csv(file_dir)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%m/%d/%Y %H:%M')
    df.set_index('Timestamp', inplace=True)
    date_start = string_to_date("2021-01-01") + timedelta(days=int(time_period) * TIME_OFFSET)
    date_end = date_start + timedelta(days=TIME_WINDOW)
    df = df[date_start:date_end]
    return {
        "pressure_points": list(df[building].values),
        "leak_points": False, #list(df[building].values),
        "time_points": [str(date) for date in df[building].index.values],
        "has_leak_now": False
    }


if __name__ == "__main__":


     # aparent leak at jan 18
     # plot_water("HW", "GPM", "2021-01-01", "2021-02-01",
     #           ['0275_HW.GPM', "0291_HW.GPM"], ylim=[], dynamic_size=True)
     '''
         plot_water("HW", "GPM", "2021-01-01", "2021-02-01",
                    ['0275_HW.GPM', "0291_HW.GPM", "0358_HW.GPM", "0400_HW.GPM",
                     "0401_HW.GPM", "0402_HW.GPM", "0403_HW.GPM", "0404_HW.GPM"]\
                    , ylim=[], dynamic_size=True)
         '''

     get_HDW_for_building(None)

     #'0275_HW.GPM'
     #scattered mess:
     # plot_water("HW", "GPM", "2021-04-12", "2021-04-18", ['0358_HW.GPM'], ylim=[])

     # print(get_df("HW", "RET"))
     # df = get_df("CHW", "GPM")['0402_HW.GPM'] # single series

     # detects actual leak incident #7
     #plot_water("HW", "GPM", "2021-06-01", "2021-07-01", ['0404_HW.GPM'], ylim=[0, 4], dynamic_size=True)
     #plot_water("HW", "GPM", "2021-06-01", "2021-07-01", ['0402_HW.GPM', '0404_HW.GPM'], ylim=[], dynamic_size=True)
