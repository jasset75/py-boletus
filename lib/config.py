class Config:
    _verbose = False
    _debug = False

    def __new__(cls):
        return cls

    @classmethod
    def verbose(cls, verbose):
        cls._verbose = verbose

    @classmethod
    def debug(cls, debug):
        cls._debug = debug

# Global config
config = Config()
