import inspect
from oboe.utils import style, right_align


LEVELS = {
    "DEBUG": 4,
    "INFO": 3,
    "WARNING": 2,
    "ERROR": 1,
    "CRITICAL": 0
}

class Logger:
    def __init__(self, level):
        try:
            # Extract log level from string
            self.level = LEVELS[level.upper()]
        except (KeyError, AttributeError):
            # If key does not match, check if log_level is a valid int or else set the level to DEBUG
            self.level = level if type(level) == int and abs(level) < 5 else 4
            
    
    def set_level(self, level):
        self.__init__(level)
        
    
    def print_message(self, msg, level_name, *styles):
        from_frame = inspect.stack()[1]
        file = inspect.getfile(from_frame[0])
        if self.level >= LEVELS[level_name]:
            # If theres room, then first print the name of the calling file right aligned
            left_align_len = len(level_name) + 2 + len(msg)
            print(right_align(f"({file})", left_align_len=left_align_len), end="\r")
            
            # Then print the message with the log level styled
            print(style(level_name, *styles) + ":", msg)
            

    def debug(self, msg):
        self.print_message(msg, "DEBUG", "bold")
    

    def info(self, msg):
        self.print_message(msg, "INFO", "bold", "blue")
    

    def warning(self, msg):
        self.print_message(msg, "WARNING", "bold", "yellow")


    def error(self, msg):
        self.print_message(msg, "ERROR", "bold", "red")


    def critical(self, msg):
        self.print_message(msg, "CRITICAL", "bold", "red", "underline")