import json
import datetime


def http_request_log_json(request):
    log_dict = {}
    log_dict['request_time'] = get_curr_time()
    log_dict['method'] = request.method
    return json.dumps(log_dict)


def scrap_request_log_json(curr_time, url, is_error):
    log_dict = {}
    log_dict['request_time'] = curr_time 
    log_dict['scrapped_url'] = url
    log_dict['is_error'] = is_error
    return json.dumps(log_dict)


def scrap_error_log_json(curr_time, url, err_msg):
    log_dict = {}
    log_dict['request_time'] = curr_time 
    log_dict['scrapped_url'] = url
    log_dict['err_msg'] = err_msg 
    return json.dumps(log_dict)
    

def get_curr_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

