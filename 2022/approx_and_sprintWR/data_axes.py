from math import ceil, floor
from manimlib import *

from typing import Optional, Sequence, Iterable, Union

def IdentityFormater(x):
	return x

def coord_in_rect(x,y, x_min,x_max,y_min,y_max):
	return (x_min<=x<=x_max) and (y_min<=y<=y_max)

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



class Axis(VGroup):
	CONFIG = {
		# total style
		"color": GREY_B,
		"stroke_width": 2,

		# length control
		"x_range": [-4, 4, 1],
		"unit_size": 1, # how big is one virtual unit, in screen rel unit.
		"width": None,

		# tick related
		"include_ticks": True,
		"tick_size": 0.1,
		"longer_tick_multiple": 1.5,
		"tick_offset": 0,
			  
		# number label related
		"include_numbers": False,
		"line_to_number_direction": DOWN,
		"line_to_number_buff": MED_SMALL_BUFF,
		"formatter": None,
		"decimal_number_config": {
			"num_decimal_places": 0,
			"font_size": 36,
			"group_with_commas": False
		},
		# When animated, WHETHER reuse old number labels or not.
		# On by default; If turned off, animations may be slow.
		# But when doing morphing animations like axes.shift/scale
		# you may want to turn this off to PREVENT unchanged number labels.
		"morph_existing_number_labels": True, 
		
		# tip related
		"include_tip": False,
		"tip_config": {
			"width": 0.25,
			"length": 0.25,
		},

		# whether dynamically change structure at interpolate
		"dynamic": True
	}

	def __init__(self, x_range: Optional[Sequence[float]] = None, **kwargs):
		super().__init__(**kwargs)

		if x_range is None:
			x_range = self.x_range
		if len(x_range) == 2:
			x_range = [*x_range, 1]
		x_min, x_max, x_step = x_range
		self.x_min, self.x_max, self.x_step = x_min, x_max, x_step

		line = self._create_line()
		self.add(line);self.line=line
		if self.width:
			self.set_width(self.width)
			self.unit_size = self._get_unit_size()
		else:
			self.scale(self.unit_size)
		self.center()

		if self.include_tip:
			line.add_tip()
			line.tip.set_stroke(
				self.stroke_color,
				self.stroke_width,
			)

		if self.include_ticks:
			self._add_ticks()
		if self.include_numbers:
			self._add_numbers()

	# coordinate conversion
	
	def get_origin(self) -> np.ndarray:
		return self.line.get_start()

	def number_to_point(self, number: Union[float, np.ndarray]) -> np.ndarray:
		alpha = (number - self.x_min) / (self.x_max - self.x_min)
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
		return interpolate(self.x_min, self.x_max, proportion)

	def n2p(self, number: float) -> np.ndarray:
		"""Abbreviation for number_to_point"""
		return self.number_to_point(number)

	def p2n(self, point: np.ndarray) -> float:
		"""Abbreviation for point_to_number"""
		return self.point_to_number(point)

	# tick related

	def _get_unit_size(self) -> float:
		return self.line.get_length() / (self.x_max - self.x_min)

	def _compute_ticks_pos(self) -> np.ndarray:
		'''根据数轴范围和单位大小自适应计算需要画出的tick位置'''

		# 自适应计算tick_step
		# some little magic here
		# which can be explained on a log-log plot of unit-interval and tick step
		tick_density=0.5 # tunable param
		exponent = -np.log10(self.unit_size*0.999*tick_density) #*0.999是为了避免一些浮点误差问题 
		整数, 小数 = floor(exponent), exponent-floor(exponent)
		tick_step = 10**(整数)
		if 小数>0.7: tick_step *= 2
		
		# 计算[tick_min, tick_max]中的、是tick_step整数倍的数值，作为tick位置
		x_min, x_max = self.x_min, self.x_max
		if self.include_tip: x_max -= self.tip_config['length']/self.unit_size
		tick_min =  ceil(x_min/tick_step)*tick_step
		tick_max = floor(x_max/tick_step)*tick_step
		
		eps=1e-6 #should be robust under all PRACTICAL cases.
		all_tick_pos = np.arange(tick_min, tick_max+tick_step-eps, tick_step)
		return all_tick_pos

	def _create_line(self, **line_kwargs) -> Line:
		
		line_config = {
			'color': self.color,
			'tip_config': self.tip_config,
		}
		final_config = merge_dicts_recursively(line_config, line_kwargs)

		line = Line(
			self.x_min * RIGHT, self.x_max * RIGHT, 
			**final_config
		)

		return line

	def _create_tick(self, x: float, size: Optional[float] = None) -> Line:
		'''create a tick, not all the ticks. 
		Does no change to structure in self.'''
		if size is None:
			size = self.tick_size
		result = Line(size * DOWN, size * UP)
		result.rotate(self.line.get_angle())
		result.move_to(self.number_to_point(x))
		result.match_style(self)
		return result

	def _add_ticks(self) -> None:
		ticks = VGroup()
		all_tick_pos = self._compute_ticks_pos()
		
		for x in all_tick_pos:
			size = self.tick_size
			ticks.add(self._create_tick(x, size))
		self.add(ticks)
		self.ticks = ticks
		self._organize_subgroups()

	def get_ticks(self) -> VGroup:
		return self.ticks

	# number label related
	def _compute_number_labels(self, formatter = None, density = None):
		if formatter is None:
			formatter = IdentityFormater

		exponent = -np.log10(self.unit_size*0.999*0.32) #*0.999是为了避免一些浮点误差问题 
		整数, 小数 = floor(exponent), exponent-floor(exponent)
		num_step = 10**(整数)
		if 小数>=0.7: num_step *= 2
		#print(self.unit_size, num_step)
		
		# 计算[tick_min, tick_max]中的、是tick_step整数倍的数值，作为tick位置
		x_min, x_max = self.x_min, self.x_max
		if self.include_tip: x_max -= self.tip_config['length']/self.unit_size
		pos_min =  ceil(x_min/num_step)*num_step
		pos_max = floor(x_max/num_step)*num_step
		
		eps=1e-6 #should be robust under all PRACTICAL cases.
		all_pos = np.arange(pos_min, pos_max+num_step-eps, num_step)
		all_num = [formatter(pos) for pos in all_pos]
		return all_num, all_pos

	def _create_number(
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
			direction = self.line_to_number_direction
		if buff is None:
			buff = self.line_to_number_buff
		if pos is None:
			pos = num

		num_mob = DecimalNumber(num, **number_config)
		self._put_number_label_in_place(num_mob, pos, direction, buff)

		return num_mob

	def _put_number_label_in_place(
		self,
		num_mob: DecimalNumber,
		pos: float,
		direction: Optional[np.ndarray] = None,
		buff: Optional[float] = None,
	) -> DecimalNumber:
		if direction is None:
			direction = self.line_to_number_direction
		if buff is None:
			buff = self.line_to_number_buff
		num_mob.next_to(
			self.number_to_point(pos),
			direction=direction,
			buff=buff
		)
		if num_mob.get_value() < 0 and direction[0] == 0:
			# Align without the minus sign
			num_mob.shift(num_mob[0].get_width() * LEFT / 2)
		return num_mob

	def _add_numbers(
		self,
		nums: Optional[Iterable[float]] = None,
		poss: Optional[Iterable[float]] = None,
		font_size: int = 24,
		**kwargs
	) -> VGroup:
		if nums is None:
			if not self.formatter is None:
				nums, poss = self._compute_number_labels(self.formatter)
			else:
				nums, poss = self._compute_number_labels()

		kwargs["font_size"] = font_size

		# experimental feature
		numbers = VGroup()
		if self.morph_existing_number_labels and hasattr(self, 'numbers'):
			if hasattr(self,'numbers'): # 考虑add_numbers第一次被调用的时候
				origin_num_mobjects = self.numbers
				self.remove(self.numbers)
			else:
				origin_num_mobjects = VGroup()
			origin_num_value = [m.get_value() for m in origin_num_mobjects]
			for num, pos in zip(nums, poss):
				if num in origin_num_value:
					num_mobj = origin_num_mobjects[origin_num_value.index(num)]
					self._put_number_label_in_place(num_mobj, pos)
				else:
					num_mobj = self._create_number(num, pos, **kwargs)
				numbers.add(num_mobj)
		else: # (typically) the first time numbers are added
			for num, pos in zip(nums,poss):
				numbers.add(self._create_number(num, pos, **kwargs))
		self.add(numbers)
		self.numbers = numbers

		self._organize_subgroups()

		return numbers

	# axis label
	def _add_axis_label(
		self,
		label_str: str = 'x',
		label_class = Tex,
		direction: np.ndarray = DOWN,
		buff: float = MED_SMALL_BUFF,
		**label_kwargs
	):
		self.label = label_class(label_str, **label_kwargs)\
			.next_to(self.line.get_end(),direction,buff)
		self.add(self.label)
		self._organize_subgroups()

	def _organize_subgroups(self):
		'''place the subgroups(ticks, numbers, label, if there're any) in a certain order
		so that they can be correctly interpolated between the same group.
		Intended to be automatically triggered through internal functions.'''
		#TODO: to make things less complicated
		if hasattr(self, 'label'): self.remove(self.label);self.add(self.label)
		if hasattr(self, 'ticks'): self.remove(self.ticks);self.add(self.ticks)
		if hasattr(self, 'numbers'): self.remove(self.numbers);self.add(self.numbers)

	# still in progress
	def set_range(self, x_min_new: float, x_max_new: float, x_step_new: Optional[float]=None):
		if x_step_new is None: x_step_new = self.x_step

		x_range_new = [x_min_new, x_max_new, x_step_new]
		self.x_range=x_range_new
		self.x_min, self.x_max, self.x_step = self.x_range

		self.unit_size = self._get_unit_size()

		if self.include_ticks: 
			self.remove(self.ticks)
			self._add_ticks()
		if self.include_numbers:
			self.remove(self.numbers)
			self._add_numbers()

		return self

	# Always better to have these two methods (copy and interp.) re-written 
	# to prevent weird probelms in animation.

	def copy(self, deep: bool = False):
		copy_mobject = super().copy(deep)
		if hasattr(copy_mobject, 'label'): copy_mobject.label =	copy_mobject[self.submobjects.index(self.label)] 
		if hasattr(copy_mobject, 'ticks'): copy_mobject.ticks = copy_mobject[self.submobjects.index(self.ticks)] 
		if hasattr(copy_mobject, 'numbers'): copy_mobject.numbers = copy_mobject[self.submobjects.index(self.numbers)] 
		return copy_mobject

	def interpolate(self, m1: VMobject, m2: VMobject, alpha: float, *args, **kwargs):
		super().interpolate(m1, m2, alpha, *args, **kwargs)
		
		x_min = interpolate(m1.x_min, m2.x_min, alpha)
		x_max = interpolate(m1.x_max, m2.x_max, alpha)
		x_step = interpolate(m1.x_step, m2.x_step, alpha)
		if self.dynamic:
			self.set_range(x_min, x_max, x_step)

		return self

	def interpolate_family(self, m1: VMobject, m2: VMobject, alpha: float, *args, **kwargs):
		#super().interpolate(m1, m2, alpha, *args, **kwargs)
		self.line.interpolate(m1.line, m2.line, alpha, *args, **kwargs)
		self.line.tip.interpolate(m1.line.tip, m2.line.tip, alpha, *args, **kwargs)

		if hasattr(self, 'label') and hasattr(m1, 'label') and hasattr(m2, 'label'):
			for sm, sm1, sm2 in zip(self.label.get_family(), m1.label.get_family(), m2.label.get_family()):
				sm.interpolate(sm1, sm2, alpha, *args, **kwargs)

		x_min = interpolate(m1.x_min, m2.x_min, alpha)
		x_max = interpolate(m1.x_max, m2.x_max, alpha)
		x_step = interpolate(m1.x_step, m2.x_step, alpha)
		self.set_range(x_min, x_max, x_step)

		return self

	# see: DataAxes.lock_matching_data
	def lock_matching_data(self, mobject1: Mobject, mobject2: Mobject):
		family = [self.line, self.line.tip]
		family1 = [mobject1.line, mobject1.line.tip]
		family2 = [mobject2.line, mobject2.line.tip]
		for sm, sm1, sm2 in zip(family, family1, family2):
			keys = sm.data.keys() & sm1.data.keys() & sm2.data.keys()
			sm.lock_data(list(filter(
				lambda key: np.all(sm1.data[key] == sm2.data[key]),
				keys,
			)))
		return self

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
		},
		"x_axis_config": {},
		"y_axis_config": {
			"line_to_number_direction": LEFT,
		},

		# advanced options, still in dev
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
		VGroup.__init__(self, **kwargs)

		if x_range is not None:
			self.x_range[:len(x_range)] = x_range
		if y_range is not None:
			self.y_range[:len(y_range)] = y_range

		#mask number labels out, or y_axis will have number labels in wrong direction.
		self.axis_config['include_numbers']=False 
		
		self.x_axis = self._create_axis(
			self.x_range, self.x_axis_config, self.width,
		)
		self.y_axis = self._create_axis(
			self.y_range, self.y_axis_config, self.height
		)
		self.y_axis.rotate(90 * DEGREES, about_point=ORIGIN)
		self.x_axis.next_to(ORIGIN,RIGHT,buff=0)
		self.y_axis.next_to(ORIGIN,  UP ,buff=0)

		if self.axis_align_towards_zero: 
			self.align_axes_towards_zero()


		if self.include_numbers:
			self._add_numbers()
		# Add as a separate group in case various other
		# mobjects are added to self, as for example in
		# NumberPlane below
		self.axes = VGroup(self.x_axis, self.y_axis)
		self.add(*self.axes)
		self.center()

		self.plots = VGroup()
		self.add(self.plots)

		self.set_dynamic(self.dynamic)

	def set_dynamic(self, dynamic):
		self.dynamic = dynamic
		self.x_axis.dynamic = dynamic
		self.y_axis.dynamic = dynamic

	# snippit for internal use
	def _add_numbers(self):
		self.x_axis._add_numbers()
		self.y_axis._add_numbers()#add numbers after init so that they can be correctly placed

		self.axis_config['include_numbers'] = True
		self.x_axis.include_numbers = True
		self.y_axis.include_numbers = True

	# for users to use
	def add_numbers(self):
		if self.include_numbers: 
			return self
		else:
			self.include_numbers=True
			self._add_numbers()
			return self

	def _create_axis(
		self,
		range_terms: Sequence[float],
		axis_config: dict[str],
		length: float
	) -> Axis:
		new_config = merge_dicts_recursively(self.axis_config, axis_config)
		#print(new_config['include_numbers'])
		new_config["width"] = length
		#print(range_terms,'\n', new_config)
		axis = Axis(range_terms, **new_config)
		return axis

	def get_origin(self) -> np.ndarray:
		origin = self.x_axis.get_origin()
		if self.axis_align_towards_zero:
			X,Y=self.x_axis, self.y_axis
			if   X.x_max<0: origin_x = X.number_to_point(X.x_max)[0]
			elif X.x_min>0: origin_x = X.number_to_point(X.x_min)[0]
			else:           origin_x = X.number_to_point(   0   )[0]
			if   Y.x_max<0: origin_y = Y.number_to_point(Y.x_max)[1]
			elif Y.x_min>0: origin_y = Y.number_to_point(Y.x_min)[1]
			else:           origin_y = Y.number_to_point(   0   )[1]
			origin = np.array([origin_x, origin_y, 0.0])

		return origin

	def coords_to_point(self, *coords: float) -> np.ndarray:
		origin = self.get_origin()
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
		tgt_x_coord = 0
		if self.x_axis.x_min>0: tgt_x_coord = self.x_axis.x_min
		if self.x_axis.x_max<0: tgt_x_coord = self.x_axis.x_max
		Δ = self.y_axis.line.get_center()[0] - self.x_axis.n2p(tgt_x_coord)[0]
		if Δ!=0: self.y_axis.shift(LEFT*Δ)

		tgt_y_coord = 0
		if self.y_axis.x_min>0: tgt_y_coord = self.y_axis.x_min
		if self.y_axis.x_max<0: tgt_y_coord = self.y_axis.x_max
		Δ = self.x_axis.line.get_center()[1] - self.y_axis.n2p(tgt_y_coord)[1]
		if Δ!=0: self.x_axis.shift(DOWN*Δ)

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
			#self.y_axis.move_to(ORIGIN)

	def add_axis_labels(
		self,
		x_label_str: str = 'x', y_label_str: str = 'y',
		label_class = Tex,
		**label_kwargs
	) -> Axes:
		self.x_axis._add_axis_label(x_label_str, label_class, DOWN, **label_kwargs)
		self.y_axis._add_axis_label(y_label_str, label_class, LEFT, **label_kwargs)

		return self

	# 作图相关

	def plot(self, func, x_range, dynamic=True, attach=True, **curve_kwargs) -> ParametricCurve:
		# handle plot range
		original_x_range = x_range.copy()
		x_range[0] = max(x_range[0],self.x_axis.x_min)
		x_range[1] = min(x_range[1],self.x_axis.x_max)
		if len(x_range)<3: x_range.append(None)
		x_range[2] = (x_range[1]-x_range[0])/100

		# create object
		curve = ParametricCurve(
			lambda t: self.c2p(t,func(t)), x_range, **curve_kwargs
		)

		# add updater if specified
		if dynamic: 
			def update_plot(m):
				x_range[0] = max(original_x_range[0],self.x_axis.x_min)
				x_range[1] = min(original_x_range[1],self.x_axis.x_max)
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
					if x_axis.x_min<=x<=x_axis.x_max and y_axis.x_min<=y<=y_axis.x_max:
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
		x_min, x_max = self.x_axis.x_min, self.x_axis.x_max
		y_min, y_max = self.y_axis.x_min, self.y_axis.x_max
		start, end = clip_line_in_rect(coord1, coord2, x_min, x_max, y_min, y_max)
		if start==None: start, end = coord1, coord1

		# cosntruct object
		line = line_class(self.c2p(*start), self.c2p(*end), **line_kwargs)

		# add updater if specified
		if dynamic: 
			def update_line(m):
				x_min, x_max = self.x_axis.x_min, self.x_axis.x_max
				y_min, y_max = self.y_axis.x_min, self.y_axis.x_max
				start, end = clip_line_in_rect(coord1, coord2, x_min, x_max, y_min, y_max)
				if start==None: start, end = coord1, coord1
				m.set_start_and_end(self.c2p(*start), self.c2p(*end))
				
			line.add_updater(update_line)

		if attach:
			self.plots.add(line)
		
		return line

	def copy(self, deep: bool = False):
		copy_mobject = super().copy(deep)
		if hasattr(copy_mobject, 'x_axis'): copy_mobject.x_axis = copy_mobject[self.submobjects.index(self.x_axis)] 
		if hasattr(copy_mobject, 'y_axis'): copy_mobject.y_axis = copy_mobject[self.submobjects.index(self.y_axis)] 
		if hasattr(copy_mobject, 'plots'): copy_mobject.plots = copy_mobject[self.submobjects.index(self.plots)] 
		return copy_mobject

	# After some TEDIOUS debugging(4hr), I figured out that this method has to be
	# weakened to have the animations work correctly.
	# Here's WHY: For mobjects whose structure may vary during animation(some mobj being added/removed)
	#             get_family() (essentially a DFS) may alias between its start and end, and cause
	#             unintended data locking(with a slim chance), which may make certain attributes
	#             static, instead of being animated as desired.
	# Example: sm=axes.y_axis.line.tip, both sm1 and sm2 is some Text object with empty points
	#          then sm1.data['points']==sm2.data['points'] and sm.data['poitns'] will be locked, 
	#          which may be the attribute that we want to animate.
	# Not sure whether this is the best way to fix it.
	# Maybe I can instead override get_family() to return family mobjects that have stable structure only
	# but that will break the semantic of "get_family".
	def lock_matching_data(self, mobject1: Mobject, mobject2: Mobject):
		family = [self.x_axis.line, self.x_axis.line.tip, self.y_axis.line, self.y_axis.line.tip]
		family1 = [mobject1.x_axis.line, mobject1.x_axis.line.tip, mobject1.y_axis.line, mobject1.y_axis.line.tip]
		family2 = [mobject2.x_axis.line, mobject2.x_axis.line.tip, mobject2.y_axis.line, mobject2.y_axis.line.tip]
		for sm, sm1, sm2 in zip(family, family1, family2):
			keys = sm.data.keys() & sm1.data.keys() & sm2.data.keys()
			sm.lock_data(list(filter(
				lambda key: np.all(sm1.data[key] == sm2.data[key]),
				keys,
			)))
		return self

	def interpolate_family(self, m1: VMobject, m2: VMobject, alpha: float, *args, **kwargs):
		self.x_axis.interpolate_family(m1.x_axis, m2.x_axis, alpha, *args, **kwargs)
		self.y_axis.interpolate_family(m1.y_axis, m2.y_axis, alpha, *args, **kwargs)
		#for plot in self.plots:
		#	plot.update()

		if self.axis_align_towards_zero:
			self.align_axes_towards_zero()

		return self
		

