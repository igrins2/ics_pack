import astropy.io.fits as fits 

# for info 
_hdul = fits.open("N20231006S0000.fits")
print(_hdul.info())

# for header
for idx in range(5):
    print("--------------------------------------------------------------")
    print(repr(_hdul[idx].header))

print("=================================================")
print(repr(_hdul[5].data))
