from importlib.metadata import version as get_version

cliversion = get_version("crashplancli")
pycpgversion = get_version("pycpg")

PRODUCT_NAME = "crashplancli"
MAIN_COMMAND = "crashplan"
BANNER = f"""\b
  _____               _     _____  _
  / ____|             | |   |  __ \\| |
 | |     _ __ __ _ ___| |__ | |__) | | __ _ _ __
 | |    | '__/ _` / __| '_ \\|  ___/| |/ _` | '_ \\
 | |____| | | (_| \\__ \\ | | | |    | | (_| | | | |
  \\_____|_|  \\__,_|___/_| |_|_|    |_|\\__,_|_| |_|


crashplancli version {cliversion}, by CrashPlan.
powered by pycpg version {pycpgversion}."""
