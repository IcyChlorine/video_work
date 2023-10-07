from manimlib import *
from manimhub import * 
import os, sys; sys.path.append(os.path.dirname(__file__))
from set_output_path import set_output_path

# Maxwell's Equation Group Scene.

class ElectricFieldFormula(StarskyScene):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		set_output_path(self.file_writer)

	def construct(self) -> None:
		# shortcuts
		global add, play, wait, narrate
		add = self.add
		play = self.play
		wait = self.wait
		narrate = self.narrate
		Mobject.a = Mobject.animate

		self.camera.background_rgba = np.array([0,0,0,0],dtype=np.float32)
		
		fml = Tex(r'\vec{E}=k\ \frac{q}{r^2}\cdot\vec{e}_r',color=FML_COLOR)
		# 微调
		fml[r'\vec{E}'].set_color(BLUE)
		fml[4].set_color(PURPLE)
		#fml[6].shift(0.08*UP)
		fml.scale(3)

		#add(fml)
		play(Write(fml),run_time=2)
		wait(5)
		play(FadeOut(fml))