#!/usr/bin/env python2.7

# Remember to run with `apm -H` and with no malloc.conf

import subprocess, sys
import matplotlib.pyplot as plt

# Real params
#REPS = 10
#HOWLONG = 60 # in seconds

# test params
REPS = 2
HOWLONG = 1 # in seconds

# carefully selected to not all be powers of two, although roughly doubling
buf_sizes = [4200, 8455, 16901, 33888, 67779]

avgs_s = ([], []) # (list of X coords, list of Y coords)
avgs_c = ([], []) # "

for bs in buf_sizes: # loop the buffer sizes

    for asm in [True, False]: # which implementation to use
        impl = "bench-s" if asm else "bench-c"
        avgs = avgs_s if asm else avgs_c
        raw_data = []

        for rep in range(REPS):
            print("--> running rep=%d, asm=%s, bufsz=%d and seconds=%d" % (rep, asm, bs, HOWLONG))

            args = ["./%s" % impl, str(bs), str(HOWLONG)]
            print("--> %s" % (" ".join(args)))

            pipe = subprocess.Popen(args, stdout=subprocess.PIPE)
            (stdout, stderr) = pipe.communicate()

            raw_data.append(float(stdout))

        print("raw data for bufsz=%d: %s" % (bs, raw_data))
        avgs[0].append(bs)
        avgs[1].append(sum(raw_data) / float(REPS)) # mean no. of bufs processed

print("Asm:")
print(avgs_s)
print("C:")
print(avgs_c)

# plot
plt.plot(avgs_s[0], avgs_s[1], label='Assembler')
plt.plot(avgs_c[0], avgs_c[1], label='C')
plt.xlabel('buffer size')
plt.ylabel('# of buffers copied in %s seconds' % (HOWLONG,))
plt.legend()
plt.show()
