import h5py
import numpy as np
from datetime import datetime

def workerSaver(fileData, meta, q):
    """Function that can be run in a separate thread for continuously save data to disk.
    fileData -- STRING with the path to the file to use.
    meta -- A string with metadata. It is kept as a string in order to provide flexibility for other programs.
    q -- Queue that will store all the images to be saved to disk.
    """
    f = h5py.File(fileData, "a")  # This will append the file.
    now = str(datetime.now())
    g = f.create_group(now)
    allocate = 50 # Number of frames to allocate along the z-axis.
    keep_saving = True  # Flag that will stop the worker function if running in a separate thread.
                        # Has to be submitted via the queue a string 'exit'
    g.create_dataset('metadata',data=meta)
    i = 0
    j = 0
    while keep_saving:
        while not q.empty():
            img = q.get()
            if type(img) == type('exit'):
                keep_saving = False
            elif i == 0:  # First time it runs, creates the dataset
                x = img.shape[0]
                y = img.shape[1]
                d = np.zeros((x,y,allocate),dtype='uint16')
                dset = g.create_dataset('timelapse', (x, y, allocate), maxshape=(x, y, None), compression='gzip', dtype='i2')  # The images are going to be stacked along the z-axis.
                #dset[:, :, i] = img                                                                 # The shape along the z axis will be increased as the number of images increase.
                # dset = g.create_dataset('thumbnail',data = imsave(img))
                d[:,:,i] = img
                i += 1
            else:
                if i == allocate:#dset.shape[2]:
                    dset[:,:,j:j+allocate] = d
                    d = np.zeros((x, y, allocate),dtype='uint16')
                    dset.resize(i+allocate,axis=2)
                    i = 0
                    j += allocate
                d[:, :, i] = img
                #dset[:,:,i] = img
                i+=1
    print('Quitting workerSaver')
    if j>0 or i>0:
        dset[:, :, j:j+allocate] = d # Last save before closeing
    f.flush()
    f.close()
