#
# Scenes for the video reside here.
#

from manimlib import *

__manimhub_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__manimhub_path__)
from manimhub import *

# custom mobjects import
import os,sys
sys.path.append(os.getcwd())

from data import *
from sprintWR_data_frame import SprintWRDataFrame
from data_axes import *
from stencil import *

class BlastHightlight(SurroundingRectangle):
	def __init__(self, scene, pos):
		super().__init__(scene.camera.frame, buff=0)

		self.set_style(
			stroke_opacity=0, stroke_width=0,
			fill_opacity=1, fill_color=YELLOW
		)

		# Use some hack to encode information into vert. attrib.
		# so as to send extra messages to the shader.
		# Since the color of blast highlight is hard-coded(see the 
		# code piece below), its ok to override the color uniform
		# for info conveying.
		# NOTE: This may lead to unexpected behaviors and is NOT
		# recommended for stable releases. Known breakings include:
		#  - set_color and related func won't work(this is trivial)
		#  - override move_to and similar pos manipulation func
		#      will cause issues
		self.data['fill_rgba'][0][0]=1
		self.data['fill_rgba'][0][1]=pos[0]
		self.data['fill_rgba'][0][2]=pos[1]

		all_shaders = self.get_shader_wrapper_list()
		for shader in all_shaders:
			if shader.shader_folder=='quadratic_bezier_fill':
				frag_shader = shader
				break

		frag_shader.replace_code('frag_color = color;',
		'''
			float radius=length(xyz_coords-vec3(color[1],color[2],0));
			vec3 yellow=vec3(1.0,1.0,0.2);
			vec3 bg_color=vec3(1./8);
			float strength=color[0];
			float factor=3*strength*exp(-radius/strength); //exp(-radius^2)更像太阳or恒星的样子，但-radius更接近我想要的效果
			//float factor=3-radius;
			frag_color.rgb=bg_color+yellow*factor;
			frag_color.a=length(frag_color.rgb)/3;
		''')
		#print(self.shader_wrapper.shader_folder)

	def set_strength(self, I):
		
		var=self.data['fill_rgba'][0]
		var[0]=I
	def set_pos(self, pos):
		self.data['fill_rgba'][0][1]=pos[0]
		self.data['fill_rgba'][0][2]=pos[1]
	#def move_to(self, pos):
	#	self.set_pos(pos)

def gen_smoothed_func(origin_func, f=1.0, ζ=0.5, r=2, time_span=1, num_sample=100):
	# See https://www.bilibili.com/video/BV1wN4y1578b
	T=np.linspace(0,1,num_sample); Δt=time_span/(num_sample-1)
	X=[origin_func(t) for t in T]; Y=[]

	π = np.pi
	k1, k2, k3 = ζ/(π*f), (2*π*f)**(-2), (r*ζ)/(2*π*f)

	#y0
	x=X[0]; y=x; Y.append(y)
	xd=(X[1]-X[0])/Δt; yd=xd
	for i in range(1, len(X)):
		x=X[i]; xd=X[i]-X[i-1]
		y +=Δt*yd; Y.append(y)
		yd+=Δt*(x+k3*xd-y-k1*yd)/k2
		
	def wrapped_func(alpha):
		i=floor(alpha*num_sample)
		if i>=len(Y): return Y[-1]
		if i<0: return Y[0]
		return Y[i] #TODO: make it linear interpolated.

	return wrapped_func

# sigmoid-like smooth step function
def smooth_step(x, threshold, sigma):
	return 1/(1+np.exp(-(x-threshold)/sigma))

class RecordsIntro(StarskyScene):
	def construct(self):
		axes = SprintWRDataFrame(include_numbers = False).align_on_border(LEFT,1.4)
		axes.add_numbers()
		axes.add_axis_labels('年份','时间/s',Text, font=落霞孤鹜, font_size=30)
		axes.set_range('y',[8,10.5])
		self.add(axes)

		dot_cfg = {'color': ORANGE}
		label_cfg = {'color': FML_COLOR, 'font_size':30}
		name_cfg = {'color':YELLOW_B, 'font_size':38, 'font':'Constantia'}

		WR1 = Dot(axes.c2p(1920-1912, 10.2), **dot_cfg) # great leap
		label1 = Text('(1920, 10.4s)', **label_cfg).next_to(WR1, RIGHT)
		name1 = Text('Charley Paddock', **name_cfg).next_to(WR1, DOWN, buff=0.3).align_to(WR1, LEFT)

		WR2 = Dot(axes.c2p(1968-1912, 9.95), **dot_cfg) # 10s break
		label2 = Text('(1968, 9.95s)', **label_cfg).next_to(WR2, RIGHT)
		name2 = Text('Jim Hines', **name_cfg).next_to(WR2, DOWN, buff=0.3).align_to(WR2, LEFT)

		WR3 = Dot(axes.c2p(2009-1912, 9.58), **dot_cfg) # Bolt's 9.58
		label3 = Text('(2009, 9.58s)', **label_cfg).next_to(WR3, RIGHT)
		name3 = Text('Usian Bolt', **name_cfg).next_to(WR3, DOWN, buff=0.3).align_to(WR3, LEFT)

		self.play(FadeIn(VGroup(WR1, label1, name1)))
		self.wait(8)
		self.play(FadeIn(VGroup(WR2, label2, name2)))
		self.wait(8)
		self.play(FadeIn(VGroup(WR3, label3, name3)))
		self.wait(8)

