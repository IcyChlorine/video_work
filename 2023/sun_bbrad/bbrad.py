import os
import numpy as np
from numpy import pi as PI
import pandas as pd
import bisect

#physical constants
c = 299792458
h = 6.62607015e-34
kB = 1.3806452e-23

_DEFAULT_TEMPERATURE = 5777 # K
_DEFAULT_INTENSITY = 1 # relative intensity, for control only
# identifiers start with "_" will not be imported
_temperature = _DEFAULT_TEMPERATURE 
_intensity = _DEFAULT_INTENSITY

#* ------------------------------------------------------------------------- *#
#* Part I theoretic functions
#  all radiation functions are for [radiance exitance], see below.
#* ------------------------------------------------------------------------- *#

# Planck's Law for BlackBody Radiation.
def fml_Planck(λ):
	# bbrad for BlackBody Radiation.
	# see https://en.wikipedia.org/wiki/Planck%27s_law
	# input  unit: wavelength in nanometer (!)
	# output unit: spectral radiant exitance, in kW/m2/nm

	nom   = 2*PI*h*c**2/(λ*1e-9)**5
	denom = np.exp(h*c/((λ*1e-9)*kB*_temperature))-1
	
	return _intensity*(nom/denom)*1e-9*1e-3 # 1e-9 for nm and 1e-3 for kW

def Planck_term1(λ):
	term1 = 2*PI*h*c**2/(λ*1e-9)**5
	return _intensity*term1*1e-12
def Planck_term2(λ):
	term2 = 1/(np.exp(h*c/((λ*1e-9)*kB*_temperature))-1)
	return _intensity*term2


# Wiens'w Law for BlackBody Radiation, which is correct for short wavelength only.
def fml_Wien(λ):
	# Wien's blackbody radiation law(not correct).
	# input: wavelength in nanometer
	# output: spectral radiant exitance, in kW/m2/nm

	term1 = 2*PI*h*c**2/(λ*1e-9)**5
	term2 = np.exp(-h*c/((λ*1e-9)*kB*_temperature))

	return _intensity*(term1*term2)*1e-9*1e-3 # 1e-9 for nm and 1e-3 for kW

# Reighley-Jeans Law for BlackBody Radiation, which is correct for long wavelength only.
def fml_ReighleyJeans(λ):
	# Reighley-Jeans law.
	# input: wavelength in nanometer
	# output: spectral radiant exitance, in kW/m2/nm

	term = 2*PI*c*kB*_temperature/(λ*1e-9)**4
	return _intensity*term*1e-9*1e-3

def fml_Wien_displacement(T):
	# Wien's displacement law.
	# input: temperature in Kelvin
	# output: peak wavelength in nanometer
	b = 2.897771955e6 
	return b / T
def fml_Planck_normalized(λ):
	return Planck(λ)/Planck(fml_Wien_displacement(_temperature))

# shortcuts
Planck = fml_Planck
Wien   = fml_Wien
RJ     = fml_ReighleyJeans
ReighleyJeans = RJ
Planck_normalized = fml_Planck_normalized
Wien_displacement = fml_Wien_displacement

def set_temperature(T: float):
	global _temperature
	_temperature = T

def set_intensity(intensity: float):
	global _intensity
	_intensity = intensity

#* ------------------------------------------------------------------------- *#
#* Part II experimental data *#
#* ------------------------------------------------------------------------- *#
_exp_data = dict()
_exp_data_loaded = False
_EXP_DATA_FILENAME = 'solar-spectrum.csv'

# NOTE: 
# [radiance exitance] 辐出度，是辐射体向外辐射的能量密度
# [irradiance]        辐照度/辐入度，是在某处接收到的能量密度
#                     这两个单位都是以单位面积而言的
# * * 但是因为经过了传播，二者并不等同，需要换算 * * #
# see: https://en.wikipedia.org/wiki/Radiance

radius_sun = 696e6 # in meter
earth_sun_dist = 149.6e9 # in meter

