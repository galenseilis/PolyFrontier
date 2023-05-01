from datetime import timedelta





def daterange(start_date_, end_date_):
    # https://stackoverflow.com/a/1060330
    for n in range(int((end_date_ - start_date_).days)):
        yield start_date_ + timedelta(n)


