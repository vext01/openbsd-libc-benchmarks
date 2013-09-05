#!/usr/bin/env python2.7

import subprocess, sys, os
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    print("usage: run_benchmarks.py <dataset_name>")
    print("e.g.: run_benchmarks.py edds_laptop")
    sys.exit(1)

print("")
print("Please check:")
print("")
print("  - You are running with `apm -H`")
print("  - You have no malloc.conf")
print("  - If this is a laptop, it is plugged in and no powersaving gunk is on")
print("  - You are running as few apps as possible")
print("")

print("Hit enter to run tests...")
raw_input()

# Real params
#REPS = 5
#HOWLONG = 60 # in seconds

# test params
REPS = 1
HOWLONG = 1 # in seconds

# carefully selected to not all be powers of two, although roughly doubling
buf_sizes = [4200, 8455, 16901, 33888, 67779, 135551]

avgs_s = ([], []) # (list of X coords, list of Y coords)
avgs_c = ([], []) # "

OUTDIR = os.path.join("results", sys.argv[1])
print("Results will be saved to: %s" % (OUTDIR,))
try:
    os.mkdir(OUTDIR)
except:
    print("error: cannot create dir: %s" % (OUTDIR, ))
    sys.exit(1)

raw_file = open("%s/raw.out" % OUTDIR, "w")
raw_file.write("# buffer sizes: %s\n" % (buf_sizes,))
raw_file.write("# sample size: %s\n" % (REPS,))
raw_file.write("# how long: %s\n\n" % (HOWLONG,))

# collect dmesg
print("Collecting dmesg...")
pipe = subprocess.Popen("/sbin/dmesg", stdout=subprocess.PIPE)
(stdout, stderr) = pipe.communicate()
with open("%s/dmesg" % OUTDIR, "w") as fh:
    fh.write(stdout)

# Experiments begin
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

        raw_file.write("# asm=%s, bufsz=%d:\n" % (asm, bs))
        raw_file.write(str(raw_data) + "\n")

        avgs[0].append(bs)
        avgs[1].append(sum(raw_data) / float(REPS)) # mean no. of bufs processed

raw_file.close()

# sanity preserved?
assert len(avgs_s[0]) == len(avgs_c[0]) == len(avgs_s[1]) == len(avgs_c[1]) == len(buf_sizes)

# GRAPH 1:
# plot raw averages
plt.plot(avgs_s[0], avgs_s[1], label='Assembler')
plt.plot(avgs_c[0], avgs_c[1], label='C')
plt.xlabel('buffer size')
plt.ylabel('Mean (of %s samples) num of buffers set in %s seconds' % (REPS, HOWLONG,))
plt.legend()
plt.savefig(os.path.join(OUTDIR, "num_set.png"))
plt.clf()
plt.close()

# GRAPH 2:
# plot ratio of bufs processed. asm vs. C
y = []
for i in range(len(buf_sizes)):
    y.append(avgs_s[1][i] / avgs_c[1][i])

plt.plot(buf_sizes, y)
plt.title('Comparison of num bufs processed in %s seconds' % HOWLONG)
plt.xlabel('buffer size')
plt.ylabel('Mean (of %s samples) ratio of buffers processed' % (REPS, ))
plt.savefig(os.path.join(OUTDIR, "ratio.png"))

print("Results in the '%s' directory" % OUTDIR)
