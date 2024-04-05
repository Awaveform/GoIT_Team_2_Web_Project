from datetime import datetime


def get_seconds_between_curr_date(future_timestamp: int) -> int:
    """
    Method calculates time difference in seconds between future date and current date.
    :param future_timestamp: Future date in timestamp format.
    :type future_timestamp: int.
    :return: Time difference in seconds.
    :rtype: int.
    """
    future_datetime_obj = datetime.utcfromtimestamp(future_timestamp)
    current_datetime = datetime.utcnow()
    time_difference = future_datetime_obj - current_datetime
    time_diff_in_seconds = time_difference.total_seconds()
    return int(time_diff_in_seconds)
