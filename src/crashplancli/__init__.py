from importlib.metadata import version as get_version

cliversion = get_version("crashplancli")
pycpgversion = get_version("pycpg")

PRODUCT_NAME = "crashplancli"
MAIN_COMMAND = "crashplan"
BANNER = f"""\b
 .d8888b.                           888      8888888b.  888
d88P  Y88b                          888      888   Y88b 888
888    888                          888      888    888 888
888        888d888 8888b.  .d8888b  88888b.  888   d88P 888  8888b.  88888b.
888        888P"      "88b 88K      888 "88b 8888888P"  888     "88b 888 "88b
888    888 888    .d888888 "Y8888b. 888  888 888        888 .d888888 888  888
Y88b  d88P 888    888  888      X88 888  888 888        888 888  888 888  888
 "Y8888P"  888    "Y888888  88888P' 888  888 888        888 "Y888888 888  888


crashplancli version {cliversion}, by CrashPlan.
powered by pycpg version {pycpgversion}."""