class IntroductionAndExtrapolation(StarskyScene):
	def section(self):
		'''Just a mark'''
		pass

	def stall(self):
		self.interact()

	def is_indev(self):
		return self.preview
	def is_rendering(self):
		return not self.preview
	
	def setup(self):
		axes = SprintWRDataFrame(include_numbers = False).align_on_border(LEFT,1.4)
		self.axes = axes

	def construct(self) -> None:
		# TODO: 调整一些等待时间，让后期剪辑轻松一点
		# TODO: extrapolate_and_error当中，给小白加上眨眼效果
		self.create_axes()
		self.plot_data_and_lin_fit()
		self.illustrate_lin_fit()
		#*------------------------*#
		self.extrapolate_and_error()

		#self.embed()
		
	def create_axes(self):
		axes = self.axes
		
		self.play(Create(axes),run_time=1.3)

		#*偷天换日动画三元组，trial for formal use
		# Step I: create the objects to be animated
		axes.add_numbers()
		axes.add_axis_labels('年份','时间/s',Text, font=落霞孤鹜, font_size=30)

		# Step II: (build animations and) play
		self.play(AnimationGroup(
			*[
				FadeIn(m, UP*0.2) for m 
				in list(axes.x_axis.numbers)+[axes.x_axis.label]
			],
			lag_ratio=0.2,run_time=2
		),AnimationGroup(
			*[
				FadeIn(m, RIGHT*0.2) for m 
				in list(axes.y_axis.numbers)+[axes.y_axis.label]
			],		
			lag_ratio=0.2,run_time=3
		))
		self.wait(1.5)
		# Step III: re-organize them in the scene, to clean up the mess(if any)
		self.add(axes)

	def plot_data_and_lin_fit(self):
		# 画数据与拟合直线

		# Precondition
		axes = self.axes
		
		# create, animate and reorganize
		data_scatter = axes.plot_data()
		self.play(AnimationGroup(
			*[
				Popup(m) for m 
				in data_scatter
			],
			lag_ratio=0.2, run_time=2.5, rate_func=linear
		)); 
		self.wait(5)
		self.add(data_scatter) 

		lin_fit_func = poly_func(linear_fit_coef)
		lin_fit_curve = axes.plot(lin_fit_func,[1900-1912,2012-1912])

		#更适合的范围
		self.play(axes.y_axis.set_range, 8,10.6)
		lin_fit_curve.update()

		self.play(Create(lin_fit_curve), run_time=2.5)

		# Postcondition
		#   .axes
		self.data_scatter = data_scatter
		self.lin_fit_func = lin_fit_func
		self.lin_fit_curve = lin_fit_curve
	
	def illustrate_lin_fit(self):
		#*展示直线参数的意义

		# Precondition
		axes = self.axes
		lin_fit_func = self.lin_fit_func
		lin_fit_curve = self.lin_fit_curve
		
		self.narrate('''可以看到，这条直线很好地捕捉了短跑世界纪录的变化趋势。
						每过一段时间，世界纪录就会加快一点。这是显然的；''')
		
		#!----------------------------------------------------------------!#
		'''但关键是，不论是一百多年前的1920年，还是21世纪的今天，
			世界纪录都几乎在以同样的速度加快。这条直线无疑是最好的证明。'''
		斜率=abs(linear_fit_coef[1])
		target_point = axes.c2p(1925-1912, lin_fit_func(1925-1912))
		屏幕空间斜率=斜率/axes.x_axis.unit_size*axes.y_axis.unit_size \
			*1.04 # out of some subtle bugs in DataAxes which I should handle later I think
		tri=Polygon(ORIGIN, RIGHT*3, UP*3*屏幕空间斜率) \
			.align_to(target_point, UL)
		tex_config = {'color': FML_COLOR, 'font_size':48}
		tex_dx = Tex(r'\Delta x', **tex_config).next_to(tri,DOWN)
		tex_dy = Tex(r'\Delta y', **tex_config).next_to(tri,LEFT)
		tri_grp = VGroup(tri, tex_dx, tex_dy)
		self.play(Create(tri), Write(tex_dx), Write(tex_dy))
		self.add(tri_grp); self.wait(2)
		self.play(tri_grp.shift,RIGHT*4+DOWN*4*屏幕空间斜率, run_time=2)
		self.wait(2)
		self.play(FadeOut(tri_grp))
		
		
		#!----------------------------------------------------------------!#
		#* 最小二乘法求出了直线表达式
		lin_fit_expr = Tex('y=','10.5s','-','0.008', r'\cdot ', 'x', color=FML_COLOR).next_to(lin_fit_curve).shift(LEFT*2.5+UP*0.3)
		lin_fit_expr[1].set_color(LIGHT_BROWN)
		lin_fit_expr[3].set_color(LIGHT_BROWN)
		self.play(Write(lin_fit_expr)); self.wait(2)#self.wait(6)

		#!-------------------------------------------------------------------!#
		#* 强调'x'
		
		tex_x = lin_fit_expr[-1]
		tex_x.generate_target()
		org_m = tex_x.copy()
		tex_x.target.scale(1.8).set_color(YELLOW).align_to(lin_fit_expr[1],DOWN)

		self.play(MoveToTarget(tex_x), run_time=0.7)
		self.wait(0.6)
		self.play(Transform(tex_x, org_m), run_time=0.7)
		self.wait()


		self.add(lin_fit_expr) #reorganize

		#!----------------------------------------------------------------!#
		#* 纵截距的意义

		y_intercept_number = axes.y_axis._create_number(10.5, 10.5, LEFT, font_size=24)
		y_intercept_number.add_updater(lambda m: 
			m.next_to(
				axes.y_axis.number_to_point(10.5),
				direction=self.axes.y_axis.line_to_number_direction,
				buff=self.axes.y_axis.line_to_number_buff
			).set_opacity(
				1 if axes.y_axis.x_min<=10.5<=axes.y_axis.x_max else 0
			)
		)
		highlight=SurroundingRectangle(lin_fit_expr[1])
		self.play(Create(highlight));self.wait(0.5)
		y_intercept_number.set_color(YELLOW) #出场自带highlight
		self.play(Write(y_intercept_number));self.wait(0.5)
		self.play(Uncreate(highlight), y_intercept_number.set_color, WHITE)
		
		#!----------------------------------------------------------------!#
		#* 斜率的意义： 纵横刻度线展示直线斜率（13年-0.1秒）

		#由于DashedLine在update时太卡，因此开发时先用Line，渲染时再用DashedLine并调参
		if self.is_indev():
			indicating_lineclass = Line
			line_config = {'color':GREY_B}
		else:
			indicating_lineclass = DashedLine
			line_config = {'color':GREY_B, 'dash_length':0.16, 'positive_space_ratio':0.6}
		
		self.play(axes.x_axis.set_range, 0,50,
				axes.y_axis.set_range, 9.5,10.7)

		vline = VGroup(
			axes.line([20,0],[20,lin_fit_func(20)], 
				False, True, line_class = indicating_lineclass, **line_config),
			axes.line([33,0],[33,lin_fit_func(33)], 
				False, True, line_class = indicating_lineclass, **line_config)
		)
		hline = VGroup(
			axes.line([0,lin_fit_func(20)],[20,lin_fit_func(20)], 
				False, True, line_class = indicating_lineclass, **line_config),
			axes.line([0,lin_fit_func(33)],[33,lin_fit_func(33)], 
				False, True, line_class = indicating_lineclass, **line_config)
		)

		highlight=SurroundingRectangle(lin_fit_expr[3])
		self.play(Create(highlight)); self.wait(0.5)

		# playing with DashedLine seems to bring endless trouble for me
		# This suspending and resuming trick is for fixing the following Create animations.
		for m in [vline[0], vline[1], hline[0], hline[1]]: 
			m.suspend_updating() 
		vline[0].suspend_updating()
		self.play(Create(vline), Create(hline))
		
		#self.add(vline)
		#self.add(hline)
		for m in [vline[0], vline[1], hline[0], hline[1]]: 
			m.resume_updating() 

		_line_segment = axes.line([20,lin_fit_func(20)],[33,lin_fit_func(33)], 
				False, False, Line)
		
		brace = Brace(_line_segment, DOWN,color=GREY_B)
		text  = Text('13年', font=落霞孤鹜, font_size=36).next_to(brace, DOWN)
		date_delta_label = VGroup(brace, text)
		brace = Brace(_line_segment, LEFT, color=GREY_B)
		text  = Text('0.1s', font=落霞孤鹜, font_size=30).next_to(brace, LEFT)
		time_delta_label = VGroup(brace, text)

		self.play(FadeIn(date_delta_label, RIGHT*0.2))
		self.play(FadeIn(time_delta_label, DOWN*0.2))
		self.wait(0.5); self.play(Uncreate(highlight))
		
		self.wait(5)
		#!----------------------------------------------------------------!#
		#* 引入概念：线性拟合

		self.play(*[
			FadeOut(m) for m in 
			[vline, hline, time_delta_label, date_delta_label]
		],
			ApplyMethod(axes.x_axis.set_range, 0, 110, rate_func = lagged(0.5,1)),
			ApplyMethod(axes.y_axis.set_range, 8.5, 10.6, rate_func = lagged(0.5,1))
		)
		axes.plots.remove(vline[0],vline[1],hline[0],hline[1])

		#self.narrate('这，就是线性拟合')
		self.narrate("""线性拟合是一种极为简单的工具，然而它却往往能抓住数据中的规律。""")

		#!----------------------------------------------------------------!#
		#* “”“当数据的选择恰当时，它更能向我们展示数据中令人意想不到的一面。"""
		#* 一段强调动画。xy_label & 线性拟合直线
		mobj_to_emph = [axes.x_axis.label, axes.y_axis.label, lin_fit_curve]
		for mobj in mobj_to_emph:
			mobj.suspend_updating()
			mobj.generate_target()
		
		axes.x_axis.label.target.scale(1.8).set_color(YELLOW_D)
		axes.y_axis.label.target.scale(1.8).set_color(YELLOW_D).shift(0.2*RIGHT)
		lin_fit_curve.target.scale(1.1).set_stroke(width=15).set_color(ORANGE)
		backstroke_xlabel = axes.x_axis.label.copy().clear_updaters()
		backstroke_xlabel.generate_target()
		backstroke_xlabel.target.scale(1.8).set_stroke(color=BLACK, width=14)
		backstroke_ylabel = axes.y_axis.label.copy().clear_updaters()
		backstroke_ylabel.generate_target()
		backstroke_ylabel.target.scale(1.8).set_stroke(color=BLACK, width=14).shift(0.2*RIGHT)
		backstroke_curve = lin_fit_curve.copy().clear_updaters()
		backstroke_curve.generate_target()
		backstroke_curve.target.scale(1.1).set_stroke(color=BLACK, width=40)
		self.add(backstroke_xlabel, backstroke_ylabel, backstroke_curve)
		self.bring_to_back(backstroke_xlabel, backstroke_ylabel, backstroke_curve)
		
		self.stop_skipping()
		
		emph_func=emphasize(0.5,2,smooth)
		play_kw = {'run_time':2, 'rate_func':emph_func}
		delayed_play_kw = {'run_time': 2, 'rate_func':emph_func,'time_span':[0.5,2]}
		self.play(
				MoveToTarget(backstroke_xlabel, **play_kw), MoveToTarget(axes.x_axis.label, **play_kw),
				MoveToTarget(backstroke_ylabel, **delayed_play_kw), MoveToTarget(axes.y_axis.label, **delayed_play_kw),
		)
		self.wait()
		self.play(MoveToTarget(backstroke_curve), MoveToTarget(lin_fit_curve), **play_kw)
		self.remove(backstroke_xlabel, backstroke_ylabel, backstroke_curve)
		self.add(axes)
		self.wait()

		for mobj in mobj_to_emph:
			mobj.resume_updating()

		self.wait(5)
		
		# Postcondition
		# .axes,
		self.lin_fit_expr = lin_fit_expr
		# x_range = [0, 110]
		# y_range = [8.5, 10.6]

	def extrapolate_and_error(self):
		#* 外推拟合直线，预测未来趋势，并在过分外推的时候得到显然的谬误

		# Precondition
		axes = self.axes
		lin_fit_func = self.lin_fit_func
		lin_fit_curve = self.lin_fit_curve
		axes.x_axis.set_range(0, 110)
		axes.y_axis.set_range(8.5, 10.6)

		#!-----------------------------------------------------!#
		#* preparation and constants

		lihua = LittleCreature(mood = 'smile', flipped=True) \
			.next_to(axes,RIGHT).align_to(axes.x_axis.line,DOWN).shift(UP*0.4)

		# 2039: 9.5s, Bolt-WR-breaking
		# 2105: 9s, everyone's Bolt?
		# 2632: 5s, 
		# 3290: c
		

		year_to_extrapolate_to = [2035, 2098, 2604, 3237.3]
		year_to_extrapolate_to = [year-1912 for year in year_to_extrapolate_to]
		time_to_extrapolate_to = [lin_fit_func(x) for x in year_to_extrapolate_to]
		
		X_RANGE_LEN = axes.x_axis.x_max-axes.x_axis.x_min #110 typically
		Y_RANGE_LEN = axes.y_axis.x_max-axes.y_axis.x_min #2.1 typically, I think?

		extra_part = axes.line([2012-1912, lin_fit_func(2012-1912)], [2022-1912,lin_fit_func(2022-1912)], False, False, stroke_width=5)
		self.play(Create(extra_part))
		target_point = axes.c2p(2015-1912, lin_fit_func(2015-1912))
		
		indicating_arrow = Arrow(target_point+DOWN*2.5+LEFT*0.8, target_point, tip_width_ratio=4, width_to_tip_len=0.05, stroke_width=10, buff=0.4)
		self.play(Popup(indicating_arrow))
		self.wait(3)
		self.play(FadeOut(indicating_arrow))
		
		self.remove(extra_part); axes.plots.remove(extra_part)
		self.remove(lin_fit_curve); axes.plots.remove(lin_fit_curve)
		extended_lin_fit_curve = axes.line([0, 10.47], [3237.3-1912,0], True, True)
		self.add(axes); lin_fit_curve=extended_lin_fit_curve

		indicating_lineclass = DashedLine
		line_config = {'color':GREY_B, 'dash_length':0.16, 'positive_space_ratio':0.6}
		
		#!-----------------------------------------------------!#
		#* 线性外推
		self.play(FadeIn(lihua))
		self.wait()

		#!-----------------------------------------------------!#
		#* 外推至9.5s
		x0, y0=year_to_extrapolate_to[0], time_to_extrapolate_to[0]
		self.play(
			ApplyMethod(axes.x_axis.set_range, x0-X_RANGE_LEN/2,   x0+X_RANGE_LEN/2,   rate_func=linear_ease_io(0.3)),
			ApplyMethod(axes.y_axis.set_range, y0-Y_RANGE_LEN*0.8, y0+Y_RANGE_LEN*0.2, rate_func=linear_ease_io(0.3)),
		)
		
		self.wait()

		vline = axes.line([x0, 0],[x0,lin_fit_func(x0)],              False,False,indicating_lineclass,**line_config)
		hline = axes.line([0, lin_fit_func(x0)],[x0,lin_fit_func(x0)],False,False,indicating_lineclass,**line_config)
		ylabel= axes.y_axis._create_number(9.5, 9.5, LEFT, font_size=24)

		self.play(Create(vline),run_time=0.6)
		self.play(Create(hline,run_time=0.6),Create(ylabel), ApplyMethod(lihua.change_mood, 'happy'))
		self.wait(3)

		self.play(FadeOut(vline),FadeOut(hline),FadeOut(ylabel),ApplyMethod(lihua.change_mood, 'smile'))

		#!-----------------------------------------------------!#
		#* 外推至9s

		x0, y0=year_to_extrapolate_to[1], time_to_extrapolate_to[1]
		shift_range_kwargs = {'rate_func':linear_ease_io(0.2), 'run_time': 2}
		self.play(
			ApplyMethod(axes.x_axis.set_range, x0-X_RANGE_LEN/2,   x0+X_RANGE_LEN/2,   **shift_range_kwargs),
			ApplyMethod(axes.y_axis.set_range, y0-Y_RANGE_LEN*0.7, y0+Y_RANGE_LEN*0.3, **shift_range_kwargs),
			
		)
		self.wait()

		vline = axes.line([x0, 0],[x0,lin_fit_func(x0)],              False,False,indicating_lineclass,**line_config)
		hline = axes.line([0, lin_fit_func(x0)],[x0,lin_fit_func(x0)],False,False,indicating_lineclass,**line_config)
		#ylabel= axes.y_axis._create_number(9, 9, LEFT, font_size=24)

		self.play(Create(vline,run_time=0.6))
		self.play(Create(hline,run_time=0.6), 
				  ApplyMethod(lihua.change_mood, 'surprised',run_time=1))
		self.wait(5)

		self.play(FadeOut(vline),FadeOut(hline), ApplyMethod(lihua.change_mood, 'plain'))
		self.wait(3)
		
		#!-----------------------------------------------------!#
		#* 外推至5s

		x0, y0=year_to_extrapolate_to[2], time_to_extrapolate_to[2]
		self.play(axes.x_axis.set_range, x0-X_RANGE_LEN/2, x0+X_RANGE_LEN/2, 
				  axes.y_axis.set_range, y0-Y_RANGE_LEN/2, y0+Y_RANGE_LEN/2, 
				  rate_func=linear_ease_io(0.2),run_time=2)
		self.wait()

		vline = axes.line([x0, 0],[x0,lin_fit_func(x0)],              False,False,indicating_lineclass,**line_config)
		hline = axes.line([0, lin_fit_func(x0)],[x0,lin_fit_func(x0)],False,False,indicating_lineclass,**line_config)
		#ylabel= axes.y_axis._create_number(9, 9, LEFT, font_size=24)

		self.play(Create(vline),run_time=0.6)
		self.play(Create(hline),run_time=0.6)
		self.wait(1)

		#!-----------------------------------------------------!#
		#* 小白“爆衣”——这个动画需要一点技巧

		overshoot_rf = lagged(0.5,0.2,braking_end )

		lihua_strong = LittleCreature('muscle', flipped=True) \
			.look(DOWN) \
			.move_to(lihua).scale(1.4).align_to(lihua,UP).shift(0.2*UP)
		muscle_stokes = lihua_strong[len(lihua):]
		lihua_copy = lihua.copy()

		# 由于带肌肉的小白与普通的小白结构是异质的(heteregeneous)
		# 因此，为了让小白能变回来，要保存小白原来的样子，让小白的copy变成
		# 肌肉猛男，然后再由copy变回原来的样子
		# time >>===================>>
		# lihua              lihua
		#   |                  ^
		#   v      (anime)     |
		# lihua_copy ---> lihua_muscle

		self.remove(lihua);self.add(lihua_copy)
		self.play(
			Transform(lihua_copy[:len(lihua)],lihua_strong[:len(lihua)],rate_func=linear_ease_io(0.2)),
			FadeIn(muscle_stokes, shift=DL*0.05, rate_func=overshoot_rf, clip_alpha=False),
			run_time=0.6 # 时间短于1s，让动画看起来更有力量感一些
		)
		#self.add(lihua_strong)

		self.wait(3)

		# 事实发现，不变回去视觉效果更好
		# 那就省点事吧hhh
		'''
		self.play(
			ReplacementTransform(lihua_copy[:len(lihua)],lihua[:len(lihua)],rate_func=linear_ease_io(0.2)),
			FadeOut(muscle_stokes, shift=UL*0.05),
			run_time=1
		)
		self.add(lihua)
		'''

		self.play(
			FadeOut(vline),FadeOut(hline),
			FadeOut(lihua_copy[:len(lihua)]), FadeOut(lihua_strong[len(lihua):])
		)
		
		
		#!-----------------------------------------------------!#
		#* 外推至0s

		blast_highlight = BlastHightlight(self, RIGHT*3)
		blast_highlight.set_pos(axes.c2p(year_to_extrapolate_to[-1],0))
		blast_highlight.set_strength(0)
		blast_highlight.add_updater(lambda m: m.set_pos(axes.c2p(year_to_extrapolate_to[-1],0)))

		self.stop_skipping()
		x0, y0=year_to_extrapolate_to[3], time_to_extrapolate_to[3]
		self.play(
			ApplyMethod(axes.x_axis.set_range, x0-X_RANGE_LEN*0.65, x0+X_RANGE_LEN*0.35, rate_func=linear_ease_io(0.3)),
			ApplyMethod(axes.y_axis.set_range, 0, Y_RANGE_LEN, rate_func=linear_ease_io(0.3)),
			
			run_time=3
		)
		self.wait(1)
		self.play(ApplyMethod(blast_highlight.set_strength, 1, run_time=2, rate_func=linear))
		self.play(blast_highlight.set_strength, 6, run_time=3)

		# Postcondition
		# * * END_SCENE * * #
		
