import inspect
import shutil


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
        
    
    def print_message(self, msg, level_name, file, *styles):
        if self.level >= LEVELS[level_name]:
            # If theres room, then first print the name of the calling file right aligned
            left_align_len = len(level_name) + 2 + len(msg)
            print(right_align(f"({file})", left_align_len=left_align_len), end="\r")
            
            # Then print the message with the log level styled
            print(style(level_name, *styles) + ":", msg)
            

    def debug(self, msg):
        from_frame = inspect.stack()[1]
        file = inspect.getfile(from_frame[0])
        self.print_message(msg, "DEBUG", file, "bold")
    

    def info(self, msg):
        from_frame = inspect.stack()[1]
        file = inspect.getfile(from_frame[0])
        self.print_message(msg, "INFO", file, "bold", "blue")
    

    def warning(self, msg):
        from_frame = inspect.stack()[1]
        file = inspect.getfile(from_frame[0])
        self.print_message(msg, "WARNING", file, "bold", "yellow")


    def error(self, msg):
        from_frame = inspect.stack()[1]
        file = inspect.getfile(from_frame[0])
        self.print_message(msg, "ERROR", file, "bold", "red")


    def critical(self, msg):
        self.print_message(msg, "CRITICAL", file, "bold", "red", "underline")
        


def style(text, *styles):
    code = {
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'bright red': '91',
        'bright green': '92',
        'bright yellow': '93',
        'bright blue': '94',
        'bright magenta': '95',
        'bright cyan': '96',
        'bold': '1',
        'faint': '2',
        'italic': '3',
        'underline': '4',
        'blink': '5',
        'strike': '9'
    }

    for style in styles:
        text = "\033[" + code[style] + "m" + text + "\033[0m"

    return text
    

def right_align(text, left_align_len=0):
    columns = shutil.get_terminal_size()[0]
    if left_align_len + len(text) < columns:
        return(text.rjust(columns))