class ShiftRange(Transform):
	CONFIG = {
		'suspend_mobject_updating': False
	}
	def __init__(
		self,
		data_axes: DataAxes,
		arg1, arg2, # (arg1, arg2) can be like ('x'|'y', [-3,3]) or ([-3,3],[-3,3])
		**kwargs
	):
		digest_config(self, kwargs)
		self.mobject = data_axes
		self.target_mobject = data_axes.copy()
		if arg1 in ['x','y']:
			self.target_mobject.set_range(arg1, arg2)
		else:
			self.target_mobject.set_all_ranges(arg1, arg2)
	
	def begin(self) -> None:
		self.check_target_mobject_validity()
		
		Animation.begin(self)
		'''if not self.mobject.has_updaters:
			self.mobject.lock_matching_data(
				self.starting_mobject,
				self.target_copy,
			)'''#TODO to be added (to accelerate animations)

	def interpolate_mobject(self, alpha: float) -> None:
		return self.mobject.interpolate_family(self.starting_mobject, self.target_mobject, alpha)

	def finish(self) -> None:
		Animation.finish(self)
		#self.mobject.unlock_data()

	def get_all_mobjects(self):
		return [
			self.mobject,
			self.starting_mobject,
			self.target_mobject,
		]
	def get_all_families_zipped(self):
		return zip(self.mobject, self.starting_mobject, self.target_mobject)
		

