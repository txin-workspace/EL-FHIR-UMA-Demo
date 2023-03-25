import logging

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s\t%(levelname)s\n%(message)s')

def error(msg):
    logging.error(msg)

def warning(msg):
    logging.warning(msg)

def info(msg):
    logging.info(msg)

def debug(msg):
    logging.debug(msg)

def print_response(resp):
    logging.debug('\tresponse_code: {}\
        \n\tresponse_head: {}\
        \n\tresponse_text: {}'.format(
            resp.status_code,resp.headers,resp.text))