class LightWeightLittleCreature(SVGMobject):
	def get_shader_wrapper_list(self):
		# SVGMobject默认会返回两个shader_wrapper, one for fill and one for stroke
		# 导致所有子路径的fill和stroke分别被一块渲染了，上下层的stroke会相交，无法正确显示重叠关系
		# 因此这里重写这一方法，返回所有sub/son的shader_wrapper，这样每个路径就会分开渲染。
		ret=[]
		for sub in self:
			ret+=sub.get_shader_wrapper_list()
		return ret
		
class LittleCreatureArgue(StarskyScene):
	def construct(self):
		self.create_debate()
		self.show_in_bubble_thought()

	def create_debate(self):
		#* precondition: None

		#! argue subjectives
		someone = LittleCreature('plain').to_corner(DL, buff=0.7).shift(RIGHT*0.3)
		someone.set_color('#E0D0D0')
		lihua = LittleCreature(flipped=True).to_corner(DR, buff=0.7).shift(LEFT*0.6)
		
		#! thought bubble
		thought_bubble = SVGMobject('assets/Bubbles_thought.svg',stroke_color=WHITE) \
			.scale(3).stretch_to_fit_width(10).shift(UP)#manually tuned params
		rect = SurroundingRectangle(thought_bubble[-1]).scale(0.7) # rect. indicating the space inside bubble
		#self.add(rect)

		#! animate
		self.play(Write(someone), Write(lihua, time_span=[0.3,1.3]))
		self.play(someone.change_mood, 'handup', FadeIn(thought_bubble, time_span=[0.5,1.5]))
		
		#* postcondition
		self.someone, self.lihua = someone, lihua
		self.thought_bubble = thought_bubble
		self.inbubble_rect = rect

	def show_in_bubble_thought(self):
		#* precondition
		someone, lihua = self.someone, self.lihua
		thought_bubble = self.thought_bubble
		inbubble_rect = self.inbubble_rect

		#! axes
		rect = inbubble_rect
		miniaxes = DataAxes(
			[0,6],[0,3],
			width=rect.get_width()-1, height=rect.get_height()-0.3, 
			include_numbers=False
		); axes = miniaxes
		axes.move_to(rect).shift(UR*0.1)
		
		lin_fit_func = lambda x: 2.5-0.2*x

		#! plot original data dots
		dots_coords_x = [0.5, 1.4, 2.3, 3]
		y_noise       = [-0.15, -0.07, 0.2, 0.02]
		dots_coords_y = [
			lin_fit_func(dots_coords_x[i])+y_noise[i] 
			for i in range(len(dots_coords_x))
		]
		dots = axes.scatter(dots_coords_x, dots_coords_y, attach=False)

		#! linear fit line
		line = axes.plot(lin_fit_func,[0,3], attach=False)
		dashedline_config = {'dash_length':0.16, 'positive_space_ratio':0.6}
		ext_line = axes.line([3,lin_fit_func(3)], [6, lin_fit_func(6)], False, False, DashedLine, **dashedline_config)
		dashedline_config = {'color': GREY_B, 'stroke_opacity': 0.3, 'dash_length':0.1, 'positive_space_ratio':0.6}
		vline = axes.line([3,0],[3,lin_fit_func(3)], False, False, DashedLine, **dashedline_config)
		lin_fit_line, ext_fit_line, delim = line, ext_line, vline

		#! angel and demon
		def scale_stroke(m: VMobject, r):
			for sm in m.submobjects:
				sm.set_stroke(width=sm.get_stroke_width()*r)

		sf = 0.7
		demon = LightWeightLittleCreature('assets/LittleCreature_demon.svg').scale(sf).flip()
		scale_stroke(demon, sf)
		demon.move_to(axes.c2p(4.5,0.8))
		# demon手上一小块颜色遮罩 
		# seems svg path with stroke_width=0 needs to be hand tuned in manim
		demon[-1].set_stroke(width=0)
		
		sf = 0.8
		angel = LightWeightLittleCreature('assets/LittleCreature_angel.svg').scale(sf).flip()
		scale_stroke(angel, sf)
		angel.move_to(axes.c2p(1.5,1))
		
		#! animate
		
		self.play(
			Create(axes),
			AnimationGroup(*[Popup(d) for d in dots],
						lag_ratio=0.2, time_span=[0.7,1.9], rate_func=linear)
		);

		self.play(Create(lin_fit_line), Blink(lihua, time_span=[0.2,0.4]))
		self.play(Write(angel));self.wait()

		self.play(FadeIn(delim),Create(ext_fit_line))
		self.play(Write(demon));self.wait()

		self.play(lihua.change_mood, 'puzzling',
				someone.change_mood, 'plain'); self.wait(0.4)
		self.play(Blink(lihua)); self.wait(0.3)
		self.play(Blink(lihua)); self.wait(0.4)

		self.wait(2)

		#* postcondition
		#* END SCENE *#

