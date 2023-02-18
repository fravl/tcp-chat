from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init(convert=True)

class bcolors:
    OKGREEN = Fore.GREEN
    WARNING = Fore.YELLOW
    FAIL = Fore.RED
    ENDC = Style.RESET_ALL
