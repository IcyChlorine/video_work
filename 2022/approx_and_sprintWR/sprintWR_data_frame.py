from manimlib import *

import os,sys
sys.path.append('C:\\StarSky\\Programming\\MyProjects\\')
from manimhub import *
sys.path.append(os.getcwd())
from data_axes import DataAxes
from data import *

from typing import Optional, Sequence

class SprintWRDataFrame(DataAxes):
	CONFIG = {
		"width": FRAME_WIDTH - 4.5,
		'x_range': [0,120],
		'y_range': [5,11],

		#'include_numbers': False,

		'x_axis_config':{
			'formatter': lambda x: x+date_origin
		},
		'y_axis_config':{
			'decimal_number_config': {
				"num_decimal_places": 2,
			}
		}
	}
	def __init__(
		self, 
		x_range: Optional[Sequence[float]] = None, 
		y_range: Optional[Sequence[float]] = None, 
		**kwargs
	):
		#self.x_axis_conifg = {'formatter': lambda x: x+1912}
		super().__init__(x_range, y_range, **kwargs)
		self.align_on_border(LEFT,buff=1)
		#self.add_axis_labels('年份','时间/s',Text, font=楷体, font_size=30)

	def plot_data(self, **kwargs):
		return super().scatter(date,time, **kwargs)

	def plot_fit_curve(self, deg=1, **kwargs):
		if deg==0:
			return super().plot(lambda x: 10.0,x_range=self.x_range, **kwargs)
		elif deg==1:
			return super().plot(lambda x: linear_fit_coef[0]+linear_fit_coef[1]*x,
								x_range=self.x_range, **kwargs)
		elif deg==2:
			return super().plot(lambda x: 
								quadratic_fit_coef[0]+
								quadratic_fit_coef[1]*x+
								quadratic_fit_coef[2]*x**2,
								x_range=self.x_range, **kwargs)
		elif deg==3:
			return super().plot(lambda x:
								cubic_fit_coef[0]+
								cubic_fit_coef[1]*x+
								cubic_fit_coef[2]*x**2+
								cubic_fit_coef[3]*x**3,
								x_range=self.x_range, **kwargs)


	def draw_axis_labels(self):
		self.add_axis_labels('年份','时间/s',Text, font=文楷, font_size=30)
		return self