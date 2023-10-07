from typing import Iterable
from manimlib import *
from manimhub import *
import os, sys
from manimlib.mobject.mobject import Mobject; sys.path.append(os.path.dirname(__file__))
from set_output_path import set_output_path
import bbrad
from utils import *


class LabelAvoidingTickLocator(SmartTickLocator):
	def __call__(self, x_min, x_max, x_step, axis) -> Iterable:
		length = (x_max-x_min)*axis.unit_size
		label_width = 1
		length -= label_width
		x_max = length/axis.unit_size+x_min
		x_max = max(x_max, x_min+1e-2)
		return super().__call__(x_min, x_max, x_step, axis)

class Check(SVGMobject):
	def __init__(self, **kwargs):
		super().__init__('assets/check.svg', **kwargs)
		self.set_stroke(width=0)

class Cross(SVGMobject): # 一点import冲突...偷个懒
	def __init__(self, **kwargs):
		super().__init__('assets/cross.svg', **kwargs)
		self.set_stroke(width=0)

#* not done yet!
class Indicator(Arrow):
	def __init__(self, target, dir_angle, length=1.5, buff=MED_SMALL_BUFF, stroke_width=8, **kwargs):
		end = target
		start = end + length* np.array([np.cos(dir_angle), np.sin(dir_angle), 0])
		super().__init__(start, end, buff=buff, stroke_width=stroke_width)

