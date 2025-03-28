from pycpg.__version__ import __version__ as pycpgversion

from crashplancli.__version__ import __version__ as cliversion


PRODUCT_NAME = "crashplancli"
MAIN_COMMAND = "crashplan"
BANNER = f"""\b
    _____               _     _____  _             
  / ____|             | |   |  __ \| |            
 | |     _ __ __ _ ___| |__ | |__) | | __ _ _ __  
 | |    | '__/ _` / __| '_ \|  ___/| |/ _` | '_ \ 
 | |____| | | (_| \__ \ | | | |    | | (_| | | | |
  \_____|_|  \__,_|___/_| |_|_|    |_|\__,_|_| |_|
                                                  

crashplancli version {cliversion}, by crashplan Software.
powered by pycpg version {pycpgversion}."""
