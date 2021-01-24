LEVELS = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4
}
class Logger:
    def __init__(self, log_level):
        try:
            # Extract log level from string
            self.log_level = LEVELS[log_level.upper()]
        except KeyError:
            # If key does not match, check if log_level is a valid int or else set the level to DEBUG
            self.log_level = log_level if type(log_level) == int and abs(log_level) < 5 else 0