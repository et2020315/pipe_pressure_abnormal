
from adtk.data import validate_series
from adtk.visualization import plot
from IPython.display import display
from sklearn.model_selection import train_test_split
from adtk.detector import SeasonalAD
from adtk.detector import LevelShiftAD
from adtk.detector import QuantileAD
from adtk.detector import InterQuartileRangeAD

import pandas as pd
import numpy as np
import json
import traceback
import os
import matplotlib.pyplot as plt


# global parameters . set to be constant if all caps, you can change methods by passing it as array
#**** Quartile method
HIGH_Q = 1
LOW_Q = 0.10
#**** level method
AWAY_FROM_MU_LEVEL = 3
WINSIZE_LEVEL = 7
#**** moving average method
WINDOW_AVG = 7
AWAY_FROM_MU = 2
SIZE = 10
WINDOW = 7
#**** Seasonal Method
WINDOW_SEASON = 8
#**** Constants
FIGSIZE = (200,60)
EXACT_TIME_FORMAT = "%y-%m-%d %H:%M:%S"
DATE_FORMAT_OUTPUT = "%Y-%m-%d"
SELECT_COLUMN = 'GainerHall_Supply'
# TEST_METHOD = ['seasonal']
# TEST_METHOD = ['iqr']
TEST_METHOD = ['quartile']
# TEST_METHOD = ['level']
# TEST_METHOD = ['moving_avg']




def convert_datetime(dataframe):
  # convert string to datetime object
  dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'])
  # you need to set index as time in order for later joining and other precessing
  dataframe = dataframe.set_index('Timestamp')
  # this was for joining when timestamp was the same name it will become "unname column", it is just in case forgot to rename timestamp
  try:
    dataframe.drop(columns = ['Unnamed: 0'], inplace=True)
  except:
    print("do not need to remove column when changing index")
  return dataframe





def generate_train_only(day_num, num_of_training_days,dataframe):
  dataframe = validate_series(dataframe)
  starting_days = num_of_training_days * 24 # k
  # max_day_num = int(math.floor(len(dataframe) / 24))
  # print(max_day_num)
  curr_records = starting_days + day_num * 24
  if (curr_records >= len(dataframe)):
    print("return none")
    return None
  #print(dataframe.iloc[: (starting_days + day_num * 24)])
  return (dataframe.iloc[: (starting_days + day_num * 24)])









# use 'time' interpolation to fill the gaps
def select_and_interpolate(hall_type, dataframe):
  df = dataframe[[hall_type]]
  # print(df.isna().any(axis = 1))
  if (len(df.isna().any(axis = 1)) > 0):
    df[hall_type] = df[hall_type].interpolate(method = 'time')
  return df


# choose which detector to use
def choose_detector(method):
  try:
    # method is a list
    if method[0] == 'seasonal':
      return SeasonalAD(freq=WINDOW_SEASON)
    elif method[0] == 'iqr':
      return InterQuartileRangeAD(c=1)
    elif method[0] == 'quartile':
      return QuantileAD(low=LOW_Q, high=HIGH_Q)
    elif method[0] == 'level':
      return LevelShiftAD(c=AWAY_FROM_MU_LEVEL, side='both', window=WINSIZE_LEVEL)
  except:
    traceback.print_exc()


# anomaly_df is a true or false dataframe, plot function just plot the graph
def predict_plot_train(detector, method, train_df):
  detector.fit(train_df)
  anomaly_df = detector.detect(train_df)
  # plot(train_df, anomaly=anomaly_df, anomaly_color="red", anomaly_tag="marker", figsize=FIGSIZE)
  # plt.show()
  return anomaly_df


def dhw_validate_and_predict(hall_type, dataframe, method, dayNum, num_of_training_days):
  dataframe = convert_datetime(dataframe)

  dataframe = select_and_interpolate(hall_type, dataframe)
  train_df = generate_train_only(dayNum, num_of_training_days, dataframe)

  detector = choose_detector(method)
  anomaly = predict_plot_train(detector, method, train_df)
  # get actual data
  jsonlist = generate_json(train_df, anomaly, hall_type)
  return jsonlist