class Reflection(StarskyScene):
	def is_indev(self):
		return self.preview
	def is_rendering(self):
		return not self.preview
	
	def setup(self):
		axes = SprintWRDataFrame(include_numbers = False).align_on_border(LEFT,1.4)
		axes.y_axis.set_range(8,10.6)
		self.axes = axes

	def construct(self):
		self.create_elements()
		self.say_another_extreme()

		curtain = SurroundingRectangle(self.camera.frame).set_style(stroke_opacity=0,fill_opacity=1,fill_color='#222222')
		self.play(FadeIn(curtain)) #fade out all
		self.clear()
		self.setup(); self.create_elements()

		self.reflect()
		#* plugin: 各种带有弧度的函数 ShowFunctionsWithCurvature
		self.show_quadratic_fit()

	def create_elements(self):
		'''创建基本的坐标轴、坐标轴元素、数据点合拟合曲线，供随后动画使用
		See also: IntroductionAndExtrapolation.create_axes()'''

		# Precondition
		axes = self.axes

		#!-------------------------------------------------------------------!#
		#* 坐标轴生成动画

		self.play(Create(axes),run_time=1.3)

		axes.add_numbers()
		axes.add_axis_labels('年份','时间/s',Text, font=落霞孤鹜, font_size=30)
		self.play(AnimationGroup(
			*[
				FadeIn(m) for m 
				in list(axes.x_axis.numbers)+[axes.x_axis.label]
			],
			lag_ratio=0.2,run_time=2
		),AnimationGroup(
			*[
				FadeIn(m) for m 
				in list(axes.y_axis.numbers)+[axes.y_axis.label]
			],		
			lag_ratio=0.2,run_time=1
		))
		self.add(axes)

		#!-------------------------------------------------------------------!#
		#* 数据和拟合曲线生成动画

		animations=[]
		# create, animate and reorganize
		data_scatter = axes.plot_data()
		lin_fit_func = poly_func(linear_fit_coef)
		lin_fit_curve = axes.plot(lin_fit_func,[1900-1912,2012-1912])
		
		animations.append(AnimationGroup(
			*[
				Popup(m) for m 
				in data_scatter
			],
			lag_ratio=0.2, run_time=1.2, rate_func=linear
		))
		animations.append(Create(lin_fit_curve, rate_func=lagged(0.6,1),run_time=1.6))

		self.play(*animations)
		self.add(axes) # reorganize, if structure is messed by play func.

		# Postcondition
		#   .axes
		self.data_scatter = data_scatter
		self.lin_fit_func = lin_fit_func
		self.lin_fit_curve = lin_fit_curve

	def say_another_extreme(self):
		#* 对应文案种“但这样又走向了另一个极端”一句。
		#* ——“短跑运动员超过光速”那一句由pr剪辑。
		#* ——“有人提出”哪一段由LittleCreatureArgue负责

		# Precondition
		axes = self.axes
		data_dots = self.data_scatter
		lin_fit_func = self.lin_fit_func
		lin_fit_curve = self.lin_fit_curve

		#!-------------------------------------------------------------------!#
		#* 画定界竖线
		dashedline_config = {'dash_length':0.16, 'positive_space_ratio':0.6, 'color':GREY_B}
		x=100; y=lin_fit_func(x)
		vline = axes.line([x,0],[x,y],False,False, DashedLine, **dashedline_config)
		
		self.play(Create(vline))
		self.wait(2)

		#!-------------------------------------------------------------------!#
		#* "对如此明显的直线，不把它向外延伸简直是一种罪过"
		#* 线性拟合直线奋力出头的样子
		#* 这个动画比我想象的更难做 :-(
		def origin_func(alpha):
			if alpha<0.04: return 1
			elif alpha<0.3: return 0.8
			elif alpha<0.4: return 1.06
			elif alpha<0.55: return 0.95
			elif alpha<0.6: return 0.9
			elif alpha<0.75: return 1.06
			elif alpha<0.85: return 1
			else: return 1
		rf = gen_smoothed_func(origin_func, 3,0.6,2, 3)

		lin_fit_curve.suspend_updating()
		y_intercept = axes.c2p(0,lin_fit_func(0))
		lin_fit_curve.generate_target()
		lin_fit_curve.scale(0.01, about_point=y_intercept)
		self.play(MoveToTarget(lin_fit_curve, clip_alpha=False), run_time=3, rate_func=rf)
		self.wait(2)
		lin_fit_curve.resume_updating()

		#!-------------------------------------------------------------------!#
		#* 下个动画的小小前摇
		lin_fit_curve.clear_updaters()
		tmp = axes.plot(lin_fit_func, [0,200], False, False)
		
		self.play(Transform(lin_fit_curve, tmp))
		# some reorganization
		ext_lin_fit_curve = axes.line([date[0],lin_fit_func(0)],[3237.3,lin_fit_func(3237.3)])
		self.remove(lin_fit_curve); axes.plots.remove(lin_fit_curve)
		lin_fit_curve=ext_lin_fit_curve; self.add(axes)

		x0, y0=3237.3-1912, 0
		X_RANGE_LEN = axes.x_axis.x_max-axes.x_axis.x_min #110 typically
		Y_RANGE_LEN = axes.y_axis.x_max-axes.y_axis.x_min #2.1 typically, I think?

		#!-------------------------------------------------------------------!#
		#* 外推并最终得出荒谬结论
		self.play(ApplyMethodToDataAxes(axes.set_all_ranges,
			[x0-X_RANGE_LEN*0.65, x0+X_RANGE_LEN*0.35],
			[0, Y_RANGE_LEN],
			rate_func=linear_ease_io(0.3),run_time=2
		),FadeOut(vline,run_time=0.5)); self.wait()
		
		from manimhub.custom_mobjects import Cross #weird import issue
		cross = Cross().move_to(axes.c2p(3237.3-1912,0.2))
		cross.set_opacity(0.8)
		self.play(Popup(cross))

		# Postcondition
		# axes, lin_fit_func, data_scatter
		self.lin_fit_curve = lin_fit_curve

	def create_elements_haste(self):
		# Precondition
		axes = self.axes
		lin_fit_curve = self.lin_fit_curve
		data_scatter = self.data_scatter

		
		animations = []
		animations.append(Create(axes))
		animations.append(AnimationGroup(
			*[
				FadeIn(m) for m 
				in list(axes.x_axis.numbers)+[axes.x_axis.label]
			],
			lag_ratio=0.2,run_time=2
		))
		animations.append(AnimationGroup(
			*[
				FadeIn(m) for m 
				in list(axes.y_axis.numbers)+[axes.y_axis.label]
			],		
			lag_ratio=0.2,run_time=1
		))
		animations.append(AnimationGroup(
			*[
				Popup(m) for m 
				in data_scatter
			],
			lag_ratio=0.2, run_time=1.2, rate_func=linear
		))
		animations.append(Create(lin_fit_curve, rate_func=lagged(0.6,1),run_time=1.6))
		self.play(*animations)
		
	def reflect(self):
		# Precondition
		axes = self.axes
		lin_fit_curve = self.lin_fit_curve
		lin_fit_func = self.lin_fit_func

		#!-------------------------------------------------------------------!#
		#* 拟合直线摆动到其他歪瓜裂枣的位置，体现真正的拟合曲线很好地代表了数据点的位置
		
		tmp=lin_fit_curve.get_updaters()
		lin_fit_curve.clear_updaters()
		#lin_fit_curve.suspend_updating()
		y_intercept = axes.c2p(0,lin_fit_func(0))
		self.play(lin_fit_curve.shift,DOWN, run_time=0.6)
		self.wait(0.6)
		self.play(lin_fit_curve.shift,UP, run_time=0.5)
		self.wait(0.6)
		self.play(lin_fit_curve.rotate,-8*DEGREES,OUT,y_intercept, run_time=0.5)
		self.wait(0.3)
		self.play(lin_fit_curve.rotate,16*DEGREES,OUT,y_intercept, run_time=0.5)
		self.wait(0.4)
		self.play(lin_fit_curve.rotate,-8*DEGREES,OUT,y_intercept, run_time=0.5)
		self.wait(2)

		#!-------------------------------------------------------------------!#
		#* 强调线性拟合曲线——它证明了自己
		
		lin_fit_curve.generate_target()
		lin_fit_curve.target.scale(1.1).set_stroke(width=20,color=ORANGE)
		self.play(MoveToTarget(lin_fit_curve),rate_func=emphasize(0.5,0.6),run_time=2)
		self.wait(2)

		#上算法课去了 #从算法课回来了

		#!-------------------------------------------------------------------!#
		#* 其它曲线形式摆动——其它可能的外推曲线的形式
		
		
		ext_curve = ParametricCurve(lambda x: axes.c2p(x+100,(x/50)**2-0.005*x+lin_fit_func(x+100)), [0,30,0.5])
		self.play(Create(ext_curve)); self.wait()

		_ = ParametricCurve(lambda x: axes.c2p(x+100,-(x/50)**2-0.005*x+lin_fit_func(x+100)), [0,30,0.5])
		self.play(ext_curve.become,_); self.wait()
		_ = ParametricCurve(lambda x: axes.c2p(x+100,0.3*(np.cos(x/3)-1)*np.exp(-x/40)+lin_fit_func(x+100)), [0,40,0.5])
		self.play(ext_curve.become,_); self.wait()
		self.play(FadeOut(ext_curve)); self.wait()

		for updater in tmp:
			lin_fit_curve.add_updater(updater)

		#!-------------------------------------------------------------------!#
		#* 放大尺度，曲线可能是趋于平缓的
		
		self.play(ShiftRange(axes, 'x', [0,200], rate_func=lagged(0.5,1), run_time=1.5))
		quad_fit_func=poly_func(quadratic_fit_coef)
		ext_curve = axes.plot(quad_fit_func, [0,200], False, False)
		
		lin_fit_curve.clear_updaters()
		self.play(Transform(lin_fit_curve, ext_curve)); self.wait(2)

		#!-------------------------------------------------------------------!#
		#* 加上箭头表现趋势

		def show_trend():
			trend_indicator1 = Arrow(axes.c2p(25,quad_fit_func(25)), axes.c2p(75,quad_fit_func(75)), 
				tip_width_ratio=3.5, width_to_tip_len=0.07)
			trend_indicator1.shift(DOWN*0.6).set_stroke(width=10)
			trend_indicator1.generate_target(); 
			angle = trend_indicator1.get_angle(); start = trend_indicator1.get_start(); 
			trend_indicator1.rotate(-angle, OUT, start).stretch_about_point(0.001,0, start).rotate(+angle, OUT, start)
			self.play(MoveToTarget(trend_indicator1))
			self.play(FadeOut(trend_indicator1)); self.wait()

			trend_indicator2 = Arrow(axes.c2p(115,quad_fit_func(125)), axes.c2p(175,quad_fit_func(175)), 
				tip_width_ratio=3.5, width_to_tip_len=0.07)
			trend_indicator2.shift(DOWN*0.6).set_stroke(width=10)
			trend_indicator2.generate_target(); 
			angle = trend_indicator2.get_angle(); start = trend_indicator2.get_start(); 
			trend_indicator2.rotate(-angle, OUT, start).stretch_about_point(0.001,0, start).rotate(+angle, OUT, start)
			self.play(MoveToTarget(trend_indicator2))
			self.play(FadeOut(trend_indicator2)); self.wait()

		show_trend()
		self.wait(3)
		show_trend()

		self.wait()
		self.remove(lin_fit_curve); axes.plots.remove(lin_fit_curve)
		self.wait()

		# Postcondition
		# axes
		# * * ALL CURVES REMOVED * * #

	def show_quadratic_fit(self):
		# Precondition
		axes = self.axes
		axes.set_range('x', [0,120])
		axes.set_range('y', [8,11])
		data_scatter = self.data_scatter

		#* object construction
		quad_fit_func=poly_func(quadratic_fit_coef)
		quad_fit_curve = axes.plot(quad_fit_func, [0,204], True, True)
		#lin_fit_func=poly_func(linear_fit_coef)
		#lin_fit_curve = axes.plot(lin_fit_func, [0,200], True, True).set_color(ORANGE)

		# legend
		quad_fit_expr = Tex('y=','a_0','+','a_1','x','+','a_2','x^2', color=FML_COLOR)
		for idx in [1, 3, 6]: quad_fit_expr[idx].set_color(LIGHT_BROWN)
		quad_fit_expr.to_corner(UR, buff=1).shift(LEFT*0.6)

		quad_coef_expr = VGroup(
			Tex('a_2','=',r'5.07\times 10^{-5}', font_size=38),
			Tex('a_1','=',r'-0.013', font_size=38), 
			Tex('a_0','=',r'10.54', font_size=38),
		)
		#arranging and styling
		for i in range(1, len(quad_coef_expr)):
			quad_coef_expr[i].next_to(quad_coef_expr[i-1], DOWN, buff=0.15)
			quad_coef_expr[i].align_to(quad_coef_expr[i-1], LEFT)
		quad_coef_expr.next_to(quad_fit_expr, DOWN)#.shift(RIGHT*0.5)
		for tex in quad_coef_expr:
			tex.set_color(FML_COLOR); 
			tex[0].set_color(LIGHT_BROWN)
			tex[2].set_color(GREY_B)
			tex[2].scale(0.8).shift(LEFT*0.1)
	
		#self.add(quad_fit_expr, quad_coef_expr)

		#!-------------------------------------------------------------------!#
		#* show off curve and func. expr.
		
		self.play(Write(quad_fit_expr))
		self.play(Create(quad_fit_curve)); self.add(axes)
		self.play(AnimationGroup(*[Write(tex) for tex in quad_coef_expr], lag_ratio=0.3))
		self.wait(2)

		#!-------------------------------------------------------------------!#
		#* 下降趋势

		# "由于二次项系数大于零，向上弯折"
		
		hint = Tex('>0', font_size=38, color=FML_COLOR).next_to(quad_coef_expr[0],RIGHT)
		highlight = SurroundingRectangle(VGroup(quad_coef_expr[0], hint))
		self.play(Write(hint), Create(highlight)); self.wait(2)
		self.play(Uncreate(highlight))

		self.play(ShiftRange(axes, 'x', [0,240]))
		hint_line = axes.line([0,quad_fit_func(0)], [180,quad_fit_func(180)-0.9], False, False, color=GREY_B)
		arrow = Arrow(axes.c2p(160,8.8), axes.c2p(175,9.4), stroke_width=15, buff=0.1, color=GREY_B)
		self.play(Create(hint_line))
		arrow.generate_target(); 
		angle = arrow.get_angle(); start = arrow.get_start(); 
		arrow.rotate(-angle, OUT, start).stretch_about_point(0.0001,0, start).rotate(+angle, OUT, start)
		self.play(MoveToTarget(arrow))

		self.wait(0.5)
		self.play(FadeOut(arrow), FadeOut(hint_line, time_span=[0.5,1.5]))

		#!-------------------------------------------------------------------!#
		#* 如果再次尝试外推，会发现？

		quad_fit_curve_restricted = axes.plot(quad_fit_func, [0,100], True, True)
		self.play(FadeOut(quad_fit_curve, run_time=0.5))
		
		self.wait(2) #如果我们把它再次外推

		line_config = {'color':'#555555', 'dash_length':0.16, 'positive_space_ratio':0.45}
		ext_delim = axes.line([100,0],[100,11], False, False, DashedLine, **line_config)
		self.play(FadeIn(ext_delim, run_time=0.4), Create(quad_fit_curve, run_time=4)); axes.plots.remove(quad_fit_curve_restricted)

		#tmp = axes.x_axis.unit_size*(100)*1/6 #ext_delim.shift, LEFT*tmp
		#self.play(ShiftRange(axes, 'x', [0,240]), )

		#!-------------------------------------------------------------------!#
		#* 曲线的最小点——外推极值

		line_config = {'color': GREY_A, 'dash_length':0.16, 'positive_space_ratio':0.55}
		X,Y=2116-1912, 9.42
		vline = axes.line([X,0],[X,Y], False, False, DashedLine, **line_config)
		hline = axes.line([0,Y],[X,Y], False, False, DashedLine, **line_config)
		ylabel= axes.y_axis._create_number(9.42, 9.42, LEFT, font_size=24)
		lim_dot = Dot(axes.c2p(X,Y),color=ORANGE)
		lim_dot_label = Text('(2116 B.C., 9.42s)', color=FML_COLOR, font_size=36, buff=0.2).next_to(lim_dot,RIGHT)

		#self.add(vline, hline, lim_dot, lim_dot_label)
		self.play(Create(vline))
		self.play(Create(hline), FadeIn(ylabel))
		self.play(FadeIn(lim_dot))
		self.play(FadeIn(lim_dot_label))
		self.wait(2)

		#!-------------------------------------------------------------------!#
		#* illustrate Bolt's (last three) WR
		self.stop_skipping()
		Bolt_WR = data_scatter[-3:]
		org_mobj = Bolt_WR.copy()
		Bolt_WR.generate_target()
		Bolt_WR.target.scale(1.5).set_style(stroke_color=DARK_BROWN, stroke_width=4, fill_color=ORANGE)
		self.play(MoveToTarget(Bolt_WR), reorganize_mobjects=False); 
		self.wait(3)
		self.play(Bolt_WR.set_opacity, 0, reorganize_mobjects=False); 
		self.wait(5)
		self.play(Transform(Bolt_WR, org_mobj), reorganize_mobjects=False); 
		self.wait(3)
		

		#!-------------------------------------------------------------------!#
		#* 二次近似也有问题：极值点之后会往上走

		lim_grp = VGroup(vline, hline, lim_dot, lim_dot_label)
		#
		quad_curve_ext = ParametricCurve(lambda x: axes.c2p(x, quad_fit_func(x)), [204,340])
		self.play(
			ApplyMethod(lim_grp.set_opacity, 0.1, rate_func=linear, run_time=0.5), 
			Create(quad_curve_ext, run_time=1.4, rate_func=lagged(0.4,1))
		)
		arrow = Arrow(RIGHT*6+DOWN*1.5, RIGHT*6, stroke_width=15, buff=0.1, color='#777777')
		arrow.generate_target(); 
		angle = arrow.get_angle(); start = arrow.get_start(); 
		arrow.rotate(-angle, OUT, start).stretch_about_point(0.0001,0, start).rotate(+angle, OUT, start)
		self.play(MoveToTarget(arrow))

		self.wait(2)

		self.play(
			FadeOut(quad_curve_ext), FadeOut(arrow),
			lim_grp.set_opacity,1
		)

		self.wait(2)
		
