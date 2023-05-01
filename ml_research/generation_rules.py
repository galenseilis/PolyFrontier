from datetime import datetime

from ml_research.generation_utils import daterange


def special_events_between(begin, end):
    return (d.strftime("%d/%m") for d in daterange(begin, end))


rules = {
    "avg_truck_waiting": 7,
    "avg_car_waiting": 3,
    "variations": {
        "trucks_ratio_variation_in": 0.1,
        "trucks_ratio_variation_out": 0.15,
        "avg_truck_waiting_variation": 0.4,
        "avg_car_waiting_variation": 0.25
    },
    "days": {
        "Monday": {
            "min_in": 2900,
            "max_in": 3200,
            "trucks_ratio_in": 1 / 10,
            "min_out": 3000,
            "max_out": 3200,
            "trucks_ratio_out": 1 / 9,
            "number_of_service_present_per_hour": 4
        },
        "Tuesday": {
            "min_in": 2700,
            "max_in": 3100,
            "trucks_ratio_in": 1 / 11,
            "min_out": 3000,
            "max_out": 3300,
            "trucks_ratio_out": 1 / 10,
            "number_of_service_present_per_hour": 4
        },
        "Wednesday": {
            "min_in": 3000,
            "max_in": 3100,
            "trucks_ratio_in": 1 / 8,
            "min_out": 2700,
            "max_out": 3100,
            "trucks_ratio_out": 1 / 9,
            "number_of_service_present_per_hour": 3
        },
        "Thursday": {
            "min_in": 2600,
            "max_in": 3100,
            "trucks_ratio_in": 1 / 12,
            "min_out": 2800,
            "max_out": 3100,
            "trucks_ratio_out": 1 / 7,
            "number_of_service_present_per_hour": 4
        },
        "Friday": {
            "min_in": 2900,
            "max_in": 3100,
            "trucks_ratio_in": 1 / 10,
            "min_out": 2800,
            "max_out": 3100,
            "trucks_ratio_out": 1 / 10,
            "number_of_service_present_per_hour": 4
        },
        "Saturday": {
            "min_in": 2900,
            "max_in": 3100,
            "trucks_ratio_in": 1 / 16,
            "min_out": 3100,
            "max_out": 3200,
            "trucks_ratio_out": 1 / 17,
            "number_of_service_present_per_hour": 5
        },
        "Sunday": {
            "min_in": 1600,
            "max_in": 1800,
            "trucks_ratio_in": 1 / 25,
            "min_out": 1700,
            "max_out": 2400,
            "trucks_ratio_out": 1 / 26,
            "number_of_service_present_per_hour": 5
        }
    },
    "special_events": {
        "dates": {

            d: f for dates, f in zip(
                [
                    special_events_between(datetime(1970, 10, 23), datetime(1970, 11, 8)),  # toussaint
                    special_events_between(datetime(1970, 12, 18), datetime(1970, 1, 3)),  # noel
                    special_events_between(datetime(1970, 2, 12), datetime(1970, 3, 7)),  # hiver
                    special_events_between(datetime(1970, 4, 16), datetime(1970, 5, 9)),  # printemps
                    special_events_between(datetime(1970, 7, 7), datetime(1970, 8, 30))  # ete
                ],
                [(2.3, 0.7), (2.5, 0.3), (2.3, 0.7), (2.1, 0.8), (2.7, 0.6)]
            ) for d in dates
        },
        "meteo": {
            "soleil": (1, 1),
            "pluie": (0.89, 1.4),
            "nuageux": (0.96, 1.1),
            "neige": (0.5, 0.6),
            "tempete": (0.2, 0.3)
        }
    }
}
