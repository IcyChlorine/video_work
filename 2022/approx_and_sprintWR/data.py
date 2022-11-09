# data for [man's 100 sprint world record]
# The origin data and data for approximations
# are moved here as they are CONSTANT data.

# date for the time that W.R. got broken, in year.
# date plays the role of X, and the origin is shifted
# to year 1912.
# 1912 is the year IETF came in, which made everything
# certificated and standardized.
# Therefore the data since 1912 is selected.

import numpy as np

date_origin=1912 
date= [
	 0.60,  9.40, 18.70, 24.56, 
	44.67, 48.56, 56.56, 56.87, 
	71.60, 76.82, 79.54, 79.74, 
	82.60, 84.66, 87.54, 90.79, 
	93.54, 95.78, 96.51, 96.71, 97.71
]
		
# the world record value, in second.
time= [
	10.6, 10.4, 10.3, 10.2, 
	10.1, 10.0, 9.99, 9.95, 
	9.93, 9.92, 9.9, 9.86, 
	9.85, 9.84, 9.79, 9.78, 
	9.77, 9.74, 9.72, 9.69, 9.58
]

# fit curve coef
# in the sequence of p0, p1, p2, p3 (incremental deg order)
linear_fit_coef = [10.47, -0.00790]
quadratic_fit_coef = [10.52, -0.01068, 2.6e-5]
quadratic_fit_coef_wo_Bolt = [10.54, -0.01273, 5.067e-5]
cubic_fit_coef = [10.62, -0.02472, 0.0003665, -2.173e-06]
# poly approx with deg>3 is almost meaningless. 
# the following fits are meant to show overfitting.
#deg5_fit_coef = [10.62, -0.03045, 0.0010, -2.31e-5, 2.61e-7, -1.11e-9]
#deg8_fit_coef = [10.59, 0.02494, -0.01013, 0.0008369, -3.265e-05, 
#				6.888e-07, -8.068e-09, 4.942e-11, -1.235e-13]
# NOTE! I can't believe the precision it requires to calculate correctly
# 1e-6 is not enough, and everything has to be updated to double precision
# to make it work.
deg5_fit_coef = np.array([
	10.617708456545717,
	-0.030451073700500,
	0.001012717159766, 
	-2.312910603944893e-05,
	2.609128949455449e-07,
	-1.107448485626398e-09
])
deg8_fit_coef = np.array([
	10.586806454774393,
	 0.024944620275936,
	-0.010129994998278,
	 8.369043007612796e-04,
	-3.265038496580343e-05,
	 6.887548516473659e-07,
	-8.068381229887277e-09,
	 4.942036617929819e-11,
	-1.235418178800306e-13,
], dtype='float64') #高精度版本


# fit data
# zero point of linear fitting
linear_zero = 1325.15 # ~ 1912 + 1325.15 = 3237.15 B.C.
# min point of quadratic fitting, (x,y)
quadratic_min = (205.38, 9.42) # x ~ 205.38+1912 = 2117.38 B.C.

def poly_func(coef):
	def func(x: float):
		ret=0
		for d,p in enumerate(coef):
			ret+=p*(x**d)
		return ret

	return func

# better precision
def spoly_func(coef):
	def func(x: float):
		terms=np.zeros(shape=(len(coef),), dtype='float64')
		x/=100
		for d,p in enumerate(coef):
			terms[d]=p*(x**d)*(100**d)
		return np.sum(terms)

	return func