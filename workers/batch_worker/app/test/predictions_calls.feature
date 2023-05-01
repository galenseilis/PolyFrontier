# Example

Feature: Prediction through the main API
    An API where developpers can make predictions


    Scenario: Customs wants to know the number of vehicules during summer holiday
        Given A developper for the customs website
        When He makes the predictions for 12 July 2020
        Then The result is greather than mid march

    Scenario: Customs wants to know the number of vehicules during the morning rush hour
        Given A developper for the customs website who wants to know the issues of the morning traffic jam
        When He makes the predictions for 4 October at 8am
        Then The result is greather than the traffic at 3pm

    Scenario: Customs wants to know the number of trucks during Sunday
        Given A developper for the customs website who wants to know the issues of the Sunday traffic
        When He makes the predictions for 20 Sunday October number of trucks
        Then The results is less than Wednesday in the same week


    Scenario: Tourism company wanted to know the waiting time at border for the first day of Easter Holiday
        Given A developper for the tourism company
        When He makes the predictions for first day of Easter Holiday
        Then The result is greather than a normal day



    Scenario: Truck company wanted to know the waiting time during night at the border
        Given A developper for the truck company
        When He makes the predictions for the night for trucks
        Then The result is greather than during the day



