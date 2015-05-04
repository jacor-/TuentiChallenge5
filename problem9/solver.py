
import fileinput
import numpy
from scipy import correlate

inp = fileinput.input()
a, b = map(int,inp.next()[:-1].split(" "))
pattern = [float(inp.next()[:-1]) for _ in range(a)]
_ = inp.next()
wave    = [float(inp.next()[:-1]) for _ in range(b)]


pattern = numpy.array(pattern)
wave = numpy.array(wave)

pattern_mean = numpy.mean(pattern)
pattern_std  = numpy.sqrt(numpy.sum(numpy.power(pattern-pattern_mean, 2)))

pattern_base = (pattern-pattern_mean)/pattern_std

projection_base = correlate(pattern_base, wave)
projection_ones = numpy.sum(pattern_base)

'''
A vectorized version of crosscorr (quite faster) which uses a precomputed version
of the pattern vector normalized. 
This vector is constant, so we do not need to compute it each time we call
this function
'''
def crosscorr3(sig_cte, i_ini, i_end):
    sig_2 = wave[i_ini:i_end]-numpy.mean(wave[i_ini:i_end])
    denom = numpy.sqrt(numpy.sum(numpy.power(sig_2, 2)))
    numerador = correlate(sig_2, sig_cte)
    return numerador / denom

'''
A vectorized version of crosscorr (quite faster)
'''
def crosscorr2(i_ini, i_end):
    sig_1 = pattern-numpy.mean(pattern)
    sig_2 = wave[i_ini:i_end]-numpy.mean(wave[i_ini:i_end])
    denom = numpy.sqrt(numpy.sum(numpy.power(sig_1, 2)) * numpy.sum(numpy.power(sig_2, 2)))
    numerador = correlate(sig_2, sig_1)
    return numerador / denom 

'''
The same code of the C file rewritten in almost pure python
'''
def crosscorr(sub_signal, xSize, y, ySize):
    xMean = numpy.sum(sub_signal[:xSize]) / xSize
    yMean = numpy.sum(y[:ySize]) / ySize

    xSumCuadraticDiff = numpy.sum((sub_signal[:xSize] - xMean) ** 2 )
    ySumCuadraticDiff = numpy.sum((y - yMean) ** 2)

    denom = numpy.sqrt(xSumCuadraticDiff * ySumCuadraticDiff)

    xcorr = numpy.zeros(ySize-xSize+1)
    for delay in range(xcorr.shape[0]):
        xySum = 0.0
        for i in range(xSize):
            xySum += (sub_signal[i] - xMean) * (y[i + delay ] - yMean)
        xcorr[delay] = xySum / denom
    return xcorr


score = 0.0
minSubvectorLength = 2
results = []
for subvectorStart in range(wave.shape[0] - minSubvectorLength + 1):
    for subvectorLength in range(minSubvectorLength, numpy.min([wave.shape[0] - subvectorStart, pattern.shape[0]])+1):
        result3 = numpy.max(crosscorr3(pattern_base, subvectorStart, subvectorStart + subvectorLength))*subvectorLength
        score = numpy.max([score, result3])
print "%0.4f" % score
        