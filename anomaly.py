
from adtk.data import validate_series
from adtk.detector import SeasonalAD
from adtk.detector import LevelShiftAD
from adtk.detector import QuantileAD
from adtk.detector import InterQuartileRangeAD
import pandas as pd
import traceback

# global parameters . set to be constant if all caps, you can change methods by passing it as array
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
  dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'])
  # you need to set index as time in order for later joining and other precessing
  dataframe = dataframe.set_index('Timestamp')
  # this was for joining when timestamp was the same name it will become "unname column", it is just in case forgot to rename timestamp
  try:
    dataframe.drop(columns = ['Unnamed: 0'], inplace=True)
  except:
    print("do not need to remove column when changing index")
  return dataframe





def generate_train_only(date, dataframe):
  dataframe = validate_series(dataframe)
  return dataframe[:date]









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
      return InterQuartileRangeAD(c=IQR_C)
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


def dhw_validate_and_predict(hall_type, dataframe, method, date):
  dataframe = convert_datetime(dataframe)

  dataframe = select_and_interpolate(hall_type, dataframe)
  train_df = generate_train_only(date, dataframe)

  detector = choose_detector(method)
  anomaly = predict_plot_train(detector, method, train_df)
  # get actual data
  jsonlist = generate_json(train_df, anomaly, hall_type)
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


def generate_json(train_df, anomaly, hall_type):
  try:
    train_df = train_df.reset_index()
    anomaly = anomaly.reset_index()
    train_df.drop(['Timestamp'],axis = 1, inplace = True)
    train_df.rename({hall_type : 'original'}, axis = 1, inplace = True)
    anomaly.rename({hall_type : 'isAbnormal'}, axis = 1, inplace = True)
    temp = train_df.join(anomaly)
    # display(temp)
    #print("len = " + str(len(temp)))
    time_list = [item.strftime("%y-%m-%d %H:%M:%S") for item in temp.loc[:, 'Timestamp']]

    #when abnormalities are not consecutive for 4 hours or more, do not record them
    remove_non_consecutive_abnormalities(temp, "isAbnormal", "pressure_points", 5)

    abnormality_list = [item for item in temp['pressure_points']]
    last_day_has_leak_df = temp.loc[:, 'pressure_points'].iloc[-24: -1]


    dict_item = {'time_points' : time_list,
                 'pressure_points' : list(temp['original'].values),
                 'leak_points': abnormality_list,
                 'last_day_has_leak': len(last_day_has_leak_df[last_day_has_leak_df]) >= 1 }
    return dict_item
  except:
    traceback.print_exc()


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


def moving_average_method(dataframe, hall_type):
  pass


if __name__ == "__main__":
  df = pd.read_csv("data/finalDHW.csv")
  data = dhw_validate_and_predict(SELECT_COLUMN, df, TEST_METHOD, "2021-02-20")





