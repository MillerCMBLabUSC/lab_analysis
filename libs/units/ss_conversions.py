import pdb
import pywtl.core.wtl_ConvertUtils as conv
from pywtl.core.wtl_ConvertUtils import convert_mb
import leap.lib.bolometer_noise.noise_prediction as noise_lib


class ss_converts(convert_mb):
    """
    This libraty inherits from the convert_mb class.  The amp_to_human and human_to_amp are over-writte.  Also, a
    function to load the gains from the HWM is written since there are bugs with the gains.
    """
    def amp_to_human(self, amp_int):
        amp = amp_int / (2**19-1.)
        return amp

    def human_to_amp(self, amp):
        amp_int = amp * (2**19-1.)
        return amp_int

    def load_gain_from_hwm(self, bolo_name, type_):
        if type_ not in ['carrier', 'nuller', 'demod']:
            raise ValueError("the gain type should be carrier, nuller or demod")
        if type_ in ['carrier', 'nuller']:
            gain = noise_lib.load_HWM_params(bolo_name)["overbias_gain_"+type_]
        elif type_ in ['demod']:
            gain = noise_lib.load_HWM_params(bolo_name)["transition_gain_"+type_]
        gain = int(gain)
        return gain
