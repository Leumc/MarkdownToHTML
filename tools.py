from datetime import datetime 
from enum import Enum,auto
from colorama import Fore,Back,Style,init

init(autoreset=True)

class info_type(Enum):
    ERROR=Fore.RED
    WARNING=Fore.YELLOW
    NOTICE=Fore.GREEN

def printInfo(type:info_type,content:str,type_name:str=""):
    now=datetime.now()
    print(f"{type.value}[{now.strftime("%H:%M:%S")}{"|" if type_name!="" else ""}{type_name}]{content}{Style.RESET_ALL}")
