

class FilterForCustomsDataPerDay():
    def __init__(self, df ):
        self.df=df
        self.high_bound_waiting_time = 360
        self.high_bound_number_vehicules = 10000

    def process(self):
        columns_name = self.df.columns
        for i in range(1, len(columns_name)):
            if columns_name[i] == 'avg_waiting_in' or columns_name[i] == 'avg_waiting_out':
                self.df = self.df.loc[ (self.df[columns_name[i]] <= self.high_bound_waiting_time)
                                       & (self.df[columns_name[i]] >= 0) ]
            else :
                self.df = self.df.loc[ (self.df[columns_name[i]] <= self.high_bound_number_vehicules)
                                      & (self.df[columns_name[i]] >= 0) ]

class FilterForCustomsDataPerHour(FilterForCustomsDataPerDay):
    def __init__(self, df):
        FilterForCustomsDataPerDay.__init__(self, df)
        self.high_bound_number_vehicules /= 24


class FilterForWeatherData():
    def __init__(self, df ):
        self.df = df
        self.avg_temperature_low_bound = -25
        self.avg_temperature_high_bound = 45
        self.pressure_low_bound = 950
        self.pressure_high_bound = 1050
        self.windspeed_low_bound = 0
        self.windspeed_high_bound = 250
        self.precipitaion_MM_low_bound = 0
        self.precipitaion_MM_high_bound = 200

    def process(self):
        columns_name = self.df.columns
        for i in range(1, len(columns_name)):
            if columns_name[i] == "avg_temperature" :
                self.df = self.df.loc[ (self.df[columns_name[i]] <= self.avg_temperature_high_bound) &
                                      (self.df[columns_name[i]] >= self.avg_temperature_low_bound) ]
            elif columns_name[i] == "pressure" :
                self.df = self.df.loc[ (self.df[columns_name[i]] <= self.pressure_high_bound) &
                                      (self.df[columns_name[i]] >= self.pressure_low_bound)]
            elif columns_name[i] == "windspeed" :
                self.df = self.df.loc[ (self.df[columns_name[i]] <= self.windspeed_high_bound) &
                                      (self.df[columns_name[i]] >= self.windspeed_low_bound) ]
            elif columns_name[i] == "precipitaion_MM" :
                self.df = self.df.loc[ (self.df[columns_name[i]] <= self.precipitaion_MM_high_bound) &
                                      (self.df[columns_name[i]] >= self.precipitaion_MM_low_bound)]




