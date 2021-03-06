#!/usr/bin/env python
# encoding: utf-8

'''
	Audio file preprocessing 
	python3 transform.py *.wav => *.txt

'''

from __future__ import absolute_import, division, print_function
import numpy as np
import sys
from madmom.processors import SequentialProcessor
import matplotlib.pyplot as plt

class PianoNoteProcessor(SequentialProcessor):
    def __init__(self, **kwargs):
        from madmom.audio.signal import SignalProcessor, FramedSignalProcessor
        from madmom.audio.stft import ShortTimeFourierTransformProcessor
        from madmom.audio.spectrogram import (
            FilteredSpectrogramProcessor, LogarithmicSpectrogramProcessor,
            SpectrogramDifferenceProcessor)
        from madmom.processors import SequentialProcessor, ParallelProcessor

        # define pre-processing chain
        sig = SignalProcessor(num_channels=1, sample_rate=44100)
        # process the multi-resolution spec & diff in parallel
        multi = ParallelProcessor([])
        for frame_size in [4096]:
            frames = FramedSignalProcessor(frame_size=frame_size, fps=100)
            stft = ShortTimeFourierTransformProcessor(window = np.hamming(frame_size))  # caching FFT window
            filt = FilteredSpectrogramProcessor(
                num_bands=12, fmin=30, fmax=16000, norm_filters=True)
            spec = LogarithmicSpectrogramProcessor(mul=5, add=1)
            #diff = SpectrogramDifferenceProcessor(diff_ratio=0.5, positive_diffs=True, stack_diffs=np.hstack)
            # process each frame size with spec and diff sequentially
            multi.append(SequentialProcessor((frames, stft, filt, spec)))
            #multi.append(SequentialProcessor((frames, stft, filt)))

        # stack the features and processes everything sequentially
        pre_processor = SequentialProcessor((sig, multi, np.hstack))
        super(PianoNoteProcessor,self).__init__(pre_processor)


def main():
    proc = PianoNoteProcessor()
    act = proc(sys.argv[1])
    filename = sys.argv[1].split(".")[0]
    '''
    plt.imshow(np.transpose(act)[:,300:400],cmap='gray')
    plt.title("logarithmic filterbanks")
    plt.show()
    print(act.shape)
    '''
    np.savetxt('%s_transform.txt'%filename,act,fmt='%.4f')

if __name__ == '__main__':
    main()