# helper functions
def _load_exp_data(filename: str = _EXP_DATA_FILENAME):
	try:
		data = pd.read_csv(filename)
	except FileNotFoundError:
		print(f"Can't find data file: {filename}!")
		os._exit(1)
		return None
	
	global _exp_data
	_exp_data['wavelength'] = data.iloc[:,0].values # wavelength in nm
	_exp_data['irradiance_space'] = data.iloc[:,1] # 在地球接收到的来自太阳的辐照度，in W/m2/nm
	_exp_data['irradiance_terra'] = data.iloc[:,2] # terra for terrestrial, 地球上的

def _ensure_data_loaded():
	global _exp_data_loaded
	if not _exp_data_loaded:
		_load_exp_data()
		_exp_data_loaded = True
	else:
		pass

def get_exp_data():
	_ensure_data_loaded()
	return _exp_data

def get_exp_data_range():
	_ensure_data_loaded()
	return [_exp_data['wavelength'][0], _exp_data['wavelength'][-1]]

def irrad_to_rad_exit(irradiance: float):
	# irradiance(on earth) -> radiance exitance(on sun)
	return irradiance * ((radius_sun+earth_sun_dist)/radius_sun)**2

def rad_exit_to_irrad(rad_exit: float):
	# radiance exitance(on sun) -> irradiance(on earth)
	return rad_exit * (radius_sun/(radius_sun+earth_sun_dist))**2

def _interp(X,Y,x):
	left  = bisect.bisect_left (X, x)
	right = bisect.bisect_right(X, x)
	# exact values found
	if right-left>0: return Y[left]
	# else: constant extrapolation
	if left==0:      return Y[0 ]
	if left==len(X): return Y[-1]
	# else: interpolate
	left = right-1
	return (Y[right]-Y[left])/(X[right]-X[left])*(x-X[left])+Y[left]

# exposed functions for retrieving experimental data
def exp_space_irrad(λ):
	# input  unit: wavelength in nanometer
	# output unit: spectral irradiance, in kW/m2/nm
	_ensure_data_loaded()
	X, Y, x = _exp_data['wavelength'], _exp_data['irradiance_space'], λ
	value = _interp(X,Y,x)
	# unit conversion
	return value*1e-3 # 1e-3 for kW; exp_data already in /nm

def exp_terra_irrad(λ):
	# input  unit: wavelength in nanometer
	# output unit: spectral irradiance, in kW/m2/nm
	_ensure_data_loaded()
	X, Y, x = _exp_data['wavelength'], _exp_data['irradiance_terra'], λ
	value = _interp(X,Y,x)
	# unit conversion
	return value*1e-3 # 1e-3 for kW; exp_data already in /nm
	
def exp_space_exit(λ):
	# input  unit: wavelength in nanometer
	# output unit: spectral radiance exitance, in kW/m2/nm
	_ensure_data_loaded()

	value = exp_space_irrad(λ)
	# irradiance -> radiance exitance
	return irrad_to_rad_exit(value)

def exp_terra_exit(λ):
	# input  unit: wavelength in nanometer
	# output unit: spectral radiance exitance, in kW/m2/nm
	_ensure_data_loaded()

	value = exp_terra_irrad(λ)
	# irradiance -> radiance exitance
	return irrad_to_rad_exit(value)

# To compare with theoretic functions,
# radiance exitance is used by default.
exp_space = exp_space_exit
exp_terra = exp_terra_exit


#* ------------------------------------------------------------------------- *#
#* Part III formula latex sources
#* ------------------------------------------------------------------------- *#
tex_planck = r'\frac{2hc^2}{\lambda^5}\frac{1}{(e^{\frac{hc}{\lambda k T}}-1)}'
tex_wien   = r'\frac{2hc^2}{\lambda^5}e^{-\frac{hc}{\lambda kT}}'
tex_rj     = r'\frac{2c}{\lambda^4}kT'