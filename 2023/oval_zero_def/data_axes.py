from math import ceil, floor
from manimlib import *

import sys
__module_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__module_path__)
from manimhub.constants import XDIM, YDIM, FML_COLOR

from typing import Optional, Sequence, Iterable, Union, Callable

def IdentityFormater(x):
	return x

def coord_in_rect(x,y, x_min,x_max,y_min,y_max):
	return (x_min<=x<=x_max) and (y_min<=y<=y_max)

def closest_to_zero(range):
	min, max = range[:2]
	if min>0: return min
	if max<0: return max
	return 0

def clip_line_in_rect(start,end,x_min,x_max,y_min,y_max):
	'''clip line into a rectangle, assuming that the rect perpendicular.
	Return value: start,end after clipping
	return None,None if the line is completely clipped.'''

	# use LiangBarsky line clipping algorithm to fulfill the task
	# see: https://stackoverflow.com/questions/11194876/clip-line-to-screen-coordinates

	Δx, Δy = end[0]-start[0], end[1]-start[1]
	t0, t1 = 0.0, 1.0 # parametrize line to be v(t)=v0+t*Δ

	for edge in range(4):
		if edge==0: p, q = -Δx, -(x_min-start[0])
		if edge==1: p, q =  Δx,  (x_max-start[0])
		if edge==2: p, q = -Δy, -(y_min-start[1])
		if edge==3: p, q =  Δy,  (y_max-start[1])

		if p==0 and q<0: return None, None
		
		if  p!=0: r = q/p
		elif q>0: r = np.inf
		else:     r =-np.inf

		if p<0: 
			if r>t1: return None, None
			elif r>t0: t0=r # line is clipped!
		elif p>0: 
			if r<t0: return None, None
			elif r<t1: t1=r # line is clipped!

	return [start[0]+t0*Δx, start[1]+t0*Δy], \
			[start[0]+t1*Δx, start[1]+t1*Δy]

# The default function that locate all tick pos.
# xmin, xmax and xstep are passed as default arguments.
# The Axis mobj is also passed as the last argument,
# in case that locator needs more info from Axis.

# Note: DefaultLocator's will align tick position
# to integer multiple of tick units.
class StubbornTickLocator:
	def __init__(self, avoid_zero=False):
		self.avoid_zero = avoid_zero # useful when axis in Axes
	def __call__(self, x_min, x_max, x_step, axis) -> np.ndarray:
		assert(x_min<x_max and x_step>0)
		if axis.include_tip:
			x_max -= axis.tip_config['length']/axis.unit_size
		tick_step = x_step
		tick_min =  ceil(x_min/tick_step)*tick_step
		tick_max = floor(x_max/tick_step)*tick_step
		
		eps=1e-6 #should be robust under all PRACTICAL cases.
		all_tick_pos = np.arange(tick_min, tick_max+tick_step-eps, tick_step)
		if self.avoid_zero:
			all_tick_pos = [tick_pos for tick_pos in all_tick_pos if tick_pos!=0]
		return all_tick_pos

class SmartTickLocator:
	def __init__(self, tick_density=0.5, avoid_zero=False):
		self.tick_density = tick_density
		self.avoid_zero = avoid_zero # useful when axis in Axes
	def __call__(self, x_min, x_max, x_step, axis) -> Iterable:
		assert(x_min<x_max)

		# 自适应计算tick_step
		# Some little math here, 
		# which can be explained on a log-log plot 
		# of unit-interval and tick step.

		# 可调参数，决定tick的密度
		tick_density=self.tick_density
		exponent = -np.log10(axis.unit_size*0.999*tick_density) #*0.999是为了避免一些浮点误差问题 
		整数, 小数 = floor(exponent), exponent-floor(exponent)
		tick_step = 10**(整数)
		if 小数>0.7: tick_step *= 2
		
		# 计算[tick_min, tick_max]中的、是tick_step整数倍的数值，作为tick位置
		x_min, x_max = axis.min, axis.max
		if axis.include_tip: 
			x_max -= axis.tip_config['length']/axis.unit_size
		tick_min =  ceil(x_min/tick_step)*tick_step
		tick_max = floor(x_max/tick_step)*tick_step

		eps=1e-6 #should be robust under all PRACTICAL cases.
		all_tick_pos = np.arange(tick_min, tick_max+tick_step-eps, tick_step)
		if self.avoid_zero:
			all_tick_pos = [tick_pos for tick_pos in all_tick_pos if tick_pos!=0]
		return all_tick_pos