class ApplyMethodToDataAxes(ApplyMethod):
	CONFIG = {
		'suspend_mobject_updating': False
	}
	def begin(self) -> None:
		self.target_mobject = self.create_target()
		self.check_target_mobject_validity()
		
		Animation.begin(self)
		'''if not self.mobject.has_updaters:
			self.mobject.lock_matching_data(
				self.starting_mobject,
				self.target_copy,
			)'''#TODO to be added (to accelerate animations)

	def interpolate_mobject(self, alpha: float) -> None:
		# the KEY that make this animation different
		return self.mobject.interpolate_family(self.starting_mobject, self.target_mobject, alpha)

	def finish(self) -> None:
		Animation.finish(self)
		#self.mobject.unlock_data()

	def get_all_mobjects(self):
		return [
			self.mobject,
			self.starting_mobject,
			self.target_mobject,
		]
	def get_all_families_zipped(self):
		return zip(self.mobject, self.starting_mobject, self.target_mobject)

class TestDataAxesAnimation(Scene):
	def construct(self):
		axes = DataAxes([-3,-1],[-3,-1], axis_align_towards_zero=True)
		self.add(axes)
		axes.add_axis_labels()
		
		self.play(ApplyMethodToDataAxes(axes.set_all_ranges, [-3,3],[-3,3]))
		self.play(ApplyMethodToDataAxes(axes.set_all_ranges, [-1,1],[-1,1]))

		curve = axes.plot(lambda x: 0.5*x**2, [-100,100])

		self.play(ApplyMethodToDataAxes(axes.set_all_ranges, [-3,3], [-3,3], suspend_mobject_updating=False))
		self.play(ApplyMethodToDataAxes(axes.shift,UP,suspend_mobject_updating=False))
		self.play(ApplyMethodToDataAxes(axes.scale,0.5,suspend_mobject_updating=False))