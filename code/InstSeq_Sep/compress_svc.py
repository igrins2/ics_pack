import numpy as np
import astropy.io.fits as pyfits

class SlitviewCompressor():
    def __init__(self, mask):
        self.m = mask
        self._comp_arguments = dict(compression_type="HCOMPRESS_1",
                                    hcomp_scale=2.5)

    def get_compressed_hdulist(self, header, data, slices, slices_guide=None):
        hdu_list = [pyfits.PrimaryHDU()]

        dm = np.ma.array(data.copy(), mask=self.m).filled(0)

        hdu_comp_all = pyfits.CompImageHDU(data=dm, header=header.copy(),
                                           **self._comp_arguments)

        hdu_list.append(hdu_comp_all)

        # hdu_subset = pyfits.CompImageHDU(data=data[slices], header=header,
        #                                  compression_type="GZIP_1")
        hdu_subset = pyfits.ImageHDU(data=data[slices], header=header.copy())

        hdu_list.append(hdu_subset)

        if slices_guide is not None:

            # hdu_subset_g = pyfits.CompImageHDU(data=data[slices_guide],
            #                                    header=header,
            #                                    compression_type="GZIP_1")
            hdu_subset_g = pyfits.ImageHDU(data=data[slices_guide],
                                           header=header.copy())

            hdu_list.append(hdu_subset_g)

        return pyfits.HDUList(hdu_list)


def test():

    f = pyfits.open("SDCS_20140316_0505.fits")
    slices = slice(1001, 1072), slice(980, 1039)

    mask_name = "slitmaskv3.fits"
    mask = pyfits.open(mask_name)[0].data>0
    comp = SlitviewCompressor(mask)

    hdu_list = comp.get_compressed_hdulist(f[0].header, f[0].data,
                                           slices, slices)

    hdu_list.writeto("comp3.fits", clobber=True)
