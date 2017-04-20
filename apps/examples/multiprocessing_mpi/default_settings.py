from leap.lib.tools import generic
from leap.lib.io_management import loading_parameters


settings = generic.Class()
settings.loading_params = loading_parameters.Params()
settings.loading_params.data_path = "latest_flight_base"
settings.loading_params.progress_indicator_enabled = False
settings.loading_params.bolo_names = ["62-2-11", "62-2-12"]
settings.loading_params.bolo_load_signals = False
