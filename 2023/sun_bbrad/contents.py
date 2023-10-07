from manimlib import *
from manimhub import * 
import os, sys; sys.path.append(os.path.dirname(__file__))
from set_output_path import set_output_path

class Contents(StarskyScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)

	def construct(self):
		kw={'color':FML_COLOR,'font_size':40}
		L0=Text('Part 0 ',**kw)
		L1=Text('Part I ',**kw)
		L2=Text('Part II ',**kw)
		L3=Text('Part III ',**kw)

		kw={'font':文楷,'font_size':40,'color':FML_COLOR}
		M0=Text('引 入', **kw)
		M1=Text('热 辐 射',**kw).set_color(interpolate_color(WHITE, YELLOW, 0.2))
		bloom = VHighlight(M1, color_bounds=(YELLOW, GREY_E),max_stroke_addition=15).set_opacity(0.2)
		M1.add(bloom)
		M2=Text('黑 体',**kw).set_color(YELLOW)
		M3=Text('太阳的黑体辐射',**kw).set_color(YELLOW)

		R0=Text('0:00',**kw)
		R1=Text('1:55',**kw)
		R2=Text('5:10',**kw)
		R3=Text('7:17',**kw)

		VGroup(L0,L1,L2,L3).arrange(DOWN,buff=1).shift(UP*0.2)
		L0.align_on_border(LEFT,buff=2)
		L1.align_on_border(LEFT,buff=2)
		L2.align_on_border(LEFT,buff=2)
		L3.align_on_border(LEFT,buff=2)
		M0.align_to(L0,DOWN).align_on_border(LEFT,buff=4.4)
		M1.align_to(L1,DOWN).align_on_border(LEFT,buff=4.4)
		M2.align_to(L2,DOWN).align_on_border(LEFT,buff=4.4)
		M3.align_to(L3,DOWN).align_on_border(LEFT,buff=4.4)
		R0.align_to(L0,DOWN).align_on_border(RIGHT,buff=2)
		R1.align_to(L1,DOWN).align_on_border(RIGHT,buff=2)
		R2.align_to(L2,DOWN).align_on_border(RIGHT,buff=2)
		R3.align_to(L3,DOWN).align_on_border(RIGHT,buff=2)

		L0.fade(0.7); M0.fade(0.7); R0.fade(0.7)

		#self.add(L1,L2,L3,M1,M2,M3,R1,R2,R3)
		self.add(L0, M0, R0)

		self.play(Write(L1))
		self.play(Write(M1[3:]),Write(M1[0:3]),)
		self.wait()
		
		self.play(Write(R1))
		self.wait(1)
		self.play(Write(L2))
		self.play(Write(M2))
		self.wait()
		self.play(Write(R2))
		self.wait(1.5)
		self.play(Write(L3))
		self.play(Write(M3),run_time=2.5)
		self.wait()
		self.play(Write(R3))
		self.wait(15)