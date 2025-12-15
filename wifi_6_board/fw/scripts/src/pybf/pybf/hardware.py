"""
   Copyright (C) 2020 ETH Zurich. All rights reserved.

   Author: Sergei Vostrikov, ETH Zurich

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import numpy as np

class Hardware:
    # Provide the constructor with either with excitation and impulse_response
    # or correction time
    def __init__(self, 
                 f_sampling_hz, 
                 start_time_s, 
                 excitation=None, 
                 impulse_response=None,
                 correction_time_shift_s=None):
    
        self._f_sampling_hz = f_sampling_hz
        self._start_time_s = start_time_s
        
        # Calc or copy correction time denepding on provided arguments
        if (excitation is None) or (impulse_response is None):
            if correction_time_shift_s is not None:
                # Copy corrections time
                self._correction_time_shift_s = correction_time_shift_s
            else:
                print('Hardware: Not enough data for correction time calculation')
                print('Tip: Provide either excitation and impulse_response or correction time')
        else:
            
            self._excitation = excitation.reshape(-1,)
            self._electroacoustic_ir = impulse_response.reshape(-1,)
            # Calculate time shift
            self._calc_time_shift()
        
        return
    
    # Calculate time_shift of the system caused by LTI system
    # electrical wave -> acoustic wave -> electrical wave
    def _calc_time_shift(self):
        
        # electrical wave -> acoustic wave
        system_ir = np.convolve(self._excitation, self._electroacoustic_ir)
        # acoustic wave -> electrical wave
        system_ir = np.convolve(system_ir, self._electroacoustic_ir)
        
        # Correction time shift in seconds
        self._correction_time_shift_s = system_ir.shape[0]/2/self._f_sampling_hz
        
        return

    # Returns excitation array
    @property
    def excitation(self):

        return self._excitation

    # Returns electroacoustic impulse response
    @property
    def electroacoustic_ir(self):

        return self._electroacoustic_ir

    # Returns sampling frequency in hz
    @property
    def f_sampling(self):

        return self._f_sampling_hz

    # Returns correction time shift in seconds
    @property
    def correction_time_shift(self):

        return self._correction_time_shift_s

    # Returns start time of the first sample in seconds
    @property
    def start_time(self):

        return self._start_time_s