HORIZONTAL = 0
VERTICAL = 1

class Axis(VGroup):
	CONFIG = {
		# total style
		"color": GREY_B,
		"stroke_width": 2,

		# length control
		"range": [-4, 4, 1],
		# how long is one logic unit, in screen rel unit.
		"unit_size": 1, 
		# only one of 'unit_size' and 'width' should be set.
		# If both are specified upon construction, we'll 
		# stick to width.
		"length": None, 

		# tick related
		"include_ticks": True,
		"tick_length": 0.1,
		"tick_locator": SmartTickLocator(),
		
		# number label related
		"include_numbers": False,
		"number_to_line_direction": DOWN,
		"number_to_line_buff": MED_SMALL_BUFF,
		"number_locator": None, # the same to tick locator if not specified
		"formatter": None,
		"decimal_number_config": {
			"num_decimal_places": 0,
			"font_size": 30,
			"group_with_commas": False
		},
		# When animated, WHETHER reuse old number labels or not.
		# On by default; If turned off, animations may be slow.
		# But when doing morphing animations like axes.shift/scale
		# you may want to turn this off to PREVENT unchanged number labels.
		"reuse_existing_number_labels": True, 
		
		# tip related
		"include_tip": False,
		"tip_config": {
			"width": 0.25,
			"length": 0.25,
		},

		# axis label
		"include_label": False,
		"label_str": 'x',
		"label_class": Tex,
		"label_config": {
			"color": FML_COLOR
		},

		# whether dynamically change structure at interpolate
		"dynamic": True,

		# direction of axis. can be either HORIZONTAL(0) or VERTICAL(1).
		"direction": HORIZONTAL

		# extra notes: 
		# 'include_ticks', 'include_numbers', 'include_tip' are NOT meant 
		# to be dynamic. Change them after mobj construction (or interp
		# between Axis with different values on these properties) at your
		# own risk.
	}

	def __init__(self, range: Optional[Sequence[float]] = None, **kwargs):
		if kwargs.get('direction', Axis.CONFIG['direction'])==VERTICAL:
			Axis.CONFIG['number_to_line_direction']=LEFT # override default config
		else:
			Axis.CONFIG['number_to_line_direction']=DOWN

		super().__init__(**kwargs)

		if range is None:
			range = self.range
		if len(range) == 2:
			range = [*range, 1]
		min, max, step = range
		self.min, self.max, self.step = min, max, step

		line = self._create_line()
		self.add(line);self.line=line # line at idx 0

		self.init_tip() # tip at idx 1
		self.init_ticks() # ticks at idx 2
		self.init_numbers() # numbers at idx 3
		self.init_label() # label at idx 4
		
	def scale(
		self, 
		scale_factor, 
		min_scale_factor: float = 1e-8, 
		about_point: Optional[np.ndarray] = None, 
		about_edge: np.ndarray = ORIGIN
	):
		self.line.scale(scale_factor, min_scale_factor, about_point, about_edge)
		if self.include_tip:
			dot = Dot(self.tip.get_tip_point())
			if about_point is None: about_point = self.line.get_center()
			dot.scale(scale_factor, min_scale_factor, about_point, about_edge)
			self.tip.shift(dot.get_center()-self.tip.get_tip_point())

		return self

	# coordinate conversion
	
	def get_origin(self) -> np.ndarray:
		return self.n2p(0)

	def number_to_point(self, number: Union[float, np.ndarray]) -> np.ndarray:
		alpha = (number - self.min) / (self.max - self.min)
		return outer_interpolate(self.line.get_start(), self.line.get_end(), alpha)

	def point_to_number(self, point: np.ndarray) -> float:
		points = self.line.get_points()
		start = points[0]
		end = points[-1]
		vect = end - start
		proportion = fdiv(
			np.dot(point - start, vect),
			np.dot(end - start, vect),
		)
		return interpolate(self.min, self.max, proportion)

	def n2p(self, number: float) -> np.ndarray:
		"""Abbreviation for number_to_point"""
		return self.number_to_point(number)

	def p2n(self, point: np.ndarray) -> float:
		"""Abbreviation for point_to_number"""
		return self.point_to_number(point)

	# tip
	def init_tip(self):
		if self.include_tip:
			tip_config = self.tip_config
			tip_config['fill_color'] = self.color
			tip = ArrowTip(**tip_config)
			tip.rotate(self.line.get_angle() - tip.get_angle())
			tip.shift(self.line.get_end() - tip.get_tip_point())
		else:
			tip = VMobject() # empty place holder
		self.tip = tip
		self.add(tip) 

	# tick related
	def _get_unit_size(self) -> float:
		length = self.line.get_length()
		return length / (self.max - self.min)

	def _compute_ticks_pos(self) -> np.ndarray:
		'''计算需要画出的tick位置'''
		return self.tick_locator(self.min, self.max, self.step, self)
		
	def _create_line(self, **line_kwargs) -> Line:
		'''Used only in __init__.'''
		line_config = {
			'color': self.color,
			'tip_config': self.tip_config,
		}
		final_config = merge_dicts_recursively(line_config, line_kwargs)

		if self.length:
			self.unit_size = self.length/(self.max-self.min)
		else:
			self.length = self.unit_size * (self.max-self.min)

		if self.direction==HORIZONTAL:
			DIR = RIGHT
		elif self.direction==VERTICAL:
			DIR = UP
		else:
			raise ValueError()

		line = Line(
			ORIGIN, self.length * DIR, 
			**final_config
		)
		line.center()

		return line

	def _generate_tick(self, x: float, size: Optional[float] = None) -> Line:
		'''create a single tick 
		Does no change to structure in self.'''
		if size is None:
			size = self.tick_length
		result = Line(size * DOWN, size * UP)
		result.rotate(self.line.get_angle())
		result.move_to(self.number_to_point(x))
		result.match_style(self)
		return result

	def init_ticks(self) -> None:
		ticks = VGroup()
		self.add(ticks)

		if not self.include_ticks: return

		all_tick_pos = self._compute_ticks_pos()
		
		for x in all_tick_pos:
			size = self.tick_length
			ticks.add(self._generate_tick(x, size))
		
		self.ticks = ticks

		# if set to True, next call to update_ticks()
		# will refresh all tick mobjects.
		self.ticks_invalidated = False
	
	def update_ticks(self) -> None:
		if not self.include_ticks: return
		self.ticks.clear()
		all_tick_pos = self._compute_ticks_pos()
		
		if self.ticks_invalidated:
			self.ticks_invalidated=False
			pass # not actually implemented yet

		for x in all_tick_pos:
			size = self.tick_length
			self.ticks.add(self._generate_tick(x, size))

	def get_ticks(self) -> VGroup:
		return self.ticks

	# number label related
	def _compute_number_labels(self):
		formatter = IdentityFormater
		if self.number_locator is None:
			locator = self.tick_locator
		else:
			locator = self.number_locator
		
		all_pos = locator(self.min, self.max, self.step, self)
		all_num = [formatter(pos) for pos in all_pos]
		return all_num, all_pos

	def _generate_number_label(
		self,
		num: float,
		pos: Optional[float] = None,
		direction: Optional[np.ndarray] = None,
		buff: Optional[float] = None,
		**number_config
	) -> DecimalNumber:
		number_config = merge_dicts_recursively(
			self.decimal_number_config, number_config
		)
		if direction is None:
			direction = self.number_to_line_direction
		if buff is None:
			buff = self.number_to_line_buff
		if pos is None:
			pos = num

		num_mob = DecimalNumber(num, **number_config)
		self._position_number_label(num_mob, pos, direction, buff)

		return num_mob

	def _position_number_label(
		self,
		num_mob: DecimalNumber,
		pos: float,
		direction: Optional[np.ndarray] = None,
		buff: Optional[float] = None,
	) -> DecimalNumber:
		if direction is None:
			direction = self.number_to_line_direction
		if buff is None:
			buff = self.number_to_line_buff
		num_mob.next_to(
			self.number_to_point(pos),
			direction=direction,
			buff=buff
		)
		# Align without the minus sign
		if num_mob.get_value() < 0 and direction[0] == 0:
			num_mob.shift(num_mob[0].get_width() * LEFT / 2)
		return num_mob

	def init_numbers(self, **kwargs) -> None:
		self.numbers = VGroup()
		self.add(self.numbers)

		if not self.include_numbers: return

		nums, poss = self._compute_number_labels()
		for num, pos in zip(nums,poss):
			self.numbers.add(self._generate_number_label(num, pos, **kwargs))

		# If set to True, next call to update_numbers()
		# will refresh all number mobjects.
		self.numbers_invalidated = False
	
	def update_numbers(
		self,
		nums: Optional[Iterable[float]] = None,
		poss: Optional[Iterable[float]] = None,
		**kwargs
	) -> VGroup:
		if not self.include_numbers: return

		nums, poss = self._compute_number_labels()

		if self.reuse_existing_number_labels and not self.numbers_invalidated:
			origin_num_mobjects = VGroup(*self.numbers.submobjects)
			self.numbers.clear()

			origin_num_value = [m.get_value() for m in origin_num_mobjects]
			for num, pos in zip(nums, poss):
				if num in origin_num_value:
					num_mobj = origin_num_mobjects[origin_num_value.index(num)]
					self._position_number_label(num_mobj, pos)
				else:
					num_mobj = self._generate_number_label(num, pos, **kwargs)
				self.numbers.add(num_mobj)
		else: # re-construct all the number label mobjects
			for num, pos in zip(nums,poss):
				self.numbers.add(self._generate_number_label(num, pos, **kwargs))

		return self.numbers

	# axis label
	def init_label(self):
		if not self.include_label:
			self.label = VMobject() # place holder
			self.add(self.label) 
		else:
			if self.direction==HORIZONTAL: direction = DOWN
			elif self.direction==VERTICAL: direction = LEFT
			self.label = self.label_class(self.label_str, **self.label_config)\
				.next_to(self.line.get_end(),direction,MED_SMALL_BUFF)
		self.add(self.label)

	def add_axis_label(
		self,
		label_str: str = 'x',
		label_class = Tex,
		direction: np.ndarray = None,
		buff: float = MED_SMALL_BUFF,
		**label_kwargs
	):
		if direction is None: 
			if self.direction==HORIZONTAL: direction = DOWN
			elif self.direction==VERTICAL: direction = LEFT
		self.remove(self.label)
		config = self.label_config.copy()
		config.update(label_kwargs)

		self.label = label_class(label_str, **label_kwargs)\
			.next_to(self.line.get_end(),direction,buff)
		self.add(self.label)

	# still in progress
	def set_range(self, min_new: float, max_new: float, step_new: Optional[float]=None, update_mobjects=True):
		if step_new is None: step_new = self.step

		range_new = [min_new, max_new, step_new]
		self.range=range_new
		self.min, self.max, self.step = self.range

		self.unit_size = self._get_unit_size()

		if not update_mobjects: return self

		self.update_ticks()
		self.update_numbers()

		return self

	# Always better to have these two methods (copy and interp.) re-written 
	# to prevent weird probelms in animation.

	def copy(self, deep: bool = False):
		copy_mobject = super().copy(deep)
		return copy_mobject

	def interpolate(self, m1: VMobject, m2: VMobject, alpha: float, *args, **kwargs):
		if 'recursive' in kwargs:
			recursive_interp = kwargs['recursive']
			del kwargs['recursive']
		else:
			recursive_interp = False
		if recursive_interp: self.dynamic=True
		min = interpolate(m1.min, m2.min, alpha)
		max = interpolate(m1.max, m2.max, alpha)
		step = interpolate(m1.step, m2.step, alpha)
		if recursive_interp:
			# 这里的顺序很重要。line.interpolate可能刷新unit_size，从而影响后面的set_range
			# (which is needed!)
			self.line.interpolate(m1.line, m2.line, alpha, *args, **kwargs)

			self.set_range(min, max, step, update_mobjects=True)
			
			if self.include_tip:
				self.tip.interpolate(m1.tip, m2.tip, alpha, *args, **kwargs)

			if hasattr(self, 'label') and hasattr(m1, 'label') and hasattr(m2, 'label'):
				for sm, sm1, sm2 in zip(self.label.get_family(), m1.label.get_family(), m2.label.get_family()):
					sm.interpolate(sm1, sm2, alpha, *args, **kwargs)
		else:
			self.set_range(min, max, step, update_mobjects=False)
			super().interpolate(m1, m2, alpha, *args, **kwargs)

		return self

	def interpolate_family(self, m1: VMobject, m2: VMobject, alpha: float, *args, **kwargs):
		#super().interpolate(m1, m2, alpha, *args, **kwargs)
		self.line.interpolate(m1.line, m2.line, alpha, *args, **kwargs)
		self.tip.interpolate(m1.tip, m2.tip, alpha, *args, **kwargs)

		if hasattr(self, 'label') and hasattr(m1, 'label') and hasattr(m2, 'label'):
			for sm, sm1, sm2 in zip(self.label.get_family(), m1.label.get_family(), m2.label.get_family()):
				sm.interpolate(sm1, sm2, alpha, *args, **kwargs)

		min = interpolate(m1.min, m2.min, alpha)
		max = interpolate(m1.max, m2.max, alpha)
		step = interpolate(m1.step, m2.step, alpha)
		self.set_range(min, max, step)

		return self

	# see: DataAxes.lock_matching_data
	def lock_matching_data(self, mobject1: Mobject, mobject2: Mobject):
		if self.dynamic: return

		family = [self.line, self.tip]
		family1 = [mobject1.line, mobject1.tip]
		family2 = [mobject2.line, mobject2.tip]
		for sm, sm1, sm2 in zip(family, family1, family2):
			keys = sm.data.keys() & sm1.data.keys() & sm2.data.keys()
			sm.lock_data(list(filter(
				lambda key: np.all(sm1.data[key] == sm2.data[key]),
				keys,
			)))
		return self
	
	# plt style API
	def lim(self, min, max, step=None):
		self.set_range(min, max, step)
	def xlim(self, min, max, step=None):
		self.set_range(min, max, step)
	def label(self, label_str):
		self.add_axis_label(label_str = label_str)
	def xlabel(self, label_str):
		self.add_axis_label(label_str = label_str)
	def set_tick_locator(self, new_locator: Callable):
		self.tick_locator = new_locator
		self.ticks_invalidated = True
	def set_number_locator(self, new_locator: Callable):
		self.number_locator = new_locator
	def set_number_formatter(self, new_formatter: Callable):
		self.formatter = new_formatter
		self.numbers_invalidated = True


