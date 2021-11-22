
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


HIGH_Q = 1
LOW_Q = 0.06
AWAY_FROM_MU_LEVEL = 3
WINSIZE_LEVEL = 7
WINDOW_AVG = 7
AWAY_FROM_MU = 2
SIZE = 10
WINDOW = 7
WINDOW_SEASON = 8
FIGSIZE = (200,60)
EXACT_TIME_FORMAT = "%y-%m-%d %H:%M:%S"
DATE_FORMAT_OUTPUT = "%Y-%m-%d"
SELECT_COLUMN = 'GainerHall_Supply'
# TEST_METHOD = ['seasonal']
K = 0.2
# TEST_METHOD = ['iqr']
TEST_METHOD = ['quartile']
# TEST_METHOD = ['level']
# TEST_METHOD = ['moving_avg']




def convert_datetime(dataframe):
  dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'])
  dataframe = dataframe.set_index('Timestamp')
  dataframe.head(3)
  # print(dataframe.index)
  try:
    dataframe.drop(columns = ['Unnamed: 0'], inplace=True)
  except:
    print("do not need to remove column when changing index")
  return dataframe


def generate_train_only(chunkNum, dataframe):
  dataframe = validate_series(dataframe)
  temp = ((1 - K) / SIZE) * chunkNum
  print("temp = " + str(temp))
  split_at = np.round(K + np.round(temp, decimals= 2), 2)

  print("split at = " + str(split_at))
  length = dataframe.shape[0]
  print(length)
  rownum = int(split_at * length)
  print(rownum)
  # rownum = ((split_at * len(dataframe)))
  # print("row num = " + str(rownum))
  print(dataframe.iloc[rownum])
  return dataframe.iloc[:rownum, :]



def select_and_interpolate(hall_type, dataframe):
  df = dataframe[[hall_type]]
  # print(df.isna().any(axis = 1))
  if (len(df.isna().any(axis = 1)) > 0):
    df[hall_type] = df[hall_type].interpolate(method = 'time')
  return df


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


def predict_plot_train(detector, method, train_df):
  detector.fit(train_df)
  anomaly_df = detector.detect(train_df)
  plot(train_df, anomaly=anomaly_df, anomaly_color="red", anomaly_tag="marker", figsize=FIGSIZE)
  plt.show()
  return anomaly_df


def dhw_validate_and_predict(hall_type, dataframe, method, chunkNum):
  dataframe = convert_datetime(dataframe)

  dataframe = select_and_interpolate(hall_type, dataframe)

  train_df = generate_train_only(chunkNum, dataframe)
  print("-----------")
  print("method = " + method[0])
  if method[0] == 'moving_avg':
    moving_average_method(dataframe, hall_type)
    print("*********** line4 **************")
  else:
    detector = choose_detector(method)
    print('detector type = ' + str(type(detector)))
    anomaly = predict_plot_train(detector, method, train_df)
    # get actual data
    jsonlist = generate_json(train_df, anomaly, hall_type)

    exactdates, daterange = getdates(anomaly, hall_type)
    print("returning extact dates, date ranges, jsonlist(all data) for plotting")
    return exactdates, daterange, jsonlist


def generate_json(train_df, anomaly, hall_type):

  train_df = train_df.reset_index()
  anomaly = anomaly.reset_index()
  train_df.drop(['Timestamp'],axis = 1, inplace = True)
  train_df.rename({hall_type : 'original'}, axis = 1, inplace = True)
  anomaly.rename({hall_type : 'isAbnormal'}, axis = 1, inplace = True)
  temp = train_df.join(anomaly)
  display(temp)
  jsonlist = []
  counter = len(temp)
  # print("len = " + str(len(temp)))
  # print(counter)

  for i in range(0,counter):
    dt = temp.at[i, 'Timestamp'].strftime("%y-%m-%d %H:%M:%S")
    jsonlist.append({'timestamp': dt, 'original': temp.at[i, 'original'], 'isAbnormal' : temp.at[i, 'isAbnormal']})
  return jsonlist

def datesdf2json(datesdf):
  jsondates = []
  display(datesdf)
  print("datesdf shape -----------------------")
  print(datesdf.shape)
  for i in range(datesdf.shape[0]):
    starttime = datesdf.at[i, 'Timestamp_start']
    endtime = datesdf.at[i, 'Timestamp_end']
    jsondates.append({'timestamp_start' : starttime.strftime(EXACT_TIME_FORMAT), 'timestamp_end': endtime.strftime(EXACT_TIME_FORMAT)})

  print("json exact start and end dates")
  print(jsondates)
  return jsondates


def getdates(anomaly, hall_type):
  series = anomaly[hall_type]
  anomaly['prev'] = anomaly[hall_type].shift()
  anomaly['diff'] = anomaly[hall_type] - anomaly['prev']
  anomaly = anomaly.reset_index()
  ones = anomaly[anomaly['diff'] >= 1.0]
  ones.reset_index(inplace=True)
  negones = anomaly[anomaly['diff'] <= -1.0]
  negones.reset_index(inplace=True)
  temp = negones[['Timestamp']]

  datesdf = ones[['Timestamp']].join(temp, lsuffix="_start", rsuffix='_end')
  # Exact start and end time
  print("----------- kakaka join sucessfully")
  jsondates = datesdf2json(datesdf)

  # josn date range
  print(ones.columns)
  series = ones.loc[:, 'Timestamp']
  series = series.dt.date
  curr = series[0];
  next = series[0];
  lst = []

  for i in range(1, len(series)):
    item = series[i] - series[i - 1]
    days = pd.Timedelta("14d")
    oneday = pd.Timedelta("1d")
    if (item <= days):
      next = series[i]
    else:
      lst.append({"start": curr.strftime(DATE_FORMAT_OUTPUT), "end": next.strftime(DATE_FORMAT_OUTPUT)})
      curr = series[i]
      next = series[i]

    if (i == len(series) - 1):
      lst.append({"start": curr.strftime(DATE_FORMAT_OUTPUT), "end": next.strftime(DATE_FORMAT_OUTPUT)})
  print("returning jsondates df -> json, lst , list of json date range")
  return jsondates, lst


def moving_average_method(dataframe, hall_type):
  pass

if __name__ == "__main__":
  df = pd.read_csv("data/finalDHW.csv")
  exact, range, data = dhw_validate_and_predict(SELECT_COLUMN, df, TEST_METHOD, 5)





