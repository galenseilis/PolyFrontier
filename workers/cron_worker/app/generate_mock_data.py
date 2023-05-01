from copy import deepcopy
import random

import ciw

from app import generation_rules
from app.generation_utils import daterange


def split(x, n):
    if x % n == 0:
        return [x // n for _ in range(n)]
    zp = n - (x % n)
    pp = x // n
    return [pp + 1 if i >= zp else pp for i in range(n)]


def avg_flow_per_hour(l):
    return sum(l) / 24


def simulate_queue_day(number_of_vehicles, service_distributions, number_of_servers):
    arrival_distribution = number_of_vehicles / 60
    network = ciw.create_network(
        arrival_distributions=[ciw.dists.Exponential(rate=arrival_distribution)],
        service_distributions=[ciw.dists.Exponential(rate=service_distributions)],
        number_of_servers=[number_of_servers]
    )

    ciw.seed(1)

    queue = ciw.Simulation(network)
    queue.simulate_until_max_time(60)

    recs = queue.get_all_records()

    waits = [r.waiting_time for r in recs]

    mean_waiting_time = sum(waits) / len(waits)
    return mean_waiting_time


class MockDataGenerator:

    def __init__(self):
        self.rules = generation_rules.rules

    @property
    def get_generation_headers(self):
        return [
            "ts", "avg_nb_vehicules_in_per_hour", "nb_trucks_in", "nb_cars_in", "avg_waiting_in",
            "avg_nb_vehicules_out_per_hour", "nb_trucks_out", "nb_cars_out", "avg_waiting_out"
        ]

    def __is_special(self, date):
        return date.strftime("%d/%m") in self.rules["special_events"]["dates"]

    def __get_generation_parameters(self, date):
        params = self.rules["days"][date.strftime("%A")]
        params["trucks_ratio_variation_in"] = self.rules["variations"]["trucks_ratio_variation_in"]
        params["trucks_ratio_variation_out"] = self.rules["variations"]["trucks_ratio_variation_out"]
        params["avg_truck_waiting"] = self.rules["avg_truck_waiting"]
        params["avg_car_waiting"] = self.rules["avg_car_waiting"]
        params["avg_truck_waiting_variation"] = self.rules["variations"]["avg_truck_waiting_variation"]
        params["avg_car_waiting_variation"] = self.rules["variations"]["avg_car_waiting_variation"]
        if self.__is_special(date):
            params = deepcopy(params)
            factors = self.rules["special_events"]["dates"][date.strftime("%d/%m")]
            params["min_in"] = int(params["min_in"] * factors[0])
            params["max_in"] = int(params["max_in"] * factors[0])
            params["min_out"] = int(params["min_out"] * factors[0])
            params["max_out"] = int(params["max_out"] * factors[0])
            params["trucks_ratio_in"] *= factors[1]
            params["trucks_ratio_out"] *= factors[1]
            params["number_of_service_present_per_hour"] = int(params["number_of_service_present_per_hour"]
                                                               * factors[0] / 1.8)
        return params

    @staticmethod
    def __generate_for_in(generation_list, gen_params):
        nb_vehicules_in = random.randint(gen_params["min_in"], gen_params["max_in"] + 1)
        list_in_per_hour = split(nb_vehicules_in, 24)
        avg_nb_vehicules_in_per_hour = avg_flow_per_hour(list_in_per_hour)
        generation_list.append(int(avg_nb_vehicules_in_per_hour))  # nb_vehicules_in
        trucks_ratio_in = gen_params["trucks_ratio_in"] * random.uniform(1 - gen_params["trucks_ratio_variation_in"],
                                                                         1 + gen_params["trucks_ratio_variation_in"])
        nb_trucks_in = int(nb_vehicules_in * trucks_ratio_in)
        generation_list.append(nb_trucks_in)  # nb_trucks_in
        nb_cars_in = nb_vehicules_in - nb_trucks_in
        generation_list.append(nb_cars_in)  # nb_cars_in
        number_of_services = gen_params["number_of_service_present_per_hour"]
        avg_waiting_time_in = simulate_queue_day(avg_nb_vehicules_in_per_hour, 0.1, number_of_services)
        generation_list.append(avg_waiting_time_in)  # avg_waiting_in

    @staticmethod
    def __generate_for_out(generation_list, gen_params):
        nb_vehicules_out = random.randint(gen_params["min_out"], gen_params["max_out"] + 1)
        list_out_per_hour = split(nb_vehicules_out, 24)
        avg_nb_vehicules_out_per_hour = avg_flow_per_hour(list_out_per_hour)
        generation_list.append(int(avg_nb_vehicules_out_per_hour))
        trucks_ratio_out = gen_params["trucks_ratio_out"] * random.uniform(1 - gen_params["trucks_ratio_variation_out"],
                                                                           1 + gen_params["trucks_ratio_variation_out"])
        nb_trucks_out = int(nb_vehicules_out * trucks_ratio_out)
        generation_list.append(nb_trucks_out)  # nb_trucks_out
        nb_cars_out = nb_vehicules_out - nb_trucks_out
        generation_list.append(nb_cars_out)  # nb_cars_out
        number_of_services = gen_params["number_of_service_present_per_hour"]
        avg_waiting_time_out = simulate_queue_day(avg_nb_vehicules_out_per_hour, 0.1, number_of_services)
        generation_list.append(avg_waiting_time_out)  # avg_waiting_out

    def generate_for_date(self, date):
        generation_params = self.__get_generation_parameters(date)
        generation_list = [date.timestamp()]
        MockDataGenerator.__generate_for_in(generation_list, generation_params)
        MockDataGenerator.__generate_for_out(generation_list, generation_params)
        return generation_list

    def generate_between_dates(self, start_date, end_date):
        for single_date in daterange(start_date, end_date):
            yield self.generate_for_date(single_date)
