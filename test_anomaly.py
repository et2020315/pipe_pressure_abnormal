import pandas as pd
import app
from anomaly import dhw_validate_and_predict

#45: incident on jan 5 2021
#119: incident on mar 21 2021
#196, incident on jun 5, 2021
#200: incident on jun 8, 2021
#278: incident on aug 21, 2021

actual_pipeleak_days = [45, 119, 196, 200, 278]

def test_method_precision(method, day_nums):
    matches_actual_leak_vs_found_leak = 0
    for item in day_nums:
        buildings = app.all_buildings()['buildings']
        buildings = [item['name'] for item in buildings]
        data = [dhw_validate_and_predict(building, app.df, method, item, app.STARTING_TRAINING_DAYS) for building in buildings]
        has_at_least_one_leak_detected = False
        for subitem in data:
            if subitem['last_day_has_leak']:
                has_at_least_one_leak_detected = True
                break

        if has_at_least_one_leak_detected:
            matches_actual_leak_vs_found_leak += 1

    #return precision
    return matches_actual_leak_vs_found_leak / len(day_nums)

def test_method_false_positive(method, day_nums):
    count_days_false_positive = 0
    count_days_true_positive = 0
    count_days_false_negative = 0
    count_days_true_negative = 0
    #assert test_method_precision(['iqr'], [119]) == 1.0
    for day in range(1, 100):
        our_algorithm_detects_abnormality = test_method_precision(method, [day]) ==1.0
        there_is_actual_leak = day in day_nums
        if (our_algorithm_detects_abnormality and there_is_actual_leak):
            count_days_true_positive += 1
        elif (our_algorithm_detects_abnormality and not there_is_actual_leak):
            count_days_false_positive += 1
        elif (not our_algorithm_detects_abnormality and there_is_actual_leak):
            count_days_false_negative += 1
        else:
            count_days_true_negative += 1

    print("true positive = " + str(count_days_true_positive))
    print("false positive = " + str(count_days_false_positive))
    print(" false negative = " + str(count_days_false_negative))
    print("true negative = " + str(count_days_true_negative))
    return (count_days_false_positive + count_days_false_negative) / (100)

def test():
    assert test_method_false_positive(['iqr'], actual_pipeleak_days) == 1.0

#check if precisions are 100%
def test_iqr():
    assert test_method_precision(['iqr'], actual_pipeleak_days) == 1.0

def test_quartile():
    assert test_method_precision(['quartile'], actual_pipeleak_days) == 1.0

def test_seasonal():
    assert test_method_precision(['seasonal'], actual_pipeleak_days) == 1.0

def test_level():
    assert test_method_precision(['level'], actual_pipeleak_days) == 1.0