class BlackbodySpectrumScene(StarskyScene):
	'''Father class with some shared functionality implemented'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)

		# shortcuts
		global add, play, wait, narrate
		add = self.add
		play = self.play
		wait = self.wait
		narrate = self.narrate
		Mobject.a = Mobject.animate

	def in_dev(self) -> bool:
		return not self.file_writer.write_to_movie

	def get_indicator(self, target, dir_angle, length=1.5, buff=MED_SMALL_BUFF, stroke_width=8) -> Arrow:
		end = target
		start = end + length* (DOWN*np.cos(dir_angle) + RIGHT*np.sin(dir_angle))
		return Arrow(start, end, buff=buff, stroke_width=stroke_width)

	def construct_axes(self, xlim=2000, ylim=80) -> DataAxes:
		'''construct mobjects only, neither added nor animated'''
		axes = DataAxes(
			_y_axis_config=dict( # now unneeded
				direction = VERTICAL,
				decimal_number_config=dict(
					num_decimal_places = 1,
					font_size = 30,
					group_with_commas = False
				),
			),
			x_axis_config=dict(
				tick_locator = SmartTickLocator(tick_density=0.3),
				number_locator = LabelAvoidingTickLocator(tick_density=0.3),
			),
			height = FRAME_HEIGHT-2,
			width  = FRAME_WIDTH-3,
		)
		axes.set_range('x',[0,xlim])
		axes.set_range('y',[0,ylim])
		label_x = Text('波长/nm',           font=文楷).scale(0.8)
		label_y = Text('辐射能/(kW/m²/nm)', font=文楷).scale(0.8).rotate(PI/2)
		label_x.next_to(axes.x_axis, DR ).shift(LEFT*1.3+UP*0.5)
		label_y.next_to(axes.y_axis,LEFT)

		return axes, label_x, label_y

	def get_advanced_axes_fadein_animation(self, axes, label_x, label_y, run_time_param) -> Iterable[Animation]:
		bare_line_x = VGroup(axes.x_axis.line, axes.x_axis.tip)
		bare_line_y = VGroup(axes.y_axis.line, axes.y_axis.tip)
		_dummy = Mobject()
		rt = run_time_param
		return [
			# x axis
			Create(bare_line_x,rate_func=linear,run_time=rt),
			AnimationGroup(
				*([Animation(_dummy)]*2 + [
				FadeIn(m, UP*0.3) for m 
				in list(axes.x_axis.ticks)
			]), lag_ratio=0.2,run_time=rt,rate_func=linear),
			AnimationGroup(
				*([Animation(_dummy)]*5 + [
				FadeIn(m, UP*0.3) for m 
				in list(axes.x_axis.numbers)
			]), lag_ratio=0.2,run_time=rt,rate_func=linear),
			
			# y axis
			Create(bare_line_y,rate_func=linear,time_span=[0.5,rt]),
			AnimationGroup(
				*([Animation(_dummy)]*2 + [
				FadeIn(m, DOWN*0.3) for m 
				in list(axes.y_axis.ticks)
			]), lag_ratio=0.2,run_time=rt,rate_func=linear),
			AnimationGroup(
				*([Animation(_dummy)]*5 + [
				FadeIn(m, RIGHT*0.3) for m 
				in list(axes.y_axis.numbers)
			]), lag_ratio=0.16,run_time=rt,rate_func=linear),
			
			# labels
			FadeIn(label_x, UP*0.3, time_span = [rt-0.5,rt+0.5]),
			FadeIn(label_y, RIGHT*0.2, time_span = [rt-0.5,rt+0.5]),
		]

	def get_image_and_mask_under_curve(self, axes, curve, dynamic=False) -> (ImageMobject, VMobject):
		# 可见光组成的背景，以及上面的mask
		bg_img = ImageMobject('bbrad-wavelength-bg.png')
		bg_img_mask = VMobject()

		xmin, xmax = axes.x_axis.min, axes.x_axis.max
		ymin  = 0
		ymax = 300 # some value that's far bigger than axes.y_axis.max

		def bg_img_gn(m):
			# 光谱图只做到2000，这里的2000是固定的
			bg_img.rescale_to_fit(axes.x_axis.unit_size*2000, HORIZONTAL)
			bg_img.rescale_to_fit(axes.y_axis.unit_size*(ymax-1), VERTICAL, stretch=True)
			bg_img.next_to(axes.c2p(0,0), UR, buff=0)
			return m
		def bg_img_mask_gn(m):
			curve.update() # 只好出此下策
			bg_img_mask.set_points(curve.get_points())
			bg_img_mask.add_points_as_corners([axes.c2p(xmax, ymax), axes.c2p(xmin,ymax), axes.c2p(xmin,ymin)])
			bg_img_mask.set_fill(BG_COLOR, 1).set_stroke(width=0)
			return m
		
		bg_img_gn(bg_img); bg_img_mask_gn(bg_img_mask)
		if dynamic:
			bg_img.add_updater(bg_img_gn)
			bg_img_mask.add_updater(bg_img_mask_gn)
		
		return bg_img, bg_img_mask



class SpectrumIntro(BlackbodySpectrumScene):
	def construct(self) -> None:
		#* ----------------------------------------------------------------- *#
		#* axes
		#* ----------------------------------------------------------------- *#

		axes, label_x, label_y = self.construct_axes()
		axes: DataAxes

		if self.skip_animations and self.in_dev():
			add(axes, label_x, label_y)
		else:
			axes_fadein_animation = self.get_advanced_axes_fadein_animation(
				axes, label_x, label_y, run_time_param=2)
			play(*axes_fadein_animation)
			add(axes, label_x, label_y)
			wait()

		#* ----------------------------------------------------------------- *#
		#* 构造各式曲线
		#* ----------------------------------------------------------------- *#
		curve_planck = axes.plot(bbrad.Planck,        [220, 1600, 10], attach=False, dynamic=True)
		curve_wien   = axes.plot(bbrad.Wien,          [  1, 2000, 10], attach=False, dynamic=True)
		curve_rj     = axes.plot(bbrad.ReighleyJeans, [100, 2000, 10], attach=False, dynamic=True)
		curve_xaxis1 = axes.plot(lambda x:0,          [220, 1600, 10], attach=False, dynamic=False)
		curve_planck.set_color(YELLOW)
		curve_xaxis1.match_style(curve_planck)
		
		data_min = bbrad.get_exp_data_range()[0]
		curve_space  = axes.plot(bbrad.exp_space, [data_min, 2000, 10], attach=False, dynamic=True)
		curve_terra  = axes.plot(bbrad.exp_terra, [data_min, 2000, 10], attach=False, dynamic=True)
		curve_xaxis2 = axes.plot(lambda x:0,      [data_min, 2000, 10], attach=False, dynamic=False)
		curve_space.set_color(YELLOW_B)
		curve_terra.set_color(YELLOW_B)
		curve_xaxis2.match_style(curve_terra)
		
		temperature = ValueTracker(5700)
		def planck_T_controller(curve):
			bbrad.set_temperature(temperature.get_value())
		temperature.add_updater(planck_T_controller)
		
		#* ----------------------------------------------------------------- *#
		# 对横纵坐标轴的介绍
		#* ----------------------------------------------------------------- *#
		#self.stop_skipping()
		play(Create(curve_planck),run_time=2)
		wait()
		ch_txt = Text('谱',font=文楷).scale(2)
		ch_txt.move_to(RIGHT*1+UP*2)
		en_txt = Text('Spectrum',font=文楷).scale(1.2)
		en_txt.next_to(ch_txt, RIGHT, buff=0.7).align_to(ch_txt,DOWN)
		ch_txt.set_fill(RED_A)
		en_txt.set_fill(RED_B)
		#ch_txt.set_stroke(YELLOW, 4, 1)
		play(Write(ch_txt))
		wait()
		play(Write(en_txt))
		wait()
		play(FadeOut(ch_txt), FadeOut(en_txt))
		wait(0.5)

		def gen_wave_func(amp, freq, phase):
			def wave_func(x):
				return UP*x + LEFT*amp*np.cos(freq*x+phase)
			return wave_func
		
		wave1 = ParametricCurve(gen_wave_func(0.3,3*TAU,PI/4),[0,1.5,0.01])
		wave1.set_color(PURPLE_B)
		bloom = VHighlight(wave1, color_bounds=[PURPLE_A, BG_COLOR], max_stroke_addition=15)
		bloom.set_stroke(opacity=0.15)
		wave1 = VGroup(bloom, wave1).next_to(axes.c2p(100,0),UP,buff=0.5)

		wave2 = ParametricCurve(gen_wave_func(0.3,2*TAU,PI/4),[0,1.5,0.01])
		wave2.set_color(GREEN_A)
		bloom = VHighlight(wave2, color_bounds=[GREEN_A, BG_COLOR], max_stroke_addition=15)
		bloom.set_stroke(opacity=0.15)
		wave2 = VGroup(bloom, wave2).next_to(axes.c2p(600,0),UP,buff=0.5)

		wave3 = ParametricCurve(gen_wave_func(0.3,1*TAU,PI/4),[0,1.5,0.01])
		wave3.set_color(RED_B)
		bloom = VHighlight(wave3, color_bounds=[RED_B, BG_COLOR], max_stroke_addition=15)
		bloom.set_stroke(opacity=0.15)
		wave3 = VGroup(bloom, wave3).next_to(axes.c2p(1800,0),UP,buff=0.5)

		#add(wave1, wave2, wave3)
		
		highlight = SurroundingRectangle(label_x)
		play(
			AnimationGroup(
				FadeIn(wave1),
				FadeIn(wave2),
				FadeIn(wave3), lag_ratio=0.4, run_time=1.5
			),
			Create(highlight, time_span=[1,2])
		)
		wait(0.5)
		play(*[FadeOut(m) for m in [wave1, wave2, wave3, highlight]])
		wait(3)

		curve_xaxis1.match_style(curve_planck).set_stroke(opacity=0)
		play(FadeIn(curve_xaxis1),run_time=0.2,rate_func=linear)
		play(Transform(curve_xaxis1, curve_planck))
		self.remove(curve_xaxis1)
		wait(3)
		
		# 截图用
		#text = Text('???', font=文楷).move_to(label_x).set_color(YELLOW)
		#text2 =Text('? ? ?', font=文楷).move_to(label_x).set_color(YELLOW).move_to(label_y).rotate(PI/2)
		#add(text, text2)
		#self.remove(label_x,label_y)
		#return

		#* ----------------------------------------------------------------- *#
		#* 实际的例子
		#* ----------------------------------------------------------------- *#
		play(FadeIn(curve_xaxis2),run_time=0.4,rate_func=linear)
		play(Transform(curve_xaxis2, curve_terra), FadeOut(curve_planck))
		self.remove(curve_xaxis2); add(curve_terra)
		wait(3)

		#* ----------------------------------------------------------------- *#
		# 波谱上的坑坑洼洼
		#* ----------------------------------------------------------------- *#
		holes_x = [760, 940, 1150, 1400]
		holes_y = [bbrad.Planck(x) for x in holes_x]
		ends = [axes.c2p(holes_x[i],holes_y[i]) for i in range(len(holes_x))]
		arrows = VGroup(
			*[Arrow(ends[i]+UP*1.5+RIGHT*0.4, ends[i], buff=0.1, stroke_width=8) for i in range(len(holes_x))],
		)
		end = axes.c2p(750,14)
		arrows[0].become(Arrow(end+LEFT*1.5+DOWN*0.4, end ,buff=0.2, stroke_width=5))
		self.stop_skipping()
		play(Create(arrows), run_time=2)
		narrate('也许比你想象得要复杂一点')
		play(FadeOut(arrows))
		narrate('也许比你想象得要复杂一点')

		#* ----------------------------------------------------------------- *#
		#* 可见光颜色组成的背景
		#* ----------------------------------------------------------------- *#
		bg_img, bg_img_mask = self.get_image_and_mask_under_curve(axes, curve_terra)

		end = axes.c2p(560, bbrad.exp_terra(560))
		start = end + 1.5*(UP + RIGHT*0.5)
		arrow = Arrow(start, end, buff=0.4, stroke_width=8)	

		#* 可见光波段
		self.bring_to_back(bg_img, bg_img_mask) # handle object visible order
		play(
			FadeIn(bg_img,time_span=[0.5,2]),
			Create(arrow)
		)
		wait(0.5)
		
		#* infrarad/long wavelength
		#self.stop_skipping()
		arrow3 = self.get_indicator(axes.c2p(1650,12), 160*DEGREES, 2)
		wave3.next_to(arrow3, RIGHT, buff=0.7)
		play(GrowArrow(arrow3))
		play(FadeIn(wave3))
		wait(0.5)

		#* ultraviolet/short wavelength
		arrow1 = self.get_indicator(axes.c2p(300,12), -105*DEGREES, 1.5)
		wave1.next_to(arrow1, UP)
		play(GrowArrow(arrow1))
		play(FadeIn(wave1))

		wait(3)
		play(FadeOut(bg_img), FadeOut(arrow), FadeOut(wave1), FadeOut(arrow1), FadeOut(wave3), FadeOut(arrow3))
		self.remove(bg_img_mask)

		play(curve_terra.a.set_stroke(width=8), run_time=1.5)
		wait(2)
		play(curve_terra.a.set_stroke(width=5), run_time=1.5)

		wait(3)

		temp = VGroup(
			Text('温度', font=文楷),
			Tex('T').scale(1.4)
		).set_color(RED_B).scale(1.2)
		temp[0].set_color(RED_A)
		temp[1].add_updater(lambda m: m.next_to(temp[0],RIGHT,buff=0.15).shift(DOWN*0.05))
		temp.move_to(RIGHT*3.5+UP*2.5)

		arrow1 = Arc(PI/2,PI/6,4).add_tip().set_stroke(width=8)
		arrow2 = arrow1.copy().rotate(PI)
		VGroup(arrow1, arrow2).rotate(30*DEGREES).move_to(axes.c2p(1300,50))
		arrow1.shift(UL*0.2+DL*0.2)
		arrow2.scale(1.2).shift(DR*0.4+DL*0.0)
		self.stop_skipping()
		play(FadeIn(temp))
		wait(0.5)
		play(Create(arrow1))
		wait(2)
		play(Create(arrow2))
		wait(2)
		play(*[FadeOut(m) for m in [temp, arrow1, arrow2]])
		wait()

#* This scene is unused.
class SpectrumAndTemperature(StarskyScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)

		# shortcuts
		global add, play, wait, narrate
		add = self.add
		play = self.play
		wait = self.wait
		narrate = self.narrate
		Mobject.a = Mobject.animate

	def construct(self) -> None:
		left = Text('谱',font=文楷).scale(2).set_color(RED_A)
		left.shift(LEFT*FRAME_WIDTH/4)

		right = VGroup(
			Text('温度',font=文楷).scale(1.8),
			Tex('T').scale(3)
		).arrange(RIGHT, buff=0.4).shift(RIGHT*FRAME_WIDTH/4).shift(RIGHT*0.5)
		right.set_color(RED_B)
		right[1].set_color(RED)

		delim = Line(UP*FRAME_HEIGHT, DOWN*FRAME_HEIGHT).set_stroke(GREY_B,2,0.3)
		conn = Tex('\\Longleftrightarrow').scale(4).stretch(0.8,YDIM)

		#add(left, right, delim, conn)
		self.camera.frame.shift(RIGHT*0.3)
		self.stop_skipping()
		play(FadeIn(left))
		play(FadeIn(delim),Write(conn), rate_func=linear)
		play(Write(right), run_time=1.5)
		wait(5)

class KirhoffRadiationLaw(StarskyScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)

		# shortcuts
		global add, play, wait, narrate
		add = self.add
		play = self.play
		wait = self.wait
		narrate = self.narrate
		Mobject.a = Mobject.animate
	
	def construct(self) -> None:
		kirhoff = ImageMobject('../assets/Kirchhoff.jpg')
		kirhoff.scale(1.3)
		kirhoff.shift(UP*0.3)
		caption = Text('Kirhhoff, (1824-1887)').scale(0.8).add_updater(lambda m: m.next_to(kirhoff, DOWN))
		#kirhoff.scale()

		play(FadeIn(kirhoff, scale=1.1, rate_func=linear), Write(caption))
		
		
		#* ----------------------------------------------------------------- *#
		#* 定理文本
		#* ----------------------------------------------------------------- *#
		self.stop_skipping()
		title = Text('基尔霍夫辐射定律',font='Smiley Sans').scale(1.1)
		txt = VGroup(
			Text('物体的辐射能力', font=文楷),
			Text('正比于', font=文楷),
			Text('它对电磁波的吸收能力', font=文楷)
		).scale(0.8)
			
		txt[0][-4:].set_color(YELLOW_A)
		txt[2][-4:].set_color(RED_B)

		txt[0].arrange(RIGHT, buff=0.1)
		txt[1].arrange(RIGHT, buff=0.2)
		txt[2].arrange(RIGHT, buff=0.1)
		txt.arrange(DOWN).shift(UP*0.4)

		txt.shift(RIGHT*FRAME_WIDTH/5)
		title.move_to(RIGHT*FRAME_WIDTH/5+UP*2.7)
		bloom = VHighlight(txt[0][-4:],
					  color_bounds=[YELLOW, BG_COLOR], 
					  max_stroke_addition=15).set_stroke(opacity=0.15)
		
		play(kirhoff.a.shift(LEFT*FRAME_WIDTH/4.5) ,Write(title, time_span=[0.5,2]))
		wait(0.5)
		self.bring_to_back(bloom)
		play(Write(txt[0], run_time=2), FadeIn(bloom, time_span=[1,2]))
		txt[0].add(bloom)
		#wait(0.5)
		play(Write(txt[1]))
		#wait(0.5)
		play(Write(txt[2]), run_time=2)
		wait(6)

		#* ----------------------------------------------------------------- *#
		#* Object showcase
		#* ----------------------------------------------------------------- *#
		radius = 1
		obj = Circle(radius=radius).set_stroke(RED, 4, 1) \
						.set_fill(RED, 0.3)
		obj.next_to(txt, DOWN, buff=0.6).shift(LEFT*0.6)

		
		play(FadeIn(obj, 0.2*UP), txt.a.shift(0.3*UP).set_anim_args(time_span=[0.5,1.5]))

		O = obj.get_center()
		A = obj.get_right()
		length = 1.4
		kw = dict( tip_width_ratio=2.5, width_to_tip_len = 0.02, max_width_to_length_ratio=100)
		arr_in = Arrow(A+RIGHT*length, A, **kw)
		arr_in.set_stroke(width=5)
		arr_in.rotate(PI/6, about_point=O)
		
		arr_out = Arrow(A, A+RIGHT*length, **kw)
		arr_out.set_stroke(width=5)
		arr_out.rotate(-PI/6, about_point=O)

		txt_in =  Text('吸收', font=文楷).scale(0.6).next_to(arr_in, RIGHT, buff=0.2).shift(UP*0.3)
		txt_out = Text('辐射', font=文楷).scale(0.6).next_to(arr_out, RIGHT, buff=0.2).shift(DOWN*0.3)

		txt_in.set_color(RED_B)
		arr_in.set_color(RED_B)
		txt_out.set_color(YELLOW_B)
		arr_out.set_color(YELLOW_B)

		arr_in.set_stroke(width=8)
		arr_out.set_stroke(width=8)
		#add(arr_in, arr_out, txt_in, txt_out)
		play(GrowArrow(arr_in), GrowFromCenter(arr_out), FadeIn(txt_in), FadeIn(txt_out))
		wait()
		play(arr_in.a.set_stroke(width=20))
		wait()
		play(arr_out.a.set_stroke(width=20), obj.a.set_stroke(RED_A).set_fill(RED_B, 0.6))
		wait(2)
		play(arr_in.a.set_stroke(width=5))
		wait()
		play(arr_out.a.set_stroke(width=5), obj.a.set_stroke(RED_E, opacity=0.4).set_fill(RED_D, 0.3))

class VariousFormulas(BlackbodySpectrumScene):
	'''黑体辐射的各种公式激荡碰撞的时候'''
	def construct(self) -> None:
		#* ----------------------------------------------------------------- *#
		#* axes
		#* ----------------------------------------------------------------- *#

		axes, label_x, label_y = self.construct_axes()
		axes: DataAxes
		
		#if self.skip_animations and self.in_dev():
		#	add(axes, label_x, label_y)
		#else:
		#	axes_fadein_animation = self.get_advanced_axes_fadein_animation(
		#		axes, label_x, label_y, run_time_param=2)
		#	play(*axes_fadein_animation)
		#	add(axes, label_x, label_y)
		add(axes, label_x, label_y) # 没有一开始的需求，直接 
		
		#* ----------------------------------------------------------------- *#
		#* curve
		#* ----------------------------------------------------------------- *#
		curve_planck = axes.plot(bbrad.Planck,        [  1, 4000, 10], attach=False, dynamic=True)
		curve_wien   = axes.plot(bbrad.Wien,          [  1, 4000, 10], attach=False, dynamic=True)
		curve_rj     = axes.plot(bbrad.ReighleyJeans, [100, 5000, 10], attach=False, dynamic=True)
		
		data_min = bbrad.get_exp_data_range()[0]
		curve_space  = axes.plot(bbrad.exp_space, [data_min, 2000, 10], attach=False, dynamic=True)
		curve_terra  = axes.plot(bbrad.exp_terra, [data_min, 2000, 10], attach=False, dynamic=True)
		curve_space.set_color(YELLOW_B)
		curve_terra.set_color(GREEN_C)
		
		temperature = ValueTracker(5777)
		def planck_T_controller(curve):
			bbrad.set_temperature(temperature.get_value())
		temperature.add_updater(planck_T_controller)

		#add(curve_planck, curve_wien, curve_rj, peak)
		#add(curve_planck, curve_space, curve_terra)
		
		#* ----------------------------------------------------------------- *#
		#* formulas construction
		#* ----------------------------------------------------------------- *#
		
		var = ['c','h','k','T','\lambda']
		fml_planck = Tex(r'W_{\mathrm{Planck}}(\lambda,T)='+bbrad.tex_planck, isolate=var)
		fml_wien   = Tex(r'W_{\mathrm{Wien}}(\lambda,T)='+bbrad.tex_wien,isolate=var)
		fml_rj     = Tex(r'W_{\mathrm{RJ}}(\lambda,T)='+bbrad.tex_rj,isolate=var)
		all_fml = VGroup(fml_planck, fml_wien, fml_rj)
		for fml in all_fml:
			fml.scale(0.8).set_color(FML_COLOR)
			#fml['c'].set_color(YELLOW_A)
			#fml['h'].set_color(YELLOW_A)
			#fml['k'].set_color(YELLOW_A)
			fml[r'\lambda'].set_color(BLUE)
			fml['T'].set_color(RED_B)
		
		fml_planck[19].set_color(BLUE)
		fml_wien  [17].set_color(BLUE)
		fml_rj    [13].set_color(BLUE)
		
		all_fml.arrange(DOWN)
		#add(all_fml)
		fml = fml_planck # shortcut

		#* ----------------------------------------------------------------- *#
		# 先推导出Wien公式
		#* ----------------------------------------------------------------- *#
		X = [200,300,400,600,1000,1400,1700,2000,2500,3000,3500]
		Y = [bbrad.Planck(x) for x in X]
		dots = axes.scatter(X,Y)
		add(dots)
		curtain = Curtain()
		add(curtain)

		check = Check().scale(0.4)
		cross = Cross().scale(0.4)
		#add(check, cross)

		if not self.skip_animations:
			fml_wien.center()
			play(FadeIn(fml_wien, LEFT), run_time=2)
			wait()
	
			self.bring_to_back(curve_wien)
			play(
				fml_wien.a.move_to(RIGHT*3+UP*1.5).scale(1.2),
				FadeOut(curtain, time_span=[0,1]), 
				Create(curve_wien, rate_func=lambda t: t**2, time_span=[0,2]), 
			)
			wait()
	
			arrow1 = self.get_indicator(axes.c2p(300,bbrad.Wien(300)), 195*DEGREES, 2, stroke_width=6).shift(DOWN*0.2+LEFT*0.2)
			arrow2 = self.get_indicator(axes.c2p(1400,bbrad.Wien(1400)), 160*DEGREES, 2, stroke_width=6, buff=MED_SMALL_BUFF).shift(UP*0.1)
			check.next_to(arrow1.get_start(), UP)
			cross.next_to(arrow2.get_start())
			#add(arrow1, arrow2)
			play(GrowArrow(arrow1), FadeIn(check, time_span=[0.5,1.5]))
			wait(2)
			play(GrowArrow(arrow2), FadeIn(cross, time_span=[0.5,1.5]))
			wait()
			
			play(*[FadeOut(m) for m in [arrow1, arrow2, check, cross]])
	
			play(FadeIn(curtain))
			self.remove(curve_wien, fml_wien)
			fml_wien.scale(1/1.2)
			wait(5)

		else: # skip animations
			pass

		#* ----------------------------------------------------------------- *#
		# 接下来推导出RJ公式~
		#* ----------------------------------------------------------------- *#
		self.stop_skipping()
		if not self.skip_animations:
			fml_rj.center()
			play(FadeIn(fml_rj, LEFT+UP), run_time=2)
			wait()
	
			self.bring_to_back(curve_rj)
			play(
				fml_rj.a.move_to(RIGHT*4+UP*3).set_anim_args(run_time=2),
				FadeOut(curtain, time_span=[0.5,1.5]),
				Create(curve_rj, time_span=[0, 4]), 
			)
			wait()
	
			axes.plots.remove(dots)
			play(axes.a.set_range('x',[0,4000]).set_anim_args(recursive=True), fml_rj.a.shift(DOWN*1.5+LEFT*1.3).scale(1.3))
			wait(.5)
			
			arrow2 = self.get_indicator(axes.c2p(800,55), -20*DEGREES, 2, stroke_width=6).shift(DOWN*0.2+LEFT*0.2)
			arrow1 = self.get_indicator(axes.c2p(2750,bbrad.ReighleyJeans(2750)), 160*DEGREES, 2, stroke_width=6, buff=MED_SMALL_BUFF).shift(UP*0.1)
			check.next_to(arrow1.get_start(),UP).shift(RIGHT*0.2 )
			cross.move_to(axes.c2p(800,60))
			play(GrowArrow(arrow1), FadeIn(check, time_span=[0.5,1.5]))
			wait(2)
			play(GrowArrow(arrow2), FadeIn(cross, time_span=[0.5,1.5]))
			wait()
			play(*[FadeOut(m) for m in [arrow1, arrow2, check, cross]])
	
			play(FadeIn(curtain))
			self.remove(curve_rj, fml_rj)
			fml_rj.scale(1/1.3)
			wait(5)

		else: # skip animations
			pass

		#* ----------------------------------------------------------------- *#
		#* 最后合体出Planck公式
		#* ----------------------------------------------------------------- *#
		
		
		# 还原坐标系范围
		axes.set_range('x',[0,2000])
		fml_wien.move_to(LEFT*FRAME_WIDTH/4.5)
		fml_rj.move_to(RIGHT*FRAME_WIDTH/4.5)
		fml_planck.center().shift(UP).scale(1.2)
		fml_planck[0].set_color(YELLOW)
		fml_planck[1:7].set_color(YELLOW_B)
		# add(fml_wien, fml_rj) #, fml_planck)

		play(FadeIn(fml_wien), FadeIn(fml_rj, time_span=[0.5,1.5]))
		wait(3)
		play(
			FadeOut(fml_wien, fml_planck.get_center()-fml_wien.get_center()), 
			FadeOut(fml_rj,   fml_planck.get_center()-fml_rj  .get_center()),
			FadeIn(fml_planck, shift=UP*0.2, time_span=[0.5,1.5]),
			run_time=2
		)
		self.remove(fml_wien, fml_rj, fml_planck); add(fml_planck)
		wait()
		#add(fml_wien, fml_rj, fml_planck)
		term2 = fml_planck[20:]
		highlight = SurroundingRectangle(term2)
		
		play(Create(highlight))
		wait(0.5)
		play(FadeOut(highlight))
		
		wait(2) # 其貌不扬，看上去复杂得不像一个正经物理公式...
		self.stop_skipping()
		self.bring_to_back(curve_planck)
		play(
			fml_planck.a.move_to(RIGHT*2.8+UP*1.5),
			FadeOut(curtain, time_span=[1,2]),
			Create(curve_planck, rate_func=lambda t: t**2, time_span=[1,4]), 
		)
		wait(0.5)
		bloom = VHighlight(curve_planck, color_bounds=[YELLOW_A, BG_COLOR], max_stroke_addition=15)
		bloom.set_stroke(opacity=0.15)
		self.bring_to_back(bloom)
		play(
			FadeIn(bloom),
			curve_planck.a.set_stroke(YELLOW),
			rate_func=emphasize(0.5,0.5),
			run_time=1.5
		)

		wait(5)
		return #* END OF SCENE *# 

class UnknownFormula(BlackbodySpectrumScene):
	'''黑体辐射的各种公式激荡碰撞的时候'''
	def construct(self) -> None:
		#* ----------------------------------------------------------------- *#
		#* axes
		#* ----------------------------------------------------------------- *#

		axes, label_x, label_y = self.construct_axes()
		axes: DataAxes
		
		#if self.skip_animations and self.in_dev():
		#	add(axes, label_x, label_y)
		#else:
		#	axes_fadein_animation = self.get_advanced_axes_fadein_animation(
		#		axes, label_x, label_y, run_time_param=2)
		#	play(*axes_fadein_animation)
		#	add(axes, label_x, label_y)
		add(axes, label_x, label_y) # 没有一开始的需求，直接 
		
		#* ----------------------------------------------------------------- *#
		#* curve
		#* ----------------------------------------------------------------- *#
		curve_planck = axes.plot(bbrad.Planck,        [  1, 4000, 10], attach=False, dynamic=True)
		curve_wien   = axes.plot(bbrad.Wien,          [  1, 4000, 10], attach=False, dynamic=True)
		curve_rj     = axes.plot(bbrad.ReighleyJeans, [100, 5000, 10], attach=False, dynamic=True)
		
		data_min = bbrad.get_exp_data_range()[0]
		curve_space  = axes.plot(bbrad.exp_space, [data_min, 2000, 10], attach=False, dynamic=True)
		curve_terra  = axes.plot(bbrad.exp_terra, [data_min, 2000, 10], attach=False, dynamic=True)
		curve_space.set_color(YELLOW_B)
		curve_terra.set_color(GREEN_C)
		
		temperature = ValueTracker(5777)
		def planck_T_controller(curve):
			bbrad.set_temperature(temperature.get_value())
		temperature.add_updater(planck_T_controller)

		#add(curve_planck, curve_wien, curve_rj, peak)
		#add(curve_planck, curve_space, curve_terra)
		
		#* ----------------------------------------------------------------- *#
		#* formulas
		#* ----------------------------------------------------------------- *#
		
		var = ['c','h','k','T','\lambda']
		fml_unknown = Tex(r'W_{??}(\lambda,T)=??', isolate=var)
		fml_wien   = Tex(r'W_{\mathrm{Wien}}(\lambda,T)='+bbrad.tex_wien,isolate=var)
		fml_rj     = Tex(r'W_{\mathrm{RJ}}(\lambda,T)='+bbrad.tex_rj,isolate=var)
		all_fml = VGroup(fml_unknown, fml_wien, fml_rj)
		for fml in all_fml:
			fml.scale(0.8).set_color(FML_COLOR)
			#fml['c'].set_color(YELLOW_A)
			#fml['h'].set_color(YELLOW_A)
			#fml['k'].set_color(YELLOW_A)
			fml[r'\lambda'].set_color(BLUE)
			fml['T'].set_color(RED_B)
		
		fml_unknown[4].set_color(BLUE)
		fml_wien  [17].set_color(BLUE)
		fml_rj    [13].set_color(BLUE)
		
		all_fml.arrange(DOWN)
		#add(all_fml)
		fml = fml_unknown # shortcut

		#* ----------------------------------------------------------------- *#
		# 先推导出Wien公式~
		#* ----------------------------------------------------------------- *#
		X = [200,300,400,600,1000,1400,1700,2000,2500,3000,3500]
		Y = [bbrad.Planck(x) for x in X]
		dots = axes.scatter(X,Y)
		add(dots)
		curtain = Curtain()
		add(curtain)

		#* ----------------------------------------------------------------- *#
		#* 最后合体出Planck公式
		#* ----------------------------------------------------------------- *#
		
		# 还原坐标系范围
		axes.set_range('x',[0,2000])
		fml_wien.move_to(RIGHT*FRAME_WIDTH/4.5)
		fml_rj.move_to(LEFT*FRAME_WIDTH/4.5)
		fml_unknown.center().shift(UP).scale(1.4)

		self.stop_skipping()
		play(FadeIn(fml_rj), FadeIn(fml_wien, time_span=[0.5,1.5]))
		wait(2.5)
		play(
			FadeOut(fml_wien, fml_unknown.get_center()-fml_wien.get_center()), 
			FadeOut(fml_rj,   fml_unknown.get_center()-fml_rj  .get_center()),
			FadeIn(fml_unknown, shift=UP*0.2, time_span=[0.5,1.5]),
			run_time=2
		)
		self.remove(fml_wien, fml_rj, fml_unknown); add(fml_unknown)
		wait()
		
		self.stop_skipping()
		self.bring_to_back(curve_wien, curve_rj, curve_planck)
		curve_wien.set_stroke(width=4, opacity=0.2)
		curve_rj.set_stroke(width=4, opacity=0.2)
		play(
			fml_unknown.a.move_to(RIGHT*2.8+UP*1.5),
			FadeOut(curtain, time_span=[0,1]),
			Create(curve_planck, rate_func=lambda t: t**2), 
		)
		wait(0.5)

		wait(5)
		return #* END OF SCENE *# 

class HypothesisBehindPlanckLaw(StarskyScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)
		
		# shortcuts
		global add, play, wait, narrate
		add = self.add
		play = self.play
		wait = self.wait
		narrate = self.narrate
		Mobject.a = Mobject.animate

	def construct(self) -> None:
		#* ----------------------------------------------------------------- *#
		#* construct elements
		#* ----------------------------------------------------------------- *#

		#* ----------------------------------------------------------------- *#
		#* 两条假设的文字 
		#* ----------------------------------------------------------------- *#
		hypo1 = VGroup(
			Text('1.'),
			Text('光的能量不是连续传输的，', font=文楷).scale(0.8),
			Text('而是一份一份地被发出和吸收', font=文楷).scale(0.8),
		).arrange(DOWN)
		hypo2 = VGroup(
			Text('2.'),
			Text('光的能量小包正比于光的频率', font=文楷).scale(0.8),
			Tex('E=h\\nu').scale(1.5)
		).arrange(DOWN,buff=0.4)

		hypotheses = VGroup(hypo1, hypo2)

		hypo1[0].align_on_border(LEFT,buff=3).align_to(hypo1[1],DOWN)
		hypo1[1].next_to(hypo1[0],RIGHT,buff=0.4)
		hypo2[0].align_on_border(LEFT,buff=3).align_to(hypo2[1],DOWN)
		hypo2[1].next_to(hypo2[0],RIGHT,buff=0.4)
		hypo2[2].shift(DOWN*0.5)

		hypotheses.arrange(DOWN,buff=3).align_on_border(LEFT,buff=3)
		# 加一点颜色
		hypo2[1][0:4].set_color(YELLOW)
		hypo2[1][-4:].set_color(ORANGE)
		fml = hypo2[-1]
		fml[0].set_color(YELLOW)
		fml[-1].set_color(ORANGE)
		
		#add(hypotheses)

		#* ----------------------------------------------------------------- *#
		#* 带渐变的冷热物体
		#* ----------------------------------------------------------------- *#
		ls = []
		nr_layers = 10
		for i in range(nr_layers):
			fac = i/nr_layers
			radius = 0.5*(1-fac)
			#color = interpolate_color(RED, YELLOW, 1/(((1-fac)*1.5)**2+0.9**2))
			color = interpolate_color(RED, YELLOW, (fac**(1/2))/1.3)
			ls.append(Circle(radius=radius, fill_color=color, fill_opacity=1, stroke_opacity=0))
		hot_obj = VGroup(*ls)
		hot_obj.shift(LEFT*4+UP*0.3)
		#add(hot_obj)

		ls = []
		for i in range(nr_layers):
			fac = i/nr_layers
			radius = 0.5*(1-fac)
			color = interpolate_color(BLUE, interpolate_color(BLUE_E,BLACK,0.4), fac**(1/4))
			ls.append(Circle(radius=radius, fill_color=color, fill_opacity=1, stroke_opacity=0))
		
		cold_obj = VGroup(*ls)
		cold_obj.shift(RIGHT*4+UP*0.3)
		#add(cold_obj)

		#* ----------------------------------------------------------------- *#
		#* 带辉光的波包
		#* ----------------------------------------------------------------- *#

		def gen_wavelet_func(A,σ,k,φ):
			def wavelet_func(x):
				y = A*np.exp(-(x/σ)**2)*np.cos(x*k+φ)
				return RIGHT*x + UP*y
			return wavelet_func
		
		#* 提前声明参数，最终变成关键帧动画了...
		scene_time = ValueTracker(0)
		def time_update(m, dt):
			m.set_value(m.get_value()+dt)
		scene_time.add_updater(time_update)
		add(scene_time)
		anim0 = ValueTracker(0)
		anim1 = ValueTracker(0)
		anim2 = ValueTracker(0)
		anim3 = ValueTracker(0)

		#* 正弦波
		wave_vel = 0.6
		wave_anchor = (cold_obj.get_center()+hot_obj.get_center())/2
		def sin_wavefunc(t):
			x = t
			k = w = 2*PI
			w *= wave_vel # well, not really "canonical" way to constructing it.
			y = np.cos(k*x-w*scene_time())
			return RIGHT*x + 0.5*UP*y + wave_anchor
		left = hot_obj.get_right()[0]; right = cold_obj.get_left()[0]
		primitive = ParametricCurve(sin_wavefunc, [left,right,0.05], color=YELLOW)
		primitive.add_updater(lambda m: m.set_points(ParametricCurve(sin_wavefunc, [left,right,0.05]).get_points()))
		primitive.max_alpha = 1
		primitive.add_updater(lambda m: m.set_stroke(opacity=m.max_alpha * anim0() * (1-anim1())))
		
		#* 辉光
		ls = []
		for i in range(6):
			stroke_width = map_range(i, 0, 5, 20, 4)
			stroke_opacity= map_range(i, 0, 5, 0, 1)
			stroke_opacity=interpolate(0,.4,(i/5))
			stroke_color = interpolate_color(YELLOW, WHITE, i/5)
			# 注意把updater也copy过来了，所以辉光能跟着波包走
			m = primitive.copy().set_stroke(stroke_color,stroke_width,stroke_opacity)
			m.max_alpha = primitive.max_alpha * stroke_opacity
			ls.append(m)
			
		primitive.set_color(YELLOW).set_stroke(width=4)
		sin_wave = VGroup(*ls,primitive)
		add(sin_wave)

		#* 正弦波两边的渐隐效果
		curt_left  = SurroundingRectangle(sin_wave).set_fill(BG_COLOR,1).set_stroke(width=1,color=WHITE)
		curt_right = curt_left.copy()
		curt_left.set_width(2,stretch=True).align_to(sin_wave,LEFT).shift(LEFT*0.05)
		curt_right.set_width(2,stretch=True).align_to(sin_wave,RIGHT).shift(RIGHT*0.05)
		bg_color = [1/8]*3 #222222
		rgba_trans = [*bg_color,0]; rgba_solid = [*bg_color,1]
		# 3 = nr_points_per_curve_node
		curt_left.set_rgba_array(
			[rgba_trans]*3 + [rgba_solid]*3 + [rgba_solid]*3 + [rgba_trans]*3
		)
		curt_right.set_rgba_array(
			[rgba_solid]*3 + [rgba_trans]*3 + [rgba_trans]*3 + [rgba_solid]*3
		)

		self.bring_to_back(curt_left, curt_right)
		self.bring_to_back(sin_wave)

		#* ----------------------------------------------------------------- *#
		#* 离散的能量小块
		#* ----------------------------------------------------------------- *#
		def get_wavelet(fac):
			ampl = 0.3*map_range(fac**2, 0,1, 0.4, 1.3)
			sig  = 0.3*map_range(fac,    0,1, 0.5, 1  )
			freq = 30* map_range(fac,    0,1, 0.4, 2.5)
			phase= TAU*fac
			width=     map_range(fac,    0,1, 0.1, 0.6)
			
			wavelet = ParametricCurve(gen_wavelet_func(ampl,sig,freq,phase), 
							 			[-width,width,0.01], color=BLUE)
			
			rgb = wavelength_to_rgb(map_range(fac, 0,1, 780,380))
			h,s,v = rgb_to_hsv(rgb)
			s -= 0.5
			v  = clip(v+0.4,0,1)
			rgb = hsv_to_rgb(h,s,v)
			color = rgb_to_hex(rgb)

			wavelet.set_stroke(color=color, width=2)
			return wavelet
		
		interval = 1
		wave_packet = Square(0.5).set_fill(YELLOW,1).set_stroke(width=0)
		wave_packets = (wave_packet*6)
		np.random.seed(2233)
		for i in range(6):
			wave_packets[i].shift(LEFT*interval*i)
			wave_packets[i].rand = np.random.rand()
		wave_packets.move_to((hot_obj.get_right()+cold_obj.get_left())/2)

		# simulation nodes 名字取自 blender；实际上是一个updater
		def wavepacket_sim_nodes(m, dt):
			# 1. move
			m.shift(RIGHT*wave_vel*dt)
			
			# 2. annihilate
			for sub in m: # loop every sub, not just m[0], for stability
				if abs(sub.get_center()[0] - cold_obj.get_center()[0])<0.4:
					m.remove(sub)
			# 3. create
			if abs(m[-1].get_center()[0] - hot_obj.get_center()[0])>interval:
				m.add(m[-1].copy().shift(LEFT*interval))
				m[-1].rand = np.random.rand()
				m[-1]._has_wavelet = False

			# 4. fade on boundary
			lb = hot_obj.get_right()[0]
			rb = cold_obj.get_left()[0]

			fade_dist = 0.1
			for square in m:
				alpha = 1
				if   (dist := clip(square.get_center()[0] - lb, 0,1)) < fade_dist:
					alpha = dist/fade_dist
				elif (dist := clip(rb - square.get_center()[0], 0,1)) < fade_dist:
					alpha = dist/fade_dist
				square.set_fill(opacity=alpha*(anim1())*(1-anim3()))
				
				scale = map_range(square.rand, 0,1, 0.2,1.6)
				scale = 0.5*interpolate(1,scale,anim2())
				square.rescale_to_fit(scale,XDIM)

			return m

		wave_packets.add_updater(wavepacket_sim_nodes)
		add(wave_packets)

		#* wavelets
		wavelets = VGroup()
		def follow_packets(m):
			# 1. create
			for square in wave_packets:
				if not hasattr(square,'_has_wavelet') or square._has_wavelet==False:
					wavelet = get_wavelet(square.rand)
					color = wavelet.get_stroke_color()
					bloom = VHighlight(wavelet, 
						color_bounds = (color,BG_COLOR),
						max_stroke_addition=15*fac
					)
					for layer in bloom:
						layer.max_opacity = 0.15
					wavelet = VGroup(bloom,wavelet)
					wavelet.father = square
					square._has_wavelet = True
					wavelet.move_to(square)
					wavelets.add(wavelet)
			# 2. annihilate
			for wavelet in wavelets:
				if wavelet.father not in wave_packets:
					wavelets.remove(wavelet)
				wavelet.move_to(wavelet.father)
			
			# 3. set opacity
			for sub in wavelets.get_family():
				alpha = anim3()
				if hasattr(sub,'max_opacity'):
					alpha*=sub.max_opacity

				sub.set_stroke(opacity=alpha)
				
		wavelets.add_updater(follow_packets)
		add(wavelets)
		
		#* ----------------------------------------------------------------- *#
		#* Now Animation!
		#* ----------------------------------------------------------------- *#
		
		# '1.'
		play(Write(hypo1[0]),run_time=0.5)
		wait(0.5)
		play( #'光的能量不是连续传输的，'
			Write(hypo1[1],run_time=2),
			FadeIn(hot_obj),FadeIn(cold_obj),
			anim0.a.set_value(1).set_anim_args(time_span=[0.5,2]),
		)
		wait(0.5)
		#self.stop_skipping()
		play( #'而是一份一份地被发出和吸收'
			Write(hypo1[2],run_time=2),
			anim1.a.set_value(1).set_anim_args(time_span=[0.5,2]))
		wait(2)
		narrate('这种能量小包被普朗克称为qt，即量子')

		# '2.'
		play(Write(hypo2[0],run_time=0.5))
		play( #'光的能量小包正比于光的频率'
			Write(hypo2[1],run_time=2),
		)
		wait(0.5)
		play(anim2.a.set_value(1).set_anim_args(time_span=[0,1.5]))
		
		play(Write(hypo2[2],run_time=1))
		wait(1.5)
		play(anim3.a.set_value(1),run_time=1.5)

		wait(20)
		
class MyDashedLine(VGroup):
	def __init__(
		self,
		start = LEFT,
		end = RIGHT,
		dash_length = DEFAULT_DASH_LENGTH,
		positive_space_ratio = 0.5,
		**kwargs
	):
		super().__init__()

		dir = normalize(end - start)
		leng= get_norm(end - start)
		t = 0
		interval = dash_length/positive_space_ratio
		while t<leng:
			self.add(Line(
				start+dir*t, 
				start+dir*min(leng, t+dash_length),
				**kwargs
			))
			t += interval

class PlanckLawExplanation(BlackbodySpectrumScene):
	'''The most complicated scene, perhaps'''
	def construct(self) -> None:
		#* ----------------------------------------------------------------- *#
		#* axes
		#* ----------------------------------------------------------------- *#

		axes, label_x, label_y = self.construct_axes(ylim=100)
		
		if self.skip_animations and self.in_dev():
			add(axes, label_x, label_y)
		else:
			axes_fadein_animation = self.get_advanced_axes_fadein_animation(
				axes, label_x, label_y, run_time_param=2)
			play(*axes_fadein_animation)
			add(axes, label_x, label_y)
			wait()
		
		#self.stop_skipping()

		#* ----------------------------------------------------------------- *#
		#* curve
		#* ----------------------------------------------------------------- *#
		curve_planck = axes.plot(bbrad.Planck,        [  1, 2000, 10], attach=False, dynamic=True)
		curve_wien   = axes.plot(bbrad.Wien,          [  1, 2000, 10], attach=False, dynamic=True)
		curve_rj     = axes.plot(bbrad.ReighleyJeans, [100, 2000, 10], attach=False, dynamic=True)
		
		data_min = bbrad.get_exp_data_range()[0]
		curve_space  = axes.plot(bbrad.exp_space, [data_min, 2000, 10], attach=False, dynamic=True)
		curve_terra  = axes.plot(bbrad.exp_terra, [data_min, 2000, 10], attach=False, dynamic=True)
		curve_space.set_color(YELLOW_B)
		curve_terra.set_color(GREEN_C)
		
		temperature = ValueTracker(6000)
		def planck_T_controller(curve):
			bbrad.set_temperature(temperature.get_value())
		temperature.add_updater(planck_T_controller)

		#add(curve_planck, curve_wien, curve_rj, peak)
		#add(curve_planck, curve_space, curve_terra)
		
		#* ----------------------------------------------------------------- *#
		#* construct formulas
		#* ----------------------------------------------------------------- *#
		
		var = ['c','h','k','T','\lambda']
		fml_planck = Tex(r'W_{\mathrm{planck}}(\lambda,T)='+bbrad.tex_planck, isolate=var)
		fml_wien   = Tex(r'W_T(\lambda)='+bbrad.tex_wien,isolate=var)
		fml_rj     = Tex(r'W_T(\lambda)='+bbrad.tex_rj,isolate=var)
		all_fml = VGroup(fml_planck, fml_wien, fml_rj)
		for fml in all_fml:
			fml.scale(0.8).set_color(FML_COLOR)
			#fml['c'].set_color(YELLOW_A)
			#fml['h'].set_color(YELLOW_A)
			#fml['k'].set_color(YELLOW_A)
			fml[r'\lambda'].set_color(BLUE)
			#fml['T'].set_color(RED_B)
		
		fml = fml_planck # shortcut
		#fml_planck[9].set_color(YELLOW)
		fml_planck[0].set_color(YELLOW)
		fml_planck[1:7].set_color(YELLOW_A)
		fml_planck[7].set_color(YELLOW_A)
		fml_planck[11].set_color(YELLOW_A)
		fml_planck[19].set_color(BLUE) #'^2'

		#* 在一开始的版本中隐藏对温度的依赖('T') (NOT implemented)
		#fml_planck[9:11].set_fill(FML_COLOR, 0)
		#fml_planck[:9].shift(RIGHT*0.42)

		all_fml.arrange(DOWN)
		#add(all_fml)

		fml_planck.move_to(RIGHT*2.5+UP*1.8)
		if self.skip_animations and self.in_dev():
			add(fml_planck, curve_planck)
		else:
			play(Write(fml_planck), Create(curve_planck))
			wait()

		term1 = fml_planck[13:20]
		term2 = fml_planck[20:]
		
		highlight = SurroundingRectangle(term1)
		if not (self.skip_animations and self.in_dev()):
			play(Create(highlight))
			wait(2)
			curve_term1 = axes.plot(bbrad.Planck, [1,2000,10], attach=False, dynamic=False)
			#play(Create(curve_term1))
			highlight.reverse_points()
			play(Uncreate(highlight))
			wait()

		highlight = SurroundingRectangle(term2)
		if not (self.skip_animations and self.in_dev()):
			play(Create(highlight))
			wait(2)
			highlight.reverse_points()
			play(Uncreate(highlight))
			wait()

			comp1 = fml_planck[23:30]
			comp2 = fml_planck[30:32]
			comp3 = fml_planck[20:22]
		
			play(comp1.a.set_color(YELLOW).set_stroke(width=3, color=YELLOW_A, opacity=0.7).scale(1.1), rate_func=there_and_back)
			play(comp2.a.set_color(YELLOW).set_stroke(width=3, color=YELLOW_A, opacity=0.7).scale(1.1), rate_func=there_and_back)
			play(comp3.a.set_color(YELLOW).set_stroke(width=3, color=YELLOW_A, opacity=0.7).scale(1.1), rate_func=there_and_back)
		
		#* ----------------------------------------------------------------- *#
		#* formula explanations(animation)
		#* ----------------------------------------------------------------- *#
		
		fml_qsum = Tex(r'\frac{1}{1-q}=1+q+q^2+q^3+\cdots', isolate=['q'], color=FML_COLOR).scale(0.8)
		fml_qsum.next_to(fml_planck, DOWN, buff=0.5)
		fml_qsum['q'].set_color(BLUE)
		if not (self.skip_animations and self.in_dev()):
			_term2 = term2.copy()
			play(TransformMatchingShapes(_term2, fml_qsum[:5]), FadeIn(fml_qsum[5:], time_span=[0.5,1.5]))
			self.remove(_term2); add(fml_qsum)
			wait()

		#self.stop_skipping()
		phy_line1 = Tex(r'\int e^{-h\nu/kT}\mathrm d \nu', isolate=[r'\nu','T'], color=FML_COLOR)
		phy_line2 = Tex(r'\sum_{n=0}^\infty e^{-nh\nu/kT}', isolate=[r'\nu','T','n'], color=FML_COLOR)
		phy_line3 = Tex(r'=\frac{1}{1-e^{-\frac{h\nu}{kT}}}', isolate=[r'\nu','T'], color=FML_COLOR)
		phy_line1[0].shift(UP*0.04)
		
		for tex in [phy_line1, phy_line2, phy_line3]:
			tex.scale(0.8)
			tex[r'\nu'].set_color(BLUE)
			tex[r'T'].set_color(RED_B)
		phy_line2['n'].set_color(YELLOW)
		phy_line3.next_to(phy_line2)

		VGroup(phy_line2, phy_line3).move_to(fml_qsum)
		phy_line1.move_to(phy_line2).shift(LEFT*0.1)
		if not (self.skip_animations and self.in_dev()):
			play(fml_qsum.a.set_opacity(0.1), Write(phy_line1,time_span=[0.8,1.8]))
			wait()
			play(FadeTransform(phy_line1, phy_line2))
			wait()
			play(Write(phy_line3))
			_start = phy_line3[1:].copy()
			wait()
			play(FadeTransform(_start, term2))
			self.remove(_start); add(term2)
			wait()
			play(*[FadeOut(m) for m in [phy_line2, phy_line3, fml_qsum]])
			wait()
		
		#self.stop_skipping()
		#return
		
		#* ----------------------------------------------------------------- *#
		#* 极限情况
		#* ----------------------------------------------------------------- *#
		
		towards_short = Tex(r'\to 0')
		towards_infty = Tex(r'\to \infty')
		xval = ValueTracker(600)
		func_dot = Dot(fill_color=YELLOW).add_updater(lambda m: m.move_to(axes.c2p(xval(), bbrad.Planck(xval()))))

		for tex in [towards_short, towards_infty]:
			tex.scale(0.8)
			tex.set_color(FML_COLOR)

		width = towards_infty.get_right()[XDIM] - towards_infty.get_left()[XDIM] + SMALL_BUFF
		left = fml_planck[:9]
		right = fml_planck[9:]
		towards_infty.next_to(left[-1], RIGHT, buff=SMALL_BUFF).shift(width*LEFT*0.7)

		#add(func_dot)
		func_dot.set_fill(opacity=0)
		if not (self.skip_animations and self.in_dev()):
			play(
				left.a.shift(width*LEFT*0.7), right.a.shift(width*RIGHT*0.3), 
				FadeIn(towards_infty, time_span=[0.5,1.5]),
				func_dot.a.set_fill(opacity=1).set_anim_args(suspend_mobject_updating=False),
				xval.a.set_value(1800).set_anim_args(time_span=[0.5,1.5])
			)
			wait(2)
		else:
			left.shift(width*LEFT*0.7); right.shift(width*RIGHT*0.3)
			xval.set_value(1800); func_dot.update()
			add(towards_infty, func_dot.set_fill(opacity=1))

		zero = Tex('0').scale(1.2)
		zero2= Tex('0').scale(1.2)
		infty= Tex('\\infty').scale(1.2)
		term1.refresh_bounding_box()
		zero.move_to(term1[4])
		if not (self.skip_animations and self.in_dev()):
			play(term1.a.fade(0.8),FadeIn(zero))
			wait()
		else:
			term1.fade(0.8); add(zero)

		term2.refresh_bounding_box()
		zero2.move_to(term2[1]) # 分数线的位置
		if not (self.skip_animations and self.in_dev()):
			play(term2.a.fade(0.8),FadeIn(zero2))
			wait()
		else:
			term2.fade(0.8); add(zero2)
		
		arrow_infty = self.get_indicator(axes.c2p(1800, bbrad.Planck(1800)), 180*DEGREES, 2.5)
		if not (self.skip_animations and self.in_dev()):
			play(GrowArrow(arrow_infty))
			wait()
		else:
			add(arrow_infty)
		

		#* lambda -> 0
		#play(left.a.shift(width*RIGHT*0.7), right.a.shift(width*LEFT*0.3), FadeIn(towards_short, time_span=[0.5,1.5]))
		delta = towards_short.get_right()[XDIM] - towards_short.get_left()[XDIM] + SMALL_BUFF - width
		towards_short.next_to(left[-1], RIGHT, buff=SMALL_BUFF).shift(delta*LEFT*0.7)
		if not (self.skip_animations and self.in_dev()):
			play(
				# 公式变化
				left.a.shift(delta*LEFT*0.7), right.a.shift(delta*RIGHT*0.3), 
				FadeTransform(towards_infty, towards_short),
				FadeOut(zero), FadeOut(zero2),
				term1.a.set_fill(opacity=1), term2.a.set_fill(opacity=1),
				# 指示箭头fadeout
				FadeOut(arrow_infty),
				# 函数珠子变化
				xval.a.set_value(100).set_anim_args(run_time=2)
			)
			wait()
		else:
			# 公式
			left.shift(delta*LEFT*0.7); right.shift(delta*RIGHT*0.3)
			self.remove(zero, zero2, towards_infty); add(towards_short)
			term1.set_fill(opacity=1); term2.set_fill(opacity=1)
			#
			self.remove(arrow_infty)
			#
			xval.set_value(100); func_dot.update()
			
		term1.refresh_bounding_box()
		term2.refresh_bounding_box()
		infty.move_to(term1[4]) # 分数线的位置
		zero2.move_to(term2[1])
		
		if not (self.skip_animations and self.in_dev()):
			play(FadeIn(infty), term1.a.fade(0.8))
			#wait()
			wait()
			play(FadeIn(zero2), term2.a.fade(0.8))
			wait()
			play(infty.a.scale(0.5), zero2.a.scale(1.3))
			#wait()
		else:
			add(infty, zero2)
			term1.fade(0.8); term2.fade(0.8)
			infty.scale(0.5); zero2.scale(1.3)
		

		self.stop_skipping()
		arrow_short = self.get_indicator(axes.c2p(100, bbrad.Planck(100)), 180*DEGREES, 2.5, buff=0.3)
		if not (self.skip_animations and self.in_dev()):
			play(GrowArrow(arrow_short), FadeOut(infty), zero2.a.shift(LEFT*0.5))
			wait()

			play(
				FadeOut(towards_short),
				FadeOut(infty), 
				FadeOut(zero2),
				term1.a.set_fill(opacity=1), term2.a.set_fill(opacity=1),
				left.a.shift(RIGHT*(width)*0.7)
			)
			wait()
		else:
			add(arrow_short)
			self.remove(infty, zero2, towards_short)
			term1.set_fill(opacity=1); term2.set_fill(opacity=1)
			left.shift(RIGHT*(width)*0.7)

		
		
		#* 中间的部分
		arrow_mid = self.get_indicator(axes.c2p(490, bbrad.Planck(490)), 0, 3.6, buff=0.8)

		# 构造主峰下的面积，比较费劲
		main_peak = Rectangle(height=10).set_fill(YELLOW_A, 1).set_stroke(BG_COLOR, 0, 0)
		peak_x = bbrad.Wien_displacement(temperature())
		main_peak.move_to(axes.c2p(peak_x, 0)).next_to(axes.c2p(peak_x, 0), UP, buff=0)
		main_peak.rescale_to_fit(3.5,XDIM,True).shift(RIGHT*0.04)

		# 魔改shader
		all_shaders = main_peak.get_shader_wrapper_list()
		frag_shader = filter(lambda sd: sd.shader_folder == 'quadratic_bezier_fill', all_shaders)
		frag_shader = list(frag_shader)[0]
		
		ORIGIN_SRC = "frag_color = color;"
		LP = main_peak.get_left()[XDIM]
		RP = main_peak.get_right()[XDIM]
		DT = 1.3
		GRAD_SRC = f''';
		float x = xyz_coords.x;
		float alpha = clamp(min(x-({LP}),-x+({RP}))/{DT}, 0, 1);
		frag_color = vec4(color.xyz, color.a*pow(alpha,4));'''
		
		frag_shader.replace_code(
			re.escape(ORIGIN_SRC),
			GRAD_SRC
		)

		mask = VMobject()
		curve_planck.update() # 只好出此下策
		mask.set_points(curve_planck.get_points())
		xmin, xmax = axes.x_axis.min, axes.x_axis.max
		ymin, ymax = axes.y_axis.min, axes.y_axis.max*5
		mask.add_points_as_corners([axes.c2p(xmax,ymax), axes.c2p(xmin,ymax), axes.c2p(xmin,ymin)])
		mask.set_fill(BG_COLOR, 1).set_stroke(width=0)

		#self.stop_skipping()
		if not (self.skip_animations and self.in_dev()):
			play(xval.a.set_value(bbrad.Wien_displacement(temperature())), FadeOut(arrow_short))
			play(term1.a.scale(1.2), term2.a.shift(RIGHT*0.1), run_time=0.7, rate_func=there_and_back)
			play(term2.a.scale(1.2), term1.a.shift(LEFT*0.14), run_time=0.7, rate_func=there_and_back)
			wait(0.5)
			play(GrowArrow(arrow_mid))
			wait(2)
		else:
			add(arrow_mid)
			self.remove(arrow_short)

		if not (self.skip_animations and self.in_dev()):
			#play(FadeOut(arrow_short), FadeOut(arrow_infty), arrow_mid.a.set_stroke(YELLOW).scale(1.2), FadeOut(func_dot))
			self.bring_to_back(mask); self.bring_to_back(main_peak)
			play(FadeIn(main_peak), FadeOut(func_dot))
			wait(2)

			play(
				FadeOut(arrow_mid),
				FadeOut(main_peak),
			)
		else:
			self.remove(arrow_infty, arrow_mid, arrow_short, func_dot)
		
		#self.stop_skipping()
		#* 为了一个特殊版加入的可将光谱图
		#* ----------------------------------------------------------------- *#
		#* 可见光颜色组成的背景
		#* ----------------------------------------------------------------- *#
		#bg_img, bg_img_mask = self.get_image_and_mask_under_curve(axes, curve_planck, dynamic=True)
		
		# handle object visible order
		#self.bring_to_back(bg_img_mask)
		#self.bring_to_back(bg_img)

		#* ----------------------------------------------------------------- *#
		#* 温度的影响
		#* ----------------------------------------------------------------- *#
		temp_text = VGroup(
			Tex('T=',color=FML_COLOR).scale(1.2),
			Integer(6000),
			Tex('\mathrm{K}').scale(1.2)
		).arrange(RIGHT)
		temp_text[0][0].set_color(RED_B)
		
		def text_geo_nodes(_):
			# text = temp_text[1]
			# kelvin = temp_text[2]
			temp_text[1].set_value(temperature())

			delta = temp_text[1][0].get_bottom()[YDIM] - temp_text[0][0].get_bottom()[YDIM]
			temp_text[1].shift(delta*DOWN).shift(DOWN*0.03)
			width = temp_text[1].get_right()[XDIM] - temp_text[1].get_left()[XDIM]
			temp_text[2].align_to(temp_text[0],DOWN).shift(DOWN*0.02) \
						.next_to(temp_text[0], RIGHT, buff=width+0.4, coor_mask = [1,0,0])
		temp_text.add_updater(text_geo_nodes)
		temp_text.next_to(fml_planck,DOWN,buff=MED_LARGE_BUFF).shift(RIGHT).shift(UP*0.4)

		if not (self.in_dev() and self.skip_animations):
			fml_planck.generate_target()
			fml_planck.target.shift(UP*0.4)
			fml_planck.target['T'].set_color(RED_B)
			play(MoveToTarget(fml_planck), FadeIn(temp_text, UP*0.2))
			wait(2)
		else:
			fml_planck.shift(UP*0.4)
			fml_planck['T'].set_color(RED_B)
			add(temp_text)
	
		peak_group = VGroup(
			VMobject(), VMobject(),
			Dot(fill_color=YELLOW_B),
			Polygon(ORIGIN, DL, DR).set_fill(RED, 1).set_stroke(width=0).scale(0.1),
			Polygon(ORIGIN, DL, DR).set_fill(RED, 1).set_stroke(width=0).scale(0.1).rotate(-PI/2)
		)
		def peak_updater(m):
			T = temperature()
			X = bbrad.Wien_displacement(T)
			Y = bbrad.Planck(X)
			vline, hline, peak, xmark, ymark = m
			peak.move_to(axes.c2p(bbrad.Wien_displacement(T), bbrad.Planck(bbrad.Wien_displacement(T))))
			vline.become(MyDashedLine(axes.c2p(X,0), axes.c2p(X,Y), 0.2, 0.5).set_stroke(GREY_B, 3, 0.5))
			hline.become(MyDashedLine(axes.c2p(0,Y), axes.c2p(X,Y), 0.2, 0.5).set_stroke(GREY_B, 3, 0.5))
			xmark.move_to(axes.c2p(X,0)).shift(DOWN*0.15)
			ymark.move_to(axes.c2p(0,Y)).shift(LEFT*0.15)

			if Y>100:
				ymark.set_fill(opacity=1-(Y-100)/100)
				hline.set_stroke(opacity=1-(Y-100)/100)

		peak_group.add_updater(peak_updater)
		if not (self.in_dev() and self.skip_animations):
			peak_group.suspend_updating()
			play(FadeIn(peak_group), run_time=0.7)
			peak_group.resume_updating()
			wait(1.5)
		else:
			add(peak_group)

		tmp = temperature.get_value()
		curve_6000 = curve_planck.update().copy().clear_updaters()
		curve_6000.set_stroke(width=3, opacity=0.7)
		temp_text_6000 = temp_text.update().copy().clear_updaters()[1:]
		temp_text_6000.next_to(axes.c2p(800,50),LEFT, buff=0.13)
		temperature.set_value(tmp)
		curve_planck.update()
		temp_text.update()

		#self.stop_skipping()
		if not (self.in_dev() and self.skip_animations):
			play(temperature.a.set_value(5400), run_time=1.5)
			wait()
			play(temperature.a.set_value(4000), run_time=2.5)
			wait(2)
			
			play(temperature.a.set_value(7000).set_anim_args(run_time=2, rate_func=lambda x: smooth(x)**(1/2 )), 
		   		self.camera.frame.a.scale(1.9, about_point=DOWN*FRAME_HEIGHT/2).set_anim_args(time_span=[0.5,1.4]))
			
			# to not mess with previous animation numbers
			#tmp = self.num_plays
			#self.num_plays += 1000
			#* +1 anim
			wait(2)
			play(Create(curve_6000), FadeIn(temp_text_6000), run_time=1.5)
			wait()

			start = curve_6000.copy()
			end = start.copy().match_points(curve_planck)
			add(start)
			play(Transform(start, end))
			self.remove(start, end)
			wait()

			#self.num_plays = tmp

			play(FadeOut(curve_6000), FadeOut(temp_text_6000))
			play(
				temperature.a.set_value(5777), self.camera.frame.a.scale(1/1.9, about_point=DOWN*FRAME_HEIGHT/2), run_time=1.6)
			wait()
		else:
			temperature.set_value(5777)

	
		#* ----------------------------------------------------------------- *#
		#* 是骡子是马拉出来遛遛 - 与真实数据的比较
		#* ----------------------------------------------------------------- *#
		
		curve_terra.set_color(YELLOW)
		curve_space.set_color(YELLOW)
		if not (self.in_dev() and self.skip_animations):
			play(Create(curve_terra), rate_func=linear_ease_io(0.1), run_time=2.5)
			wait(0.4)
			peak_group.suspend_updating()
			play(FadeOut(peak_group))

			wait()
			play(TransformFromCopy(curve_terra, curve_space), 
				curve_terra.a.set_stroke(color=YELLOW_A, opacity=0.3, width=2.5), 
				run_time=1.5)
		else:
			add(curve_terra)
			self.remove(peak_group)
			add(curve_space)
			curve_terra.set_stroke(color=YELLOW_A, opacity=0.3, width=2.5)
			temperature.set_value(5777)
			curve_planck.update()
		
		#* 分子吸收谱
		def get_apsorp_block(l1, l2, eps=10):
			block = VMobject()
			upper_curve = axes.plot(bbrad.exp_space, [l1,l2,eps], False, False)
			lower_curve = axes.plot(bbrad.exp_terra, [l1,l2,eps], False, False)
			
			upper_curve.add_points_as_corners([axes.c2p(l2,0), axes.c2p(l1,0), axes.c2p(l1, bbrad.exp_space(l1))])
			lower_curve.add_points_as_corners([axes.c2p(l2,100), axes.c2p(l1,100), axes.c2p(l1, bbrad.exp_terra(l1))])
			block = Intersection(upper_curve, lower_curve)
			block.set_fill(YELLOW_E,0.7).set_stroke(width=0)
			return block
		blocks = VGroup()
		blocks.add(get_apsorp_block(750, 780)) #O2, (H2O)
		blocks.add(get_apsorp_block(890, 1000)) # H2O
		blocks.add(get_apsorp_block(1050, 1240)) # H2O
		blocks.add(get_apsorp_block(1290, 1530)) # CO2, (H2O)
		blocks.add(get_apsorp_block(1760, 1990)) # CO2, (H2O)
		blocks[0].set_fill(TEAL)
		blocks[1:3].set_fill(BLUE)
		
		molecules = VGroup(
			Tex(r'\mathrm{O}_2').set_fill(TEAL_A),
			Tex(r'\mathrm{H_2O}').set_fill(BLUE_A),
			Tex(r'\mathrm{H_2O}').set_fill(BLUE_A),
			Tex(r'\mathrm{CO_2}').set_fill(YELLOW_B),
			Tex(r'\mathrm{CO_2}').set_fill(YELLOW_B)
		).arrange(RIGHT)
		for tex in molecules:
			tex.scale(0.8)
		molecules[0].next_to(blocks[0],UR, buff=0)
		molecules[1].next_to(blocks[1],UR, buff=-0.2)
		molecules[2].next_to(blocks[2],UP, buff=0).shift(RIGHT*0.2)
		molecules[3].next_to(blocks[3],UP, buff=0).shift(RIGHT*0.1)
		molecules[4].next_to(blocks[4],UP, buff=0)

		#* number plays uncertain here
		play(FadeIn(blocks))
		play(FadeIn(molecules))
		
		#* 为了思考题改一下图
		"""self.stop_skipping()
		self.remove(fml_planck, temp_text, curve_planck, func_dot)
		curve_space.set_stroke(YELLOW_B)
		blocks.set_fill(BLUE)
		m1 = molecules[1].copy().move_to(molecules[0]).shift(UR*0.1)
		m2 = molecules[1].copy().move_to(molecules[3]).shift(UP*0.07)
		m3 = molecules[1].copy().move_to(molecules[4]).shift(UP*0.16)
		molecules[0].next_to(m1,UP, buff=SMALL_BUFF)
		molecules[3].next_to(m2,UP, buff=SMALL_BUFF)
		molecules[4].next_to(m3,UP, buff=SMALL_BUFF)
		add(m1,m2,m3)
		return"""
		wait(2)
		play(FadeOut(blocks), FadeOut(molecules), FadeOut(curve_terra))
		wait(2)

		influence = ValueTracker(1)
		def match_highlight(m):
			δ = (temperature()-5840)
			σ = 40
			fac = np.exp(-((δ/σ)**2))
			color = interpolate_color(WHITE, YELLOW_E, fac)
			curve_planck.set_stroke(interpolate_color(WHITE, color, influence()))
		curve_planck.add_updater(match_highlight)

		self.stop_skipping()
		play(temperature.a.set_value(5500))
		wait()
		play(temperature.a.set_value(6120))
		wait(0.5)
		play(temperature.a.set_value(5840))
		wait(3)

		# 得出最后的结论
		#self.stop_skipping()

		temp_text.clear_updaters()
		text_sun = Text('太阳', font=文楷).set_color(YELLOW_B).scale(0.4)
		
		temp_text.generate_target()
		temp_text.target[0][1].set_color(WHITE)
		temp_text.target[1:].set_color(WHITE)
		temp_text.target.shift(DOWN*0.8+LEFT*0.5).scale(1.3)
		width = text_sun.get_width()
		temp_text.target[0][0]
		temp_text.target[0][1].shift(RIGHT*width*0.5)
		temp_text.target[1:].shift(RIGHT*width*0.5)

		text_sun.move_to(temp_text.target[0]).shift(DL*0.2+RIGHT*0.05)
		
		play(MoveToTarget(temp_text), FadeIn(text_sun, DOWN*0.8+LEFT))
		highlight = SurroundingRectangle(temp_text)
		play(Create(highlight), run_time=1.5)
		wait()
		highlight.reverse_points()
		play(Uncreate(highlight), influence.a.set_value(0), run_time=1.5)
		wait(5)
		return

class WavelengthToColorShowcase(BlackbodySpectrumScene):
	'''The most complicated scene, perhaps'''
	def construct(self) -> None:
		#* ----------------------------------------------------------------- *#
		#* axes and curve
		#* ----------------------------------------------------------------- *#

		axes, label_x, label_y = self.construct_axes(ylim=100)
		add(axes, label_x, label_y)
		curve_planck = axes.plot(bbrad.Planck,[  1, 2000, 10], attach=False, dynamic=True)
		temperature = ValueTracker(6000)
		def planck_T_controller(curve):
			bbrad.set_temperature(temperature.get_value())
		temperature.add_updater(planck_T_controller)
		add(curve_planck)
		
		#* ----------------------------------------------------------------- *#
		#* construct formulas
		#* ----------------------------------------------------------------- *#
		var = ['c','h','k','T','\lambda']
		fml_planck = Tex(r'W_{\mathrm{planck}}(\lambda,T)='+bbrad.tex_planck, isolate=var)
		fml = fml_planck

		# formula styling
		fml.scale(0.8).set_color(FML_COLOR)
		fml[r'\lambda'].set_color(BLUE)
		#fml['T'].set_color(RED_B)
		fml_planck[0].set_color(YELLOW)
		fml_planck[1:7].set_color(YELLOW_A)
		fml_planck[7].set_color(YELLOW_A)
		fml_planck[11].set_color(YELLOW_A)
		fml_planck[19].set_color(BLUE) #'^2'
		# formula positioning
		fml_planck.move_to(RIGHT*2.5+UP*2.2)

		add(fml_planck)
		
		#self.stop_skipping()
		#* ----------------------------------------------------------------- *#
		#* wavelength to visible light background
		#* ----------------------------------------------------------------- *#
		bg_img, bg_img_mask = self.get_image_and_mask_under_curve(axes, curve_planck, dynamic=True)
		
		# handle object visible order
		self.bring_to_back(bg_img_mask)
		self.bring_to_back(bg_img)

		#* ----------------------------------------------------------------- *#
		#* 温度的影响
		#* ----------------------------------------------------------------- *#
		temp_text = VGroup(
			Tex('T=',color=FML_COLOR).scale(1.2),
			Integer(6000),
			Tex('\mathrm{K}').scale(1.2)
		).arrange(RIGHT)
		temp_text[0][0].set_color(RED_B)
		
		def text_geo_nodes(_):
			#'T=','6000','K'
			T,     num,   K = temp_text

			num.set_value(temperature())
			# some careful positioning
			delta = num[0].get_bottom()[YDIM] - T[0].get_bottom()[YDIM]
			num.shift(delta*DOWN).shift(DOWN*0.03)
			width = num.get_right()[XDIM] - num.get_left()[XDIM]
			K.align_to(T,DOWN).shift(DOWN*0.02).next_to(T, RIGHT, buff=width+0.4, coor_mask = [1,0,0])

		temp_text.add_updater(text_geo_nodes)
		temp_text.next_to(fml_planck,DOWN,buff=MED_LARGE_BUFF).shift(RIGHT)

		add(temp_text)
	
		peak_group = VGroup(
			VMobject(), VMobject(),
			Dot(fill_color=YELLOW_B),
			Polygon(ORIGIN, DL, DR).set_fill(RED, 1).set_stroke(width=0).scale(0.1),
			Polygon(ORIGIN, DL, DR).set_fill(RED, 1).set_stroke(width=0).scale(0.1).rotate(-PI/2)
		)
		def peak_updater(m):
			T = temperature()
			X = bbrad.Wien_displacement(T)
			Y = bbrad.Planck(X)
			vline, hline, peak, xmark, ymark = m
			peak.move_to(axes.c2p(bbrad.Wien_displacement(T), bbrad.Planck(bbrad.Wien_displacement(T))))
			vline.become(MyDashedLine(axes.c2p(X,0), axes.c2p(X,Y), 0.2, 0.5).set_stroke(GREY_B, 3, 0.5))
			hline.become(MyDashedLine(axes.c2p(0,Y), axes.c2p(X,Y), 0.2, 0.5).set_stroke(GREY_B, 3, 0.5))
			xmark.move_to(axes.c2p(X,0)).shift(DOWN*0.15)
			ymark.move_to(axes.c2p(0,Y)).shift(LEFT*0.15)

			if Y>100:
				ymark.set_fill(opacity=1-(Y-100)/100)
				hline.set_stroke(opacity=1-(Y-100)/100)
		peak_group.add_updater(peak_updater)
		add(peak_group)

		#*------------------------------------------------------------------*#
		#* Now Animation!
		#*------------------------------------------------------------------*#
		

		self.stop_skipping()
		#* 较高温度的恒星偏蓝
		play(temperature.a.set_value(7000).set_anim_args(run_time=2, rate_func=lambda x: smooth(x)**(1/2 )), 
		  		self.camera.frame.a.scale(1.9, about_point=DOWN*FRAME_HEIGHT/2).set_anim_args(time_span=[0.5,1.4]))
		wait()
		pur_arrow = self.get_indicator(axes.c2p(400, bbrad.Planck(400)), 90*DEGREES, 4.5, buff=0.5).set_color(interpolate_color('#2222ff', PURPLE, 0.3))
		play(GrowArrow(pur_arrow))
		wait(2)
		
		play(temperature.a.set_value(6000), self.camera.frame.a.scale(1/1.9, about_point=DOWN*FRAME_HEIGHT/2), run_time=1.6)
		wait()


		#* 较低温度的恒星偏红
		play(temperature.a.set_value(4500), run_time=1.5)
		red_arrow = self.get_indicator(axes.c2p(640, bbrad.Planck(640)), 180*DEGREES, 2.5, buff=0.3).set_color(RED)
		pur_arrow = self.get_indicator(axes.c2p(400, bbrad.Planck(400)), 200*DEGREES, 2, buff=0.3).set_color(BLUE).set_stroke(width=6)
		wait(1)
		play(GrowArrow(red_arrow))
		wait(0.5)
		play(GrowArrow(pur_arrow))
		wait(2)


		


class SmoothHandle(VMobject):
	def __init__(self, start, end, smooth=0.3, buff=MED_SMALL_BUFF, color = TEAL, **kwargs):
		super().__init__(**kwargs)
		self.start = start + buff*RIGHT
		self.end   = end + buff*LEFT
		self.buff  = buff
		self.smooth= smooth
		FadeIn
		dir = end - start
		length = get_norm(dir)

		self.add_cubic_bezier_curve(
			self.start, self.start+smooth*length*RIGHT, 
			self.end-smooth*length*RIGHT, self.end
		)
		self.set_stroke(color)
	
	def set_start(self, start):
		self.start = start; end = self.end
		self.clear_points()
		dir = end - start
		length = get_norm(dir)
		self.add_cubic_bezier_curve(
			start, start+smooth*length*RIGHT, end-smooth*length*RIGHT, end
		)
		return self
	def set_end(self, end):
		self.end = end; start = self.start
		self.clear_points()
		dir = end - start
		length = get_norm(dir)
		self.add_cubic_bezier_curve(
			start, start+smooth*length*RIGHT, end-smooth*length*RIGHT, end
		)
		return self
	def set_start_and_end(self, start, end):
		self.start = start; self.end = end
		self.clear_points()
		dir = end - start
		length = get_norm(dir)
		self.add_cubic_bezier_curve(
			start, start+smooth*length*RIGHT, end-smooth*length*RIGHT, end
		)
		return self

	def add_dots(self):
		self.d1, self.d2 = Dot(self.start), Dot(self.end)
		self.d1.set_fill(self.get_stroke_color(), 1)
		self.d2.set_fill(self.get_stroke_color(), 1)
		self.d1.set_stroke(BLACK, 2)
		self.d2.set_stroke(BLACK, 2)
		self.add(self.d1, self.d2)
		
		return self

class Lit(Transform):
	def create_target(self) -> Mobject:
		return self.mobject.set_opacity(1)

class TechTree2(StarskyScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)

		# shortcuts
		global add, play, wait, narrate
		add = self.add
		play = self.play
		wait = self.wait
		narrate = self.narrate
		Mobject.a = Mobject.animate
	
	def construct(self) -> None:
		a1 = Text('电磁学', font=文楷).scale(1.1).set_color(BLUE)
		a2 = Text('辐射测量学', font=文楷).scale(1.1)#.set_color(YELLOW)
		a3 = Text('热力学', font=文楷).scale(1.1).set_color(RED_B)
		b1 = Text('热辐射', font=文楷).scale(1.1).set_color(YELLOW_A)
		b2 = Text('...', font=文楷).scale(1.1)
		c1 = Text('辐射测温', font=文楷).scale(1.1)
		c2 = Text('量子力学', font=文楷).scale(1.1).set_color(PURPLE_A)
		d1 = Text('...', font=文楷).scale(1.1)
		d2 = Text('...', font=文楷).scale(1.1)
		d3 = Text('...', font=文楷).scale(1.1)
		d4 = Text('...', font=文楷).scale(1.1)

		a = VGroup(a1, a2, a3).arrange(DOWN, buff=1)
		b = VGroup(b1, b2).arrange(DOWN, buff=1)
		c = VGroup(c1, c2).arrange(DOWN, buff=1)
		d = VGroup(d1, d2, d3, d4).arrange(DOWN, buff=0.7)
		b.move_to(RIGHT*5).shift(DOWN*(b[0].get_center()[1])); b2.align_to(b1,RIGHT)
		c.move_to(RIGHT*10)#.shift(UP*(0-c[1].get_center()))
		d.move_to(RIGHT*13.5)

		def de_emph(m):
			m.scale(0.8).set_fill(interpolate_color(GREY_B, GREY_C,0.5))
			return m
		de_emph(a[1])
		#de_emph(c[0])

		ab = VGroup(
			SmoothHandle(a1.get_right(), b1.get_left()+UP*0.15),
			SmoothHandle(a2.get_right(), b1.get_left()),
			SmoothHandle(a3.get_right(), b1.get_left()-UP*0.15),
		)
		bc = VGroup(
			SmoothHandle(b1.get_right()+UP*0.15, c1.get_left()),
			SmoothHandle(b1.get_right(), c2.get_left()),
			SmoothHandle(b2.get_right(), c2.get_left()+DOWN*0.15),
		)
		cd = VGroup(
			SmoothHandle(c2.get_right(), d1.get_left()),
			SmoothHandle(c2.get_right(), d2.get_left()),
			SmoothHandle(c2.get_right(), d3.get_left()),
			SmoothHandle(c2.get_right(), d4.get_left()),
		)
		
		#add(a,b,c,d,ab,bc,cd)
		#for sub in ab:
		#	sub.add_dots()

		def moving_right(m, dt):
			vel = 1
			m.shift(vel*RIGHT*dt)
		#self.camera.frame.add_updater(moving_right)
		self.camera.frame.shift(RIGHT*2.5)
		
		#self.stop_skipping()
		#box = RoundedRectangle(a1.get_width(), a1.get_height(), 0.1).move_to(a1).scale(1.5)
		#add(box)

		S = [a,ab,b]
		#add(*S)
		add(a[1],ab[1])
		#for s in S:
		#	s.fade(0.8)
		#play(Write(a1, time_span=[0, 1]),
		#	Create(ab, time_span=[0.7, 2], rate_func=linear),
		#	Write(b1, time_span=[1.7, 2.7]))
		

		play(LaggedStart(Write(a[0]),Create(ab[0]), lag_ratio=0.5))
		#wait(2)
		play(LaggedStart(Write(a[2]),Create(ab[2]), lag_ratio=0.5))
		#wait(0.5)
		bloom = VHighlight(b1, 5, (YELLOW_E, BG_COLOR), 10) # 当前进度：bloom
		self.bring_to_back(bloom)
		play(Write(b1), *[Write(layer) for layer in bloom], run_time=2)
		wait(1.5)
		
		"""
		lihua = LittleCreature('wanna', flipped=True).to_corner(DR, buff=1).shift(RIGHT*2)
		frontier = Text('1900年的学术前沿', font=文楷, color=YELLOW_A)
		frontier.next_to(b1, UP, buff=1).shift(RIGHT*1.5).rotate(-PI/20)
		ft_arr = Line(frontier.get_bottom()+UP*0.4+LEFT*0.2, b1.get_top(), 
				buff=0.2, color=YELLOW_A, 
				stroke_width=7, tip_width_ratio=1)
		ft_arr.data['points'][1] += UL*0.1
		ft_arr.add_tip(length=0.3)

		play(FadeIn(frontier), Create(ft_arr, time_span=[.5,1.5]), FadeIn(lihua, time_span=[.5,1.5]))
		#play(lihua.a.change_mood('wanna'),run_time=1.5)
		self.stop_skipping()
		wait(2)
		play(FadeOut(lihua))
		wait(2)

		return
		"""
		

		AG = AnimationGroup
		play(LaggedStart(AG(Create(bc[1]),Create(bc[2]), Write(b[1])),Write(c[1]), lag_ratio=0.5), 
	   		self.camera.frame.a.shift(RIGHT*5).set_anim_args(run_time=2))
		play(LaggedStart(Create(bc[0]),Write(c[0]), lag_ratio=0.5))

		#wait()

		play(LaggedStart(*[Write(m) for m in cd], lag_ratio=0.9),LaggedStart(*[Write(m) for m in d], lag_ratio=0.9))



class MaxwellEquation(StarskyScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)
		
	def construct(self) -> None:
		#isolate = [r'\mathbf{'+c+'}' for c in ['D','B','E','H','J']]
		tex = Tex(r'''\left\{\begin{array}{l}  
  \nabla\ \cdot\ \mathbf{D} =\rho _f \\  
  \nabla\ \cdot\ \mathbf{B} = 0 \\  
  \nabla \times  \mathbf{E} = -\partial_t \mathbf{B}  \\  
  \nabla \times  \mathbf{H} =  + \partial_t\mathbf{D}+\mathbf{J}_f
\end{array} \right.''',color=FML_COLOR).scale(1.5)
		
		tex[9].set_color(BLUE)
		tex[15].set_color(PURPLE)
		tex[20].set_color(BLUE)
		tex[25].set_color(PURPLE)
		tex[28].set_color(PURPLE)
		tex[33].set_color(BLUE)

		title = Text('Maxwell Equation Groups, 1885').move_to(UP*2.3).scale(1.4)
		#tex.move_to(DOWN*1)

		self.play(FadeIn(tex))
		self.wait(3)
		self.play(FadeIn(title, DOWN/2), tex.animate.shift(DOWN))
		self.wait(10)

class ProblemSetup(StarskyScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)

		# shortcuts
		global add, play, wait, narrate
		add = self.add
		play = self.play
		wait = self.wait
		narrate = self.narrate
		Mobject.a = Mobject.animate
	
	def construct(self) -> None:
		title = Text('问 题', font=黑体)
		delim = Line(LEFT*(FRAME_WIDTH/2-1), RIGHT*(FRAME_WIDTH/2-1))
		#delim.set_stroke(GREY_C)
		title.to_edge(UP, buff=0.3)
		delim.next_to(title,DOWN)
		

		Q = VGroup(
			Text('给定', font=黑体),
			Text('温度',font=文楷),
			Tex('T')
		).arrange(DOWN)

		A = VGroup(
			Text('任务',font=黑体),
			Text('找出黑体的热辐射谱',font=文楷),
			Tex(r'W_{\mathrm{BlackBody}}(\lambda)')
		).arrange(DOWN).shift(DOWN*3)
		Q[0].set_color(GREY_B); A[0].set_color(GREY_B)
		Q[-1].scale(1.3); A[-1].scale(1.2)

		# positioning
		Q[0].align_on_border(UL,1).shift(DOWN*0.6)
		Q[1].next_to(Q[0]).shift(DOWN)
		Q[2].next_to(Q[1]).shift(DOWN*.05)

		A[0].move_to(Q[0]).shift(DOWN*2.7)
		A[1].next_to(A[0]).shift(DOWN)
		A[2].next_to(A[1]).shift(DOWN*.07+LEFT*.05)

		# styling
		Q[1:].set_color(RED_B)
		A[1][-4:].set_color(YELLOW_A)
		A[-1].set_color(YELLOW_A)
		A[-1][-2].set_color(BLUE)

		self.stop_skipping()
		play(Write(Q), FadeIn(VGroup(title, delim)))
		wait()
		play(Write(A), run_time=3)
		wait(3)

class SunTemperatureAE(StarskyScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)

		# shortcuts
		global add, play, wait, narrate
		add = self.add
		play = self.play
		wait = self.wait
		narrate = self.narrate
		Mobject.a = Mobject.animate

	def construct(self) -> None:
		p1 = ORIGIN
