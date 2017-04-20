from leap.lib.io_management import loading_parameters
from leap.lib.tools import generic, bolo_mapping

settings = generic.Class()

params = loading_parameters.Params()
params.data_path = "latest_flight_base"
params.segment_list = ["2012-12-31--13-17-57"]
params.bolo_names = bolo_mapping.get_all_bolos()
settings.dirfile_loading = params

