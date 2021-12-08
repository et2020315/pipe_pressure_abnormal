import pandas as pd
import app
from anomaly import dhw_validate_and_predict, dhw_validate_and_predict_get_df
import pandas as pd
import numpy as np

'''
This list contains the dates from the leaks of the hot domestic water distribution
system where pressure fluctuations were visible by eye with the pressure data.
The dates were originally compiled by the TAMU utilities team and then our team select the
visible fluctuations that occurred a few days before the indicated dates.
The incident numbers and dates come from the file DHW_Incidents1.pdf found in the MS Teams.
More data can be found in PipeLeakLocations.ipynb
'''
actual_pipeleak_fluctuation_days = [["2020-12-28 11:00", "2021-01-11 18:00"],  # incident 3
                                    ["2021-02-15 10:00", "2021-02-18 12:00"],
                                    ["2021-03-20 2:00", "2021-03-23 23:00"],  # incident 4
                                    ["2021-06-07 18:00", "2021-06-08 00:00"],  # incident 6
                                    ["2021-08-04 4:00", "2021-08-04 10:00"],  # incident 8
                                    ["2021-08-23 21:00", "2021-08-24 2:00"]]  # incident 9

'''
create the object pipeleaks_datelist_merged, which is a series of dates (each day in
which there was a leak)
'''
datelists_separated = [pd.date_range(e[0], e[1], freq="1H") for e in actual_pipeleak_fluctuation_days]

for index, datelist in enumerate(datelists_separated):
    if index == 0:
        pipeleaks_datelist_merged = datelist
    else:
        pipeleaks_datelist_merged = pipeleaks_datelist_merged.append(datelist)


def get_method_precision(method, day):
    buildings = app.get_all_buildings()['buildings']
    buildings = [item['name'] for item in buildings]
    data = [dhw_validate_and_predict_get_df(building, app.df, method, day)[1] for building in
            buildings]

    return np.any(data)


def get_method_false_positive(method, day_nums):
    count_days_false_positive = 0
    count_days_true_positive = 0
    count_days_false_negative = 0
    count_days_true_negative = 0
    # assert test_method_precision(['iqr'], [119]) == 1.0
    for day in pd.date_range("2020-12-29", "2021-10-01", freq="1H"):
        our_algorithm_detects_abnormality = get_method_precision(method, day) == 1.0
        there_is_actual_leak = day in day_nums
        if our_algorithm_detects_abnormality and there_is_actual_leak:
            count_days_true_positive += 1
        elif our_algorithm_detects_abnormality and not there_is_actual_leak:
            count_days_false_positive += 1
        elif not our_algorithm_detects_abnormality and there_is_actual_leak:
            count_days_false_negative += 1
        else:
            count_days_true_negative += 1

    print("true positive = " + str(count_days_true_positive))
    print("false positive = " + str(count_days_false_positive))
    print(" false negative = " + str(count_days_false_negative))
    print("true negative = " + str(count_days_true_negative))

    return (count_days_true_positive / (count_days_true_positive + count_days_false_positive)), \
           (count_days_true_positive / (count_days_true_positive + count_days_false_negative))


def test_error_rate():
    print("iqr = ")
    print(get_method_false_positive(['iqr'], pipeleaks_datelist_merged))
    #print("seasonal = ")
    #print(get_method_false_positive(['seasonal'],pipeleaks_datelist_merged ))
    #print("quartile = ")
    #print(get_method_false_positive(['quartile'], pipeleaks_datelist_merged))
    #print("level = ")
    #print(get_method_false_positive(['level'], pipeleaks_datelist_merged))

#
# check if precisions are 100%
def test_precision_iqr():
    precision, recall = get_method_false_positive(['iqr'], pipeleaks_datelist_merged)
    assert precision == 1.0

# check if precisions are 100%
def test_recall_iqr():
    precision, recall = get_method_false_positive(['iqr'], pipeleaks_datelist_merged)
    assert recall == 1.0


def test_precision_quartile():
    precision, recall = get_method_false_positive(['quartile'], pipeleaks_datelist_merged)
    assert precision == 1.0

def test_recall_quartile():
    precision, recall = get_method_false_positive(['quartile'], pipeleaks_datelist_merged)
    assert recall == 1.0


def test_precision_seasonal():
    precision, recall = get_method_false_positive(['seasonal'], pipeleaks_datelist_merged)
    assert precision == 1.0


def test_recall_seasonal():
    precision, recall = get_method_false_positive(['seasonal'], pipeleaks_datelist_merged)
    assert recall == 1.0

def test_precision_level():
    precision, recall = get_method_false_positive(['level'], pipeleaks_datelist_merged)
    assert precision == 1.0


def test_recall_level():
    precision, recall = get_method_false_positive(['level'], pipeleaks_datelist_merged)
    assert recall == 1.0