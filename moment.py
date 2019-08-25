from datetime import timedelta


def days_passed(seconds):
    return timedelta(seconds=seconds).days


def get_seconds(days):
    return days*24*3600