# 专门为下面的scene用的
class CustomNumberLabel(DecimalNumber):
	CONFIG = {'dynamic': True}
	def __init__(self, 
		val, 小数位数, 
		axes, axis: str,
		appear_scale, **kwargs):

		super().__init__(val, num_decimal_places=小数位数, font_size=26)
		if val!=1 and val!=0.1: self.set_color(GREY_B)

		dir  = DOWN if axis=='x' else LEFT
		axis = axes.x_axis if axis=='x' else axes.y_axis
		
		self.next_to(axis.n2p(val), dir, buff=0.2)
		
		if not self.dynamic: return
		def updater(m):
			if not axis.x_min<val<axis.x_max: m.set_opacity(0); return m
			scale=axis.x_max-axis.x_min
			if not appear_scale[0]<scale<appear_scale[1]: m.set_opacity(0); return m
			m.set_opacity(1)
			m.next_to(axis.n2p(val), dir, buff=0.2); return m
		self.add_updater(updater)

class ShowFunctionsWithCurvature(StarskyScene):
	def construct(self):
		self.show_all_functions()
		self.move_to_single_func()
		self.show_merits_of_quadratic_func()

	def show_all_functions(self):
		# Precondition
		# * * NONE * * #

		#!-------------------------------------------------------------------!#
		#* 构造坐标系元素

		#* 构造四个迷你坐标系；添加静态网格
		a1 = self.create_mini_axes(); self.add_grid_line(a1, 1,1); self.add_grid_line(a1, 2, 0.5)
		a2 = self.create_mini_axes(); self.add_grid_line(a2, 1,1); self.add_grid_line(a2, 2, 0.5)
		a3 = self.create_mini_axes(); self.add_grid_line(a3, 1,1); self.add_grid_line(a3, 2, 0.5)
		a4 = self.create_mini_axes(); self.add_grid_line(a4, 1,1); self.add_grid_line(a4, 2, 0.5)

		#* 画函数曲线
		plot_config = {'color': ORANGE, 'stroke_width':6}
		a1.plot(lambda x: np.exp(-1*x**2), [0,2], **plot_config)
		a2.plot(lambda x:    1/(x**2+1),   [0,2], **plot_config)
		a3.plot(lambda x: np.sin(x*PI/2),  [0,1], **plot_config)
		a4.plot(lambda x:      x**2,       [0,1], **plot_config)

		#* 函数曲线标签
		legend_config = {'color': ORANGE, 'font_size': 70}
		t1=Tex(r'e^{-x^2}',       **legend_config)
		t2=Tex(r'1\over x^2+a^2', **legend_config).scale(0.65) #微调使得不同标签大小平衡
		t3=Tex(r'\sin x',         **legend_config).scale(0.8 )
		t4=Tex(r'x^2',            **legend_config).scale(0.86)

		#* 按2x2表格排列
		VGroup(t1, a1, a2, t2, t3, a3, a4, t4). arrange_in_grid(2,4, v_buff=0.5, h_buff=1)
		t1.next_to(a1, LEFT).shift(UP*0.2); t2.next_to(a2, RIGHT)
		t3.next_to(a3, LEFT).shift(UP*0.1); t4.next_to(a4, RIGHT).shift(UP*0.14)
		self.add(a1, a2, a3, a4, t1, t2, t3, t4)

		#!-------------------------------------------------------------------!#
		#* 四个函数图像沿不同的方向飞入

		g1 = VGroup(a1, t1); g2 = VGroup(a2, t2)
		g3 = VGroup(a3, t3); g4 = VGroup(a4, t4)
		for g in [g1, g2, g3, g4]:
			g.suspend_updating(); g.generate_target(); g.set_opacity(0)

		g1.shift(RIGHT); g2.shift(RIGHT+DOWN*0.5); g3.shift(RIGHT*0.5+DOWN); g4.shift(RIGHT+DOWN)
		
		self.play(AnimationGroup(*[MoveToTarget(g) for g in [g1, g2, g3, g4]], lag_ratio=0.3))
		self.wait()

		# Postcondition
		self.a1=a1; self.a2=a2; self.a3=a3; self.a4=a4
		self.t1=t1; self.t2=t2; self.t3=t3; self.t4=t4
		self.g1=g1; self.g2=g2; self.g3=g3; self.g4=g4
		self.plot_config=plot_config; self.legend_config=legend_config

	def move_to_single_func(self):
		# Precondition
		a1=self.a1; a2=self.a2; a3=self.a3; a4=self.a4
		t1=self.t1; t2=self.t2; t3=self.t3; t4=self.t4
		g1=self.g1; g2=self.g2; g3=self.g3; g4=self.g4

		#!-------------------------------------------------------------------!#
		#* 其它函数图像淡出，x^2移至左边成为"THE function"

		#self.stop_skipping()
		for g in [g1, g2, g3]: g.suspend_updating() #出于某些奇怪的原因，这里得手动暂停updating. ？
		lagging_config = {'rate_func': lagged(0.3,1), 'run_time':1.3}
		self.stop_skipping()
		self.play(
			FadeOut(VGroup(g1, g2, g3)), 
			ApplyMethodToDataAxes(a4.move_to, LEFT*3.5, **lagging_config), 
			ApplyMethod(          t4.move_to, LEFT*2, **lagging_config) # 别忘了函数标签不在axes group里面
		)
		axes = a4; quadratic_label = t4
		
		#!-------------------------------------------------------------------!#
		#* 增添元素：axis_label

		axes.add_axis_labels()
		self.play(Write(axes.x_axis.label),Write(axes.y_axis.label))

		#!-------------------------------------------------------------------!#
		#* 增添元素：number labels

		number1 = CustomNumberLabel(1,    0, axes, 'x', [0, np.inf])
		number2 = CustomNumberLabel(0.5,  1, axes, 'x', [0, 1.5])
		number3 = CustomNumberLabel(0.25, 2, axes, 'x', [0, 0.75])
		number4 = CustomNumberLabel(0.1 , 1, axes, 'x', [0, 0.4])
		number5 = CustomNumberLabel(0.05, 2, axes, 'x', [0, 0.2])
		x_numbers = VGroup(number1, number2, number3, number4, number5)
		number1 = CustomNumberLabel(1,    0, axes, 'y', [0, np.inf])
		number2 = CustomNumberLabel(0.5,  1, axes, 'y', [0, 1.5])
		number3 = CustomNumberLabel(0.25, 2, axes, 'y', [0, 0.75])
		number4 = CustomNumberLabel(0.1 , 1, axes, 'y', [0, 0.4])
		number5 = CustomNumberLabel(0.05, 2, axes, 'y', [0, 0.2])
		y_numbers = VGroup(number1, number2, number3, number4, number5)

		x_numbers[0].suspend_updating(); y_numbers[0].suspend_updating() # 同上，不手动suspend就渲染不正确，不知道为什么
		self.play(Write(x_numbers[0]), Write(y_numbers[0]))
		self.add(x_numbers, y_numbers)

		#!-------------------------------------------------------------------!#
		#* 增添元素：小尺度时的额外的网格线

		self.add_grid_line(axes, 2, 0.25, True, 0.9)
		self.add_grid_line(axes, 2, 0.1,  True, 0.7)

		# Postcondition
		self.axes = axes
		self.quadratic_label = quadratic_label

	def show_merits_of_quadratic_func(self):
		# Postcondition
		axes = self.axes
		quadratic_label = self.quadratic_label
		plot_config = self.plot_config; legend_config=self.legend_config

		#* 构造文字
		text_config = {'color':FML_COLOR, 'font': 文楷, 'font_size':40, 'stroke_width':0}
		point1 = Text('+ 简单，易于计算',        **text_config)
		point2 = Text('+ 近处<<x, 可作为修正项', **text_config)
		#* 文字的位置排版
		point1.shift(RIGHT*1.6+UP*0.4)
		point2.next_to(point1, DOWN, buff=0.5)
		point2.align_to(point1, LEFT)

		#!-------------------------------------------------------------------!#
		#* 第一点动画
		self.wait(3)
		self.play(Write(point1), run_time=1.6)
		self.wait(3)

		#!-------------------------------------------------------------------!#
		#* 第二个优点
		#* 画用作对比的线性直线及其标签

		plot_config['color']=BLUE; legend_config['color']=BLUE
		
		linear_curve = axes.plot(lambda x: x, [0,1],True, True, **plot_config)
		linear_label = Tex('x', **legend_config) .move_to(axes.c2p(0.25,0.75)).scale(0.86) #微调
		self.play(Write(linear_label),Create(linear_curve))

		#!-------------------------------------------------------------------!#
		#* 曲线放大的动画，第二个优点

		#some little math here
		range = np.array([-0.4,1.4])
		scale_ratio=0.1
		# build a rate function that has the same shape with org_rate_func
		# in log(alpha)-t graph. useful when making multi-scale animations.
		'''def log_smooth(alpha):
			return (1-scale_ratio**smooth(alpha))/(1-scale_ratio)'''
		def logarized(scale_factor, org_rate_func=smooth):
			def logarized_rf(alpha):
				return (1-scale_factor**org_rate_func(alpha))/(1-scale_factor)
			return logarized_rf
		
		# zoom in
		self.play(
			ApplyMethodToDataAxes(
				axes.set_all_ranges, 
				range*scale_ratio, range*scale_ratio, 
				run_time=2.5, rate_func=logarized(scale_ratio, smooth)
			),
			linear_label.shift,UP*1.1, quadratic_label.shift,RIGHT*0.5
		)

		# get conclusion
		self.play(Write(point2), run_time=1.5); self.wait()

		# zoom out (zoom back)
		scale_ratio=10
		#detach linear_curve
		axes.plots.remove(linear_curve)
		linear_curve.clear_updaters()
		self.add(linear_curve)
		self.play(
			ApplyMethodToDataAxes(axes.set_all_ranges, range, range, 
								run_time=1, rate_func=logarized(scale_ratio, smooth)),
			quadratic_label.shift,LEFT*0.5,
			#linear_label.shift,DOWN*1.4, 
			FadeOut(linear_curve), FadeOut(linear_label)
		); self.wait()

		# postcondition
		# linear_curve detached
	
	def create_mini_axes(self) -> DataAxes:
		range = np.array([-0.4,1.4])
		length = (range[1]-range[0])*1.6
		axes_config = {
			'width': length, 'height': length,
			'include_numbers': False,
			'axis_align_towards_zero': True
		}
		return DataAxes(range, range, **axes_config)

	def add_grid_line(self, axes, tier, val, dynamic=False, show_threshold=None) -> None:
		'''add both vertical and horizontal grid lines of a value.
		very SPECIFIC for this scene and do not use it for other usages.'''
		grid_config = {'color':GREY_B, 'stroke_width':2}
		if tier==2: grid_config['stroke_width'] = 1

		axes: DataAxes
		l1 = axes.line([val,0],[val,1],True, True, Line, **grid_config)
		l2 = axes.line([0,val],[1,val],True, True, Line, **grid_config)

		if not dynamic: return
		def line_updater(m):
			range=axes.x_axis.x_max-axes.x_axis.x_min
			m.set_opacity(1-smooth_step(range, 0.7,0.1))
		l1.add_updater(line_updater); l2.add_updater(line_updater)
		

	#* simplified ver. of item construction and animation. for REFERENCE only!
	def simple_construct(self): 
		#! axes
		range = np.array([-0.4,1.3])
		length = (range[1]-range[0])*1.6
		axes_config = {
			'width': length, 'height': length,
			'include_numbers': False,
			'axis_align_towards_zero': True
		}
		axes = DataAxes(range, range, **axes_config)
		self.miniaxes = axes
		self.add(axes)

		#! axis labels
		axes.add_axis_labels()

		#! grid lines (dynamic)
		grid_config = {'color':GREY_B, 'stroke_width':2}
		half_line_config = grid_config.copy()
		half_line_config['stroke_width'] = 1

		axes.line([1,0],[1,1],True, True, Line, **grid_config)
		axes.line([0.5,0],[0.5,1],True, True, Line, **half_line_config)
		axes.line([0,1],[1,1],True, True, Line, **grid_config)
		axes.line([0,0.5],[1,0.5],True, True, Line, **half_line_config)

		def smooth_step(x, threshold, sigma):
			return 1/(1+np.exp(-(x-threshold)/sigma))
		def line_updater(m):
			range=axes.x_axis.x_max-axes.x_axis.x_min
			m.set_opacity(1-smooth_step(range, 0.9,0.1))
		axes.line([0,0.25],[1,0.25],True, True, Line, **half_line_config).add_updater(line_updater)
		axes.line([0.25,0],[0.25,1],True, True, Line, **half_line_config).add_updater(line_updater)
		def line_updater(m):
			range=axes.x_axis.x_max-axes.x_axis.x_min
			m.set_opacity(1-smooth_step(range, 0.7,0.1))
		axes.line([0,0.1],[1,0.1],True, True, Line, **half_line_config).add_updater(line_updater)
		axes.line([0.1,0],[0.1,1],True, True, Line, **half_line_config).add_updater(line_updater)

		#! number labels
		number1 = CustomNumberLabel(1,0, axes,'x', [0, np.inf])
		number2 = CustomNumberLabel(0.5,1,axes, 'x', [0,1.5])
		number3 = CustomNumberLabel(0.25,2,axes, 'x', [0,0.75])
		number4 = CustomNumberLabel(0.1,1,axes, 'x', [0,0.4])
		number5 = CustomNumberLabel(0.05,2,axes, 'x', [0,0.2])
		self.add(number1, number2, number3, number4, number5)
		number1 = CustomNumberLabel(1,0, axes,'y', [0, np.inf])
		number2 = CustomNumberLabel(0.5,1,axes, 'y', [0,1.5])
		number3 = CustomNumberLabel(0.25,2,axes, 'y', [0,0.75])
		number4 = CustomNumberLabel(0.1,1,axes, 'y', [0,0.4])
		number5 = CustomNumberLabel(0.05,2,axes, 'y', [0,0.2])
		self.add(number1, number2, number3, number4, number5)

		#! curve plots (and their labels)
		linear_plot = axes.plot(lambda x:x, x_range=[0,1], color=BLUE, stroke_width=6)
		quadratic_plot = axes.plot(lambda x:x**2, x_range=[0,1], color=ORANGE, stroke_width=6)

		linear_label = Tex('x',color=BLUE).scale(1.2).next_to(axes.c2p(0.5,0.7),UL, buff=0.1)
		quadratic_label = Tex('x^2',color=ORANGE).scale(1.2).next_to(axes.c2p(0.7,0.5),DR, buff=0.1)
		self.add(linear_label,quadratic_label)

		#! scale animations (finally)	
		#some little math here
		scale_ratio=0.1
		def log_smooth(alpha):
			#scale_ratio=0.1
			return (1-scale_ratio**smooth(alpha))/(1-scale_ratio)
		
		self.play(
			ApplyMethodToDataAxes(axes.set_all_ranges, range*scale_ratio, range*scale_ratio, run_time=1, rate_func=log_smooth),
			linear_label.shift,UP*0.4, quadratic_label.shift,RIGHT
		)

		self.wait()

		scale_ratio=10
		def log_smooth(alpha):
			#scale_ratio=0.1
			return (1-scale_ratio**smooth(alpha))/(1-scale_ratio)
		self.play(
			ApplyMethodToDataAxes(axes.set_all_ranges, range, range, run_time=1, rate_func=log_smooth),
			linear_label.shift,DOWN*0.4, quadratic_label.shift,LEFT
		)

