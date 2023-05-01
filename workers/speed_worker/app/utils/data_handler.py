from app.utils.data_generator import generate_waiting_time_data, data, generate_waiting_time_for_date
from app.utils.date_manager import get_day_and_month, get_date_from_date_month_year, is_weekend

generate_waiting_time_data()


def get_average_waiting_time_date(date):
    saved_date = date
    day, month = get_day_and_month(date)
    dates = [get_date_from_date_month_year(day, month, year) for year in range(2019, 2022)]
    waiting_time_non_weekend, non_weekend = 0, 0
    waiting_time_weekend, weekend = 0, 0
    for date in dates:
        if date in data:
            if is_weekend(date):
                waiting_time_weekend += data[date]
                weekend += 1
            else:
                waiting_time_non_weekend += data[date]
                non_weekend += 1
    if is_weekend(saved_date):
        if weekend != 0:
            return waiting_time_weekend / weekend
    else:
        if non_weekend != 0:
            return waiting_time_non_weekend / non_weekend
    return generate_waiting_time_for_date(saved_date)
