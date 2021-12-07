
from adtk.data import validate_series
from adtk.detector import SeasonalAD
from adtk.detector import LevelShiftAD
from adtk.detector import QuantileAD
from adtk.detector import InterQuartileRangeAD
import pandas as pd
import traceback

# global parameters . set to be constant if all caps, you can change methods by passing it as array
NUM_CONSECUTIVE_ANOMALIES_ALLOWED = 2
# Interquartile
IQR_C = 3.0
#**** Quartile method
HIGH_Q = 1.0
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
  dataframe['time_points'] = pd.to_datetime(dataframe['time_points'])
  # you need to set index as time in order for later joining and other precessing
  dataframe = dataframe.set_index('time_points')
  # this was for joining when timestamp was the same name it will become "unname column", it is just in case forgot to rename timestamp
  try:
    dataframe = dataframe.drop(columns = ['Unnamed: 0'])
  except:
    print("do not need to remove column when changing index")
  return dataframe


def generate_train_only(date, dataframe):
  dataframe = validate_series(dataframe)
  return dataframe[:date]


# use 'time' interpolation to fill the gaps
def interpolate(dataframe):
  if (len(dataframe.isna().any(axis = 1)) > 0):
    dataframe["pressure_points"] = dataframe["pressure_points"].interpolate(method = 'time')
  return dataframe


# choose which detector to use
def choose_detector(method):
  try:
    # method is a list
    if method[0] == 'seasonal':
      return SeasonalAD(freq=WINDOW_SEASON)
    elif method[0] == 'iqr':
      return InterQuartileRangeAD(c=IQR_C)
    elif method[0] == 'quartile':
      return QuantileAD(low=LOW_Q, high=HIGH_Q)
    elif method[0] == 'level':
      return LevelShiftAD(c=AWAY_FROM_MU_LEVEL, side='both', window=WINSIZE_LEVEL)
  except:
    traceback.print_exc()


# anomaly_df is a true or false dataframe, plot function just plot the graph
def predict_plot_train(detector, train_df):
  detector.fit(train_df)
  train_df.loc[:, "leak_points"] = detector.detect(train_df)

  return train_df

# ALL DATAFRAMES that go through
# dhw_validate_and_predict_get_df must be refined with this dataframe!
def refine_dataframe(dataframe):
  dataframe = dataframe.rename(columns={"Timestamp": "time_points"})
  dataframe = convert_datetime(dataframe)

  return dataframe


def dhw_validate_and_predict_get_df(hall_type: str, dataframe : pd.DataFrame, method : [str], date):
  dataframe = dataframe.rename(columns={hall_type: "pressure_points"})
  dataframe = dataframe[["pressure_points"]]
  dataframe = interpolate(dataframe)
  train_df = generate_train_only(date, dataframe)
  detector = choose_detector(method)
  anomaly_with_train_df = predict_plot_train(detector, train_df)

  last_day_has_leak_df = anomaly_with_train_df["leak_points"].iloc[-24: -1]
  last_day_has_leak = len(last_day_has_leak_df[last_day_has_leak_df]) >= 1

  return anomaly_with_train_df, last_day_has_leak


def dhw_validate_and_predict(hall_type, dataframe, method, date):
  train_df_with_anomaly, last_day_has_leak = dhw_validate_and_predict_get_df(hall_type, dataframe, method, date)

  jsonlist = generate_json(train_df_with_anomaly, last_day_has_leak)
  return jsonlist


def remove_non_consecutive_abnormalities(df, column_name, new_column_name, num_of_consecutive_trues):
  new_data = []
  subleak_points = df[column_name]
  count = 0
  for index, item in enumerate(subleak_points):
    next_is_false = True if index + 1 >= len(subleak_points) else not subleak_points.iloc[index + 1]
    if item:
      count += 1
      if next_is_false and count >= num_of_consecutive_trues:
        for i in range(count):
          new_data.append(True)
      elif next_is_false:
        for i in range(count):
          new_data.append(False)
      else:
        continue
    else:
      count = 0
      new_data.append(False)

  df[new_column_name] = new_data


def generate_json(train_df_with_anomaly: pd.DataFrame, last_day_has_leak : bool):
  # when abnormalities are not consecutive for 4 hours or more, do not record them
  #remove_non_consecutive_abnormalities(temp, "isAbnormal", "pressure_points", NUM_CONSECUTIVE_ANOMALIES_ALLOWED)
  dataframe = train_df_with_anomaly.reset_index()
  dataframe["time_points"] = dataframe["time_points"].dt.strftime(EXACT_TIME_FORMAT)
  dict_item = dataframe.to_dict("list")
  dict_item["last_day_has_leak"] = last_day_has_leak

  return dict_item


if __name__ == "__main__":
  df = pd.read_csv("data/finalDHW.csv")
  data = dhw_validate_and_predict(SELECT_COLUMN, df, TEST_METHOD, "2021-02-20")





