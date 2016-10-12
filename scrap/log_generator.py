import json
import datetime


def http_request_log_json(request):
    """
        HTTP Request: (요청날짜/시간, method)
        로그 목적: 사용자 접속횟수를 분석을 위함
    """
    log_dict = {}
    log_dict['log_name'] = 'http-request'
    log_dict['request_time'] = get_curr_time()
    log_dict['method'] = request.method
    return json.dumps(log_dict)


def scrap_request_log_json(curr_time, url, is_error):
    """
        Scrap Request: (요청날짜/시간, 요청 URL, Error 유무)
        로그 목적: 전체 스크랩 요청 횟수 파악, URL별 스크랩 요청 횟수 파악
    """
    log_dict = {}
    log_dict['log_name'] = 'scrap-request'
    log_dict['request_time'] = curr_time 
    log_dict['scrapped_url'] = url
    log_dict['is_error'] = is_error
    return json.dumps(log_dict)


def scrap_error_log_json(curr_time, url, err_msg):
    """
        Scrap Error: (요청날짜/시간, 요청 URL, Error 메시지)
        로그 목적: 어떤 에러가 났는지에 파악
    """
    log_dict = {}
    log_dict['log_name'] = 'scrap-error'
    log_dict['request_time'] = curr_time 
    log_dict['scrapped_url'] = url
    log_dict['err_msg'] = err_msg 
    return json.dumps(log_dict)
    

def cache_access_log_json(server_name, access_method, url):
    """
        Cache Access: (접근날짜/시간, 접근캐시서버 이름, 캐시저장or조회, 접근 URL)
        로그 목적: 각 캐시 서버별 접근(api 데이터 SET, GET) 횟수를 통해,
                   각 캐시 서버별 부하 상황을 체크할 수 있기 위함.
    """
    log_dict = {}
    log_dict['log_name'] = 'cache-access'
    log_dict['request_time'] = get_curr_time() 
    log_dict['cached_server_name'] = server_name
    log_dict['cache_method'] = access_method
    log_dict['cached_url'] = url
    return json.dumps(log_dict)


def other_errors_log_json(err_msg):
    """
        Other Errors: (날짜/시간, StackTrace)
        로그 목적: 스크랩을 제외한 파악가능한 모든 에러의 message를 로그화한다.
    """
    log_dict = {}
    log_dict['log_name'] = 'other-error'
    log_dict['error_time'] = get_curr_time() 
    log_dict['error_msg'] = err_msg
    return json.dumps(log_dict)



def get_curr_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

