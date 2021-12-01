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


#check if precisions are 100%
def test_iqr():
    assert test_method_precision(['iqr'], actual_pipeleak_days) == 1.0

def test_quartile():
    assert test_method_precision(['quartile'], actual_pipeleak_days) == 1.0

def test_seasonal():
    assert test_method_precision(['seasonal'], actual_pipeleak_days) == 1.0

def test_level():
    assert test_method_precision(['level'], actual_pipeleak_days) == 1.0