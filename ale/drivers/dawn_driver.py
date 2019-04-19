import ale
from ale.drivers.base import *
from ale import config

import pvl

class DawnSpice(Driver, Framer, Spice):
    """
    Dawn specific spice mixin to handle dawn specific spice calls and property
    overrides. This class is not used as a driver.
    """
    # TODO: Update focal2pixel samples and lines to reflect the rectangular
    #       nature of dawn pixels
    @property
    def _odtk(self):
        """
        Returns
        -------
        : list
          Radial distortion coefficients
        """
        return spice.gdpool('INS{}_RAD_DIST_COEFF'.format(self.ikid),0, 1).tolist()

    @property
    def focal2pixel_samples(self):
        # Microns to mm
        pixel_size = spice.gdpool('INS{}_PIXEL_SIZE'.format(self.ikid), 0, 1)[0] * 0.001
        return [0.0, 1/pixel_size, 0.0]

    @property
    def focal2pixel_lines(self):
        # Microns to mm
        pixel_size = spice.gdpool('INS{}_PIXEL_SIZE'.format(self.ikid), 0, 1)[0] * 0.001
        return [0.0, 0.0, 1/pixel_size]

    @property
    def _metakernel_dir(self):
        """
        Returns latest instrument metakernels

        Returns
        -------
        : string
          Path to latest metakernel file
        """
        return config.dawn

class DawnPDS3Driver(PDS3, DawnSpice, RadialDistortion):
    """
    Dawn driver for generating an ISD from a Dawn PDS3 image.
    """
    @property
    def instrument_id(self):
        """
        Returns an instrument id for uniquely identifying the instrument, but often
        also used to be piped into Spice Kernels to acquire IKIDs. Therefore the
        the same ID that Spice expects in bods2c calls.

        Returns
        -------
        : str
          instrument id
        """
        instrument_id = self._label["INSTRUMENT_ID"]
        filter_number = self._label["FILTER_NUMBER"]

        return "DAWN_{}_FILTER_{}".format(instrument_id, filter_number)

    @property
    def _label(self):
        """
        Loads a PVL from from the _file attribute and
        parses the binary table data.

        Returns
        -------
        PVLModule :
            Dict-like object with PVL keys
        """
        # PvlDecoder class to ignore all escape sequences when getting
        # the label
        class PvlDecoder(pvl.decoder.PVLDecoder):
            def unescape_next_char(self, stream):
                esc = stream.read(1)
                string = '\{}'.format(esc.decode('utf-8')).encode('utf-8')
                return string

        if not hasattr(self, "_pvl_label"):
            if isinstance(self._label_source, pvl.PVLModule):
                self._pvl_label = self._file
            try:
                self._pvl_label = pvl.loads(self._label_source, PvlDecoder)
            except Exception:
                self._pvl_label = pvl.load(self._label_source, PvlDecoder)
            except:
                raise ValueError("{} is not a valid label".format(self._label_source))
        return self._pvl_label

    @property
    def spacecraft_name(self):
        """
        Spacecraft name used in various Spice calls to acquire
        ephemeris data.

        Returns
        -------
        : str
          Spacecraft name
        """
        return self._label['INSTRUMENT_HOST_NAME']

    @property
    def target_name(self):
        """
        Returns an target name for unquely identifying the instrument, but often
        piped into Spice Kernels to acquire Ephermis data from Spice. Therefore they
        the same ID the Spice expects in bodvrd calls. In this case, vesta images
        have a number infront of them like "4 VESTA" which needs to be simplified
        to "VESTA" for spice.

        Returns
        -------
        : str
          target name
        """
        target = self._label['TARGET_NAME']
        target = target.split(' ')[-1]
        return target

    @property
    def starting_ephemeris_time(self):
        """
        Compute the center ephemeris time for a Dawn Frame camera. This is done
        via a spice call but 193 ms needs to be added to
        account for the CCD being discharged or cleared.
        """
        if not hasattr(self, '_starting_ephemeris_time'):
            sclock = self._label['SPACECRAFT_CLOCK_START_COUNT']
            self._starting_ephemeris_time = spice.scs2e(self.spacecraft_id, sclock)
            self._starting_ephemeris_time += 193.0 / 1000.0
        return self._starting_ephemeris_time
