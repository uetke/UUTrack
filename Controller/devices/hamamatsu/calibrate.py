#!/usr/bin/python
#
## @file
#
# This script is used for camera calibration. It records the sum of x and
# the sum of x*x for every pixel in every frame.
#
# Hazen 10/13
#

import numpy
import sys
import time

import hamamatsu_camera as hc

if (len(sys.argv) != 3):
    print "usage: <filename> <number frames>"
    exit()

hcam = hc.HamamatsuCameraMR(0)

# Set camera parameters.
cam_offset = 0
hcam.setPropertyValue("defect_correct_mode", "OFF")
hcam.setPropertyValue("exposure_time", 0.01)
hcam.setPropertyValue("binning", "1x1")
hcam.setPropertyValue("readout_speed", 2)

if True:
    cam_x = 2048
    cam_y = 2048
    hcam.setPropertyValue("subarray_hsize", cam_x)
    hcam.setPropertyValue("subarray_vsize", cam_y)

if False:
    cam_x = 512
    cam_y = 512
    hcam.setPropertyValue("subarray_hpos", 768)
    hcam.setPropertyValue("subarray_vpos", 768)
    hcam.setPropertyValue("subarray_hsize", cam_x)
    hcam.setPropertyValue("subarray_vsize", cam_y)

print "integration time (seconds):", 1.0/hcam.getPropertyValue("internal_frame_rate")[0]

# Create numpy arrays.
mean = numpy.zeros((cam_x, cam_y), dtype = numpy.int64)
var = numpy.zeros((cam_x, cam_y), dtype = numpy.int64)

# Acquire data.
#break_on_next_loop = False
n_frames = int(sys.argv[2])
hcam.startAcquisition()
processed = 0
captured = 0
start_time = time.time()
while (processed < n_frames):

    # Get frames.
    [frames, dims] = hcam.getFrames()
    captured += len(frames)

    if ((processed%10)==0):
        print "Accumulated", processed, "frames, current back log is", len(frames), "frames"

    if (len(frames) > 0):
        aframe = frames[0].getData().astype(numpy.int32) - cam_offset
        aframe = numpy.reshape(aframe, (cam_x, cam_y))
        mean += aframe
        var += aframe * aframe
        processed += 1

    #if break_on_next_loop:
    #    break

    #if (len(frames) == 0):
    #    break_on_next_loop = True

end_time = time.time()
hcam.stopAcquisition()
print "Captured:", captured, "frames in", (end_time - start_time), "seconds."
print "FPS:", captured/(end_time - start_time)

# Compute mean & variance & save results.
#mean = mean/float(n_frames)
#var = var/float(n_frames) - mean*mean

numpy.save(sys.argv[1], [numpy.array([n_frames]), mean, var])

mean_mean = numpy.mean(mean)/float(n_frames)
print "mean of mean:", mean_mean
print "mean of variance:", numpy.mean(var)/float(n_frames) - mean_mean*mean_mean
