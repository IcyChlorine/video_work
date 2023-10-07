from manimlib import *
from manimhub import *
import os, sys; sys.path.append(os.path.dirname(__file__))
#__manimhub_path__ = '/c/StarSky/Programming/MyProjects/manimhub/'
#sys.path.append(__manimhub_path__)
#from manimhub import *

from set_output_path import set_output_path

class ThreeSubjectsInvolved(StarskyScene):
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

		#!-------------------------------------------------------------------!#
		#* constructs
		
		text_kwargs = dict(font=文楷,)
		texts = VGroup(
			Text('热力学', **text_kwargs),
			Text('电磁学', **text_kwargs),
			Text('量子力学', **text_kwargs)
		)
		for m in texts: m.scale(1.2)
		#texts[0].add_updater(lambda m: print(m[0].get_area_vector()))
		#texts.arrange(RIGHT)
		#add(texts)
		
		images = Group(
			ImageMobject('../assets/thermal2.png'),
			ImageMobject('../assets/electromagnetic.png'),
			ImageMobject('../assets/quantum.png'),
		)
		for m in images: m.scale(0.7)
		#images.arrange(RIGHT)
		#add(images)

		cards = Group(*[Group(text, image) for text, image in zip(texts, images)])
		for g in cards: g.arrange(DOWN, buff=1.5)
		cards.arrange(RIGHT)
		
		delim = Line(DOWN*4, UP*4).scale(0.9).set_stroke(color=GREY_C)
		delim.move_to(FRAME_WIDTH/2*RIGHT).shift(RIGHT*0.1) # shift 0.1 to move out of scene completely
		delims = VGroup(VMobject(), delim, delim.copy())

		#!-------------------------------------------------------------------!#
		#* animation

		SCENE_LEFT = LEFT*FRAME_WIDTH/2
		SCENE_RIGHT= RIGHT*FRAME_WIDTH/2
		SCENE_WIDTH= RIGHT*FRAME_WIDTH
		card_pos_trans = [SCENE_LEFT+SCENE_WIDTH*(0.5+idx)/2 for idx in range(2)]
		card_pos = [SCENE_LEFT+SCENE_WIDTH*(0.5+idx)/3 for idx in range(3)]

		# card 1: EM
		cards[0].center()
		cards[0][1].generate_target()
		cards[0][1].scale(0.01)
		play(Write(cards[0][0]), MoveToTarget(cards[0][1]))
		narrate('磁学，热')

		# card 2: thermal
		cards[1].next_to(SCENE_RIGHT,RIGHT)
		cards[2].next_to(SCENE_RIGHT,RIGHT)
		add(delims[1],delims[2])
		play(
			cards[0].a.move_to(card_pos_trans[0], coor_mask=RIGHT),
			delims[1].a.move_to(ORIGIN),
			cards[1].a.move_to(card_pos_trans[1], coor_mask=RIGHT),
		)
		narrate('力学，甚至是量子')

		# card 3: QM
		play(
			cards[0].a.move_to(card_pos[0], coor_mask=RIGHT),
			delims[1].a.move_to(SCENE_LEFT/3),
			cards[1].a.move_to(card_pos[1], coor_mask=RIGHT),
			delims[2].a.move_to(SCENE_RIGHT/3),
			cards[2].a.move_to(card_pos[2], coor_mask=RIGHT),
		)
		narrate('力学')
		wait(5)

class MaterialBoundary(StarskyScene):
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

		boundary = Circle(radius = 2, stroke_width = 20) \
			.shift(LEFT*5)
		boundary = Rectangle()#get_subcurve(0,0.7)
		#boundary = DashedVMobject(boundary, num_dashes = 10, positive_space_ratio = 0.5)

		group = VGroup()

		nr_sectors = 4.7
		angle_start = -0.4
		d_angle = 0.4*2/nr_sectors
		for i in range(10):
			m = Arc(radius = 10, start_angle = angle_start+i*d_angle, angle = d_angle*0.5, stroke_width = 20) \
				.shift(LEFT*9)
			m.set_stroke(YELLOW_A)
			group.add(m)

		add(group)
		wait()

class CollisionAE(StarskyScene):
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

		vel_line1 = DashedLine(RIGHT*5, ORIGIN, dash_length=0.2) \
			.rotate(PI/4,about_point=ORIGIN).shift(RIGHT/3.5)
		vel_line2 = DashedLine(LEFT*5, ORIGIN, dash_length=0.2) \
			.rotate(PI/4,about_point=ORIGIN).shift(LEFT/3.5)
		vel_line1.set_color(WHITE)
		vel_line2.set_color(WHITE)
		#add(vel_line1, vel_line2)
		#self.stop_skipping()
		play(FadeIn(vel_line1), FadeIn(vel_line2))
		wait(2.5)

		
		arr1 = Arrow(ORIGIN, 1.5*(RIGHT*2+DOWN), stroke_width = 10)
		arr2 = arr1.copy().rotate(PI,about_point=ORIGIN)
		particle_pos = RIGHT*1.2+UP*0.5+DL*0.5+RIGHT*0.2
		arr1.shift(particle_pos)
		arr2.shift(-particle_pos)
		arr1.set_color(WHITE)
		arr2.set_color(WHITE)


		tex1 = Tex('\\vec{a}',color=RED_B).scale(2)
		tex1.next_to(arr1.get_end(),RIGHT)
		tex2 = tex1.copy()
		tex2.next_to(arr2.get_end(),LEFT)
		
		self.stop_skipping()
		play(
			GrowArrow(arr1), GrowArrow(arr2),
			FadeIn(tex1, arr1.get_end()-arr1.get_start()),
			FadeIn(tex2, arr2.get_end()-arr2.get_start()),
		)
		wait(4)

class ScratchHead(StarskyScene):
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

		lihua = LittleCreature('puzzling')
		#play(FadeIn(lihua))
		add(lihua)
		play(lihua.a.change_mood('puzzling2'),run_time=0.5)
		play(lihua.a.change_mood('puzzling'),run_time=0.5)
		play(lihua.a.change_mood('puzzling2'),run_time=0.5)
		play(lihua.a.change_mood('puzzling'),run_time=0.5)
		play(lihua.a.change_mood('puzzling2'),run_time=0.5)
		play(lihua.a.change_mood('puzzling'),run_time=0.5)
		wait(2)
		