# 用于遮挡后面mobj的幕布
# 用的时候请注意mobj图层顺序——Curtain类本身不保证遮挡关系。
class Curtain(Rectangle):
	CONFIG = {
		'fill_opacity': 1,
		'fill_color': BG_COLOR,
		'stroke_width': 0,
		'stroke_opacity': 0,

		'scale_factor': 1.0, # effective only 1)when init 2)when lrdu options are not specified
		'left': -FRAME_WIDTH/2,
		'right':+FRAME_WIDTH/2,
		'up':   +FRAME_HEIGHT/2,
		'down': -FRAME_HEIGHT/2
	}
	def __init__(self, **kwargs):
		digest_config(self, kwargs)
		self.left *= self.scale_factor
		self.right*= self.scale_factor
		self.up   *= self.scale_factor
		self.down *= self.scale_factor

		super().__init__(self.right-self.left, self.up-self.down)

		self._put_into_place()

	def _put_into_place(self):
		self.next_to(RIGHT*self.left, RIGHT, buff=0, coor_mask = np.array([1,0,0]))
		self.next_to(  UP *self.down,   UP , buff=0, coor_mask = np.array([0,1,0]))

	def set_left(self, left):
		if isinstance(left, np.ndarray): left=left[0]
		self.left=left
		self.rescale_to_fit(self.right-self.left, dim=0, stretch=True)
		self._put_into_place()
		return self
	def set_right(self, right):
		if isinstance(right, np.ndarray): right=right[0]
		self.right=right
		self.rescale_to_fit(self.right-self.left, dim=0, stretch=True)
		self._put_into_place()
		return self
	def set_up(self, up):
		if isinstance(up, np.ndarray): up=up[1]
		self.up=up
		self.rescale_to_fit(self.up-self.down, dim=1, stretch=True)
		self._put_into_place()
		return self
	def set_down(self, down):
		if isinstance(down, np.ndarray): down=down[1]
		self.down=down
		self.rescale_to_fit(self.up-self.down, dim=1, stretch=True)
		self._put_into_place()
		return self

class TestCurtain(StarskyScene):
	def construct(self):
		content = Rectangle(FRAME_WIDTH*2, FRAME_HEIGHT*2, fill_color = ORANGE, fill_opacity=1)
		self.add(content)
		self.wait()

		#curtain = Rectangle(FRAME_WIDTH, FRAME_HEIGHT, fill_opacity=1, fill_color='#222222')
		#curtain.next_to(ORIGIN, RIGHT, buff=0, coor_mask=np.array([1,0,0]))
		#curtain.next_to(-FRAME_HEIGHT/2*UP, UP, buff=0, coor_mask=np.array([0,1,0]))
		curtain = Curtain(left=0, scale_factor=1.5)
		#self.add(curtain)
		self.camera.frame.scale(2)
		self.play(FadeIn(curtain))
		self.play(curtain.set_left, -FRAME_WIDTH/2)

# 通过魔改shader实现的圆头直线——最终没有用上。
class RoundHeadedLine(Line):
	def __init__(
		self,
		start: np.ndarray = LEFT,
		end: np.ndarray = RIGHT,
		**kwargs
	):
		super().__init__(start, end, **kwargs)
		self._replace_shader_code()

	def _replace_shader_code(self):
		frag_shader_code = ''
		with open('shader/round_headed_line.frag', 'r') as f:
			frag_shader_code = f.read()
		self.get_stroke_shader_wrapper().set_code('frag',frag_shader_code)

class TestRoundHeadedLine(StarskyScene):
	def construct(self):
		self.camera.frame.scale(0.2)
		line = RoundHeadedLine(LEFT,RIGHT, stroke_width=40)
		#line = RoundHeadedLine(LEFT,RIGHT+UP*0.2, stroke_width=40)
		#line.reverse_points()
		self.play(Create(line))

