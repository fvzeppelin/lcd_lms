import logging
from sys import exit
from telnetlib import Telnet
from re import sub
from urllib.parse import unquote

class Lms:

    def __init__(self, lms, lmsport):
        self.lmshost = lms
        self.lmsport = lmsport
        try:
            self.lms = Telnet(lms, lmsport)
        except Exception as e:
            exit('cannot connect to LMS server at ' + self.lmshost + ':' + self.lmsport + ': {0}'.format(e))
        logging.info('connected to LMS server at ' + self.lmshost + ':' + self.lmsport)

    def send_receive(self, question, raw = False):
        try:
            if (raw == False):
                self.lms.write(question.encode('ascii') + b' ?\n')
            else:
                self.lms.write(question.encode('ascii') + b'\n')
            answer = self.lms.read_until(b'\n').decode('utf-8')[:-1]
        except Exception as e:
            logging.warning('lms_send_receive: cannot connect to LMS server at ' + self.lmshost + ':' + self.lmsport + ': {0}'.format(e))
        if (raw == False):
            answer = sub('^' + question + '\s', '', answer)
            answer = unquote(answer)
        logging.debug('lms_send_receive: send ' + question + ' ?')
        logging.debug('lms_send_receive: receive ' + answer)
        return answer

    def send_player(self, question, id):
        question = id + ' ' + question + "\n"
        try:
            self.lms.write(question.encode('ascii'))
        except Exception as e:
            logging.warning('lms_send_player: cannot connect to LMS server at ' + self.lmshost + ':' + self.lmsport + ': {0}'.format(e))
        logging.debug('lms_send_player: send ' + question[:-1])

    def check_queue(self):
        response = ''
        try:
            response = self.lms.read_very_eager().decode('utf-8')[:-1]
        except Exception as e:
            logging.warning('lms_check_queue: cannot connect to LMS server at ' + self.lmshost + ':' + self.lmsport + ': {0}'.format(e))
        if (response != ''):
            response = unquote(response)
            logging.debug('lms_check_queue: received: ' + response)
            return response
        else:
            return None
