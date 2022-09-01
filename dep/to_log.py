"""
Author: Yanis Schärer, yanis.schaerer@swissnuclear.ch
As of: see README.txt
"""
import os
from datetime import datetime

def to_log(text: str, no_time=False):
    log_date = datetime.today()
    user = os.getlogin()
    with open('log.txt', 'a') as log:
        if no_time:
            log.write(f'{text}\n')
        else:
            log.write(f'{log_date.year}-{log_date.month:02d}-{log_date.day:02d} {log_date.hour:02d}:{log_date.minute:02d}:{log_date.second:02d}: ({user}) {text}\n')