def generate_json(train_df, anomaly, hall_type):
  try:
    train_df = train_df.reset_index()
    anomaly = anomaly.reset_index()
    train_df.drop(['Timestamp'],axis = 1, inplace = True)
    train_df.rename({hall_type : 'original'}, axis = 1, inplace = True)
    anomaly.rename({hall_type : 'isAbnormal'}, axis = 1, inplace = True)
    temp = train_df.join(anomaly)
    # display(temp)
    time_list = []
    pressure_list = []
    abnormality_list = []
    counter = len(temp)
    #print("len = " + str(len(temp)))
    time_list = [item.strftime("%y-%m-%d %H:%M:%S") for item in temp.loc[:, 'Timestamp']]
    pressure_list = [item for item in temp.loc[: , 'original']]

    # remove single hour false positive
    # modified = modified_anomaly(3, temp['isAbnormal'])
    # print("modified length = " + str(len(modified)))
    # print("original length = " + str(len(temp['isAbnormal'])))
    #
    # if (len(modified) == 0):
    #   print("empty length ")
    #   print("length of original = " + len(temp['isAbnormal']))
    #   return {}
    # temp['isAbnormal'] = modified

    abnormality_list = [item for item in temp.loc[:, 'isAbnormal']]
    last_day_has_leak_df = temp.loc[:, 'isAbnormal'].iloc[-24: -1]



    #print(last_day_has_leak_df)
    dict_item = {'time_points' : time_list, 'pressure_points' : pressure_list, 'leak_points': abnormality_list, 'last_day_has_leak': len(last_day_has_leak_df[last_day_has_leak_df]) >= 1}
    return dict_item
  except:
    traceback.print_exc()

# def datesdf2json(datesdf):
#   display(datesdf)
#   print("datesdf shape -----------------------")
#   print(datesdf.shape)
#
#   start_list = [starttime.strftime(EXACT_TIME_FORMAT) for starttime in datesdf.loc[:, 'Timestamp_start']]
#   end_list = [endtime.strftime(EXACT_TIME_FORMAT) for endtime in datesdf.loc[:, 'Timestamp_end']]
#
#   jsondates = {'start': start_list, 'end': end_list}
#   print("json exact start and end dates")
#   print(jsondates)
#   return jsondates

def modified_anomaly(NUM, tf):
  counts = []
  counter = 0
  for i in range(len(tf)):
    if tf[i] == False:
      counter = 0
      counts.append(0)
    else:
      counter += 1
      counts.append(counter)
    # print(str(tf[i]) + " " + str(counts[i]))
  #print("ori")
  #print(counts)
  # reversed = counts[::-1]
  # print("revserse")
  # print(reversed)
  modified = []
  counter2 = len(counts) - 1

  while (counter2 >= 0):
    if (counter2 >= 0 and (counts[counter2] >= NUM)):
      while (counts[counter2] > 0):
        # print("display = " + str(counts[counter2]) + " " + "actual = true, counter2 = " + str(counter2))
        modified.append(True)
        counter2 -= 1

    if (counter2 >= 0):
      # print("display = " + str(counts[counter2]) + " " + "actual = false, counter2 = " + str(counter2))
      modified.append(False)
      counter2 -= 1
  modified2 = modified[::-1]
  print("\n")
  print("len tf series = " + str(len(tf)))
  print("len count = " + str(len(counts)))
  print("len modified = " + str(len(modified)))
  return modified2


# def getdates(anomaly, hall_type):
#   series = anomaly[hall_type]
#   anomaly['prev'] = anomaly[hall_type].shift()
#   anomaly['diff'] = anomaly[hall_type] - anomaly['prev']
#   anomaly = anomaly.reset_index()
#   ones = anomaly[anomaly['diff'] >= 1.0]
#   ones.reset_index(inplace=True)
#   negones = anomaly[anomaly['diff'] <= -1.0]
#   negones.reset_index(inplace=True)
#   temp = negones[['Timestamp']]
#
#   datesdf = ones[['Timestamp']].join(temp, lsuffix="_start", rsuffix='_end')
#   # Exact start and end time
#   print("----------- kakaka join sucessfully")
#   jsondates = datesdf2json(datesdf)
#
#   # josn date range
#   print(ones.columns)
#   series = ones.loc[:, 'Timestamp']
#   series = series.dt.date
#   curr = series[0];
#   next = series[0];
#   start_lst = []
#   end_lst = []
#
#   for i in range(1, len(series)):
#     item = series[i] - series[i - 1]
#     days = pd.Timedelta("14d")
#     oneday = pd.Timedelta("1d")
#     if (item <= days):
#       next = series[i]
#     else:
#       start_lst.append(curr.strftime(DATE_FORMAT_OUTPUT))
#       end_lst.append(next.strftime(DATE_FORMAT_OUTPUT))
#       curr = series[i]
#       next = series[i]
#
#     if (i == len(series) - 1):
#       start_lst.append(curr.strftime(DATE_FORMAT_OUTPUT))
#       end_lst.append(next.strftime(DATE_FORMAT_OUTPUT))
#
#   aggregate_range = {'aggregateStart': start_lst, 'aggregateEnd': end_lst}
#   print("returning jsondates df -> json, lst , list of json date range")
#   return jsondates, aggregate_range


def moving_average_method(dataframe, hall_type):
  pass

if __name__ == "__main__":
  df = pd.read_csv("data/finalDHW.csv")
  data = dhw_validate_and_predict(SELECT_COLUMN, df, TEST_METHOD, 10, 80)





