from lantz.messagebased import MessageBasedDriver
from lantz import Action
from lantz import Feat, DictFeat
# from lantz import Q_

import numpy as np


class Funcgen(MessageBasedDriver):
    """The agilent 33220a function generator"""

    MANUFACTURER_ID = '0x15BC'
    MODEL_CODE = '0x1518'


    DEFAULTS = {'USB': {'write_termination': '\n',
                        'read_termination': '\n',
                        'timeout': 500000,
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
    inst = Funcgen.via_usb()
    inst.initialize()
    print(inst.idn)
