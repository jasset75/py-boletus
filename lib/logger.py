import logging
import sys

from lib import config

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
if config.debug:
    handler.setLevel(logging.DEBUG)
else:
    handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

class Log:
    def __new__(cls):
        return cls

    @classmethod
    def verbose(cls, text):
        if config.verbose:
            logging.log(logging.INFO, text)