class DataAxes(VGroup):
	CONFIG = {
		"height": FRAME_HEIGHT - 2,
		"width": FRAME_WIDTH - 2,

		"x_range": [0, 8],
		"y_range": [0, 6],

		"include_numbers": True,

		"axis_config": {
			"include_tip": True,
			#"include_numbers": True #this is according to the above lines
			"number_locator": SmartTickLocator(avoid_zero=True)
		},
		"x_axis_config": {"direction": HORIZONTAL},
		"y_axis_config": {"direction": VERTICAL},

		# still a bit buggy with number labels
		"axis_align_towards_zero": False,

		# whether dynamically change structure at interpolate
		"dynamic": True
	}

	def __init__(
		self,
		x_range: Optional[Sequence[float]] = None,
		y_range: Optional[Sequence[float]] = None,
		**kwargs
	):
		super().__init__(**kwargs)
		if x_range is not None:
			self.x_range[:len(x_range)] = x_range
		if y_range is not None:
			self.y_range[:len(y_range)] = y_range

		self.init_axis()

		if self.axis_align_towards_zero: 
			self.align_axes_towards_zero()

		self.center()

		self.plots = VGroup()
		self.add(self.plots) # plots at idx 2

	def init_axis(self) -> None:
		x_axis_config = dict()
		y_axis_config = dict()
		x_axis_config['range'] = self.x_range
		y_axis_config['range'] = self.y_range
		x_axis_config['length'] = self.width
		y_axis_config['length'] = self.height
		x_axis_config['label_str'] = 'x'
		y_axis_config['label_str'] = 'y'
		for config in [x_axis_config, y_axis_config]:
			config['include_numbers'] = self.include_numbers
			config['dynamic'] = self.dynamic
			config.update(self.axis_config)
		x_axis_config.update(self.x_axis_config)
		y_axis_config.update(self.y_axis_config)

		self.x_axis = Axis(**x_axis_config) 
		self.y_axis = Axis(**y_axis_config) 
		self.axes = VGroup(self.x_axis, self.y_axis)

		self.add(self.x_axis, self.y_axis) # x,y_axis at idx 0,1

		x_axis_shift = ORIGIN - self.x_axis.line.get_start()
		y_axis_shift = ORIGIN - self.y_axis.line.get_start()
		# this roughly equals to: 
		# x_axis.next_to(ORIGIN, RIGHT, buff=0)
		# y_axis.next_to(ORIGIN,   UP , buff=0)
		self.x_axis.shift(x_axis_shift)
		self.y_axis.shift(y_axis_shift)

	def init_numbers(self):
		self.x_axis.init_numbers()
		self.y_axis.init_numbers()#add numbers after init so that they can be correctly placed

		self.axis_config['include_numbers'] = True
		self.x_axis.include_numbers = True
		self.y_axis.include_numbers = True

	# TODO: add_label_axis还没有处理好
	# TODO: 提供numbers和axis等元素的attach/detach接口
	# for users to use
	def add_numbers(self):
		if self.include_numbers: 
			return self
		else:
			self.include_numbers=True
			self.init_numbers()
			return self

	def get_origin(self, clip_to_border=True) -> np.ndarray:
		if not clip_to_border:
			origin_x, origin_y = 0, 0
		else:
			if self.axis_align_towards_zero:
				origin_x = closest_to_zero(self.x_axis.range)
				origin_y = closest_to_zero(self.y_axis.range)
		origin = RIGHT*self.x_axis.n2p(origin_x)[XDIM]+UP*self.y_axis.n2p(origin_y)[YDIM]
		return origin

	def coords_to_point(self, *coords: float) -> np.ndarray:
		origin = self.get_origin(clip_to_border=False)
		return origin + sum(
			axis.number_to_point(coord) - origin
			for axis, coord in zip(self.get_axes(), coords)
		)

	def point_to_coords(self, point: np.ndarray) -> tuple[float, ...]:
		return tuple([
			axis.point_to_number(point)
			for axis in self.get_axes()
		])

	def c2p(self, *coords: float) -> np.ndarray:
		return self.coords_to_point(*coords)

	def p2c(self, point: np.ndarray) -> tuple[float, ...]:
		return self.points_to_coords(point)

	def get_axes(self) -> VGroup:
		return self.axes 

	def get_all_ranges(self) -> list[Sequence[float]]:
		return [self.x_range, self.y_range]

	def align_axes_towards_zero(self):
		# align y_axis towards zero coord at x_axis
		tgt_x_coord = closest_to_zero(self.x_axis.range)
		Δ = self.y_axis.line.get_center()[0] - self.x_axis.n2p(tgt_x_coord)[0]
		if Δ!=0: self.y_axis.shift(LEFT*Δ)

		tgt_y_coord = closest_to_zero(self.y_axis.range)
		Δ = self.x_axis.line.get_center()[1] - self.y_axis.n2p(tgt_y_coord)[1]
		if Δ!=0: self.x_axis.shift(DOWN*Δ)

		self.x_axis.number_locator.avoid_zero=(self.y_axis.min<tgt_y_coord<self.y_axis.max)
		self.y_axis.number_locator.avoid_zero=(self.x_axis.min<tgt_x_coord<self.x_axis.max)

		return self

	def set_all_ranges(self, x_range_new, y_range_new):
		self.x_axis.set_range(*x_range_new)
		self.y_axis.set_range(*y_range_new)
		if self.axis_align_towards_zero:
			self.align_axes_towards_zero()

	def set_range(self, dim, new_range):
		if dim in [0,'x']:
			self.x_axis.set_range(*new_range)
		elif dim in [1, 'y']:
			self.y_axis.set_range(*new_range)
		else:
			raise ValueError("Invalid dimension!")
			
		if self.axis_align_towards_zero:
			self.align_axes_towards_zero()

	def add_axis_labels(
		self,
		x_label_str: str = 'x', y_label_str: str = 'y',
		label_class = Tex,
		**label_kwargs
	) -> Axes:
		self.x_axis.add_axis_label(x_label_str, label_class, DOWN, **label_kwargs)
		self.y_axis.add_axis_label(y_label_str, label_class, LEFT, **label_kwargs)

		return self

	# 作图相关
	# TODO: 2023年重构后，还没有处理作图相关的（可能的）新bug

	def plot(self, func, x_range, dynamic=True, attach=True, **curve_kwargs) -> ParametricCurve:
		# handle plot range
		original_x_range = x_range.copy()
		x_range[0] = max(x_range[0],self.x_axis.min)
		x_range[1] = min(x_range[1],self.x_axis.max)
		if len(x_range)<3: x_range.append(None)
		x_range[2] = (x_range[1]-x_range[0])/100

		# create object
		curve = ParametricCurve(
			lambda t: self.c2p(t,func(t)), x_range, **curve_kwargs
		)

		# add updater if specified
		if dynamic: 
			def update_plot(m):
				x_range[0] = max(original_x_range[0],self.x_axis.min)
				x_range[1] = min(original_x_range[1],self.x_axis.max)
				#print(x_range)
				if x_range[0]>x_range[1]:
					x_range[1]=x_range[0]
				new_curve = ParametricCurve(
					lambda t: self.c2p(t,func(t)), x_range, **curve_kwargs
				)
				m.set_points(new_curve.get_points())
				m.t_range = x_range
				return m
				
			curve.add_updater(update_plot)
		
		# attach to self if required
		if attach:
			self.plots.add(curve)
		
		return curve
		
	def scatter(self, X,Y, dynamic=True, attach=True, **dot_kwargs):
		# handle dot parameters
		DOT_CONFIG = {'color':YELLOW}
		dot_kwargs = merge_dicts_recursively(DOT_CONFIG, dot_kwargs)

		# generate object
		dots = VGroup(
			*[Dot(self.c2p(x,y), **dot_kwargs) for x,y in zip(X,Y)]
		)

		# add updater if specified
		if dynamic: 
			def update_scatter(m):
				x_axis, y_axis = self.x_axis, self.y_axis
				for dot,x,y in zip(m,X,Y): 
					dot.move_to(self.c2p(x,y))
					if x_axis.min<=x<=x_axis.max and y_axis.min<=y<=y_axis.max:
						dot.set_opacity(1)
					else:
						dot.set_opacity(0)
			dots.add_updater(update_scatter)

		# attach to self if required
		if attach:
			self.plots.add(dots)

		return dots

	def line(self, coord1, coord2, dynamic=True, attach=True, line_class=Line, **line_kwargs):
		# clip coords into axes frame
		x_min, x_max = self.x_axis.min, self.x_axis.max
		y_min, y_max = self.y_axis.min, self.y_axis.max
		start, end = clip_line_in_rect(coord1, coord2, x_min, x_max, y_min, y_max)
		if start==None: start, end = coord1, coord1

		# cosntruct object
		line = line_class(self.c2p(*start), self.c2p(*end), **line_kwargs)

		# add updater if specified
		if dynamic: 
			def update_line(m):
				x_min, x_max = self.x_axis.min, self.x_axis.max
				y_min, y_max = self.y_axis.min, self.y_axis.max
				start, end = clip_line_in_rect(coord1, coord2, x_min, x_max, y_min, y_max)
				if start==None: start, end = coord1, coord1
				m.set_start_and_end(self.c2p(*start), self.c2p(*end))
				
			line.add_updater(update_line)

		if attach:
			self.plots.add(line)
		
		return line

	# 方便获得一些辅助线，生成的线默认不由DataAxes管
	def get_vline(self, x, y, line_class=Line, **line_kwargs):
		return self.line((x,0),(x,y), dynamic=False, attach=False, line_class=line_class, **line_kwargs)
	def get_hline(self, x, y, line_class=Line, **line_kwargs):
		return self.line((0,y),(x,y), dynamic=False, attach=False, line_class=line_class, **line_kwargs)

	def copy(self, deep: bool = False):
		copy_mobject = super().copy(deep)
		copy_mobject.x_axis = copy_mobject[self.submobjects.index(self.x_axis)] 
		copy_mobject.y_axis = copy_mobject[self.submobjects.index(self.y_axis)] 
		copy_mobject.plots = copy_mobject[self.submobjects.index(self.plots)] 
		copy_mobject.axes = VGroup(copy_mobject.x_axis, copy_mobject.y_axis)
		return copy_mobject

	# After 4hrs of TEDIOUS debugging, I figured out that this 
	# locking mechanism has to be weakened(or disabeld) to let the 
	# animations that changes mobject structure dynamically 
	# work correctly. Here's WHY: 
	# For mobjects whose structure may vary during animation(some mobj 
	# being added/removed), get_family() (essentially a DFS) may ALIAS 
	# between the animation start and end, causing unexpected data 
	# locking(with a slim chance), which may make certain attributes
	# static, instead of being animated as desired.
	# I think the best way to fix it is to disable data locking, in 
	# which case we sacrifice performance but recover animation
	# correctness.
	def lock_matching_data(self, mobject1: Mobject, mobject2: Mobject):
		if self.dynamic: return self
		# else
		return super().lock_matching_data(self, mobject1, mobject2)
		'''family = [self.x_axis.line, self.x_axis.tip, self.y_axis.line, self.y_axis.tip]
		family1 = [mobject1.x_axis.line, mobject1.x_axis.tip, mobject1.y_axis.line, mobject1.y_axis.tip]
		family2 = [mobject2.x_axis.line, mobject2.x_axis.tip, mobject2.y_axis.line, mobject2.y_axis.tip]
		for sm, sm1, sm2 in zip(family, family1, family2):
			keys = sm.data.keys() & sm1.data.keys() & sm2.data.keys()
			sm.lock_data(list(filter(
				lambda key: np.all(sm1.data[key] == sm2.data[key]),
				keys,
			)))
		return self'''

	def interpolate(self, start: VMobject, end: VMobject, alpha: float, *args, **kwargs):
		recursive_interp = kwargs.get('recursive', False)
		if not recursive_interp:
			if 'recursive' in kwargs: del kwargs['recursive']
			return super().interpolate(start, end, alpha, *args, **kwargs)
		else:
			self.x_axis.interpolate(start.x_axis, end.x_axis, alpha, *args, **kwargs)
			self.y_axis.interpolate(start.y_axis, end.y_axis, alpha, *args, **kwargs)
			# self.update_plots()

	def interpolate_family(self, m1: VMobject, m2: VMobject, alpha: float, *args, **kwargs):
		self.x_axis.interpolate_family(m1.x_axis, m2.x_axis, alpha, *args, **kwargs)
		self.y_axis.interpolate_family(m1.y_axis, m2.y_axis, alpha, *args, **kwargs)
		#for plot in self.plots:
		#	plot.update()

		if self.axis_align_towards_zero:
			self.align_axes_towards_zero()

		return self
	