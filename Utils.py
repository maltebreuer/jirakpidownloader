import datetime


def epoch_with_milli_to_iso(timestamp):
    dt = datetime.datetime.utcfromtimestamp((int(round(timestamp / 1000))))
    return dt.isoformat() + '.' + str(timestamp % 1000) + 'Z'
