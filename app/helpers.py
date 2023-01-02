from datetime import datetime
import pytz


def get_date():
    return datetime.today()


def get_date_and_time():
    zone = pytz.timezone("Europe/Ljubljana")
    now = datetime.now(tz=zone)
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string
