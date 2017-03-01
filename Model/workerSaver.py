import h5py
import yaml
from datetime import datetime

def workerSaver(fileData,dic,q):
    """Function that can be run in a separate thread for continuously save data to disk.
    fileData -- STRING with the path to the file to use.
    dic -- A dictionary with metadata
    q -- Queue that will store all the images to be saved to disk.
    """
    f = h5py.File(fileData, "a") # This will append the file.
    now = str(datetime.now())
    g = f.create_group(now)
    allocate = 1000 # Number of frames to allocate along the z-axis.
    keep_saving = True # Flag that will stop the worker function if running in a separate thread.
    metaData = yaml.dump(dic)          # Has to be submitted via the queue a string 'exit'
    g.create_dataset('metadata',data=metaData)
    i=0
    while keep_saving:
        while not q.empty():
            img = q.get()
            if type(img)==type('exit'):
                keep_saving = False
            elif i == 0: # First time it runs, creates the dataset
                x = img.shape[0]
                y = img.shape[1]
                dset = g.create_dataset('timelapse', (x,y,allocate), maxshape=(x,y,None)) # The images are going to be stacked along the z-axis.
                dset[:,:,i] = img                                                                 # The shape along the z axis will be increased as the number of images increase.
                i+=1
            else:
                if i == dset.shape[2]:
                    dset.resize(i+allocate,axis=2)
                dset[:,:,i] = img
                i+=1
    f.flush()
    f.close()
