import pylab as pl
import csv
import os
import math
import leap.lib.units.spectral_bands as spectral_bands
from leap.lib.physics.black_body import BlackBody


class ThermoUnits():

    def __init__(self, band_name, remove_negative=True, band_suffix='band_avespect_bin.csv', optical_efficiency=1.):
        """
        Thermodynamic units for bolometers

        Args:
            band_name - '150' for example
            remove_negative - Sets the negative sections of the band to 0
            band_suffix - The filename suffix for the band in leap/resources/bands/
            optical_efficiency - The optical efficiency of the band.
        """
        #constants
        self.c = 2.998e8  # [m/s]
        self.k = 1.381e-23  # [J/K]
        self.h = 6.626e-34  # [Js]
        self.T_cmb = 2.725  # [K]

        #settings
        self.remove_negative = remove_negative
        self.band_name = spectral_bands.check_band_name(band_name)
        self.band_suffix = band_suffix

        #frequencies for integrations
        if self.band_name == "150":
            self.frequencies = pl.arange(90, 240, 0.1)*1e9  # [Hz]
        elif self.band_name == "250":
            self.frequencies = pl.arange(180, 320, 0.1)*1e9  # [Hz]
        elif self.band_name == "410":
            self.frequencies = pl.arange(260, 770, 0.1)*1e9  # [Hz]

        #blackbody and derivatives
        self.cmb_BB = BlackBody(self.T_cmb)  # [W / sr m^2 Hz]
        self.cmb_dPdT = self.cmb_BB.dP_by_dT(self.frequencies)  # [W / sr m^2 Hz K]
        self.RJ_dPdT = 2. * self.k * (self.frequencies/self.c)**2  # [W / sr m^2 Hz K]

        #EBEX values
        #self.throughput = self.get_band_throughput(self.band_name)
        self.throughput = self.get_throughput(self.band_name, self.frequencies)  # [sr m^2]
        self.bandwidth = spectral_bands.integrate_band(self.band_name, remove_negative=remove_negative,
                                                       band_suffix=self.band_suffix)  # [Hz]
        self.optical_efficiency = optical_efficiency

    def get_band_throughput(self, band_name):
        """
        Calculates the band throughput from the band name (str).
        """
        lambda_ = self.c/(int(band_name)*1e9)
        throughput = lambda_**2
        if band_name == '150':
            throughput *= 0.8
        return throughput

    def get_throughput(self, band_name, frequencies):
        """
        Calculates the band throughput from the band name (str) for the numpy array frequencies.
        """
        lambda_ = self.c / frequencies
        throughput = lambda_**2
        if band_name == '150':
            throughput *= 0.8
        return throughput

    def from_P_to_Tcmb(self, P=1.):
        """
        Conversion from W to K_CMB

        <(dTcmb/dP) / throughput> is average over the band and then divided by bandwidth and multiplied by the power to
        convert
        """
        function = (1./self.cmb_dPdT) / self.throughput  # (K / [W / sr m^2 Hz]) / [sr m^2] = [K Hz / W]
        dTcmbdP_averaged = spectral_bands.average_function_over_band(self.band_name, self.frequencies, function,
                                                                     remove_negative=self.remove_negative,
                                                                     band_suffix=self.band_suffix)
        dTcmbdP_averaged /= self.bandwidth  # [K / W]
        return dTcmbdP_averaged * P

    def from_NEP_to_NET_CMB(self, nep=1.):
        """
        Conversion from W/sqrt(Hz) to K_CMB sqrt(s)
        """
        return self.from_P_to_Tcmb(nep) / pl.sqrt(2.) / self.optical_efficiency

    def from_Tcmb_to_P(self, Tcmb=1.):
        """
        Conversion from K_CMB to W

        <(dP/dTcmb) / throughput> is average over the band and then dividedmultiplied by bandwidth and the temperature
        to convert
        """
        function = self.cmb_dPdT * self.throughput  # ([W / sr m^2 Hz] / K) * [sr m^2] = [W / K Hz]
        dPdTcmb_averaged = spectral_bands.average_function_over_band(self.band_name, self.frequencies, function,
                                                                     remove_negative=self.remove_negative,
                                                                     band_suffix=self.band_suffix)
        dPdTcmb_averaged *= self.bandwidth  # [W / K]
        return dPdTcmb_averaged * Tcmb

    def from_NET_CMB_to_NEP(self, net=1.):
        """
        Conversion from K_CMB sqrt(s) to W/sqrt(Hz)
        """
        return self.from_Tcmb_to_P(net) * pl.sqrt(2.) * self.optical_efficiency

    def from_P_to_Trj(self, P=1.):
        """
        Conversion from W to K_CMB

        <(dTcmb/dP) / throughput> is average over the band and then divided by bandwidth and multiplied by the power to
        convert
        """
        function = (1./self.RJ_dPdT) / self.throughput  # (K / [W / sr m^2 Hz]) / [sr m^2] = [K Hz / W]
        dTrjdP_averaged = spectral_bands.average_function_over_band(self.band_name, self.frequencies, function,
                                                                    remove_negative=self.remove_negative,
                                                                    band_suffix=self.band_suffix)
        dTrjdP_averaged /= self.bandwidth  # [K / W]
        return dTcmbdP_averaged * P

    def from_NEP_to_NET_RJ(self, nep=1.):
        """
        Conversion from W/sqrt(Hz) to K_RJ sqrt(s)
        """
        return self.from_P_to_Trj(nep) / pl.sqrt(2.) / self.optical_efficiency

    def from_Trj_to_P(self, Trj=1.):
        """
        Conversion from K_CMB to W

        <(dP/dTcmb) / throughput> is average over the band and then dividedmultiplied by bandwidth and the temperature
        to convert
        """
        function = self.RJ_dPdT * self.throughput  # ([W / sr m^2 Hz] / K) * [sr m^2] = [W / K Hz]
        dPdTrj_averaged = spectral_bands.average_function_over_band(self.band_name, self.frequencies, function,
                                                                    remove_negative=self.remove_negative,
                                                                    band_suffix=self.band_suffix)
        dPdTrj_averaged *= self.bandwidth  # [W / K]
        return dPdTcmb_averaged * Trj

    def from_NET_RJ_to_NEP(self, net=1.):
        """
        Conversion from K_RJ sqrt(s) to W/sqrt(Hz)
        """
        return self.from_Trj_to_P(nep) * pl.sqrt(2.) * self.optical_efficiency

    def from_NET_CMB_to_mapping_speed(self, net=1., beam_width_arcmin=8.):
        '''
        From noise equivalent temperature to mapping speed.
        '''
        beam_area = math.pi*((beam_width_arcmin/2.)/60.)**2
        mapping_speed = net / math.sqrt(beam_area)
        return mapping_speed

#test script
if __name__ == "__main__":
    print("Expectations for top-hat between 133-173, 218-288 and 366-450 GHz")
    print("{0:s}\t{1:8s}\t{2:8s}\t{3:8s}\t{4:s}".format('band', 'dTcmb_dP', 'dTcmb_dP_exp', 'dTrj_dP', 'dTrj_dP_exp'))
    expectations = {'150': {'CMB': 2.49e+17, 'RJ': 1.41e+17}, '250': {'CMB': 2.18e+17, 'RJ': 5.18e+17},
                    '410': {'CMB': 5.11e+17, 'RJ': 1.98e+17}}
    for band_name in ['150', '250', '410']:
        app = ThermoUnits(band_name)
        dTcmb_dP = app.from_P_to_Tcmb() * app.bandwidth * app.throughput.mean()
        dTrj_dP = app.from_P_to_Trj() * app.bandwidth * app.throughput.mean()
        print band_name, dTcmb_dP, expectations[band_name]['CMB']
        text = "{0:s}\t{1:8.2e}\t{2:8.2e}\t".format(band_name, dTcmb_dP, expectations[band_name]['CMB'])
        text += "{0:8.2e}\t{1:8.2e}".format(dTrj_dP, expectations[band_name]['RJ'])
        print(text)
