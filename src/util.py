from datetime import datetime

def validate_and_convert_date(date_str: str) -> datetime.date:
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return date
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def seconds_from_past_to_now(past_date: datetime.date) -> int:
    past_datetime = datetime.combine(past_date, datetime.min.time())
    now = datetime.now()
    difference = now - past_datetime
    return int(difference.total_seconds())