from manimlib import *
from manimhub import *
import os, sys
from manimlib.mobject.mobject import Mobject; sys.path.append(os.path.dirname(__file__))
from set_output_path import set_output_path
from utils import *
		
class PhotoElectric(StarskyScene):
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
		cube = Cube(gloss=0)
		
		"""plane = Square().set_fill(BLUE, 0.5).set_stroke(WHITE, 0, 0)
		temp = VGroup(
			plane,
			plane.copy().rotate(PI/2, axis=RIGHT),
			plane.copy().rotate(PI/2, axis=UP),
		).shift(RIGHT)
		temp[0].shift(IN)
		temp[1].shift(DOWN)
		temp[2].shift(LEFT)
		cube = VGroup(
			temp[0],temp[1],temp[2],
			temp[0].copy().shift(OUT*2),
			temp[1].copy().shift(UP*2),
			temp[2].copy().shift(RIGHT*2),
		)
		back, down, left, front, up, right = cube
		up.set_color(BLUE_A)
		
		self.camera.set_ctx_depth_test(True)"""
		add(cube)
		self.stop_skipping()
		self.camera.frame.add_updater(lambda m, dt: m.rotate(dt, axis=RIGHT))
		#play(self.camera.frame.a.rotate(-PI/6, axis=RIGHT))