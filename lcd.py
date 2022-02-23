import logging
from sys import exit
from telnetlib import Telnet

class Lcd:

    def __init__(self, lcdd, lcdport):
        self.lcdd = lcdd
        self.lcdport = lcdport
        try:
            self.lcd = Telnet(lcdd, lcdport)
        except Exception as e:
            exit('cannot connect to LCDd daemon at ' + self.lcdd + ':' + self.lcdport + ': {0}'.format(e))
        logging.info('connected to LCDd daemon at ' + self.lcdd + ':' + self.lcdport)

    def send_receive(self, question):
        try:
            self.lcd.write(question.encode('iso-8859-1') + b'\n')
            answer = self.lcd.read_until(b'\n').decode('utf-8')[:-1]
        except Exception as e:
            logging.waring('lcd_send_receive: cannot connect to LCDd daemon at ' + self.lcdd + ':' + self.lcdport + ': {0}'.format(e))
        logging.debug('lcd_send_receive: send ' + question)
        logging.debug('lcd_send_receive: receive ' + answer)
        return answer

    def check_queue(self):
        response = ''
        try:
            response = self.lcd.read_very_eager().decode('utf-8')
        except Exception as e:
            logging.warning('lcd_check_queue: cannot connect to LCDd daemon at ' + self.lcdd + ':' + self.lcdport + ': {0}'.format(e))
        if (response != ''):
            logging.debug('LCD message received: ' + response)
            return response
        else:
            return None
