import numpy as np
import astropy.io.fits as pyfits

class SlitviewProc():
    def __init__(self, mask):
        self.m = mask

    def get_hdulist(self, header, data, slices, slices_guide=None):
        hdu_list = [pyfits.PrimaryHDU()]

        dm = np.ma.array(data.copy(), mask=self.m).filled(0)        
        hdu_comp_all = pyfits.ImageHDU(data=dm, header=header.copy())
        hdu_list.append(hdu_comp_all)

        hdu_subset = pyfits.ImageHDU(data=data[slices], header=header.copy())
        hdu_list.append(hdu_subset)

        if slices_guide is not None:
            hdu_subset_g = pyfits.ImageHDU(data=data[slices_guide], header=header.copy())

            hdu_list.append(hdu_subset_g)

        return pyfits.HDUList(hdu_list)