# 零阶、一阶、二阶近似的比较。最后还是用了stencil scene的版本
class ToTaylorSeries(StencilScene):
	def construct(self) -> None:
		self.create_elements() #static
		self.move_to_zero_tier_axes()	
		self.illustrate_zero_tier_approx()
		self.move_to_all_cells()
		self.compare_between_approx()

	def create_elements(self):
		self.create_cell_contents()
		self.create_delim()
		
	def create_cell_contents(self):
		#!-------------------------------------------------------------------!#
		#* mobj configs
		mask_config = {'fill_opacity': 0.001, 'stroke_opacity': 0}
		axis_label_config = {'font': 文楷, 'font_size': 30}
		axis_label_args = {'x_label_str': '年份', 'y_label_str': '时间/s', 'label_class': Text, **axis_label_config}

		#!-------------------------------------------------------------------!#
		#* object construction

		grp = [None]*3
		axes= [None]*3
		
		mask   = Curtain(**mask_config)
		axes[0]= SprintWRDataFrame(x_range=[0,160], y_range=[9.4,10.7], dynamic=False) \
		         .add_axis_labels(**axis_label_args)
		dots   = axes[0].plot_data(dynamic=False)
		curve  = axes[0].plot_fit_curve(0, dynamic=False)
		grp[0] = StencilGroup(mask, axes[0], dots, curve)
		
		mask    = Curtain(**mask_config)
		axes[1] = SprintWRDataFrame(x_range=[0,160],y_range=[9.4,10.7], dynamic=False) \
		          .add_axis_labels(**axis_label_args)
		dots    = axes[1].plot_data(dynamic=False)
		curve   = axes[1].plot(lambda x: poly_func(linear_fit_coef)(x), x_range=[0,120], dynamic=False)
		grp[1]  = StencilGroup(mask, axes[1], dots, curve)
		
		mask    = Curtain(**mask_config)
		axes[2] = SprintWRDataFrame(x_range=[0,200],y_range=[9.4,10.69], dynamic=False) \
		          .add_axis_labels(**axis_label_args)
		dots    = axes[2].plot_data(dynamic=False)
		curve   = axes[2].plot_fit_curve(2, dynamic=False)
		grp[2] = StencilGroup(mask, axes[2], dots, curve)
		
		#!-------------------------------------------------------------------!#
		#* positioning

		axes[0].shift(LEFT*FRAME_WIDTH*0.25)
		#axes[1].shift(RIGHT*3)
		axes[2].shift(RIGHT*FRAME_WIDTH*(0.25+0.1)).shift(RIGHT*5.2)
		grp[0].stencil_mobject
		grp[1].stencil_mobject.center()
		grp[2].stencil_mobject.center().shift(RIGHT*FRAME_WIDTH*1/2)
	
		#!-------------------------------------------------------------------!#
		
		#self.add(grp[2], grp[1], grp[0])

		self.axes, self.grp = axes, grp

	def create_delim(self):
		def calc_pos(rel_x,rel_y): # (2d) NDC to manim rel. coord. (take camera scale into consideration)
			return np.array([rel_x*FRAME_WIDTH/2*1.5, rel_y*FRAME_HEIGHT*1.5/2, 0])

		_ = None
		delim = [ _, None, None ]

		delim_config = {'stroke_width': 2, 'color': GREY_C}
		delim[1] = Line(calc_pos(-1/3,1), calc_pos(-1/3,-1), **delim_config)
		delim[2] = Line(calc_pos(+1/3,1), calc_pos(+1/3,-1), **delim_config)
		#delim2.reverse_points()
		#shadow = delim1.copy().scale(1.05).set_stroke(color=BG_COLOR, width=40)
		#shadow = delim2.copy().scale(1.05).set_stroke(color=BG_COLOR, width=40)

		#self.add(*delim[1:])
		#self.play(Create(delim1),reorganize_mobjects=False)
		#self.play(Create(delim2),reorganize_mobjects=False)
		
		self.delim = delim

	def calculate_cell_border(self, camera_sf, cell_num):
		pos = [None]*(cell_num+1)
		pos[0] = FRAME_WIDTH*camera_sf*0.5*LEFT
		for i in range(cell_num+1):
			pos[i]=pos[0]+(FRAME_WIDTH*camera_sf*i/cell_num*RIGHT) 

		return pos

	def move_to_zero_tier_axes(self):
		axes, grp, delim = self.axes, self.grp, self.delim
		axes: Iterable[DataAxes]
		grp: Iterable[StencilGroup]
		
		#!-------------------------------------------------------------------!#
		#* 一次近似frame fadein. 
		#* 为了让本来属于axes[1]的lin_fit_curve单独动画进入，采用了新提出的
		#* detach-animate-attach语义，感觉效果非常不错。
		
		#detach
		lin_fit_curve = axes[1].plots[-1]
		axes[1].plots.remove(lin_fit_curve); grp[1].stenciled_mobjects.remove(lin_fit_curve)
		#animate
		self.add(grp[1])
		self.play(FadeIn(axes[1])); self.wait(0.5)
		self.play(Create(lin_fit_curve))
		#attach
		axes[1].plots.add(lin_fit_curve)
		grp[1].stenciled_mobjects.add(lin_fit_curve)

		self.add(grp[1]) #reorganize
		
		#!-------------------------------------------------------------------!#
		#* 二次近似axes挤进来。

		self.add(grp[1], grp[2])
		# As the "reorganize_mobjects" functionality is not completely implemented bugfree,
		# it's needed to add updaters to them to prevent them from being locked.
		# i.e. this tells manim that the mobj is to be animated
		# A useful trick if you try to animate mobjects in an unusual way but they don't move.
		IdentityUpdater =  lambda m: m
		for i in range(3):
			axes[i].add_updater(IdentityUpdater)

		# put in place
		camera_sf = 1.2
		left, mid, right = self.calculate_cell_border(camera_sf, 2)

		delim[2].move_to(FRAME_WIDTH*0.5*RIGHT*1.01)
		delim[2].generate_target()
		delim[2].target.move_to(ORIGIN)
		self.add(delim[2])

		mask1 = grp[1].stencil_mobject
		mask1.generate_target()
		mask1.target.set_left(left).set_right(ORIGIN)

		axes[2].next_to(ORIGIN, RIGHT)

		self.play(
			ApplyMethod(self.camera.frame.scale, camera_sf),

			ApplyMethod(axes[1].next_to, left, RIGHT),
			MoveToTarget(grp[1].stencil_mobject),

			MoveToTarget(delim[2]),
			
			FadeIn(axes[2], shift=LEFT*FRAME_WIDTH*0.5),

			run_time=1.5,
			reorganize_mobjects=False
		); self.wait(2)

		#!-------------------------------------------------------------------!#
		#* 零次近似axes挤进来。

		# put in place
		camera_sf1=camera_sf
		camera_sf = 1.5
		camera_sf2=camera_sf/camera_sf1

		pos = self.calculate_cell_border(camera_sf, 3)
		
		delim[1].move_to(FRAME_WIDTH*camera_sf1*0.5*LEFT*1.01)
		for i in [1,2]:	
			delim[i].generate_target()
			delim[i].target.move_to(pos[i])
		self.add(delim[1], delim[2]) #reorganize a bit

		grp[0].stencil_mobject.set_left(FRAME_WIDTH*3*LEFT).set_right(FRAME_WIDTH*1.2*0.5*LEFT)
		for i in range(3):
			mask = grp[i].stencil_mobject
			mask.generate_target()
			mask.target.set_left(pos[i]).set_right(pos[i+1])

		axes[2].next_to(ORIGIN, RIGHT)
		self.add(grp[0], grp[1], grp[2])

		self.play(
			ApplyMethod(self.camera.frame.scale, camera_sf2),

			*[ApplyMethod(axes[i].next_to, pos[i], RIGHT) for i in [0,1,2]],
			*[MoveToTarget(grp[i].stencil_mobject) for i in [0,1,2]],

			MoveToTarget(delim[1]), MoveToTarget(delim[2]),
			
			#FadeIn(axes[2], shift=LEFT*FRAME_WIDTH*0.5),
			run_time=2,
			reorganize_mobjects=False
		)

		self.wait(3)

		#!-------------------------------------------------------------------!#
		#* 零阶的axes独占屏幕
		
		x_shift = (FRAME_WIDTH*0.5*RIGHT) - pos[1]
		mask = grp[0].stencil_mobject
		mask.generate_target()
		mask.target.set_right(FRAME_WIDTH/2).set_left(-FRAME_WIDTH/2)

		Rectangle.next_to
		self.play(
			ApplyMethod(self.camera.frame.to_default_state), #相机归位

			ApplyMethod(axes[0].next_to, FRAME_WIDTH*0.5*LEFT, RIGHT, 1),
			MoveToTarget(grp[0].stencil_mobject),

			*[ApplyMethod(m.shift, x_shift) for m in [*grp[1:], *delim[1:]]], #其它元素向右平移即可

			run_time=1.5,
			reorganize_mobjects=False
		)

		for i in range(3):
			axes[i].remove_updater(IdentityUpdater)

	def illustrate_zero_tier_approx(self):
		#* precondition
		axes, grp, delim = self.axes, self.grp, self.delim
		axes: Iterable[DataAxes]
		grp: Iterable[StencilGroup]
		# lift mobj in grp[0] to scene root to simplify following animations
		self.remove(grp[0])
		self.add(*(grp[0].stenciled_mobjects))

		# z for zero tier
		zfit_curve=self.grp[0].stenciled_mobjects[-1]

		#!-------------------------------------------------------------------!#
		#* y=a0=10.0 公式进场
		self.stop_skipping()
		fml = Tex('y','=','a_0','=','10.0s', color=FML_COLOR, font_size=60)
		fml[2].set_color(LIGHT_BROWN)
		fml.to_corner(UR, buff=1.5).shift(LEFT*0.6)
		x0_factor = Tex('x^0', color=FML_COLOR, font_size=60).next_to(fml[2],RIGHT, buff=SMALL_BUFF) \
			.shift(0.17*UP) #不得不手动微调一下

		self.play(Create(fml[0:3]))
		self.wait(1)
		self.play(Create(x0_factor))
		self.interact()
		self.wait(2)
		self.play(FadeOut(x0_factor))
		self.play(Create(fml[3:]))
		self.add(fml)
		self.wait(1)
		#!-------------------------------------------------------------------!#
		#* 强调-坐标轴数字和直线
		# 先找到10.0数字
		ynr_labels=axes[0].y_axis.numbers
		y_intercept_label = filter(
				lambda m: abs(m.number-10.0)<1e-6, 
				ynr_labels
		)
		y_intercept_label = list(y_intercept_label)[0]

		# prepare target
		m1 = y_intercept_label.copy() #reserve for transform back
		y_intercept_label.generate_target()
		y_intercept_label.target.scale(2).align_to(ynr_labels[0],RIGHT) \
				.set_color(YELLOW_D)
		ylabel_backstroke=y_intercept_label.copy()
		ylabel_backstroke.set_stroke(color=BLACK, width=14)
		m2 = ylabel_backstroke.copy()
		ylabel_backstroke.generate_target()
		ylabel_backstroke.target.scale(2).align_to(ynr_labels[0],RIGHT)
		
		self.add(ylabel_backstroke); self.bring_to_back(ylabel_backstroke)
		self.play(
			MoveToTarget(ylabel_backstroke), MoveToTarget(y_intercept_label), 
			FadeOut(zfit_curve)
		)
		self.wait()
		self.play(Create(zfit_curve))
		self.wait()
		self.play(Transform(ylabel_backstroke, m2.set_opacity(0)),
				Transform(y_intercept_label, m1))
		self.remove(ylabel_backstroke)

		#* postcondition
		# attach grp[0] back to scene root to preserve the cell structure
		self.add(grp[2],grp[1],grp[0])
		self.res_tex = fml

	def move_to_all_cells(self):
		#* precondition
		axes, grp, delim = self.axes, self.grp, self.delim
		axes: Iterable[DataAxes]
		grp: Iterable[StencilGroup]
		#* remenber that the 1-tier and 2-tier cell is still at the right of the scene
		res_tex=self.res_tex
		#!-------------------------------------------------------------------!#
		#* move to show all cell contents
		camera_sf = 1.5
		pos = self.calculate_cell_border(camera_sf, 3)

		mask = grp[0].stencil_mobject
		mask.generate_target()
		mask.target.set_left(pos[0]).set_right(pos[1])

		x_shift=pos[1]-FRAME_WIDTH*1*0.5*RIGHT

		#self.stop_skipping()
		axes[0].add_updater(lambda m: m)
		self.play(
			ApplyMethod(axes[0].next_to, pos[0], RIGHT),
			MoveToTarget(grp[0].stencil_mobject),
			FadeOut(res_tex),

			*[ApplyMethod(m.shift, x_shift) for m in [delim[1],grp[1],delim[2],grp[2]]],

			ApplyMethod(self.camera.frame.scale, camera_sf),

			run_time=1.5,
			reorganize_mobjects=False
		)
		self.wait(2)

		#* postcondition
		self.camera_sf = camera_sf

	def _emph_dots_and_curve(self, tier):
		#* precondition
		axes, grp, delim = self.axes, self.grp, self.delim
		axes: Iterable[DataAxes]
		grp: Iterable[StencilGroup]
		camera_sf = self.camera_sf # 1.5 should be

		dots = grp[tier].stenciled_mobjects[-2]
		curve= grp[tier].stenciled_mobjects[-1]
		emph_rf=emphasize(0.5,0.5,smooth)
		IdentityUpdater = lambda m: m
		dots.add_updater(IdentityUpdater)
		curve.add_updater(IdentityUpdater)
		self.play(
			*[ApplyMethod(d.scale,2.5, rate_func=there_and_back, time_span=[0.06*i, 0.06*i+0.8]) for i,d in enumerate(dots)],
			ApplyMethod(curve.set_stroke, {'width':14}, time_span=[0.6,1.6], rate_func=emph_rf),
			reorganize_mobjects=False
		)
		dots.remove_updater(IdentityUpdater)
		curve.remove_updater(IdentityUpdater)

	def compare_between_approx(self):
		#* precondition
		axes, grp, delim = self.axes, self.grp, self.delim
		axes: Iterable[DataAxes]
		grp: Iterable[StencilGroup]
		camera_sf = self.camera_sf # 1.5 should be

		self._emph_dots_and_curve(1)
		self.wait(0.5)
		self._emph_dots_and_curve(0)
		self.wait(1)
		self._emph_dots_and_curve(2)
		self.wait(0.5)
		self._emph_dots_and_curve(1)
		self.wait(1)

		#!-------------------------------------------------------------------!#
		#* 一段公式强调
		curtain = Curtain(scale_factor=1.5, fill_opacity=0.98)
		self.play(FadeIn(curtain))
		TS_fml = Tex('f(x)=',
			'a_0','+',
			'a_1','x','+',
			'a_2','x^2','+',
			'\\cdots',
			color=FML_COLOR, font_size=100
		)
		for idx in [1,3,6]:
			TS_fml[idx].set_color(LIGHT_BROWN)

		self.play(Create(TS_fml[0]), FadeIn(TS_fml[1],shift=UP*0.6, time_span=[0.5,1.5]))
		self.wait(0.5)
		self.play(FadeIn(TS_fml[2:5], shift=UP))
		self.wait(0.5)
		self.play(FadeIn(TS_fml[5:8], shift=UP), FadeIn(TS_fml[8:], shift=UP, time_span=[0.4,1.4]))
		self.wait()

		# "这，就是泰勒展开"
		self.add(TS_fml)
		self.play(TS_fml.shift, DOWN*3)
		self.wait(3)

		self.play(FadeOut(curtain), FadeOut(TS_fml))
		self.wait()
		
		#!-------------------------------------------------------------------!#
		#* 配合已有的三个axes再强调一次

		TS_fml = Tex(
			'f(x)\\approx y=', 'a_0',
			'+','a_1','x',
			'+', 'a_2','x^2',
			color=FML_COLOR, font_size=100
		)
		for idx in [1,3,6]: # TODcoef 'a's
			TS_fml[idx].set_color(LIGHT_BROWN)
		TS_fml.shift(UP*3)
			
		fml_grp = [
			VGroup(TS_fml[0:2]),
			VGroup(TS_fml[2:5]),
			VGroup(TS_fml[5:]),	
		]
		for tier in range(3):
			fml_grp[tier].move_to(grp[tier].stencil_mobject).shift(UP*3.7)

		self.play(
			*[ApplyMethod(grp[i].shift, DOWN*1.7) for i in range(3)],
			reorganize_mobjects=False
		)
		self.wait()

		self.play(Write(fml_grp[0]),run_time=1.5)
		self.wait()
		self.play(Write(fml_grp[1]))
		self.wait()
		self.play(Write(fml_grp[2]))
		self.wait(3)

