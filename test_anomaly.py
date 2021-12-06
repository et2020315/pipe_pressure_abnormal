import pandas as pd
import app
from anomaly import dhw_validate_and_predict
import pandas as pd

'''
This list contains the dates from the leaks of the hot domestic water distribution
system where pressure fluctuations were visible by eye with the pressure data.
The dates were originally compiled by the TAMU utilities team and then our team select the
visible fluctuations that occurred a few days before the indicated dates.
The incident numbers and dates come from the file DHW_Incidents1.pdf found in the MS Teams.
More data can be found in PipeLeakLocations.ipynb
'''
actual_pipeleak_fluctuation_days = [["2020-12-29", "2021-01-12"],  # incident 3
                                    ["2021-03-20", "2021-03-23"],  # incident 4
                                    ["2021-06-07", "2021-06-08"],  # incident 6
                                    ["2021-08-04", "2021-08-04"],  # incident 8
                                    ["2021-08-23", "2021-08-24"]]  # incident 9

'''
create the object pipeleaks_datelist_merged, which is a series of dates (each day in
which there was a leak)
'''
datelists_separated = [pd.date_range(e[0], e[1]) for e in actual_pipeleak_fluctuation_days]

for index, datelist in enumerate(datelists_separated):
    if index == 0:
        pipeleaks_datelist_merged = datelist
    else:
        pipeleaks_datelist_merged = pipeleaks_datelist_merged.append(datelist)


def get_method_precision(method, day_nums):
    matches_actual_leak_vs_found_leak = 0
    for item in day_nums:
        buildings = app.get_all_buildings()['buildings']
        buildings = [item['name'] for item in buildings]
        data = [dhw_validate_and_predict(building, app.df, method, item) for building in
                buildings]
        has_at_least_one_leak_detected = False
        for subitem in data:
            if subitem['last_day_has_leak']:
                has_at_least_one_leak_detected = True
                break

        if has_at_least_one_leak_detected:
            matches_actual_leak_vs_found_leak += 1

    # return precision
    return matches_actual_leak_vs_found_leak / len(day_nums)


def get_method_false_positive(method, day_nums):
    count_days_false_positive = 0
    count_days_true_positive = 0
    count_days_false_negative = 0
    count_days_true_negative = 0
    # assert test_method_precision(['iqr'], [119]) == 1.0
    for day in pd.date_range("2020-12-29", "2021-10-01"):
        our_algorithm_detects_abnormality = get_method_precision(method, [day]) == 1.0
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
    print(get_method_false_positive(['iqr'], pipeleaks_datelist_merged))


# check if precisions are 100%
def test_precision_iqr():
    assert get_method_precision(['iqr'], pipeleaks_datelist_merged) == 1.0


def test_precision_quartile():
    assert get_method_precision(['quartile'], pipeleaks_datelist_merged) == 1.0


def test_precision_seasonal():
    assert get_method_precision(['seasonal'], pipeleaks_datelist_merged) == 1.0


def test_precision_level():
    assert get_method_precision(['level'], pipeleaks_datelist_merged) == 1.0
