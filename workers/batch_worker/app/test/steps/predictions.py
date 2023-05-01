from behave import given, then, when
import requests
import json



#Customs wants to know the difference of number of vehicules between summer holiday and march

@given("A developper for the customs website")
def log_in_dev1(context):
    pass

@when("He makes the predictions for 12 July 2020")
def get_response_for_july_prediction(application):
    response_12_july_traffic_in = requests.get("http://localhost:8080/predict-number/cars/in/12/07")
    response_12_july_traffic_out = requests.get("http://localhost:8080/predict-number/cars/out/12/07")
    traffic_in_12_july = response_12_july_traffic_in.json()["average number cars (in)"]
    traffic_out_12_july = response_12_july_traffic_out.json()["average number cars (out)"]
    global traffic_12_july
    traffic_12_july = traffic_in_12_july + traffic_out_12_july

@then("The result is greather than mid march")
def compare_march_and_july_traffic(application):
    response_20_march_traffic_in = requests.get("http://localhost:8080/predict-number/cars/in/20/03")
    response_20_march_traffic_out = requests.get("http://localhost:8080/predict-number/cars/out/20/03")
    traffic_in_20_march = response_20_march_traffic_in.json()["average number cars (in)"]
    traffic_out_20_march = response_20_march_traffic_out.json()["average number cars (out)"]
    traffic_20_march = traffic_in_20_march + traffic_out_20_march

    assert traffic_12_july > traffic_20_march




#Customs wants to know the number of vehicules during the morning rush hour

@given("A developper for the customs website who wants to know the issues of the morning traffic jam")
def log_in_dev2(context):
    pass

@when("He makes the predictions for 4 October at 8am")
def get_response_for_the_morning_4_october_prediction(application):
    response_4_october_8am_traffic_in = requests.get("http://localhost:8080/predict-number/cars/in/04/10/2020/8")
    response_4_october_8am_traffic_out = requests.get("http://localhost:8080/predict-number/cars/out/04/10/2020/8")
    traffic_in_4_october_8am = response_4_october_8am_traffic_in.json()["average number cars (in)"]
    traffic_out_4_october_8am = response_4_october_8am_traffic_out.json()["average number cars (out)"]
    global traffic_4_october_8am
    traffic_4_october_8am = traffic_in_4_october_8am + traffic_out_4_october_8am

@then("The result is greather than the traffic at 3pm")
def compare_morning_and_afternoon_traffic_jam(application):
    response_4_october_3pm_traffic_in = requests.get("http://localhost:8080/predict-number/cars/in/04/10/2020/15")
    response_4_october_3pm_traffic_out = requests.get("http://localhost:8080/predict-number/cars/out/04/10/2020/15")
    traffic_in_4_october_3pm = response_4_october_3pm_traffic_in.json()["average number cars (in)"]
    traffic_out_4_october_3pm = response_4_october_3pm_traffic_out.json()["average number cars (out)"]
    traffic_4_october_3pm = traffic_in_4_october_3pm + traffic_out_4_october_3pm

    assert traffic_4_october_8am > traffic_4_october_3pm




#Customs wants to know the number of trucks during Sunday

@given("A developper for the customs website who wants to know the issues of the Sunday traffic")
def log_in_dev3(context):
    pass

@when("He makes the predictions for 20 Sunday October number of trucks")
def get_response_for_the_20_october_prediction_number_trucks(application):
    response_20_october_traffic_in = requests.get("http://localhost:8080/predict-number/trucks/in/20/9/2020")
    response_20_october_traffic_out = requests.get("http://localhost:8080/predict-number/trucks/out/20/9/2020")
    traffic_in_20_october_= response_20_october_traffic_in.json()["average number trucks (in)"]
    traffic_out_20_october= response_20_october_traffic_out.json()["average number trucks (out)"]
    global traffic_20_october
    traffic_20_october = traffic_in_20_october_ + traffic_out_20_october

@then("The results is less than Wednesday in the same week")
def compare_wednesday_sunday_traffic_trucks(application):
    response_17_october_traffic_in = requests.get("http://localhost:8080/predict-number/trucks/in/17/9/2020")
    response_17_october_traffic_out = requests.get("http://localhost:8080/predict-number/trucks/out/17/4/2020")
    traffic_in_17_october = response_17_october_traffic_in.json()["average number trucks (in)"]
    traffic_out_17_october = response_17_october_traffic_out.json()["average number trucks (out)"]
    traffic_17_october = traffic_in_17_october + traffic_out_17_october

    assert traffic_20_october < traffic_17_october






#Tourism company wanted to know the waiting time at border for the first day of Easter Holiday

@given("A developper for the tourism company")
def log_in_dev4(context):
    pass

@when("He makes the predictions for first day of Easter Holiday")
def get_response_for_the_1_day_easter_holiday_prediction_waiting_time(application):
    response_16_april_waiting_time_in = requests.get("http://localhost:8080/predict-waiting-time/in/16/04/2022")
    response_16_april_waiting_time_out = requests.get("http://localhost:8080/predict-waiting-time/out/16/04/2022")
    waiting_time_in_16_april_ = response_16_april_waiting_time_in.json()["average waiting time (in)"]
    waiting_time_out_16_april = response_16_april_waiting_time_out.json()["average waiting time (out)"]
    global waiting_time_16_april
    waiting_time_16_april = waiting_time_in_16_april_ + waiting_time_out_16_april

@then("The result is greather than a normal day")
def result_greather_than_the_last_day(application):
    response_2_february_waiting_time_in = requests.get("http://localhost:8080/predict-waiting-time/in/02/02/2022")
    response_2_february_waiting_time_out = requests.get("http://localhost:8080/predict-waiting-time/out/02/02/2022")
    waiting_time_in_2_february = response_2_february_waiting_time_in.json()["average waiting time (in)"]
    waiting_time_out_2_february = response_2_february_waiting_time_out.json()["average waiting time (out)"]
    waiting_time_2_february = waiting_time_in_2_february + waiting_time_out_2_february

    assert waiting_time_16_april > waiting_time_2_february








#Truck company wanted to know the waiting time during night at the border

@given("A developper for the truck company")
def log_in_dev5(context):
    pass


@when("He makes the predictions for the night for trucks")
def get_response_for_prediction_waiting_time_during_night(application):
    response_16_april_1_waiting_time_in = requests.get("http://localhost:8080/predict-waiting-time/in/16/04/2022/1")
    response_16_april_1_waiting_time_out = requests.get("http://localhost:8080/predict-waiting-time/out/16/04/2022/1")
    waiting_time_in_16_april_1 = response_16_april_1_waiting_time_in.json()["average waiting time (in)"]
    waiting_time_out_16_april_1 = response_16_april_1_waiting_time_out.json()["average waiting time (out)"]
    global waiting_time_16_april_1
    waiting_time_16_april_1 = waiting_time_in_16_april_1 + waiting_time_out_16_april_1



@then("The result is greather than during the day")
def result_greather_than_the_day(application):
    response_15_april_1_waiting_time_in = requests.get("http://localhost:8080/predict-waiting-time/in/15/04/2022/15")
    response_15_april_1_waiting_time_out = requests.get("http://localhost:8080/predict-waiting-time/out/15/04/2022/15")
    waiting_time_in_15_april_1 = response_15_april_1_waiting_time_in.json()["average waiting time (in)"]
    waiting_time_out_15_april_1 = response_15_april_1_waiting_time_out.json()["average waiting time (out)"]
    waiting_time_15_april_1 = waiting_time_in_15_april_1 + waiting_time_out_15_april_1

    assert waiting_time_16_april_1 < waiting_time_15_april_1








