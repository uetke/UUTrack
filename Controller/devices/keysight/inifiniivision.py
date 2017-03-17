from lantz.messagebased import MessageBasedDriver
from lantz import Action
from lantz import Feat, DictFeat
from lantz import Q_

#TODO: Acquire waveform
#TODO: Function generation
#TODO: All the functions of the func. gen.

import numpy as np


class Funcgen(MessageBasedDriver):
    """The agilent 33220a function generator"""
    volt = Q_('volt')
    hertz = Q_('hertz')
    MANUFACTURER_ID = '0x0957'
    MODEL_CODE = '0x1797'

    DEFAULTS = {'USB': {'write_termination': '\n',
                        'read_termination': '\n',
                        'timeout': 5000,
                        'encoding': 'ascii'
                        }}
    @Feat()
    def idn(self):
        return self.query('*IDN?')

    @Feat()
    def func(self):
        """ Return the function type.
        """
        return self.query('FUNC?')

    @func.setter
    def func(self,functype):
        """ Sets the function type.
        """
        self.write('FUNC {}'.format(functype))

    @Feat(units='Hz')
    def freq(self):
        """ Return the frequency.
        """
        return self.query('FREQ?')

    @freq.setter
    def freq(self,value):
        """ Set the frequency.
        """
        self.write('FREQ {} Hz'.format(value))

    @Feat(units='V')
    def volt(self):
        """ Return the amplitude.
        """
        return self.query('VOLT?')

    @volt.setter
    def volt(self,value):
        """ Sets the output voltage.
        """
        self.write('VOLT {} VPP'.format(value))

    @Feat(units='V')
    def offset(self):
        """ Return the offset.
        """
        return self.query('VOLT:OFFS?')

    @offset.setter
    def offset(self,value):
        """ Sets the offset
        """
        self.write('VOLT:OFFS {}'.format(value))

    @Action(values={True:'ON', False:'OFF'})
    def output(self,value):
        """ Turns the output on or off.
        """
        self.write('OUTP {}'.format(value))

    ### Functions related to the function generator and not to the oscilloscope are prepended
    ### with the word wgen.

    @Feat(units='hertz')
    def wgen_frequency(self):
        """gets the frequency of the function generator
        :params -- frequency (in Hz)
        """
        return self.query(':WGEN:FREQuency?')

    @wgen_frequency.setter
    def wgen_frequency(self,freq):
        self.write(':WGEN:FREQuency %s'%freq)

    @DictFeat(values={'SIN':'SIN', 'SQU':'SQU', 'RAMP':'RAMP', 'PULS':'PULS', 'NOIS':'NOIS', 'DC':'DC'})
    def wgen_function(self):
        """Gets the function pased to the function generator"""
        return self.query(':WGEN:FUN?')

    @wgen_function.setter
    def wgen_function(self,fun):
        """Sets the function of the function generator"""
        self.write(':WGEN:FUN %s'%fun)

    ### Functions related to the oscilloscope and not to the function generator are prepended
    ### with the word measure.

    def measure_VPP(self, chan):
        """Gets the Voltage peak to peak from the oscilloscope in the desired channel"""
        return self.query(':MEAS:VPP? CHAN%s'%chan)*Q_('volt')

    def measure_Vmin(self,chan):
        """Measures the minimum voltage from the selected channel. """
        return self.query(':MEAS:VMIN? CHAN%s' % chan) * Q_('volt')

    def measure_Vmax(self,chan):
        """Measures the maximum voltage from the selected channel. """
        return self.query(':MEAS:VMAX? CHAN%s' % chan) * Q_('volt')

    def measure_frequency(self,chan):
        """Measures the frequency from the selected channel. """
        return self.query(':MEAS:FREQ? CHAN%s' % chan) * Q_('hertz')

    def measure_clear(self):
        """Clears all the measurements from the screen."""
        self.write(':MEASure:CLEar')
        return True
    # def apply(self,func=None,freq=None,ampl=None,offset=None):
    #     if not func==None:
    #         self.set_function_type(func)
    #     if not freq==None:
    #         self.set_frequency(freq)
    #     if not ampl==None:
    #         self.set_amplitude(ampl)
    #     if not offset==None:
    #         self.set_offset(offset)
    #
    # #@DictFeat(keys=['SIN','SQUare','RAMP','PULS','DC'])
    # def set_function_type(self,func):
    #     self.send('FUNC %s' %func)
    #
    # #@Feat(units='Hz', limits=freqlimits[self.func])
    # def set_frequency(self,freq):
    #     self.send('FREQ %s' %freq)
    #
    # #@Feat(units='V', limits=(10e-3,10))
    # def set_amplitude(self,ampl):
    #     self.send('VOLT %s' %ampl)
    #
    # #@Feat(units='V', limits=(-10+self.ampl/2,10-self.ampl/2))
    # def set_offset(self, offset):
    #     self.send('VOLT:OFFS %s' %offset)
    #
    # def get_wfrm_setting(self):
    #     """returns the waveform settings
    #        example format 'func type freq,amplitude,offset'
    #        'SIN +5.0000000000000E+03,+3.0000000000000E+00,-2.5000000000000E+00' """
    #     return self.query('APPL?')

if __name__ == '__main__':
    with Funcgen.via_usb() as inst:
        inst.initialize()

        print(inst.idn)
        print('++++++++++++++++++++')
        print("VPP in channel 1: %s" % inst.measure_VPP(1))
        print("VMax in channel 1: %s" % inst.measure_Vmax(1))
        print("VMin in channel 1: %s" % inst.measure_Vmin(1))
        print("Freq in channel 1: %s" % inst.measure_frequency(1))
        print('++++++++++++++++++++')
        # inst.test()
        # print('Current Frequency: %s'%inst.wgen_frequency)
        # inst.wgen_frequency = 20
        # print('Updated Frequency: %s'%inst.wgen_frequency)

        inst.measure_clear()
        print(inst.wgen_frequency)
        inst.wgen_frequency = 20