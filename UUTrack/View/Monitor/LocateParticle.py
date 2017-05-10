"""
    openCET.View.LocateParticle.py
    ==================================
    The LocateParticle class contains necessary methods for localizing centroid of a particle and following its track.
    the idea is to make the output suitable for analysis with TrackPy of similar open-source tracking packages

    .. lastedit:: 10/5/2017
    .. sectionauthor:: Sanli Faez <s.faez@uu.nl>
"""
import numpy as np
#from scipy.ndimage.measurements import center_of_mass as cenmass

class LocatingParticle:
    """
    initiate the localization requirements
    :param psize: expected particle size (e.g. point spread function)
    :param step: expected step size for searching for next location
    :param noiselvl: noise level below which all image data will be set to zero
    :param iniloc: starting position of the track passed by the monitoring routine
    [not implemented] consistently return success/failure messages regarding locating the particle
    """
    def __init__(self, psize, step, noiselvl, iniloc):
        self.noise = noiselvl
        self.psize = psize
        self.step = step
        self.loc = iniloc

    def findParticleSize(self, image, location):
        """Estimates size of the PSF of the particle at the specified :location: in the :image:"""
        x, y = np.int(location)
        w = np.int(2 * (self.psize + self.step))
        imgpart = image[x-w:x+w+1,y-w:y+w+1]
        imgpart[imgpart<self.noise] = 0
        cy, cx = self.centroid(imgpart)
        self.loc = [x+w-cx, y+w-cy]
        self.psize = np.int(2*np.sqrt(np.sum(imgpart)/np.amax(imgpart)))
        return self.psize

    def centroid(data):
        h, w = np.shape(data)
        x = np.arange(0, w)
        y = np.arange(0, h)

        X, Y = np.meshgrid(x, y)

        cx = np.sum(X * data) / np.sum(data)
        cy = np.sum(Y * data) / np.sum(data)

        return cx, cy

    def pointspread(data, cx, cy):
        h, w = np.shape(data)
        x = np.arange(0, w) - cx
        y = np.arange(0, h) - cy

        X, Y = np.meshgrid(x, y)

        sx = np.sqrt(np.sum(np.square(X * data)) / np.square(np.sum(data)))
        sy = np.sqrt(np.sum(np.square(Y * data)) / np.square(np.sum(data)))

        return sx, sy

    def Locate(self, image):
        """extracts the particle localization information close the lastly known location (self.loc) and updates it"""
        x, y = np.int(self.loc)
        w = np.int(2 * (self.psize + self.step))
        imgpart = image[x-w:x+w+1,y-w:y+w+1]
        imgpart[imgpart<self.noise] = 0
        cx, cy = self.centroid(imgpart)
        self.loc = [x+w-cx, y+w-cy]
        mass = np.sum(imgpart)
        sx, sy = self.pointspread(imgpart, cx, cy)
        locinfo = [mass, cx, cy, sx, sy]
        return locinfo