# 只用幕布前后遮挡的版本
class ToTaylorSeries2(StarskyScene):
	def construct(self) -> None:
		axes = SprintWRDataFrame(y_range=[9.4,10.7])
		axes.draw_axis_labels()
		dots = axes.plot_data()
		curve= axes.plot_fit_curve(0)
		grp1 = VGroup(axes, dots, curve); a1 = axes
		a1.shift(RIGHT)

		axes = SprintWRDataFrame(y_range=[9.4,10.7])
		axes.draw_axis_labels()
		dots = axes.plot_data()
		curve= axes.plot_fit_curve(1)
		curt = Curtain(left=-1/6, scale_factor=1.5); c1=curt
		grp2 = VGroup(axes, dots, curve); a2 = axes
		a2.shift(RIGHT*3)

		axes = SprintWRDataFrame(x_range=[0,200],y_range=[9.4,10.7])
		axes.draw_axis_labels()
		dots = axes.plot_data()
		curve= axes.plot_fit_curve(2)
		curt = Curtain(left=+1/6, scale_factor=1.5); c2=curt
		grp3 = VGroup(axes, dots, curve); a3 = axes

		a3.shift(RIGHT*FRAME_WIDTH*(0.25+0.1)).shift(RIGHT*5)

		#self.add(rect, axes, dots, curve)
	
		self.add(grp1, c1, grp2, c2, grp3) #注意 后加的对象图层在前
		#self.camera.frame.scale(1.5)

		self.play(
			self.camera.frame.scale,1.5,

			#grp1.stencil_mobject.shift,LEFT*FRAME_WIDTH*3/4, 
			ApplyMethodToDataAxes(a1.shift, LEFT*FRAME_WIDTH*(0.25+0.1)),

			ApplyMethod(c1.set_opacity,0, run_time=1.5, rate_func=lagged(0.5,1)),

			ApplyMethod(c2.set_opacity,0, run_time=2,   rate_func=lagged(1,1)),
			
			reorganize_mobjects=False
		)
		
		delim1 = Line(LEFT*FRAME_WIDTH*0.25+3*UP, LEFT*FRAME_WIDTH*0.25+3*DOWN, stroke_width=10)
		shadow = delim1.copy().scale(1.05).set_stroke(color=BG_COLOR, width=40)

		self.add(shadow, delim1)
		self.play(Create(shadow),Create(delim1),reorganize_mobjects=False)

		delim2 = Line(RIGHT*FRAME_WIDTH*0.25+3*UP, RIGHT*FRAME_WIDTH*0.25+3*DOWN, stroke_width=10)
		delim2.reverse_points()
		shadow = delim2.copy().scale(1.05).set_stroke(color=BG_COLOR, width=40)

		self.add(shadow, delim2)
		self.play(Create(shadow),Create(delim1),reorganize_mobjects=False)

# 用经典和相对论的能动量关系illustrate泰勒展开的用法
class RelClsPhysicalShowcase(StarskyScene):
	# Rel Cls stands for relativity and classical
	def section(self):
		'''Just a mark'''
		pass

	def stall(self):
		self.interact()

	def is_indev(self):
		return self.preview
	def is_rendering(self):
		return not self.preview
	
	def setup(self):
		pass

	def construct(self) -> None:
		#!-------------------------------------------------------------------!#
		#* 创建坐标系并进入

		#decimal_number_config = {"num_decimal_places": 2}
		#axis_config = {'decimal_number_config':decimal_number_config}	
		axes_config = {
			'width':10,
			'include_numbers':False
		}
		axes = DataAxes([0,2],[0,2], **axes_config).shift(LEFT*0.5)
		p_axis_label_tex = Tex('p')
		p_axis_label_cn  = Text('动量',font=文楷, font_size=34)
		p_axis_label_cn.next_to(p_axis_label_tex,LEFT,buff=0.1)
		p_axis_label=VGroup(p_axis_label_cn,p_axis_label_tex)
		p_axis_label.next_to(axes.x_axis,DOWN)
		self.add(p_axis_label)

		E_axis_label_tex = Tex('E_k')
		E_axis_label_cn  = Text('动能',font=文楷, font_size=34)
		E_axis_label_cn.next_to(E_axis_label_tex,LEFT,buff=0.1)
		E_axis_label=VGroup(E_axis_label_cn,E_axis_label_tex)
		E_axis_label.rotate(PI/2).next_to(axes.y_axis,LEFT)
		self.add(E_axis_label)

		self.play(Create(axes), FadeIn(p_axis_label), FadeIn(E_axis_label))
		self.wait(3)

		#!-------------------------------------------------------------------!#
		#* 曲线，公式和文字

		#一些科学计算函数
		e=1.6022e-19
		MeV=1e6*e
		m_e=9.109e-31
		c=2.998e8

		def classical(pc_MeV):
			p_SI=pc_MeV*MeV/c
			return p_SI**2/(2*m_e)/MeV
		def relativity(pc_MeV):
			E_0_MeV=m_e*c**2/MeV
			return (pc_MeV**2+E_0_MeV**2)**0.5-E_0_MeV

		classical_plot  = axes.plot(classical,  [0,1.4], False,False, color=BLUE,   stroke_width=6)
		relativity_plot = axes.plot(relativity, [0,1.8], False,False, color=ORANGE, stroke_width=6)

		classical_label_cn=Text('经典',font=文楷, font_size=44, color=BLUE)
		classical_label_en=Text('Classical',font=文楷, font_size=24, color=BLUE)
		classical_label_en.next_to(classical_label_cn,DOWN, buff=0.1)
		classical_label = VGroup(classical_label_cn, classical_label_en)
		classical_label.next_to(axes.c2p(0.9,classical(0.9)),UL, buff=0.5)
		#self.add(classical_label)
		
		relativity_label_cn=Text('相对论',font=文楷, font_size=44, color=ORANGE)
		relativity_label_en=Text('Relativistic',font=文楷, font_size=24, color=ORANGE)
		relativity_label_en.next_to(relativity_label_cn,DOWN, buff=0.1)
		relativity_label = VGroup(relativity_label_cn, relativity_label_en)
		relativity_label.next_to(axes.c2p(1.1,relativity(1.1)),DR, buff=0.4)
		#self.add(relativity_label)

		classical_fml = Tex(r'E_k={p^2\over 2m}',r'=\frac{1}{2}m_0v^2', color=BLUE, font_size=40)
		classical_fml.next_to(axes.c2p(1.3,classical(1.3)),LEFT, buff=0.5)
		relativity_fml= Tex(r'E_k=\sqrt{m_0^2c^4+c^2p^2}-m_0c^2', color=ORANGE, font_size=40)
		relativity_fml.next_to(axes.c2p(1.3,relativity(1.3)),RIGHT, buff=0.8)
		#self.add(classical_fml, relativity_fml)

		
		self.play(Create(relativity_plot)); self.wait()
		self.play(Write(relativity_fml))
		self.play(Write(relativity_label))
		self.wait(5)
		self.play(Create(classical_plot)); self.wait()
		self.play(Write(classical_fml[0])); self.wait(5)
		self.play(Write(classical_fml[1])); self.wait(2)
		self.play(Write(classical_label))

		#!-------------------------------------------------------------------!#
		#* 渐进地认识真理
		self.wait(3)
		rel_grp = VGroup(relativity_fml, relativity_label)
		self.play(rel_grp.set_opacity, 0.1, relativity_plot.set_stroke, {'opacity':0.1})
		self.wait(1)
		self.play(rel_grp.set_opacity, 1, relativity_plot.set_stroke, {'opacity':1})
		self.wait(7)

		'''
		def brignten_fill(m, extent=0.5):
			white = Color('white')
			org_col=Color(hex_l = m.get_fill_color())
			#np.array(white.rgb)*extent+
			#np.array(org_col.rgb)*(1-extent)
			brightend=Color(rgb = np.clip(np.array(org_col.rgb)*extent, 0.,1.))
			m.set_fill(color=brightend)

		def brighten_group_fill(M: VGroup, extent=0.5):
			for m in M: 
				brignten_fill(m, extent)
		self.stop_skipping()
		highlight = VHighlight(classical_label, color_bounds=[BLUE_C, '#222222'], max_stroke_addition=10)
		
		
		classical_label.generate_target()
		brighten_group_fill(classical_label.target, extent=1.4)
		
		self.wait()
		self.add(highlight); self.bring_to_back(highlight)
		self.play(FadeIn(highlight), MoveToTarget(classical_label), reorganize_mobjects=False)
		#highlight.shift(LEFT)
		'''

class ShowOverfitting(StarskyScene):
	# 单个坐标系的Scene出现了很多次，应该写一个公共基类的
	# 以后吸取教训
	def construct(self) -> None:
		self.create_axes()
		self.show_overfitting()
		
	def create_axes(self, simple=False):
		# precondition
		#* NONE *#

		self.xrange=[-20,120]
		
		axes = SprintWRDataFrame(x_range=self.xrange,y_range=[9.3,11.0],include_numbers = False).align_on_border(LEFT,1.4)
		self.play(Create(axes),run_time=1.3)

		axes.add_numbers()
		axes.add_axis_labels('年份','时间/s',Text, font=落霞孤鹜, font_size=30)

		if simple:
			self.play(FadeIn(axes))
		else:
			self.play(
				AnimationGroup(*[
					FadeIn(m, UP*0.2) for m 
					in list(axes.x_axis.numbers)+[axes.x_axis.label]],
				lag_ratio=0.2,run_time=2),

				AnimationGroup(*[
					FadeIn(m, RIGHT*0.2) for m 
					in list(axes.y_axis.numbers)+[axes.y_axis.label]],		
				lag_ratio=0.2,run_time=3)
			)
		self.add(axes)
		self.wait(1.5)
		
		# postcondition
		self.axes = axes
		# plus self.xrange

	def show_overfitting(self):
		# 画数据与拟合直线

		# Precondition
		axes = self.axes
		
		lihua = LittleCreature(flipped=True).to_corner(DR, buff=1)

		# create, animate and reorganize
		data_scatter = axes.plot_data(radius=0.06)
		self.play(AnimationGroup(*[
				Popup(m) for m 
				in data_scatter],
			lag_ratio=0.2, run_time=2.5, rate_func=linear)
		)
		self.add(data_scatter) 

		xrange = self.xrange
		lin_fit_curve = axes.plot(poly_func(linear_fit_coef), xrange, False, False)
		quad_fit_curve = axes.plot(poly_func(quadratic_fit_coef), xrange, False, False)
		cubic_fit_curve = axes.plot(poly_func(cubic_fit_coef), xrange, False, False)
		# note that extra precision is needed to get high-deg poly fit work correctly.
		deg5_fit_curve = axes.plot(spoly_func(deg5_fit_coef), xrange, False, False)
		deg8_fit_curve = axes.plot(spoly_func(deg8_fit_coef), xrange, False, False)

		#更适合的范围

		T,RT = Transform, ReplacementTransform
		self.play(Create(quad_fit_curve, run_time=1.5), 
				FadeIn(lihua, time_span=[0.5,1.5]))
		self.play(lihua.change_mood, 'happy'); self.wait(1)
		#self.play(RT(lin_fit_curve, quad_fit_curve), 
		#		ApplyMethod(lihua.change_mood,'happy'))
		self.play(RT(quad_fit_curve, cubic_fit_curve), 
				lihua.change_mood, 'plain'); self.wait(0.5)
		self.play(RT(cubic_fit_curve, deg5_fit_curve), 
				ApplyMethod(lihua.change_mood,'puzzling')); self.wait(0.5)
		self.play(RT(deg5_fit_curve, deg8_fit_curve))
		self.wait(1)
		self.play(Blink(lihua)); self.wait(0.4)
		self.play(Blink(lihua))
		self.wait(20)

		# Postcondition
		#* END SCENE *#
