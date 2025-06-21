import datetime
import json

def convert_datetime(obj):
    if isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime(i) for i in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        return obj

def safe_json_dump(data, fp, **kwargs):
    json.dump(convert_datetime(data), fp, **kwargs)

def safe_json_dumps(data, **kwargs):
    return json.dumps(convert_datetime(data), **kwargs)
