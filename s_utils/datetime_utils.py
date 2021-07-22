import datetime


def get_datetime_borders_from_args(args, latest_utc_hour=False):
    start_date = args.start_date
    end_date = args.end_date

    if end_date:
        end_timestamp = datetime.datetime.strptime(end_date, "%y-%m-%d")
    else:
        dt_now = datetime.datetime.now()
        end_timestamp = datetime.datetime(dt_now.year, dt_now.month, dt_now.day)

    if start_date:
        start_timestamp = datetime.datetime.strptime(start_date, "%y-%m-%d")
    else:
        start_timestamp = end_timestamp - datetime.timedelta(1)
    if latest_utc_hour:
        end_timestamp = datetime.datetime.utcnow()
    return start_timestamp, end_timestamp