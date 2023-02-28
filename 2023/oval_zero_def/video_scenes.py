from manimlib import *
import os,sys

__manimhub_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__manimhub_path__)
from manimhub import *

sys.path.append(os.getcwd())
from data_axes import *
from stencil import *
from zooming import *
from mobjects import *

# base scene class for many scenes that include ellipses/ovals.
class OvalScene(StarskyScene):
	def setup(self) -> None:
		return super().setup()

		#self.init_axes()
		#self.init_oval()
		
	def init_axes(self, wh_ratio = 1, **axes_kw):
		# does NOT add mobj into scene.
		xmax = 3; width=6
		axes_config = {
			#'axis_config': {'include_tip': True},
			'x_range': [-xmax,xmax], 
			'y_range': [-xmax*wh_ratio, xmax*wh_ratio], 
			'width': width, 
			'height': width*wh_ratio,
			'axis_align_towards_zero': True,
			'include_numbers': False,
			'axis_config': {
				'include_label': True,
				'number_locator': (lambda _a,_b,_c,_d: [1]) # return only 1 conditionlessly
			}
		}
		axes_config.update(axes_kw)
		self.axes = DataAxes(**axes_config)#.to_edge(LEFT, buff=1)
		#self.axes.add_axis_labels() # fix it a bit later

	def init_oval(self, a=2.6, b=1.4, **oval_kw):
		# assumes that axes is inited.
		# does NOT add mobj into scene.
		assert(hasattr(self,'axes'))
		axes = self.axes

		r = 1
		self.unit_circ = Circle(
			color = WHITE,
			radius = r * axes.x_axis.unit_size
		).move_to(axes.c2p(0,0))

		self.oval = self.unit_circ.copy()
		self.a, self.b = a, b
		self.c = (a**2-b**2)**0.5
		kw = {'about_point': axes.c2p(0,0)}
		self.oval.stretch(a, XDIM, **kw).stretch(b, YDIM, **kw)
		
	def get_oval_coord(self, theta):
		return np.array((self.a*np.cos(theta), self.b*np.sin(theta)))
	
	def point(self, coord=(0,0), **point_kw):
		dot_config = {'color': YELLOW}
		final_config = dot_config.copy()
		final_config.update(point_kw)
		return Dot(self.axes.c2p(*coord), **final_config)
	
	def line(self, coord1=(-1,0), coord2=(1,0), **line_kw):
		line_config = {}#'stroke_width': 3, 'stroke_color': GREY_A}
		final_config = line_config.copy()
		final_config.update(line_config)
		return Line(
			start = self.axes.c2p(*coord1),
			end = self.axes.c2p(*coord2),
			**final_config
		)

	@staticmethod
	def hint_dynamic(*mobjects: Iterable[Mobject]):
		# add identity updater to hint manim that mobj is dynamic
		for mobj in mobjects:
			mobj.add_updater(lambda m: m)

def overlap_timespan(k,T,n,overlap_ratio=0):
	'''当总共有n个动画需要进行、动画间有overlap_ratio部分重叠时，
	第k个动画的time span. T为总时间。'''
	α = overlap_ratio
	t = T / ( 1+(n-1)*(1-α) )
	return np.array([k*(1-α)*t, k*(1-α)*t+t])

#!-------------------------------------------------------------------!#
#* Part O: Introduction and Main Idea

class OvalIntro(OvalScene):
	def construct(self) -> None:
		a, b = 2, 1.4
		c = (a**2-b**2)**0.5
		self.init_axes()
		self.init_oval(a,b)
		axes, oval = self.axes, self.oval
			
		t2c = {'a^2':BLUE_B, 'b^2':BLUE_B}
		oval_fml = MTex(r'{x^2\over a^2}+{y^2\over b^2}=1', tex_to_color_map=t2c).scale(1.2)
		
		oval_text = Text('椭 圆',font=文楷,font_size=100,color=GREY_A)
		#positioning
		
		axes.shift(LEFT*2.8); oval.shift(LEFT*2.8)
		oval_text.shift(RIGHT*3+UP*1.4)
		oval_fml.next_to(oval_text,DOWN,buff=1).align_to(oval_text,LEFT)

		#!-------------------------------------------------------------------!#
		#* elements进场
		self.play(
			Create(axes, time_span=[0,2]), Create(oval, time_span=[0,2]), 
			Write(oval_text, time_span=[0,1]),
			Write(oval_fml, time_span=[2,3]),
		)
	
		self.wait(2)
		self.play(FadeOut(oval_text), oval_fml.animate.shift(UP*2.5))
		self.wait()
		#!-------------------------------------------------------------------!#
		#* 第一定义
		theta = ValueTracker(PI/2*0.95)
		
		P_LC = self.get_oval_coord(theta.get_value())
		A_LC, B_LC = np.array((-c,0)), np.array((c,0))
		P_MC = axes.c2p(*P_LC)
		A_MC, B_MC = axes.c2p(*A_LC), axes.c2p(*B_LC)
		P = self.point(P_LC)
		A = self.point(A_LC)
		B = self.point(B_LC)
		PA = self.line(P_LC,A_LC)
		PB = self.line(P_LC,B_LC)

		# 对P.label用next_to会产生一个很奇怪的glitchy，迫不得已只好用move_to
		P.label = Tex('P').move_to(axes.c2p(*(P_LC*1.3)))
		A.label = Tex('A').next_to(A, direction=DOWN,buff=SMALL_BUFF)
		B.label = Tex('B').next_to(B, direction=DOWN,buff=SMALL_BUFF)
		P.label.set_backstroke(width=8)

		# show elements

		# 公式
		firstdef_fml = Tex('|PA|+|PB|=2','a')
		firstdef_fml[1].set_color(BLUE_B)
		firstdef_fml.next_to(oval_fml,DOWN,buff=0.92)

		PA.reverse_points()#,PB.reverse_points()

		self.play(
			FadeIn(firstdef_fml,time_span=[0,0.7]),
			oval_fml.animate.set_opacity(0.2).set_anim_args(time_span=[0,0.7]),
			FadeIn(A,time_span=[0.7,1.5]),FadeIn(A.label,time_span=[0.7,1.5]),
			Create(PA,time_span=[1,2]),
			FadeIn(P,time_span=[1,1.5]), FadeIn(P.label,time_span=[1,1.5]),
			Create(PB,time_span=[1.5,2.5]),
			FadeIn(B,time_span=[1.2,2.7]),FadeIn(B.label,time_span=[1.2,2.7]),
		)

		def controller(_):
			P_LC = self.get_oval_coord(theta.get_value())
			P_MC = axes.c2p(*P_LC)
			P.move_to(P_MC)
			P.label.move_to(axes.c2p(*(P_LC*1.3)))
			PA.put_start_and_end_on(P_MC,A_MC)
			PB.put_start_and_end_on(P_MC,B_MC)
			self.bring_to_front(P,A,B)
		
		# 动的对象：P,P-label,PA,PB
		P.add_updater(controller)
		P.label.add_updater(controller)
		PA.add_updater(lambda m: m)
		PB.add_updater(lambda m: m)

		#* 完成几何对象的逻辑控制
		#!-------------------------------------------------------------------!#
		#* moving geometry
		self.play(theta.animate.set_value(PI * 2/3))
		self.wait(0.5)
		self.play(theta.animate.set_value(PI * 1/7), run_time=1.5)
		self.wait(0.6)
		self.play(theta.animate.set_value(PI * 1/2))
		self.wait(1)

		# '距离公式有点复杂'
		self.stop_skipping()
		sqrt_fml = Tex(r'\sqrt{(x+c)^2+y^2}','+',r'\sqrt{(x-c)^2+y^2}',color=FML_COLOR)
		sqrt_fml.next_to(firstdef_fml,DOWN,buff=1.5).shift(LEFT*.5)
		arrow1 = Arrow(firstdef_fml[0].get_bottom()+LEFT, sqrt_fml[0].get_top())
		arrow2 = Arrow(firstdef_fml[0].get_bottom(), sqrt_fml[2].get_top())
		#self.add(sqrt_fml,arrow1,arrow2)
		arrow_time_span = np.array([0,.6])
		fml_time_span= np.array([0,0.4])
		self.play(
			GrowArrow(arrow1,time_span=0+arrow_time_span),
			GrowArrow(arrow2,time_span=0.5+arrow_time_span),
			FadeIn(sqrt_fml[0],time_span=0.3+fml_time_span),
			FadeIn(sqrt_fml[1],time_span=0.5+fml_time_span),
			FadeIn(sqrt_fml[2],time_span=0.6+fml_time_span),
		)
		self.add(sqrt_fml)
		self.wait()
		self.play(FadeOut(arrow1),FadeOut(arrow2),FadeOut(sqrt_fml))
		self.wait()
		
		# fade all
		self.play(*[FadeOut(m) for m in self.mobjects[1:]])

# 第一定义的内容合并到OvalIntro里了。
class OvalFirstDef(OvalScene):
	def construct(self) -> None:
		a, b = 2, 1.4
		c = (a**2-b**2)**0.5

		self.init_axes()
		self.init_oval(a=a, b=b)		
		
		axes, oval = self.axes, self.oval

		theta = ValueTracker(PI/2*0.95)
		
		cP = self.get_oval_coord(theta.get_value())
		cA, cB = np.array((-c,0)), np.array((c,0))
		vP = axes.c2p(*cP)
		vA, vB = axes.c2p(*cA), axes.c2p(*cB)
		P = self.point(cP)
		A = self.point(cA)
		B = self.point(cB)
		PA = self.line(cP,cA)
		PB = self.line(cP,cB)

		# 对P.label用next_to会产生一个很奇怪的glitchy，迫不得已只好用move_to
		P.label = Tex('P').move_to(axes.c2p(*(cP*1.3)))
		A.label = Tex('A').next_to(A, direction=DOWN)
		B.label = Tex('B').next_to(B, direction=DOWN)
		P.label.set_backstroke(width=8)

		self.add(axes, oval)
		self.add(P,A,B,PA,PB)
		self.add(P.label, A.label, B.label)
		self.bring_to_front(P,A,B)

		def controller(_):
			cP = self.get_oval_coord(theta.get_value())
			vP = axes.c2p(*cP)
			P.move_to(vP)
			P.label.move_to(axes.c2p(*(cP*1.3)))
			PA.put_start_and_end_on(vP,vA)
			PB.put_start_and_end_on(vP,vB)
			self.bring_to_front(P,A,B)
		
		# 动的对象：P,P-label,PA,PB
		P.add_updater(controller)
		P.label.add_updater(controller)
		PA.add_updater(lambda m: m)
		PB.add_updater(lambda m: m)

		#* 完成几何对象的逻辑控制
		#!-------------------------------------------------------------------!#
		#* 添加公式

		firstdef_fml = Tex('|PA|+|PB|=2a')
		firstdef_fml.next_to(oval, UR)
		self.add(firstdef_fml)

		self.play(theta.animate.set_value(PI * 2/3))
		self.wait(0.5)
		self.play(theta.animate.set_value(PI * 1/2))
		self.wait(1)
	
class OvalSecondDef(OvalScene):
	def construct(self) -> None:
		a,b=2.5,2
		c=(a*a-b*b)**0.5; e=c/a

		self.init_axes()	
		self.init_oval(a,b)
		axes = self.axes
		oval = self.oval

		# 极坐标
		polar_axis = Axis(
			include_ticks=False,
			include_tip=True,
			length=6,
			range=[0,5]#让原点在线的最左端
		)
		line = Line(DOWN*3, UP*3,)
		
		# 把line挪到准线的位置
		Δr=axes.c2p(-c,0)-polar_axis.get_origin()
		polar_axis.shift(Δr)
		line.move_to(axes.c2p(-a**2/c,0))
		
		line_bs = line.copy().set_stroke(GREEN,15)
		line_bs.move_to(line)

		θθ = ValueTracker(3*PI/4)
		A,O,H = self.point()*3
		OA, AH = self.line()*2
		AH.backstroke = AH.copy().set_stroke(GREY_E, 10)
		AH.backstroke.add_updater(lambda m: m.set_points(AH.get_points()))

		A.label = Tex('P').set_backstroke(GREY_E,8)

		def geometry_controller(m):
			θ = θθ.get_value()
			O_LC = (-c,0)
			A_LC = self.get_oval_coord(θ)
			H_LC = A_LC.copy()
			H_LC[0] = -a**2/c

			O_MC = axes.c2p(*O_LC)
			A_MC = axes.c2p(*A_LC)
			H_MC = axes.c2p(*H_LC)
			O.move_to(O_MC)
			A.move_to(A_MC)
			H.move_to(H_MC)

			label_buff = MED_LARGE_BUFF
			A.label.move_to(A_MC+normalize(A_MC)*label_buff)

			OA.put_start_and_end_on(O_MC, A_MC)
			AH.put_start_and_end_on(A_MC, H_MC)
		geometry_controller(None) # call it once to put things in place
		
		text = Text('第二定义',font=文楷).to_corner(UR,buff=1.5)
		'''self.add(oval, polar_axis, line,line_bs)
		self.bring_to_back(line_bs)
		self.add(A,A.label,O,H,OA,AH)
		self.bring_to_front(A,O,H)

		self.add(AH.backstroke)
		self.bring_to_back(AH.backstroke)
		self.bring_to_back(oval)
		self.bring_to_back(polar_axis)'''

		# show elements
		self.play(
			Create(polar_axis),
			Create(oval),
			Create(OA),
			Create(AH),
			Create(line_bs),Create(line),
			FadeIn(O),FadeIn(A),FadeIn(A.label),FadeIn(H),
			FadeIn(text,time_span=[0.5,2]),
			run_time=2
		)

		A.add_updater(geometry_controller)
		self.hint_dynamic(A,A.label,O,H,OA,AH)
		self.play(θθ.animate.set_value(PI/6))
		self.wait(0.5)
		self.play(θθ.animate.set_value(3*PI/4),run_time=2)
		self.wait(0.5)
		self.play(θθ.animate.set_value(PI*1.6),run_time=2)

class OvalAndCircle(OvalScene):
	def construct(self) -> None:
		a, b = 2, 1.4
		xmax=2.5; wh_ratio=1.2; width=5
		self.init_axes(
			x_range=[-xmax,xmax], 
			y_range= [-xmax*wh_ratio, xmax*wh_ratio], 
			width= width, 
			height= width*wh_ratio,
		)
		self.init_oval(a,b)
		oval_axes, oval = self.axes, self.oval
		circ_axes = oval_axes.copy()
		oval_group = VGroup(oval_axes, oval)
		oval_group.shift(LEFT*3)

		circ = self.unit_circ
		circ_group = VGroup(circ_axes, circ)		
		circ_group.shift(RIGHT*3)

		text = Text('椭 圆',font=文楷,color=YELLOW)
		text.to_edge(UP, buff=1.2)

		# plays
		self.play(Create(oval_axes), Create(oval))
		self.wait()
		self.play(TransformFromCopy(oval_axes, circ_axes), Create(circ,time_span=[0.6,1.6]))
		self.wait()
		#text[1].set_color(BLUE)
		self.play(Write(text),run_time=0.8)
		self.play(text[0].animate.set_color(GREY_B).set_opacity(0.4).set_anim_args(run_time=0.5))
		self.wait()

		# '长得像圆'
		self.play(
			oval.animate.set_stroke(GREY_D).set_anim_args(rate_func=there_and_back),
	    	circ.animate.set_stroke(GREY_D).set_anim_args(time_span=[0.7,1.7],rate_func=there_and_back)
		)

		t2c = {'a^2':BLUE, 'b^2':BLUE}
		oval_eq = MTex(r'\frac{x^2}{a^2}+\frac{y^2}{b^2}=1',color=FML_COLOR,tex_to_color_map=t2c)
		circ_eq = MTex(r'x^2+y^2=1',color=FML_COLOR)
		oval_eq.move_to(oval_axes.c2p(2,-2))
		circ_eq.move_to(circ_axes.c2p(2,-2))
		
		# '方程也和圆很像'
		self.wait()
		self.add(oval_eq)
		self.wait()
		self.add(circ_eq)
		self.wait()
		self.play(text[0].animate.set_color(YELLOW).set_opacity(1))
		self.wait()

		#* for another scene...
		self.remove(text)
		circ_axes.set_opacity(0.3)
		circ.set_stroke(opacity=0.3)
		oval_text = Text('椭圆',font=文楷,color=YELLOW).move_to(oval_axes.c2p(2,2))
		circ_text = Text('圆',font=文楷).move_to(circ_axes.c2p(2,2)).set_fill(opacity=0.5)
		a_label = Tex('a',color=BLUE_B).next_to(oval_axes.c2p(a,0),DL,buff=MED_SMALL_BUFF).shift(UP*0.05)
		b_label = Tex('b',color=BLUE_B).next_to(oval_axes.c2p(0,b),UL,buff=MED_SMALL_BUFF)
		ind_tgt = oval_eq.select_part('a^2').get_bottom()
		indicator = Arrow(ind_tgt+DL,ind_tgt).shift(LEFT*0.1)
		self.add(oval_text,circ_text)

		self.wait()
		
		self.play(FadeIn(a_label))
		self.wait()
		self.play(FadeIn(b_label))
		self.wait(2)
		
		self.play(GrowArrow(indicator))
		self.play(oval_eq.select_part('a^2').animate.set_color(WHITE),rate_func=there_and_back,run_time=0.7)
		self.play(oval_eq.select_part('b^2').animate.set_color(WHITE),rate_func=there_and_back,run_time=0.7)
		self.play(FadeOut(indicator))
		
class ContentPreview(StarskyScene):
	def construct(self):
		pi=LittleCreature().align_on_border(DL)
		frame=Rectangle(9,5.5).set_style(stroke_color=YELLOW).shift(RIGHT*0.6)

		pi.look_at(frame)
		self.add(pi)
		self.play(ShowCreation(frame))

		#self.play(Transform(pi,pi.copy().change_mode('happy').look(OUT)))
		self.play(pi.change_mood,'smile')
		self.wait(1)
		self.wait(0.6)
		self.play(Blink(pi))
		self.wait(0.4)
		self.play(Blink(pi))

		self.wait(3)
		self.play(Blink(pi))
		self.wait(5)
		self.play(Blink(pi))
		self.wait(10)

class OvalZeroDef(OvalScene):
	def construct(self) -> None:
		a, b = 2.6, 1.4

		self.init_axes()
		#self.axes.shift(LEFT*3)
		self.init_oval(a=a, b=b)		
		
		axes, oval, circ = self.axes, self.oval, self.unit_circ
		theta = PI/4

		self.show_elements()
		self.showcase_transform()
		self.point_mapping()

	def show_elements(self):
		axes, oval, circ = self.axes, self.oval, self.unit_circ
		self.play(Create(axes), Create(circ))
		self.wait()

	def showcase_transform(self):
		axes, oval, circ = self.axes, self.oval, self.unit_circ
		a, b = self.a, self.b

		tmp = circ.copy()
		self.play(tmp.animate.stretch(a,XDIM))
		self.wait()
		self.play(tmp.animate.stretch(b,YDIM))
		'''self.play(tmp.animate.stretch(a,XDIM).stretch(b,YDIM))
		self.wait()'''
		self.remove(tmp); self.add(oval)
		self.wait()

	def point_mapping(self):
		a, b = self.a, self.b
		axes, oval, circ = self.axes, self.oval, self.unit_circ

		eps = 1e-6
		all_theta = np.arange(0, 2*PI+eps, PI/4)
		all_theta = all_theta[1:]+all_theta[0]
		circ_coords, oval_coords = [], []
		circ_vec,    oval_vec = [], []
		circ_points, oval_points = [], []
		conn_lines = []
		dashedline_config = {
			'dash_length':0.12, 
			'positive_space_ratio':0.6
		}
		for theta in all_theta:
			c_circ = (1*np.cos(theta), 1*np.sin(theta))
			c_oval = (a*np.cos(theta), b*np.sin(theta))
			v_circ = axes.c2p(*c_circ)
			v_oval = axes.c2p(*c_oval)
			p_circ = self.point(c_circ)
			p_oval = self.point(c_oval)
			circ_coords.append(c_circ)
			oval_coords.append(c_oval)
			circ_vec.append(v_circ)
			oval_vec.append(v_oval)
			circ_points.append(p_circ)
			oval_points.append(p_oval)

			conn_line = DashedLine(v_circ, v_oval, **dashedline_config)
			conn_lines.append(conn_line)

		circ_point_label = Tex('(x,y)').next_to(circ_points[0],UR, buff=0)
		oval_point_label = Tex("(x',y')").next_to(oval_points[0],UR, buff=0)

		#!-------------------------------------------------------------------!#
		#* 以下是动画
		self.play(FadeIn(circ_points[0]), oval.animate.set_stroke(opacity=0.4))
		self.play(FadeIn(circ_point_label))
		self.wait(.5)

		oval_points[0].generate_target()
		oval_points[0].move_to(circ_points[0])
		self.play(
			MoveToTarget(oval_points[0]),
			Create(conn_lines[0]),
			FadeTransform(circ_point_label, oval_point_label)
		)
		self.wait()

		#!-------------------------------------------------------------------!#
		#* Formula Deductions
		self.play(*[
			m.animate.shift(LEFT*2.5)
			for m in [axes, circ, circ_points[0], oval, oval_points[0],oval_point_label,conn_lines[0]]
		])
		VGroup(*circ_points[1:]).shift(LEFT*2.5)
		VGroup(*oval_points[1:]).shift(LEFT*2.5)

		t2c = {'a': BLUE, 'b': BLUE}
		tex_config = {'color': GREY_A, 't2c': t2c}; tex_config=tex_config

		# deduction I: x'=ax -> x'/a=x
		ded_lines = VGroup(
			VGroup(Tex("x'",'=','a','x', **tex_config), Tex("y'",'=','b','y', **tex_config)),
			VGroup(Tex("{x'",'\\over',' a}','=','x', **tex_config), Tex("{y'",'\\over',' b}','=','y', **tex_config))
		)
		ded_lines[0].arrange(RIGHT, buff=MED_LARGE_BUFF)
		ded_lines[1][0].next_to(ded_lines[0][0], direction=DOWN, aligned_edge=LEFT)
		ded_lines[1][1].next_to(ded_lines[0][1], direction=DOWN, aligned_edge=LEFT)
		ded_lines.move_to(FRAME_WIDTH/4*RIGHT)
		self.play(FadeIn(ded_lines[0]))
		self.wait()

		TC = TransformFromCopy
		# build tex transform animation
		anime = []
		for i in [0,1]:
			m1, m2 = ded_lines[0][i], ded_lines[1][i]
			anime.append(TC(m1[0],m2[0]))
			anime.append(TC(m1[1],m2[3]))
			anime.append(TC(m1[2],m2[2]))
			anime.append(TC(m1[3],m2[4]))
			anime.append(FadeIn(m2[1]))

		self.play(*anime)
		self.add(ded_lines[0], ded_lines[1])
		self.wait()

		# deduction II: x^2+y^2=1 -> (x'/a)^2+(y'/b)^2=1

		tex_config = {
			'color': GREY_A, 
			'tex_to_color_map': t2c, 
			'isolate': ['x','y','a','b','^2','+','=1']
		}
		fml_circ = MTex("x^2+y^2=1", **tex_config)

		ROLLUP_SHIFT = 0.5*UP
		fml_circ.next_to(ded_lines[1],DOWN).shift(ROLLUP_SHIFT)

		term_a = r"\left(\frac{x'}{a}\right)^2"
		term_b = r"\left(\frac{y'}{b}\right)^2"
		tex_config['isolate'] += [term_a,term_b]
		fml_oval = MTex(term_a+"+"+term_b+"=1", **tex_config)
		fml_oval.next_to(ded_lines[1],DOWN).shift(ROLLUP_SHIFT)
		tex_config['isolate'] = tex_config['isolate'][:-2]

		self.play(
			ded_lines.animate.shift(ROLLUP_SHIFT),
			FadeIn(fml_circ)
		)
		self.wait()

		FT = FadeTransform; T = Transform

		ROLLUP_SHIFT = 0.2*UP
		fml_oval.shift(ROLLUP_SHIFT)

		self.play(
			FT(fml_circ.select_part('x^2'),fml_oval.select_part(term_a)),
			FT(fml_circ.select_part('y^2'),fml_oval.select_part(term_b)),
			T (fml_circ.select_part('^2',index=0),fml_oval.select_part('^2',index=0)),
			T (fml_circ.select_part('^2',index=1),fml_oval.select_part('^2',index=1)),
								  
			FT(fml_circ.select_part('=1'),fml_oval.select_part('=1')),
			FT(fml_circ.select_part('+'),fml_oval.select_part('+')),
							 
			ded_lines.animate.shift(ROLLUP_SHIFT),

			run_time=1.5
		)
		self.remove(fml_circ);
		self.add(fml_oval)

		self.wait()
		
		# 这两个动画可跳过
		tot_time=2
		self.play(*[
			ApplyMethod(circ_points[i].move_to,oval_points[i],
				run_time=tot_time,
				time_span=overlap_timespan(i-1,tot_time,7,0.6))
			for i in range(1,8)
		])
		self.wait()
		self.play(*[FadeOut(circ_point) for circ_point in circ_points[1:]])
		self.wait()

		# oval2: 从θ=PI/4处开始
		oval2 = ParametricCurve(lambda t: axes.c2p(*self.get_oval_coord(t)), t_range=[PI/4,PI/4+2*PI])
		self.play(Create(oval2), run_time=1.5)
		oval.set_stroke(opacity=1)
		self.add(oval); self.remove(oval2)
		self.wait()
		
		# deduction: x' 替换回 x
		term_a_new = r"\frac{x^2}{a^2}"
		term_b_new = r"\frac{y^2}{b^2}"
		tex_config['isolate'] += [term_a_new,term_b_new]
		fml_oval_new = MTex(term_a_new+"+"+term_b_new+"=1", **tex_config)
		fml_oval_new.move_to(fml_oval)
		oval_text = Text('椭 圆', font=文楷,font_size=60,color=YELLOW).move_to(RIGHT*3+UP*1.6)

		oval_point_label_new = circ_point_label.move_to(oval_point_label)

		δr_a = fml_oval_new.select_part(term_a_new).get_center()-fml_oval.select_part(term_a).get_center()
		self.play(
			FadeOut(fml_oval.select_part(term_a),shift=δr_a),FadeIn(fml_oval_new.select_part(term_a_new),shift=δr_a),
			FadeOut(fml_oval.select_part(term_b)),FadeIn(fml_oval_new.select_part(term_b_new)),
								  
			FT(fml_oval.select_part('=1'),fml_oval_new.select_part('=1')),
			FT(fml_oval.select_part('+'),fml_oval_new.select_part('+')),

			FT(oval_point_label, oval_point_label_new),
							 
			run_time=1
		)
		self.wait(.5)

		# '完全得到了椭圆的方程'
		self.play(
			FadeOut(ded_lines), fml_oval_new.animate.shift(UP),
			FadeIn(oval_text),
			circ.animate.set_stroke(opacity=0.3),
			circ_points[0].animate.set_fill(opacity=0.3),
			conn_lines[0].animate.set_stroke(opacity=0.3)	
		)
		self.wait()

		# '这就是每个椭圆内隐藏的圆'
		
		self.play(
			circ.animate.set_stroke(YELLOW, 6, 1),
			rate_func = emphasize(0.5,1),run_time=2
		)
		self.wait()

		self.stop_skipping()
		zerodef_text = Text('第零定义',font=文楷,font_size=50,color=YELLOW_B) \
			.move_to((oval_text.get_bottom()+fml_oval_new.get_top())/2).align_to(oval_text,LEFT)
		oval_text.generate_target().shift(UP*0.4)
		#oval_text.target[1].shift(LEFT*0.2)
		self.play(
			MoveToTarget(oval_text),
			FadeIn(zerodef_text),
			fml_oval_new.animate.shift(DOWN/2),
		)
		self.wait()

		transform_text = Text('单位圆变换',font=文楷,font_size=50,color=YELLOW_B) \
			.next_to(zerodef_text,DOWN,buff=0.4).align_to(oval_text,LEFT)
		self.play(
			FadeIn(transform_text),
			fml_oval_new.animate.shift(DOWN*.8),
		)
		self.wait()


class ProblemSolvingSchemeBasedOnTransform(OvalScene):
	def construct(self) -> None:
		self.construct_elements()
		self.do_animation()

	def construct_elements(self):
		self.init_axes(
			width=3, height=2,
			include_numbers = False,
			axis_config = {
				'include_tip': False,
				'include_label': False,
				'include_ticks': False
			},
			
		)
		a=1.7; b=1
		self.init_oval(a,b)
		axes, oval, circ = self.axes, self.oval, self.unit_circ
		axes.set_stroke(width=2)

		line_oval = Line(axes.c2p(0.3,-2.2),axes.c2p(1.2,2))
		group_LU = VGroup(axes, oval, line_oval)
		oval.move_to(axes.get_origin())
		group_LU.move_to(LEFT*FRAME_WIDTH/4+UP*FRAME_HEIGHT/4)

		axes = axes.copy()
		line_circ = Line(axes.c2p(0.2,-2),axes.c2p(0.8,2))
		group_LD = VGroup(axes, circ, line_circ)
		circ.move_to(axes.get_origin())
		group_LD.move_to(LEFT*FRAME_WIDTH/4+DOWN*FRAME_HEIGHT/4)

		# 右下块
		answer_txt = Text('Answer', color=GREEN)
		circ_subscript = Text('圆',font=宋体, color=BLUE).scale(0.7)
		circ_subscript.next_to(answer_txt, DR, buff=0).shift(UP*0.1)
		group_RD = VGroup(answer_txt, circ_subscript)
		group_RD.move_to(RIGHT*FRAME_WIDTH/4+DOWN*FRAME_HEIGHT/4)

		answer_txt = answer_txt.copy()
		oval_subscript = Text('椭圆',font=宋体, color=BLUE).scale(0.7)
		oval_subscript.next_to(answer_txt, DR, buff=0).shift(UP*0.1)
		group_RU = VGroup(answer_txt, oval_subscript)
		group_RU.move_to(RIGHT*FRAME_WIDTH/4+UP*FRAME_HEIGHT/4)

		# 箭头
		arrow_L = Tex(r'\Rightarrow', color=FML_COLOR).stretch(0.8, YDIM)
		arrow_R = Tex(r'\Rightarrow', color=FML_COLOR).stretch(0.8, YDIM)
		arrow_D = Tex(r'\Longrightarrow', color=FML_COLOR).stretch(0.8, YDIM)
		arrow_U = Tex(r'\Longrightarrow', color=FML_COLOR).stretch(0.8, YDIM)
		arrow_L.scale(3).rotate(-PI/2)
		arrow_R.scale(3).rotate(+PI/2)
		arrow_D.scale(3).stretch(0.8,YDIM)
		arrow_U.scale(3).stretch(0.8,YDIM)
		arrow_L.move_to(LEFT*FRAME_WIDTH/4)
		arrow_R.move_to(RIGHT*FRAME_WIDTH/4)
		arrow_D.move_to(DOWN*FRAME_HEIGHT/4)
		arrow_U.move_to(UP*FRAME_HEIGHT/4)

		self.group_LU, self.group_LD = group_LU, group_LD
		self.group_RU, self.group_RD = group_RU, group_RD
		self.arrow_L, self.arrow_R = arrow_L, arrow_R
		self.arrow_U, self.arrow_D = arrow_U, arrow_D

	def do_animation(self):
		group_LU, group_LD = self.group_LU, self.group_LD
		group_RU, group_RD = self.group_RU, self.group_RD
		arrow_L, arrow_R = self.arrow_L, self.arrow_R
		arrow_U, arrow_D = self.arrow_U, self.arrow_D

		def 日光灯(alpha):
			if 0.15<alpha<0.3 or 0.4<alpha<0.6 or alpha>0.8: return 1
			return 0
		
		#self.play(arrow_L.animate.set_color(WHITE))
		#highlight = VHighlight(arrow_L, max_stroke_addition=20, color_bounds=(GREY_B, GREY_E))
		#self.play(FadeIn(highlight), arrow_L.animate.set_color(WHITE))

		#arrow_L.set_color(GREY_D)
		#self.play(arrow_L.animate.set_color(WHITE), rate_func=日光灯, run_time=1)

		text_hard = Text('难',font=文楷,color=RED).next_to(arrow_U,UP,buff=SMALL_BUFF)
		text_easy = Text('简单',font=文楷,color=GREEN).next_to(arrow_D,DOWN,buff=SMALL_BUFF)
		text_solve = Text('求解',font=文楷,color=FML_COLOR).next_to(arrow_D,UP,buff=SMALL_BUFF)
		text_transform = Text('变换',font=文楷,color=FML_COLOR).next_to(arrow_L,LEFT)
		text_mapping = Text('映射',font=文楷,color=FML_COLOR).next_to(arrow_R,RIGHT)
		text_mapping.set_opacity(0) # disabled
		arrow_D.stretch(1.2,XDIM)

		pl = self.play
		wait = self.wait

		pl(LaggedStart(
			FadeIn(group_LD),
			FadeIn(VGroup(text_solve,text_easy,arrow_D),shift=RIGHT),
			FadeIn(group_RD,shift=0.5*RIGHT),
			lag_ratio=0.1)
		)
		wait()

		pl(FadeIn(group_LU))
		wait()
		pl(FadeIn(VGroup(arrow_L,text_transform),shift=DOWN*0.5))
		wait()

		VGroup(arrow_U,text_hard).set_opacity(0.5)
		pl(LaggedStart(FadeIn(arrow_U,shift=RIGHT*0.5),FadeIn(text_hard),lag_ratio=0.1))
		wait()

		pl(LaggedStart(
			FadeIn(VGroup(text_mapping,arrow_R),shift=UP*0.5),
			FadeIn(group_RU),
			lag_ratio=0.1)
		)
		wait()

#!-------------------------------------------------------------------!#
#* Part I: Area Transform


class AreaPartStart(StarskyScene):
	def construct(self):
		kw = {'font': 文楷}
		title = Text('1. 面积',font_size=100,**kw)
		trans = TextGroup('面积', '→ ', 'ab x ','面积')
		trans.scale(1.2)#.set_color(WHITE)
		trans[2].set_color(BLUE_B)
		trans.next_to(title,DOWN).shift(UP*.5)

		self.play(FadeIn(title))
		self.wait()
		self.play(title.animate.shift(UL+DOWN*.3),Write(trans[0],time_span=[0.5,2]))
		self.wait(.5)
		self.play(Write(trans[1:],run_time=1.5))
		self.wait(2)
		self.play(FadeOut(title),FadeOut(trans),run_time=.7)

class TrigAreaTransform(StarskyScene):
	def construct(self) -> None:
		#!-------------------------------------------------------------------!#
		#* 三角形及其分割

		trig_config = {'stroke_color': BLUE_B, 'fill_color': BLUE_E, 'fill_opacity': 1}
		# 一个最一般的三角形
		trig = Polygon(RIGHT, UP, DL, **trig_config)
		# 上下半平面
		upper = Rectangle(width=FRAME_WIDTH, height=FRAME_HEIGHT/2)
		lower = upper.copy()
		upper.to_edge(UP, buff=0); lower.to_edge(DOWN, buff=0)
		# 分割出的两个三角形
		trig_up = Intersection(trig, upper, **trig_config)
		trig_down=Intersection(trig, lower, **trig_config)
		#分割线
		dashedline_config = {
			'dash_length':0.16, 
			'positive_space_ratio':0.6
		}
		delim = DashedLine(LEFT, RIGHT*1.5, **dashedline_config)
		
		self.play(FadeIn(trig))
		self.wait()
		self.play(Create(delim), )
		#self.play(FadeIn(trig_up), FadeIn(trig_down), delim.animate.shift(ORIGIN))
		self.add(trig_up, trig_down)
		self.remove(trig)
		self.play(trig_up.animate.shift(UP/2), trig_down.animate.shift(DOWN/2))
		self.play(FadeOut(delim))

		#!-------------------------------------------------------------------!#
		#* under transform
		a, b=1.5, 1.7

		height_mark = LengthMark(ORIGIN, UP).add_updater(lambda m: m.next_to(trig_up, LEFT).align_to(trig_up, DOWN))
		width_mark = LengthMark(LEFT/2, RIGHT).add_updater(lambda m: m.next_to(trig_up, DOWN).align_to(trig_up, LEFT))

		lines = VGroup(
			TextGroup('底', ' → ', 'a', ' x 底'),
			TextGroup('高', ' → ', 'b', ' x 高'),
			TextGroup('面积=底x高/2 ', '→ ', 'ab',' x 面积')
		)
		for i,m in enumerate([lines[0][2], lines[1][2], lines[2][2]]):
			m.set_color(BLUE)
			m.align_to(lines[0],DOWN).shift(UP*0.05)
		lines[2][1:].next_to(lines[2][0],DOWN).shift(RIGHT*0.63)
		lines.arrange(DOWN); 
		lines[2].align_to(lines[1],LEFT); lines[2].shift(DOWN/2)
		lines.move_to(FRAME_WIDTH/5*RIGHT)

		# construction dones, now animations
		group = VGroup(trig_up, trig_down)
		self.play(group.animate.move_to(FRAME_WIDTH/5*LEFT),)

		# a COMPOSED animation for length mark showcase
		#width_mark.set_start_and_end(ORIGIN, ORIGIN+RIGHT*1e-6)
		width_mark.generate_target(); width_mark.shrink_to_start()
		self.play(FadeIn(width_mark), run_time=0.3)
		self.play(
			#width_mark.animate.set_start_and_end(LEFT/2, RIGHT),
			MoveToTarget(width_mark),
			FadeIn(lines[0][0],shift=RIGHT)
		)
		self.wait()
	
		# XDIM stretch
		group.add(width_mark)
		self.play(
			group.animate.stretch(a,XDIM, about_point=trig_up.get_bottom()),
			FadeIn(lines[0][1:])
		)
		self.wait(2)
		self.remove(group); self.add(*group)  #reorganize

		# height mark showcase
		height_mark.generate_target(); height_mark.shrink_to_start()
		self.play(FadeIn(height_mark), run_time=0.3)
		self.play(
			#height_mark.animate.set_start_and_end(ORIGIN, UP),
			MoveToTarget(height_mark),
			FadeIn(lines[1][0], shift=UP)
		)
		self.wait()

		# YDIM stretch
		group = VGroup(trig_up, height_mark)
		self.play(
			group.animate.stretch(b,YDIM, about_point=trig_up.get_bottom()),
			trig_down.animate.stretch(b,YDIM, about_point=trig_down.get_top()),
			FadeIn(lines[1][1:])		   
		)
		self.wait()

		# 面积变化
		def double_blink(alpha):
			if alpha<=0.5: return there_and_back(2*alpha)
			else: return there_and_back(2*(alpha-0.5))

		self.play(FadeIn(lines[2][0]))
		self.play(
			ApplyMethod(
				VGroup(trig_up,trig_down).set_fill, BLUE, 
				rate_func=double_blink,run_time=1.3
		))
		self.wait()

		self.play(
			FadeIn(lines[2][1:], shift=RIGHT),
		)

		self.wait()
		self.play(*[
			FadeOut(m) for m in self.mobjects
		])

class IrrAreaTransform(StencilScene):
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.fix_stencil_border = False # True

	def construct(self) -> None:
		self.construct_elements()
		self.show_elements()
		#self.fade_all()

	def construct_elements(self) -> None:
		_ = SVGMobject('arb_area.svg').scale(1.5)
		area = VMobject()
		area.set_points(_[0].get_points())
		#self.add(area)

		bb = SurroundingRectangle(area).scale(1.1)

		# type: scalar. 
		# Interesting fact: np.float64与py内置的float不一样
		# 为了能在range中使用需要转换 —— 但我直接使用了np.arange
		left, right = bb.get_left()[XDIM], bb.get_right()[XDIM]
		top, bottom = bb.get_top()[YDIM], bb.get_bottom()[YDIM]
		
		eps = 1e-6; line_interval = 0.2

		line_config = {'stroke_width': 1, 'stroke_color':GREY_B}
		vlines, hlines = VGroup(), VGroup()
		δ = 0.2 # 为了让边缘的网格线条少一点——that looks better.
		for x in np.arange(left+δ, right-δ+eps, line_interval):
			line = Line(
				start = np.array([x, bottom, 0]),
				end   = np.array([x,  top  , 0]),
				**line_config
			)
			vlines.add(line)
		for y in np.arange(bottom+δ, top-δ+eps, line_interval):
			line = Line(
				start = np.array([left,  y, 0]),
				end   = np.array([right, y, 0]),
				**line_config
			)
			hlines.add(line)
		
		stencil = area.copy().scale(1.2, about_point=area.get_center()+RIGHT*0.2) \
				  .set_style(stroke_width=0, fill_opacity=0.01)
		snode_grid = StencilGroup(stencil, VGroup(vlines, hlines))

		tiny_area_config = {'stroke_width': 0, 'fill_color': TEAL, 'fill_opacity': 0}
		tiny_areas = VGroup()
		for y in np.arange(bottom+δ, top-δ+eps, line_interval)[::-1]:
			for x in np.arange(left+δ, right-δ+eps, line_interval):
				tiny_area = Rectangle(line_interval, line_interval, **tiny_area_config)
				tiny_area.next_to( np.array([x, y, 0]), UR, buff=0 )
				tiny_areas.add(tiny_area)

		nv = len(np.arange(bottom+δ, top-δ+eps, line_interval))
		nh = len(np.arange(left+δ, right-δ+eps, line_interval))

		stencil = area.copy().set_style(stroke_width=0, fill_opacity=0.01)
		if self.fix_stencil_border:
			self.modify_shader_for_stencil(stencil)

		#stencil = bb.copy().scale(0.8).set_style(stroke_width=0, fill_opacity=0.01)
		snode_area = StencilGroup(stencil, tiny_areas)

		s=self
		s.area = area
		s.vlines, s.hlines = vlines, hlines
		s.snode_grid = snode_grid
		s.tiny_areas = tiny_areas
		s.nv, s.nh = nv, nh
		s.line_interval = line_interval
		s.snode_area = snode_area
		s.stencil = stencil

	def show_elements(self):
		s=self
		area = s.area
		vlines, hlines = s.vlines, s.hlines
		snode_grid = s.snode_grid
		tiny_areas = s.tiny_areas
		nv, nh = s.nv, s.nh
		line_interval = s.line_interval
		snode_area = s.snode_area
		
		self.play(Create(area)); self.wait()
		
		self.add(snode_grid)
		self.play(Create(vlines), Create(hlines), reorganize_mobjects=False, run_time=2)
		self.wait()

		# 从左上到右下滚动效果
		self.add(snode_area)
		#self.bring_to_front(snode_grid)
		animations = []
		def overlap_timespan(k,T,n,overlap_ratio):
			α = overlap_ratio
			t = T / ( 1+(n-1)*(1-α) )
			return [k*(1-α)*t, k*(1-α)*t+t]
		
		# 每个图形
		for i in range(nv):
			for j in range(nh):
				arg = [tiny_areas[i*nh+j].set_opacity, 1]
				animations.append(ApplyMethod(
					*arg,
					rate_func = there_and_back, 
					time_span = overlap_timespan(i+j, 2, nv+nh-1, 0.9)
				))

		self.play(*animations, reorganize_mobjects = False)
		self.wait()

		animations = []
		def across_border(tiny_area):
			m = Intersection(area, tiny_areas[i*nh+j])
			return get_norm(m.get_area_vector())<get_norm(tiny_area.get_area_vector())-2e-5
		
		tiny_areas.set_fill(TEAL_B)
		for i in range(nv):
			for j in range(nh):
				if across_border(tiny_areas[i*nh+j]):
					tiny_areas[i*nh+j].set_color(GREY_C)
					arg = [tiny_areas[i*nh+j].set_opacity, .6]
				else:
					arg = [tiny_areas[i*nh+j].set_opacity, 1]
				animations.append(ApplyMethod(
					*arg,
					#rate_func = there_and_back, 
					time_span = overlap_timespan(i+j, 2, nv+nh-1, 0.9)
				))
		self.play(*animations, reorganize_mobjects = False)
		self.wait()
		
		#!-------------------------------------------------------------------!#
		#* 小矩形褪色
		animations=[]
		for i in range(nv):
			for j in range(nh):
				arg = [tiny_areas[i*nh+j].set_opacity, 0]
				animations.append(ApplyMethod(
					*arg,
					#rate_func = there_and_back, 
					time_span = overlap_timespan(i+j, 2, nv+nh-1, 0.9)
				))
		
		self.play(*animations, reorganize_mobjects = False)
		tiny_areas.set_fill(TEAL)
		self.wait()

		group = Group(area, snode_grid, snode_area)
		self.play(*[
			m.animate.shift(LEFT*2.5)
			for m in group
		])
		self.wait()

		#if self.fix_stencil_border:
		#	return
		
		#!-------------------------------------------------------------------!#
		#* now transform

		highlight_cell_idx = (nv//2-1, nh//2)
		highlight_cell = tiny_areas[highlight_cell_idx[0]*nh+highlight_cell_idx[1]]

		# construct zoom in camera
		detail = CameraCapture(self.camera.ctx, camera_class=StencilCamera).shift(RIGHT*3)
		def updater(m: CameraCapture):
			detail.camera.fbo_msaa.use(); 
			detail.camera.fbo_msaa.clear()
			detail.camera.capture(*self.mobjects)
			detail.camera.refresh_static_mobjects()
		detail.add_updater(updater)

		# shape of the zoom in part
		upper=1; down=0; left=0; right=1
		detail.data['im_coords']=np.array([(left, upper), (left, down), (right, upper), (right, down)])
		detail.camera.frame.set_width(detail.camera.frame.get_height(),stretch=True)
		detail.set_width(detail.get_height(),stretch=True)
		#capture_bb=SurroundingRectangle(detail, buff=0).add_updater(lambda m:m.surround(detail, buff=0, stretch=True))
		zoomin_bb=SurroundingRectangle(detail.camera.frame, buff=0.) \
			.add_updater(lambda m:m.surround(detail.camera.frame, buff=0.02, stretch=True)) \
			#.add_updater(lambda m:self.bring_to_front(m))
		
		zoomin_lines = VGroup(
			Line(),Line()
		)
		zoomin_lines.set_stroke(WHITE, 7)
		zoomin_lines_bs = zoomin_lines.copy().set_stroke(BG_COLOR, 18)
		def updater(m):
			m[0].put_start_and_end_on(highlight_cell.get_center()+DR*0.22,detail.get_center()+DL*2+UP*0.05)
			m[1].put_start_and_end_on(highlight_cell.get_center()+UR*0.22,detail.get_center()+UL*2-UP*0.05)
			#self.bring_to_front(m)
		zoomin_lines.add_updater(updater)
		zoomin_lines_bs.add_updater(updater)
		
		group_center = area.get_center()
		detail.camera.frame.add_updater(lambda m: m.move_to(highlight_cell))
		zoomin_scale = ValueTracker(1) # should be synced with detail.camera
		def stroke_sf_notifier(m):
			detail.camera.stroke_sf=zoomin_scale.get_value()
		detail.add_updater(stroke_sf_notifier)
		
		self.add(detail, detail.camera.frame)
		detail.camera.frame.scale(0.1); zoomin_scale.set_value(10)
		detail.camera.refresh_static_mobjects()	

		# FadeIn!
		self.play(
			highlight_cell.animate.set_opacity(1),
			Create(zoomin_lines_bs), Create(zoomin_lines), FadeIn(zoomin_bb), FadeIn(detail), 
			detail.camera.frame.animate.scale(0.5),
			zoomin_scale.animate.set_value(10*2)
		); self.wait()
	
		a, b = 1.2, 1.3

		width_mark       = LengthMark(LEFT, RIGHT).add_updater(lambda m: m.next_to(detail,DOWN))
		height_mark      = LengthMark(DOWN, UP).add_updater(lambda m: m.next_to(detail,LEFT))
		width_label      = Tex('dx', color=FML_COLOR).add_updater(lambda m: m.next_to(width_mark, DOWN))
		height_label     = Tex('dy', color=FML_COLOR).add_updater(lambda m: m.next_to(height_mark, LEFT))
		width_label_new  = Tex('a','dx', color=FML_COLOR).add_updater(lambda m: m.next_to(width_mark, DOWN))
		height_label_new = Tex('b','dy', color=FML_COLOR).add_updater(lambda m: m.next_to(height_mark, LEFT,buff=MED_SMALL_BUFF))
		width_label_new[0] .set_color(BLUE)
		height_label_new[0].set_color(BLUE)

		# 又一个坑爹的bug：前面修改shader代码之后会导致其它矢量对象的渲染方式也改了，没有了
		# smooth_step_AA 的公式很丑。
		# debug后已经排除可能导致问题的点位有：1)从文件读取代码的filename_to_code_map 缓存机制
		# 2)camera的id_to_shader_program缓存机制 3)排查Tex对象的shader代码也发现没有改变
		# 4)将原来对象的shader代码改回去也没有好转。
		# 于是，只好渲染两段，通过后期拼接在一起。

		self.play(FadeIn(width_mark), FadeIn(width_label))
		self.wait()

		self.play(
			*[
				m.animate.stretch(a,XDIM,about_point=group_center)
				for m in group
			],
			width_mark.animate.stretch(a,XDIM,about_point=group_center),
			FadeTransform(width_label,width_label_new),
			run_time=1,
			reorganize_mobjects = False
		)
		self.wait()
		self.play(FadeIn(height_mark),FadeIn(height_label))
		self.wait()
		self.play(
			*[
				m.animate.stretch(b,YDIM,about_point=group_center)
				for m in group
			],
			height_mark.animate.stretch(b,YDIM,about_point=group_center),
			FadeTransform(height_label,height_label_new),
			run_time=1,
			reorganize_mobjects = False
		)
		detail.camera.refresh_static_mobjects()
		self.wait()

		dS_label=Tex('S=dxdy',stroke_color=WHITE)
		
		dS_label_new=Tex(r'ab\cdot S')
		dS_label.move_to(detail)
		dS_label_new.move_to(detail)
		self.play(Write(dS_label))
		self.wait()
		self.play(FadeTransform(dS_label, dS_label_new))
		self.wait()

		self.play(*[
			FadeOut(m) for m in
			self.mobjects if (not m in group)
		])
		self.wait()

	def fade_all(self):
		self.play(*[
			FadeOut(m) for m in
			self.mobjects
			#[detail, width_mark, height_mark, width_label_new, height_label_new, dS_label_new]
		])

	@staticmethod
	def modify_shader_for_stencil(mobj: VMobject):
		# Modify bezier curve fill shader so that they use hard discarding
		# to get rid of fragments outside a curve instead of soft discarding.
		# Hard discarding(discard;) will not write into stencil, while
		# soft discarding (alpha*=smoothstep(1,0,sdf();) will still write 
		# fragments into stencil, though they're perceptually invisible.
		all_shaders = mobj.get_shader_wrapper_list()
		for shader in all_shaders:
			if shader.shader_folder=='quadratic_bezier_fill':
				frag_shader = shader
				break
		# 注意replace_code里使用正则表达式进行替换
		# 因此原代码段中的re字符需要escape。
		SOFT_DISCARD = "frag_color.a *= smoothstep(1, 0, sdf() / uv_anti_alias_width);"
		HARD_DISCARD = 'if(sdf()>0) discard;'

		frag_shader.replace_code(
			re.escape(SOFT_DISCARD),
			HARD_DISCARD
		)

class AreaTransformCalculusDeduction(StarskyScene):
	def construct(self) -> None:
		self.construct_formula()
		self.do_animations()

	def construct_formula(self):
		#!-------------------------------------------------------------------!#
		#* construct latex kwargs

		# 默认的latex模板中有宏包wasysym，会导致重积分号(\iint)变得不好看。
		# 因此要把它去掉。
		preamble=r"""
			\usepackage[english]{babel}
			\usepackage{amsmath}
			\usepackage{amssymb}
			\usepackage{dsfont}
			\usepackage{setspace}
			\usepackage{tipa}
			\usepackage{relsize}
			\usepackage{textcomp}
			\usepackage{mathrsfs}
			\usepackage{calligra}
			\usepackage{ragged2e}
			\usepackage{physics}
			\usepackage{xcolor}
			\usepackage{microtype}
			\usepackage{pifont}
		"""
		t2c = {'a': BLUE, 'b': BLUE, r'\mathrm{Area}': TEAL}
		isolate = ['=', 'a', 'b']
		tex_config = {
			'template': 'empty',
			'additional_preamble': preamble,
			'color': GREY_A, 
			'isolate': isolate,
			'tex_to_color_map': t2c
		}; kw=tex_config

		ded_lines = VGroup(
			MTex(r'\mathrm{Area}=\iint_S\mathrm{d}x\,\mathrm{d}y', **kw),
			MTex(r"\mathrm{Area}'=\iint_{S'}\mathrm{d}x'\mathrm{d}y'",**kw),
			MTex(r"====\iint_S\mathrm{d}(ax)\mathrm{d}(by)",**kw),
			MTex(r"=ab\iint_S\mathrm{d}x\,\mathrm{d}y",**kw),
			MTex(r"=ab\cdot\mathrm{Area}",**kw)
		)
		#kw=dict()
		hint = VGroup(MTex(r"x'=ax",**kw), MTex(r"y'=by", **kw))

		def next_line_by_equiv(prev_row: MTex, row: MTex):
			i = prev_row.get_submob_indices_lists_by_selector('=')[-1][0]
			j =      row.get_submob_indices_lists_by_selector('=')[-1][0]
			row.next_to(prev_row,DOWN)
			# get_center返回的是mobject中bb变量的切片... 
			# 会产生变量纠缠问题。需要copy一下去除纠缠。
			r1=row[j].get_center().copy()
			row[j].align_to(prev_row[i],LEFT)
			r2=row[j].get_center()
			Δr=r2-r1
			row[j].shift(-Δr)
			row.shift(Δr)

		ded_lines.arrange(DOWN)
		for row in range(1,len(ded_lines)):
			next_line_by_equiv(ded_lines[row-1],ded_lines[row])
		#ded_lines[-1].next_to(ded_lines[-2],RIGHT).shift(UP*0.08)

		#hint[0][3].set_color(BLUE) # x'=[a]x
		#hint[1][3].set_color(BLUE) # y'=[b]
		hint.scale(0.7)
		tmp = VGroup(ded_lines[2][1:3])
		hint[0].next_to(tmp, UP,buff=0.1)
		hint[1].next_to(tmp, DOWN,buff=0.1)
		ded_lines[0].shift(UP*0.3)

		ded_lines.replace_submobject(2,VGroup(hint, ded_lines[2]))
		ded_lines.shift(RIGHT*3)

		self.ded_lines = ded_lines
	
	def do_animations(self):
		ded_lines = self.ded_lines

		self.play(FadeIn(ded_lines[0]))
		self.wait()
		self.play(LaggedStart(*[FadeIn(line,shift=UP) for line in ded_lines[1:]],lag_ratio=0.08))
		self.wait()

class OvalAreaProblem(OvalScene):
	def construct(self) -> None:
		self.construct_elements()
		self.do_animations()
		
	def construct_elements(self):
		a, b = 1.6, 1.2
		self.init_axes(include_numbers=False)
		self.init_oval(a, b)
		axes, oval, circ = self.axes, self.oval, self.unit_circ
		
		circ.set_fill(color=BLUE, opacity=0.8)
		oval.set_fill(color=BLUE, opacity=0.8)
		circ_axes = axes
		oval_axes = axes.copy()
		circ.add_updater(lambda m: m.move_to(circ_axes.c2p(0,0)))
		oval.add_updater(lambda m: m.move_to(oval_axes.c2p(0,0)))

		t2c = {'a':BLUE, 'b':BLUE}
		tex_config = {'font_size': 70, 't2c':t2c}
		circ_fml = Tex('S',r'=\pi r^2',**tex_config)
		circ_fml_2 = Tex(r'=\pi',**tex_config)
		oval_fml = Tex('S',r'=\pi',' a','b',**tex_config)
		circ_fml.add_updater(lambda m: m.next_to(circ_axes.c2p(.4,-1.5),RIGHT))
		oval_fml.add_updater(lambda m: m.next_to(oval_axes.c2p(.7,-1.5),RIGHT))
		circ_text = Text('圆',font=文楷)
		oval_text = Text('椭圆',font=文楷,color=YELLOW)

		self.axes = axes
		self.circ, self.circ_axes = circ, circ_axes
		self.oval, self.oval_axes = oval, oval_axes
		self.circ_fml, self.oval_fml = circ_fml, oval_fml
		self.circ_fml_2 = circ_fml_2
		self.circ_text, self.oval_text = circ_text, oval_text

	def do_animations(self):
		axes = self.axes
		circ, circ_axes = self.circ, self.circ_axes
		oval, oval_axes = self.oval, self.oval_axes
		circ_fml, oval_fml = self.circ_fml, self.oval_fml
		circ_fml_2 = self.circ_fml_2
		circ_text, oval_text = self.circ_text, self.oval_text

		self.stop_skipping()
		circ_text.move_to(circ_axes.c2p(1.5,+1.5))
		tmp=circ.copy().set_stroke(WHITE,0)
		circ.set_fill(opacity=0)
		self.play(
			Create(axes),
			FadeIn(tmp,time_span=[.5,1.5]),
			Create(circ),
			FadeIn(circ_text),
			run_time=1.5
		)
		circ_text.add_updater(lambda m: m.move_to(circ_axes.c2p(1.5,+1.5)))
		oval_text.add_updater(lambda m: m.move_to(oval_axes.c2p(2,+1.5)))
		circ.set_fill(color=BLUE, opacity=0.8)
		self.remove(tmp)
		self.wait()

		self.play(Write(circ_fml)); 
		self.wait()
		circ_fml_2.next_to(circ_fml[0],RIGHT).align_to(circ_fml,DOWN)
		self.play(FadeOut(circ_fml[1:]),FadeIn(circ_fml_2,shift=LEFT))
		circ_fml.replace_submobject(1,circ_fml_2[0]) # 替换mobj的话，会改变next_to的相对位置...
		
		LEFT_HALF = FRAME_WIDTH/5*LEFT
		RIGHT_HALF = FRAME_WIDTH/5*RIGHT

		self.play(
			TransformFromCopy(circ,oval),
			
			circ_fml.animate.set_opacity(opacity=0.3),
		); self.wait()
		self.add(oval_axes); self.bring_to_back(oval_axes)

		self.add(oval_axes, oval)
		self.play(
			FadeIn(oval_text),
			circ_axes.animate.move_to(LEFT_HALF),
			oval_axes.animate.move_to(RIGHT_HALF),
			circ_fml.animate.set_opacity(opacity=1),
			reorganize_mobjects=False
		); self.wait()

		oval_fml.update()
		self.play(Write(oval_fml))

		self.wait()
		self.play(FadeIn(Curtain()))
		
class ComplicatedAreaProblem(OvalScene):
	def construct(self) -> None:
		self.construct_geometry_elements()
		self.show_geometry_elements_and_bind_constrains()
		self.transform_to_unit_circle()
		self.analyze_after_transform()

		self.solve_and_summarize()
		self.fade_all()

	def construct_geometry_elements(self):
		# parameters
		aa, bb = ValueTracker(2), ValueTracker(1.4)
		a,b = aa.get_value(), bb.get_value()
		self.init_axes()
		self.init_oval(a,b)
		axes, oval = self.axes, self.oval

		# positioning are postponed
		P,A,B,O = self.point(color=WHITE)*4 # see Mobject.__mul__
		P.set_color(YELLOW)
		P.label = Tex('P') # empty now
		A.label = Tex('A')
		B.label = Tex('B')
		O.label = Tex('O')

		trig_config = {'fill_color': BLUE, 'fill_opacity': 0.7}
		_ = ORIGIN
		trig = Polygon(_,_,_, **trig_config)
		
		# parameters
		pp = ValueTracker(0.7)
		mm = ValueTracker(1)

		def geometry_controller(_: Mobject):
			a, b = aa.get_value(), bb.get_value()
			p, m = pp.get_value(), mm.get_value()

			# LC for Logical Coordinates
			P_LC = (p,0)
			A_LC,B_LC = self.calc_line_oval_intersection(a,b, m,p)

			# MC for Manim Coordinates
			P_MC = self.axes.c2p(*P_LC)
			A_MC = self.axes.c2p(*A_LC)
			B_MC = self.axes.c2p(*B_LC)
			O_MC = self.axes.c2p(0, 0)

			P.move_to(P_MC)
			A.move_to(A_MC)
			B.move_to(B_MC)
			O.move_to(O_MC)

			trig.vertices = [A_MC, B_MC, O_MC]
			trig.set_points_as_corners([*trig.vertices, trig.vertices[0]])

			LABEL_BUFF = MED_LARGE_BUFF
			OA_MC = A_MC - O_MC
			OB_MC = B_MC - O_MC
			P.label.next_to(P,DR,buff=0)
			A.label.move_to(A_MC+normalize(OA_MC)*LABEL_BUFF)
			B.label.move_to(B_MC+normalize(OB_MC)*LABEL_BUFF)
			O.label.next_to(O,DL,buff=SMALL_BUFF)
		
		geometry_controller(None)

		# text lines
		oval_fml = MTex(r'\frac{x^2}{a^2}+\frac{y^2}{b^2}=1', 
			tex_to_color_map = {'a^2':BLUE, 'b^2':BLUE},color=FML_COLOR) \
			.to_corner(UR, buff=1.1)
		prob_descrp = VGroup(
			Text('求',font=文楷,color=YELLOW),
			MTex(r'S_{\triangle\mathrm{OAB}}'),
			Text('的最大值',font=文楷,color=YELLOW),
		).arrange(RIGHT).scale(.8)
		#prob_descrp[0].next_to(prob_descrp[1],UP).align_to(prob_descrp[1],LEFT)
		prob_descrp.next_to(oval_fml,DOWN,buff=.4)

		self.axes, self.oval = axes, oval
		self.oval_fml, self.prob_descrp= oval_fml, prob_descrp
		self.aa, self.bb, self.pp, self.mm = aa, bb, pp, mm
		self.A, self.A.label, self.B, self.B.label = A, A.label, B, B.label
		self.P, self.P.label, self.O, self.O.label = P, P.label, O, O.label
		self.trig = trig
		self.geometry_controller = geometry_controller
		
	def show_geometry_elements_and_bind_constrains(self):
		#* precondition *#
		axes, oval = self.axes, self.oval
		oval_fml, prob_descrp= self.oval_fml, self.prob_descrp
		aa, bb, pp, mm = self.aa, self.bb, self.pp, self.mm
		A, A.label, B, B.label = self.A, self.A.label, self.B, self.B.label
		P, P.label, O, O.label = self.P, self.P.label, self.O, self.O.label
		trig = self.trig
		geometry_controller = self.geometry_controller

		self.play(Create(axes), Create(oval))
		self.wait()
		self.play(Write(oval_fml))
		self.wait()
		self.play(FadeIn(P),FadeIn(P.label))
		self.wait()
		line_AB = Line(A.get_center(),B.get_center()).scale(1.4,about_point=P.get_center())
		self.play(
			Create(line_AB),
			FadeIn(VGroup(A,A.label),time_span=[0,1]),
			FadeIn(VGroup(B,B.label),time_span=[.3,1.3])
		)
		self.wait()
		
		trig_tmp1 = Polygon(B.get_center(),O.get_center(),A.get_center()).match_style(trig)
		trig_tmp2 = trig_tmp1.copy().set_stroke(opacity=0)
		trig_tmp1.set_fill(opacity=0)
		self.play(
			FadeIn(trig_tmp2), Create(trig_tmp1), 
			FadeIn(VGroup(O,O.label)), FadeOut(line_AB),
			Write(prob_descrp),
			Animation(P),
			run_time=2
		)

		self.remove(trig_tmp1, trig_tmp2); self.add(trig)
		self.wait()
		
		self.add(trig,P,A,B,O,P.label,A.label,B.label,O.label)
		P.add_updater(geometry_controller)
		self.hint_dynamic(
			P,A,B,O,
			P.label,A.label,B.label,O.label,
			trig
		)

	def transform_to_unit_circle(self):
		#* precondition *#
		axes, oval = self.axes, self.oval
		oval_fml, prob_descrp= self.oval_fml, self.prob_descrp
		aa, bb, pp, mm = self.aa, self.bb, self.pp, self.mm
		A, A.label, B, B.label = self.A, self.A.label, self.B, self.B.label
		P, P.label, O, O.label = self.P, self.P.label, self.O, self.O.label
		trig = self.trig

		a,b,p,m=aa.get_value(),bb.get_value(),pp.get_value(),mm.get_value()
		self.play(
			oval.animate.stretch(1/a,XDIM,about_point=axes.c2p(0,0)),
			aa.animate.set_value(1),
			pp.animate.set_value(p/a),mm.animate.set_value(m*1/a)
		)
		self.wait()
		p,m=pp.get_value(),mm.get_value()
		self.play(
			oval.animate.stretch(1/b,YDIM,about_point=axes.c2p(0,0)),
			bb.animate.set_value(1),
			pp.animate.set_value(p/1),mm.animate.set_value(m*b/1)
		)
		self.wait()

		# focus on circle
		oval.add_updater(lambda m: m.rescale_to_fit(axes.x_axis.unit_size*2*aa.get_value(),XDIM))
		self.play(	
			axes.animate.set_all_ranges([-1.5,1.5],[-1.5,1.5]).set_anim_args(recursive=True),
			reorganize_mobjects=False)
		self.wait()

		trig_hl = trig.copy().clear_updaters()
		trig_hl.set_fill(opacity=0)
		trig_hl.set_stroke(YELLOW,8)
		self.play(Create(trig_hl))
		self.wait(3)
		self.play(Uncreate(trig_hl))

		self.play(
			#*[m.animate.shift(FRAME_WIDTH/5*LEFT) for m in [axes,oval]], 
			FadeOut(oval_fml), FadeOut(prob_descrp),
			reorganize_mobjects=False
		)

	def analyze_after_transform(self):
		#* precondition *#
		axes, oval = self.axes, self.oval
		aa, bb, pp, mm = self.aa, self.bb, self.pp, self.mm
		A, A.label, B, B.label = self.A, self.A.label, self.B, self.B.label
		P, P.label, O, O.label = self.P, self.P.label, self.O, self.O.label
		trig = self.trig

		H = self.point(color=WHITE)
		OH = self.line()
		H.label = Tex('H')

		m, p = mm.get_value(), pp.get_value()
		
		def H_updater(self):
			m, p = mm.get_value(), pp.get_value()
			H_LC = ( p/(m*m+1), -m*p/(m*m+1) )
			O_MC, H_MC = axes.c2p(0,0), axes.c2p(*H_LC)

			H.move_to(H_MC)
			OH.put_start_and_end_on(O_MC, H_MC)
			H.label.next_to(H,DR,buff=0)
		H.add_updater(H_updater)
		H.update()

		rect_mark = RightAngleMark(O.get_center(),H.get_center(),A.get_center())

		self.hint_dynamic(OH,H.label)
		
		H.suspend_updating()
		self.play(
			Create(OH),
			FadeIn(H, time_span=[0.5,1.5]),
			FadeIn(H.label, time_span=[0.5,1.5]),
			Create(rect_mark, time_span=[1,2]),
		)
		H.resume_updating()
		self.wait()

		half_trig = VGroup(
			Polygon(O.get_center(),B.get_center(),H.get_center()),
			Polygon(O.get_center(),A.get_center(),H.get_center()),
		)

		half_trig.set_fill(TEAL_B, 0)
		half_trig.set_stroke(WHITE)
		self.add(half_trig)
		self.bring_to_back(half_trig); self.bring_to_back(axes, trig)
		
		def blink(alpha):
			return emphasize(0.4,0.5)(alpha)
		
		self.play(half_trig[0].animate.set_fill(opacity=1),rate_func=blink,reorganize_mobjects=False)
		self.play(half_trig[1].animate.set_fill(opacity=1),rate_func=blink,reorganize_mobjects=False)
		
		#!-------------------------------------------------------------------!#
		#* 右半边的widget
		widget_radius=1.5
		anchor = Dot(FRAME_WIDTH/4*RIGHT+DOWN/2).set_opacity(0)
		trig_config = {'fill_color': BLUE, 'fill_opacity': 0.7}
		_ = ORIGIN
		right_trig = Polygon(_,_,_, **trig_config)
		widget_rect_mark = RightAngleMark(UP,ORIGIN,RIGHT)
		semicirc = Arc(0,PI, radius=widget_radius, stroke_opacity=0.4)
		semicirc.reverse_points() # for correct direction when Create

		# parameters
		θθ = ValueTracker(PI/4)
		def widget_controller(_):
			ctr = anchor.get_center()
			θ = θθ.get_value()
			right_trig.vertices = [
				ctr+RIGHT*widget_radius, 
				ctr+LEFT*widget_radius, 
				ctr+np.array([np.cos(θ),np.sin(θ),0])*widget_radius
			]
			tmp = right_trig.vertices[1:]+[right_trig.vertices[0]]
			widget_rect_mark.set_points(RightAngleMark(*tmp).get_points())
			right_trig.set_points_as_corners([*right_trig.vertices, right_trig.vertices[0]])
			semicirc.move_arc_center_to(ctr)

		right_trig.add_updater(widget_controller)
		self.hint_dynamic(semicirc,widget_rect_mark)
		#self.add(anchor, right_trig, semicirc)
		#self.bring_to_back(semicirc)
		
		#!-------------------------------------------------------------------!#
		#* 从左边的直角三角形 transform 到右边的直角三角形，非常tricky
		self.play(
			*[m.animate.shift(FRAME_WIDTH/5*LEFT) for m in [axes,oval,half_trig,H.label,rect_mark]],
			reorganize_mobjects=False
		) # 先往左腾挪出位置
		self.wait()

		tmp = half_trig[0].copy().clear_updaters()
		tmp.set_fill(BLUE, 0.7)
		# Step I: 让右边的三角形和左边的三角形形状一致
		# 需要用到一点 inverse kinetics :-)
		def inv_kinetics_point2θ(A,B,O): # 这个函数后面还会有用
			BO,BH = O.get_center()-B.get_center(), A.get_center()-B.get_center()
			return 2*np.arccos(np.dot(normalize(BO),normalize(BH)))
		θθ.set_value(inv_kinetics_point2θ(A,B,O)) 
		right_trig.update()
		
		# Step II: 
		# 计算出移动到目的位置需要的变换量，有点tricky
		tmp.generate_target() # preserve the original one
		angle = np.arctan2(*(B.get_center()-O.get_center())[:2])+PI/2
		shift = right_trig.get_center()-tmp.rotate(angle).get_center()
		scale = (2*widget_radius)/axes.x_axis.unit_size
		# roll back
		tmp.rotate(-angle).move_to(tmp.target)

		# finally do the animation
		alpha = ValueTracker(0)
		def transform_param_interp(m):
			# Step III:
			# 模仿blender，在scale和rotate参数空间中interp
			# 而不是直接对points进行内插
			a=alpha.get_value()
			m.set_points(m.target.get_points())
			m.rotate(a*angle).shift(a*shift).scale(interpolate(1,scale,a))
		tmp.add_updater(transform_param_interp)
		self.add(tmp)
		# That's it!
		self.play(alpha.animate.set_value(1),run_time=2)
		self.play(FadeIn(widget_rect_mark),run_time=.5)
		self.wait()
		self.play(FadeOut(widget_rect_mark),run_time=.5)
		self.wait()
		# Step IV: 偷天换日
		self.remove(tmp)
		self.add(anchor, right_trig)

		#!-------------------------------------------------------------------!#
		#* 直角三角形分离出来展示

		def make_ghost_trig(origin, radius, theta):
			return Polygon(
				origin+LEFT*radius, 
				origin+RIGHT*radius, 
				origin+np.array([np.cos(theta),np.sin(theta),0])*radius,
				fill_color=BLUE, fill_opacity=0.3,
				stroke_opacity=0
			)

		ghost_trig = VGroup()
		ghost_trig.add(make_ghost_trig(anchor.get_center(),widget_radius,PI*3/4))
		ghost_trig.add(make_ghost_trig(anchor.get_center(),widget_radius,PI*1/4))
		#self.add(ghost_trig); self.bring_to_back(ghost_trig)

		# height mark
		height_mark = LengthMark()
		height_mark.add_updater(
			lambda m: m.set_start_and_end(
				start = right_trig.get_bottom(),
				end   = right_trig.get_top(),
			).next_to(right_trig,LEFT).align_to(right_trig,DOWN)
		).update()

		update_func = height_mark.get_updaters()[0]
		height_mark.clear_updaters()
		
		height_mark.generate_target(); 
		height_mark.refresh_attr().shrink_to_start()
		self.play(FadeIn(height_mark), run_time=0.3)
		self.play(MoveToTarget(height_mark), run_time=0.7)
		
		height_mark.add_updater(update_func)
		
		# show triangle with different shapes
		self.play(θθ.animate.set_value(PI*0.5),FadeIn(semicirc),run_time=1.2)
		self.wait()

		# width mark
		width_mark = LengthMark()
		width_mark.add_updater(lambda m: m.set_start_and_end(
			start = right_trig.get_left(),
			end   = right_trig.get_right(),
		).next_to(right_trig,DOWN)).refresh_attr()
		
		width_mark.generate_target()
		width_mark.shrink_to_middle()
		self.play(FadeIn(width_mark, run_time=0.3))
		self.play(MoveToTarget(width_mark, run_time=0.7))
		self.wait()

		# 越偏离等腰直角，面积越小
		self.play(θθ.animate.set_value(PI*0.75),run_time=1.5)
		self.wait(.5)
		self.play(θθ.animate.set_value(PI*0.95))
		#self.wait()
		self.play(
			θθ.animate.set_value(PI*0.15).set_anim_args(run_time=1.6,rate_func=linear_ease_io(0.3)),
			FadeIn(ghost_trig[0], time_span=[0.4,0.6]),
			FadeIn(ghost_trig[1], time_span=[1.3,1.5])
		)
		self.wait(0.5)
		self.play(θθ.animate.set_value(PI*0.4))
		self.wait()
		self.play(θθ.animate.set_value(PI*0.5))
		self.wait()

		#* postcondition *#
		self.half_trig = half_trig; self.semicirc = semicirc
		self.H, self.OH, self.H.label = H, OH, H.label
		self.anchor, self.right_trig = anchor, right_trig
		self.rect_mark, self.widget_rect_mark = rect_mark, widget_rect_mark
		self.width_mark, self.height_mark = width_mark, height_mark
		self.θθ, self.inv_kinetics_point2θ, self.ghost_trig = θθ, inv_kinetics_point2θ, ghost_trig

	def solve_and_summarize(self):
		#* precondition *#
		axes, oval = self.axes, self.oval
		aa, bb, pp, mm = self.aa, self.bb, self.pp, self.mm
		A, A.label, B, B.label = self.A, self.A.label, self.B, self.B.label
		P, P.label, O, O.label = self.P, self.P.label, self.O, self.O.label
		trig = self.trig
		half_trig = self.half_trig; semicirc = self.semicirc
		rect_mark, widget_rect_mark = self.rect_mark, self.widget_rect_mark
		H, OH, H.label = self.H, self.OH, self.H.label
		anchor, right_trig = self.anchor, self.right_trig
		width_mark, height_mark = self.width_mark, self.height_mark
		θθ, inv_kinetics_point2θ, ghost_trig = self.θθ, self.inv_kinetics_point2θ, self.ghost_trig

		# 直线过P的约束
		
		def blink_highlight(*mobjects):
			return [
				m.animate.set_opacity(0.2).set_anim_args(rate_func=there_and_back,run_time=0.6)
				for m in mobjects
			]
		# Simply play twice to mimic double blink rate_func -- This is more flexible.
		self.play(*blink_highlight(P,P.label))
		self.play(*blink_highlight(P,P.label))
		self.wait()

		# dont let half trig interfere in
		half_trig.set_stroke(opacity=0)
		OH_group = [O,O.label,OH,H,H.label,rect_mark]
		self.play(*blink_highlight(*OH_group))
		self.play(*blink_highlight(*OH_group))
		self.wait()

		OP = self.line()
		OP.add_updater(lambda m: m.put_start_and_end_on(O.get_center(),P.get_center()))
		#OP.set_opacity(0); 
		OP_group = [O,O.label,OP,P,P.label]
		
		self.play(FadeIn(OP),Animation(P),run_time=0.3)
		self.play(*blink_highlight(*OP_group))
		self.play(*blink_highlight(*OP_group))

		self.play(θθ.animate.set_value(inv_kinetics_point2θ(A,B,O)),FadeOut(ghost_trig))
		# "即直角三角形的直角边是短于OP的"
		widget_OH_highlight = self.line().put_start_and_end_on(right_trig.vertices[0],right_trig.vertices[2]).set_stroke(YELLOW,10)
		
		OH_group.append(widget_OH_highlight)
		# OH是三角形的直角边
		self.play(*blink_highlight(*OH_group))
		self.play(*blink_highlight(*OH_group))
		self.play(FadeOut(widget_OH_highlight))

		def widget_follow_control(m):
			θθ.set_value(inv_kinetics_point2θ(A,B,O))
		right_trig.add_updater(widget_follow_control)
		self.play(pp.animate.set_value(0.5), FadeOut(rect_mark))
		self.wait()
		# 而不难发现，OH是小于OP的
		self.play(*blink_highlight(OH,O,O.label,H,H.label))
		self.play(*blink_highlight(OH,O,O.label,H,H.label))
		self.wait(.5)
		self.play(*blink_highlight(OP,O,O.label,P,P.label))
		self.play(*blink_highlight(OP,O,O.label,P,P.label))
		self.wait(3)

		# 如果OP很短，OH最长时也无法取到。。
		self.play(mm.animate.set_value(0))
		self.wait()

		def OBH_motion_updater(m):
			Polygon.set_points_as_corners
			half_trig[0].set_points_as_corners([O.get_center(),B.get_center(),H.get_center()])
		half_trig[0].add_updater(OBH_motion_updater)
		half_trig[0].set_stroke(WHITE,3,1)
		def modify_color_updater(m):
			BO = O.get_center()-B.get_center()
			HO = O.get_center()-H.get_center()
			angle = np.arccos(np.dot(normalize(BO),normalize(HO)))
			deviation = 1-np.exp(-((angle-PI/4)/0.1)**2)
			alpha = clip(deviation,0,1)
			right_trig.set_fill(interpolate_color(GREEN,BLUE,alpha),interpolate(1,0.7,alpha))
			half_trig[0].set_fill(interpolate_color(GREEN,BLUE,alpha),interpolate(1,0.7,alpha))
		half_trig.add_updater(modify_color_updater)
		# 调整P的位置并观察

		P.label.set_backstroke(BG_COLOR,8)
		self.play(pp.animate.set_value(0.8), FadeOut(OP))
		
		self.wait()
		self.play(mm.animate.set_value(1),run_time=2)
		self.play(mm.animate.set_value(.5),run_time=1.5)
		self.wait()
		#self.play(mm.animate.set_value(0),run_time=2)
		#self.play(mm.animate.set_value(-0.5),run_time=1.5)
		#self.wait()
		#self.play(mm.animate.set_value(-1),run_time=2)
		self.wait()
		
		# 分析&展示完成，准备写结论
		
		text_c1 = Text('情形 1°',font=文楷,color=YELLOW)
		text_c2 = Text('情形 2°',font=文楷,color=YELLOW)
		fml_c1 = MTex(r'p<1/\sqrt{2}')
		fml_c2 = MTex(r'\frac{1}{\sqrt{2}}<p<1')
		fml_c2[:5].scale(.9)

		Strig_c1 = VGroup(MTex(r'S_{\triangle \mathrm{OAB}}='),MTex(r'ab',color=BLUE),MTex(r'p\cdot\sqrt{1-p^2}'))
		Strig_c2 = VGroup(MTex(r'S_{\triangle \mathrm{OAB}}='),MTex(r'ab\cdot',color=BLUE),MTex(r'\frac 12'))
		for m in [Strig_c1, Strig_c2]:
			m.arrange(RIGHT)
			m[2].next_to(m[0],RIGHT)
		
		Strig_c2[1][-1].shift(RIGHT*.1) # no idea why cdot gets so close to the symbol on its left
		Strig_c2[1][-1].set_color(WHITE)
		
		# layout
		text_c1.move_to(RIGHT*2+UP*2.5)
		text_c2.move_to(RIGHT*2+UP*-.2)
		fml_c1.next_to(text_c1,RIGHT,buff=.6)
		fml_c2.next_to(text_c2,RIGHT,buff=.6)
		Strig_c1.next_to(text_c1,DOWN, buff=.4).align_to(text_c1,LEFT).shift(RIGHT*.5)
		Strig_c2.next_to(text_c2,DOWN, buff=.4).align_to(text_c1,LEFT).shift(RIGHT*.5)

		# ^ construct | animation v #
		
		self.play(
			Write(text_c1),
	    	*[FadeOut(m) for m in [right_trig,semicirc,width_mark,height_mark]]
		)
		self.wait(.5)
		case_delim = DashedLine(axes.c2p(1/2**.5, -.5),axes.c2p(1/2**.5,.5),dash_length=.1)

		
		self.play(
			Write(fml_c1), 
			Create(case_delim), 
			pp.animate.set_value(.5), 
		)
		
		self.wait()
		self.play(mm.animate.set_value(0), FadeOut(case_delim))
		#self.play(mm.animate.set_value(.5))
		#self.play(mm.animate.set_value(0))
		self.wait()
		# show edge length
		OP_len_fml, BP_len_fml, OB_len_fml  = Tex('p'), Tex(r'\sqrt{1-p^2}'), Tex('1')
		OP_len_fml.next_to((O.get_center()+P.get_center())/2,DOWN, buff=0.1).shift(RIGHT*.1)
		BP_len_fml.next_to((B.get_center()+P.get_center())/2,RIGHT, buff=0.05)
		OB_len_fml.next_to((B.get_center()+O.get_center())/2,UL,buff=0.05)
		OP_len_fml.set_backstroke(BG_COLOR, 10)
		BP_len_fml.set_backstroke(BG_COLOR, 10)
		OP_hl, BP_hl = Line(stroke_color=YELLOW, stroke_width=7)*2
		OP_hl.put_start_and_end_on(O.get_center(),P.get_center())
		BP_hl.put_start_and_end_on(B.get_center(),P.get_center())
		
		self.add(OP_hl, O)
		self.play(Write(OP_len_fml), Create(OP_hl))
		self.wait()
		self.play(Write(OB_len_fml))
		self.wait()
		self.play(Write(BP_len_fml), Create(BP_hl))
		self.wait()
		
		self.play(Write(Strig_c1[::2]))
		self.wait()
		self.play(FadeIn(Strig_c1[1]), Strig_c1[2].animate.shift(RIGHT*.45))
		self.wait()

		# ^ case 1 | case 2 v # 
		self.play(*[
			FadeOut(m) for m in 
			[OP_len_fml, BP_len_fml, OB_len_fml, OP_hl, BP_hl]
		])
		self.wait()

		self.play(Write(text_c2)); self.wait(.5)
		case_delim = DashedLine(axes.c2p(1/2**.5, -1),axes.c2p(1/2**.5,1),dash_length=.1)
		case_delim_tex = MTex(r'\frac{1}{\sqrt 2}').scale(.7).next_to(case_delim,UP)
		self.play(
			Write(fml_c2), 
			Create(VGroup(case_delim,case_delim_tex)), 
			pp.animate.set_value(.8), 
		)
		self.wait()
		trig.add_updater(modify_color_updater)
		self.play(mm.animate.set_value(1).set_anim_args(run_time=2),FadeOut(VGroup(case_delim,case_delim_tex),run_time=1))
		self.wait(.5)
		self.play(mm.animate.set_value(.5))
		trig.clear_updaters()

		half_trig[1].set_points_as_corners([O.get_center(),H.get_center(),A.get_center(),O.get_center()])
		
		rect_mark = RightAngleMark(A.get_center(),O.get_center(),B.get_center())
		self.play(
			half_trig[1].animate.match_style(half_trig[0]),
			Create(rect_mark),
			OH.animate.set_stroke(GREEN,opacity=.7),
			reorganize_mobjects=False
		)
		self.wait()
		OA_len_fml = Tex('1')
		OA_len_fml.next_to((O.get_center()+A.get_center())/2,LEFT, buff=0.1)
		OB_len_fml = OA_len_fml.copy().next_to((O.get_center()+B.get_center())/2,UP, buff=0.1)
		self.play(FadeIn(OA_len_fml)); self.wait()
		self.play(FadeIn(OB_len_fml)); self.wait()

		self.play(Write(Strig_c2[::2]))
		self.wait()
		self.play(FadeIn(Strig_c2[1]), Strig_c2[2].animate.shift(RIGHT*.8))
		self.wait()

		done_mark = Tex('\\square.').next_to(Strig_c2,RIGHT,buff=1)
		self.play(Write(done_mark))
		self.wait()

		trig.remove_updater(modify_color_updater)
		half_trig.remove_updater(modify_color_updater)
		self.play(
			half_trig.animate.set_fill(opacity=0),
			FadeOut(OA_len_fml),FadeOut(OB_len_fml),
			reorganize_mobjects=False
		)
		self.wait(7)

		#* end of contents *#

	def fade_all(self):
		self.play(FadeIn(Curtain()))

	@staticmethod
	def calc_line_oval_intersection(a,b,m,p):
		'''计算直线x=my+p与椭圆x^2/a^2+y^2/b^2=1的两个交点。
		需要-a<p<a。
		返回格式为 ( (x1,y1), (x2,y2) ) 其中x1<=0<=x2.
		接受m= +-np.inf或 +-math.inf'''
		
		if m==+np.inf or m==+math.inf:
			return ((-a,0),(a,0))
		if m==-np.inf or m==-math.inf:
			return ((a,0),(-a,0))
		
		# we have Ay^2 + By + C = 0
		A = (m/a)**2 + (1/b)**2
		B = 2*m*p/a**2
		C = (p/a)**2 - 1

		# 希望不会有数值精度问题
		Δ = B**2 - 4*A*C
		y1= (-B-np.sqrt(Δ))/(2*A)
		y2= (-B+np.sqrt(Δ))/(2*A)
		x1= m*y1 + p
		x2= m*y2 + p

		return ((x1,y1),(x2,y2))

#!-------------------------------------------------------------------!#
#* Part II: Slope Transform

class SlopePartStart(StarskyScene):
	def construct(self):
		kw = {'font': 文楷}
		title = Text('2. 斜率',font_size=100,**kw)
		trans = TextGroup('斜率', '→ ', 'b/a x ','斜率')
		trans.scale(1.2)#.set_color(WHITE)
		trans[2].set_color(BLUE_B)
		trans.next_to(title,DOWN).shift(UP*.5)

		self.play(FadeIn(title))
		self.wait()
		self.play(FadeOut(title),run_time=.7)
		return
	
		self.play(title.animate.shift(UL+DOWN*.3),Write(trans[0],time_span=[0.5,2]))
		self.wait(.5)
		self.play(Write(trans[1:],run_time=1.5))
		self.wait(2)
		self.play(FadeOut(title),FadeOut(trans),run_time=.7)

class SlopeTransform(StarskyScene):
	CONFIG = {
		'slope': 1.5,
		'length': 3
	}
	def construct(self) -> None:
		self.construct_elements()
		self.show_elements()
		self.transform()
		self.formula_deductions()

	def construct_elements(self):
		slope, length = self.slope, self.length
		line = Line(
			start = LEFT+DOWN*slope,
			end   = RIGHT+UP*slope,
			color = TEAL,
			stroke_width = 8
		).scale(length/(1+slope**2))
		grp_ctr_point = line.get_center()

		ind_sf = 0.7 # indicator scale factor
		dashedline_config = {
			'dash_length':0.16, 
			'positive_space_ratio':0.6
		}
		run = DashedLine(
			start = ind_sf*(LEFT+DOWN*slope),
			end   = ind_sf*(LEFT+DOWN*slope+RIGHT*2),
			**dashedline_config
		)
		rise = DashedLine(
			start = ind_sf*(RIGHT+UP*slope),
			end   = ind_sf*(RIGHT+UP*slope+DOWN*2*slope),
			**dashedline_config
		)
		# construct group of the geometric components
		# labels will be later attached, so no need to be added to group
		geometries = VGroup(line, run, rise)
		#geo_group.move_to(FRAME_WIDTH/5*LEFT)
		
		tex_config = {'color': FML_COLOR}
		run_label  = Tex(r'\Delta x', **tex_config).next_to(run, DOWN)
		rise_label = Tex(r'\Delta y', **tex_config).next_to(rise,RIGHT)
		org_slope_label = Tex(r'k',r'=\frac{\Delta y}{\Delta x}', **tex_config).next_to(grp_ctr_point, UL)
		
		self.line, self.run, self.rise = line, run, rise
		self.run_label, self.rise_label = run_label, rise_label
		self.org_slope_label = org_slope_label
		self.geometries = geometries
		self.grp_ctr_point = grp_ctr_point
	
	def show_elements(self):
		line, run, rise = self.line, self.run, self.rise
		run_label, rise_label = self.run_label, self.rise_label
		org_slope_label = self.org_slope_label
		
		self.play(Create(line))
		self.wait()
		self.play(Write(run), Write(rise), FadeIn(run_label), Animation(line)) # keep line on top
		self.wait()
		self.play(FadeIn(rise_label), Animation(line))
		self.wait()
		
		org_slope_label[0].next_to(line.get_center(),UL)
		org_slope_label.shift(.2*DOWN)
		self.play(Write(org_slope_label[0]))
		self.wait()
		org_slope_label[0].generate_target().next_to(org_slope_label[1],LEFT)
		self.play(MoveToTarget(org_slope_label[0]),FadeIn(org_slope_label[1],shift=LEFT*.5))
		self.wait()

	def transform(self):
		line, run, rise = self.line, self.run, self.rise
		run_label, rise_label = self.run_label, self.rise_label
		org_slope_label = self.org_slope_label
		grp_ctr_point = self.grp_ctr_point

		a, b = 1.5, 1.8
		tex_config = {'color': FML_COLOR}
		run_label_new  = Tex('a',r'\Delta x', **tex_config)
		rise_label_new = Tex('b',r'\Delta y', **tex_config)
		# make them dynamic as they'll be involved in animations
		run_label. add_updater(lambda m: m.next_to(run, DOWN))
		rise_label.add_updater(lambda m: m.next_to(rise,RIGHT))

		# stretch x
		# "peek" to the new loc
		run_label_new.next_to(run.copy().stretch(a, XDIM, about_point=grp_ctr_point), DOWN)
		self.play(
			FadeOut(org_slope_label),
			line.animate.stretch(a, XDIM, about_point=grp_ctr_point),
			run .animate.stretch(a, XDIM, about_point=grp_ctr_point),
			rise.animate.stretch(a, XDIM, about_point=grp_ctr_point),
			FadeIn(run_label_new[0]),
			run_label[0].animate.move_to(run_label_new[1]),
			run_time=2
		)
		self.remove(run_label); self.add(run_label_new)
		run_label_new.add_updater(lambda m: m.next_to(run,DOWN))

		self.wait(2)

		# stretch y
		rise_label_new.next_to(rise.copy().stretch(b, YDIM, about_point=grp_ctr_point), RIGHT)
		
		self.play(
			line.animate.stretch(b, YDIM, about_point=grp_ctr_point),
			run .animate.stretch(b, YDIM, about_point=grp_ctr_point),
			rise.animate.stretch(b, YDIM, about_point=grp_ctr_point),
			FadeIn(rise_label_new[0]),
			rise_label[0].animate.move_to(rise_label_new[1]),
			run_time=2
		)
		self.wait(2)
		self.remove(rise_label); self.add(rise_label_new)
		run_label.clear_updaters()

		#* postcondition *#
		self.run_label = run_label_new
		self.rise_label = rise_label_new
	
	def formula_deductions(self):
		geometries = self.geometries
		#grp_ctr_point = self.grp_ctr_point
		line,run,rise = self.line,self.run,self.rise
		run_label, rise_label = self.run_label, self.rise_label

		isolate = ['a','b',r'\Delta x',r'\Delta y','=']
		t2c = {'a': BLUE, 'b': BLUE}
		tex_config = {
			'color': FML_COLOR, 
			'isolate': isolate, 
			'tex_to_color_map': t2c
		}; kw=tex_config
		ded_lines = VGroup(
			MTex("k'", **kw),
			MTex(r"=\frac{b\Delta y}{a\Delta x}", **kw),
			MTex(r"=\frac{b}{a}\cdot\frac{\Delta y}{\Delta x}", **kw),
			MTex(r"=\frac{b}{a}\cdot k", **kw)
		)
		ded_lines[1].next_to(ded_lines[0],RIGHT)
		ded_lines[2].next_to(ded_lines[1],RIGHT)
		ded_lines[3].next_to(ded_lines[1],DOWN)
		ded_lines[3].align_to(ded_lines[1],LEFT)
		ded_lines.move_to(FRAME_WIDTH/5*RIGHT)
		#self.add(ded_lines)
		self.stop_skipping()
		self.play(*[m.animate.shift(LEFT*2.8) for m in [line,run,rise,run_label,rise_label]])

		self.play(Write(ded_lines[0]), run_time=0.5)
		self.wait()
		self.play(Write(ded_lines[1]))
		self.wait(2)
		self.play(FadeIn(ded_lines[2]))
		self.wait(2)
		self.play(FadeIn(ded_lines[3]))
		self.wait()

		new_slope_label = MTex(r"k'=\frac{b}{a}\cdot k", **tex_config)
		grp_ctr_point = line.get_center()
		new_slope_label.next_to(grp_ctr_point,UL)
		self.play(Write(new_slope_label))
		self.wait(3)

	def fade_all(self):
		self.play(FadeIn(Curtain()))

class TangentLineProblem(OvalScene):
	def construct(self) -> None:
		self.setup_oval()
		self.construct_geometry_elements()
		self.show_problem()
		self.transform_and_solve()
		self.show_homework()

	def setup_oval(self):
		aa, bb = ValueTracker(2.6), ValueTracker(1.4)
		a, b = aa.get_value(), bb.get_value()
		self.init_axes(include_numbers=False)
		self.init_oval(a,b)

		axes, oval = self.axes, self.oval
		self.add(axes, oval)

		self.aa, self.bb = aa, bb

	def update_ab_parameter(self):
		self.a, self.b = self.aa.get_value(), self.bb.get_value()
		return self.a, self.b

	def construct_geometry_elements(self):
		'''geometry components and their relation'''

		axes, oval = self.axes, self.oval
		aa, bb = self.aa, self.bb

		theta = ValueTracker(PI/4)
		T  = self.point()
		T.label = Tex('T')
		
		O = self.point((0,0))
		O.label = Tex('O')
		O.label.next_to(O, DL, buff=SMALL_BUFF)

		# 构造直线
		half_tanlen = 2 # 切线长度的一半
		tangent_line = self.line()
		OT = self.line()

		self.dynamic_ab = False
		# make them dynamic
		def geometry_components_updater(_):
			global a, b
			a, b = self.update_ab_parameter()
			if self.dynamic_ab:	
				ctr = axes.get_origin()
				self.unit_circ.rescale_to_fit(axes.x_axis.unit_size*2,XDIM)
				oval.set_points(
					self.unit_circ.copy() \
						.stretch(a, XDIM) \
						.stretch(b, YDIM) \
						.move_to(axes.get_origin())
						.get_points()
				)

			T_LC = self.get_oval_coord(theta.get_value())
			#T_MC = axes.c2p(*T_LC)
			T.move_to(axes.c2p(*T_LC))

			# next_to will cause some glitchy, no idea why
			T_LC_norm = normalize(T_LC)
			label_MC = T_LC + T_LC_norm*MED_LARGE_BUFF
			T.label.move_to(axes.c2p(*label_MC))

			x0, y0 = T_LC
			OT.put_start_and_end_on(
				start = axes.c2p(0,0),
			 	end   = axes.c2p(*T_LC)
			)

			half_tanlen = 2*0.4 + ((a+b)*axes.x_axis.unit_size/1.3)*0.6
			θ_tan = np.arctan2(x0/a**2, -y0/b**2)# 直线倾角
			line_dir = np.array([np.cos(θ_tan), np.sin(θ_tan)])
			start_LC = T_LC + half_tanlen * line_dir
			end_LC   = T_LC - half_tanlen * line_dir
			tangent_line.put_start_and_end_on(
				start = axes.c2p(*start_LC),
				end   = axes.c2p(*end_LC)
			)

		T.add_updater(geometry_components_updater)
		self.hint_dynamic(T,T.label,OT,tangent_line,oval)
		
		self.T, self.O = T, O
		self.OT = OT; self.tangent_line = tangent_line

	def show_problem(self):
		axes, oval = self.axes, self.oval
		T, O = self.T, self.O
		OT = self.OT; tangent_line = self.tangent_line
		
		tangent_line.label = MTex(r'\ell_1').add_updater(lambda m: m.next_to(tangent_line, DR).shift(UP*0.3))
		OT.label = MTex(r'\ell_2').add_updater(lambda m: m.move_to((OT.get_start()+OT.get_end())/2).shift(UL*0.3))
		
		self.play(
			Write(axes, run_time=2), 
			FadeIn(O.label, time_span=[0.5,1.5]),
			Create(oval, time_span=[0.5,1.5])
		)
		self.wait()
		
		self.play(
			FadeIn(T), FadeIn(T.label), 
			Create(tangent_line,time_span=[1,2]),
			FadeIn(tangent_line.label, time_span=[1.5,2.5])
		)
	
		self.wait()
		
		T.suspend_updating() # controller is at T
		self.play(
			FadeIn(O, time_span=[0,0.5]),
			Create(OT, time_span=[0.3,1.3]),
			FadeIn(OT.label, time_span=[0.5,1.5])
		)
		T.resume_updating()
		self.wait()
		
		# 问题出场
		prob_text = Text('求证：', font=文楷)
		t2c = {
			'k_1': YELLOW, 'k_2': YELLOW,
			r'\frac{b^2}{a^2}': BLUE,
		}
		tex_config = {
			'tex_to_color_map': t2c
		}
		prob_tex = MTex(r'k_1\cdot k_2=-\frac{b^2}{a^2}', **tex_config)
		prob_descrp = VGroup(prob_text, prob_tex).arrange(RIGHT)
		prob_descrp.to_corner(UR, buff=1.6)
		
		OT.label.set_backstroke(width=6)
		self.play(*[
				m.animate.shift(FRAME_WIDTH/5*LEFT)
				for m in [axes, oval, O, O.label]
			],
			FadeIn(prob_descrp, time_span=[0.5,1.5]),
			reorganize_mobjects=False
		)
		self.wait(2)
		self.prob_descrp = prob_descrp

	def transform_and_solve(self):
		aa, bb = self.aa, self.bb
		axes, oval = self.axes, self.oval
		O,T = self.O,self.T
		tangent_line = self.tangent_line
		prob_descrp = self.prob_descrp

		self.stop_skipping()
		origin_a, origin_b = aa.get_value(), bb.get_value()
		self.dynamic_ab = True
		self.play(
			aa.animate.set_value(1),
			bb.animate.set_value(1),
		)
		self.dynamic_ab = False
		self.wait()
		
		# 圆中：OT与l1垂直
		rect_mark = RightAngleMark(O.get_center(),T.get_center(),tangent_line.get_end())
	
		kw = {
			'tex_to_color_map': {r'k_1\cdot k_2': YELLOW}
		}
		reasoning = VGroup(
			MTex(r'\ell_1\perp OT'),
			VGroup(MTex(r'k_1\cdot k_2=', color=YELLOW), MTex('-1'), MTex(r'-\frac{b^2}{a^2}', color=BLUE))
		)
		reasoning[1][0][-1].set_color(WHITE) # 等号是白色
		reasoning[1][2][0].set_color(WHITE) # 负号是白色

		reasoning[1][0].next_to(reasoning[0],DOWN).align_to(reasoning[0],LEFT)
		reasoning[1][1].next_to(reasoning[1][0],RIGHT)
		reasoning[1][2].next_to(reasoning[1][0],RIGHT).set_opacity(0)
		reasoning.next_to(prob_descrp, DOWN, buff=1.5).align_to(prob_descrp, LEFT).shift(RIGHT*0.5)

		self.play(Create(rect_mark), Write(reasoning[0]))
		self.wait()
		self.play(Write(reasoning[1]))
		self.wait()

		# 变换回椭圆
		self.dynamic_ab = True
		reasoning.generate_target()
		reasoning.target.shift(RIGHT)
		reasoning.target[0].set_opacity(0.3)
		self.play(
			aa.animate.set_value(origin_a),
			bb.animate.set_value(origin_b),
			FadeOut(rect_mark),
			MoveToTarget(reasoning)
		)
		self.dynamic_ab = False
		self.wait()

		reasoning[1][2].shift(UP*0.04).set_opacity(1)
		self.remove(reasoning[1][2])
		self.play(
			FadeTransform(reasoning[1][1], reasoning[1][2])
		)
		self.wait()
		reasoning[1][1].set_opacity(0)

		QED_text = Text('∴得证.', font=文楷, font_size=40)
		QED_text.next_to(reasoning, DOWN, buff=0).align_to(reasoning, LEFT)
		self.play(Write(QED_text))
		self.wait()
		
		self.reasoning = reasoning
		self.QED_text = QED_text
		
	def show_homework(self):
		axes, oval = self.axes, self.oval
		T = self.T; O = self.O
		prob_descrp = self.prob_descrp
		reasoning = self.reasoning
		QED_text = self.QED_text

		hw_text = VGroup(
			Text('课后作业', font=文楷, color=YELLOW),
			Text('求证：', font=文楷),
		).arrange(RIGHT, buff=MED_LARGE_BUFF)
		hw_text.move_to(prob_descrp).shift(RIGHT*0.5)
		T_coord = MTex('(x_0,y_0)').add_updater(lambda m: m.next_to(T.label, RIGHT, buff=SMALL_BUFF))

		fml = MTex(
			r'\ell_1:\ \frac{x_0x}{a^2}+\frac{y_0y}{b^2}=1',
			tex_to_color_map = {'a^2':BLUE, 'b^2':BLUE}
		)
		fml.next_to(hw_text, DOWN, buff=MED_LARGE_BUFF).align_to(hw_text, LEFT)

		hw_text[0].generate_target()
		hw_text[0].rotate(-PI/2, LEFT).shift(UP*0.5).set_opacity(0)
		
		self.play(
			*[
				m.animate.shift(LEFT*0.7)
				for m in [axes, oval, O, O.label]
			],

			FadeOut(prob_descrp, shift=DOWN),
			FadeOut(reasoning, shift=DOWN),
			FadeOut(QED_text, shift=DOWN),

			MoveToTarget(hw_text[0], time_span=[0.5,1]),

			reorganize_mobjects=False
		)
		self.wait()

		self.play(Write(T_coord))
		self.wait()
		self.play(Write(hw_text[1]))
		self.play(Write(fml))

		self.wait()
		self.play(FadeIn(Curtain()))

#!-------------------------------------------------------------------!#
#* Part III: Length Transform

class LengthPartStart(StarskyScene):
	def construct(self):
		kw = {'font': 文楷}
		title = Text('3. 长度',font_size=100,**kw)
		trans = TextGroup('长度', '→ ', '？')
		trans.scale(1.2)#.set_color(WHITE)
		trans[2].set_color(BLUE_B)
		trans.next_to(title,DOWN).shift(UP*.5).shift(RIGHT)

		self.play(FadeIn(title))
		self.wait()
		self.play(FadeOut(title),run_time=.7)
		return
	
		self.play(title.animate.shift(UL+DOWN*.3),Write(trans[0],time_span=[0.5,2]))
		self.play(Write(trans[1:],run_time=1.5))
		self.wait(2)
		self.play(FadeOut(title),FadeOut(trans),run_time=.7)

class LengthTransform(StarskyScene):
	CONFIG = {
		'slope': 1.5,
		'length': 3
	}
	def construct(self) -> None:
		self.construct_elements()
		self.show_elements()
		self.show_origin_length_formula()
		self.transform()
		self.show_transformed_length_formula()
		self.show_curtain_and_compare()
		self.fade_all()

	def construct_elements(self):
		slope, length = self.slope, self.length
		line = Line(
			start = LEFT+DOWN*slope,
			end   = RIGHT+UP*slope,
			color = TEAL,
			stroke_width = 8
		).scale(length/(1+slope**2))
		grp_ctr_point = line.get_center()

		ind_sf = 0.7 # indicator scale factor
		dashedline_config = {
			'dash_length':0.16, 
			'positive_space_ratio':0.6
		}
		run = DashedLine(
			start = ind_sf*(LEFT+DOWN*slope),
			end   = ind_sf*(LEFT+DOWN*slope+RIGHT*2),
			**dashedline_config
		)
		rise = DashedLine(
			start = ind_sf*(RIGHT+UP*slope),
			end   = ind_sf*(RIGHT+UP*slope+DOWN*2*slope),
			**dashedline_config
		)
		# construct group of the geometric components
		# labels will be later attached, so no need to be added to group
		geo_group = VGroup(line, run, rise)
		
		tex_config = {'color': FML_COLOR}
		run_label  = Tex(r'\Delta x', **tex_config).add_updater(lambda m: m.next_to(run, DOWN))
		rise_label = Tex(r'\Delta y', **tex_config).add_updater(lambda m: m.next_to(rise,RIGHT))
		length_label = MTex(r'l', **tex_config).add_updater(lambda m: m.next_to(grp_ctr_point, UL))
		
		slope_indicator = VGroup(
			Arrow(ORIGIN, 1.2*(RIGHT+UP*slope)),
			MTex(r'k', **tex_config).next_to(grp_ctr_point, UL),
		)
		slope_indicator[1].add_updater(lambda m: m.next_to(slope_indicator[0].get_center(),UL, buff=0.2))
		slope_indicator.add_updater(lambda m: m.next_to(grp_ctr_point, UL, buff=0.4).shift(DOWN*0.3))
		
		#self.add(line, run, rise)
		#self.bring_to_front(line)
		#self.add(run_label, rise_label, length_label, slope_indicator)

		self.line, self.run, self.rise = line, run, rise
		self.run_label, self.rise_label = run_label, rise_label
		self.length_label = length_label
		self.geo_group = geo_group
		self.grp_ctr_point = grp_ctr_point
		self.slope_indicator = slope_indicator
	
	def show_elements(self):
		line, run, rise = self.line, self.run, self.rise
		run_label, rise_label = self.run_label, self.rise_label
		length_label = self.length_label
		grp_ctr_point = self.grp_ctr_point
		slope_indicator = self.slope_indicator
		
		self.play(FadeIn(line))
		self.wait(.5)
		self.play(GrowArrow(slope_indicator[0]),FadeIn(slope_indicator[1],shift=normalize(RIGHT+UP*self.slope)))
		self.add(slope_indicator)
		self.wait()
		self.play(Write(run), Write(rise), FadeIn(run_label), Animation(line)) # keep line on top
		self.wait()
		self.play(FadeIn(rise_label), Animation(line))
		self.wait()
		self.play(FadeIn(length_label,shift=RIGHT))
		self.wait()
	
	def show_origin_length_formula(self):
		geo_group = self.geo_group
		grp_ctr_point = self.grp_ctr_point

		isolate = ['l','a','b',r'\Delta x',r'\Delta y','=']
		t2c = {'a': BLUE, 'b': BLUE}
		tex_config = {
			'color': FML_COLOR, 
			'isolate': isolate, 
			'tex_to_color_map': t2c
		}; kw=tex_config

		ded_lines = VGroup(
			MTex("l", **kw),
			MTex(r"=\sqrt{(\Delta x)^2+(\Delta y)^2}", **kw),
			MTex(r"=\sqrt{(k\Delta x)^2+(\Delta x)^2}", **kw),
			MTex(r"=\sqrt{k^2+1}\cdot\Delta x", **kw),
		)
		ded_lines[1].next_to(ded_lines[0],RIGHT)
		ded_lines[2].next_to(ded_lines[1],DOWN)
		ded_lines[2].align_to(ded_lines[1],LEFT)
		ded_lines[3].next_to(ded_lines[2],DOWN)
		ded_lines[3].align_to(ded_lines[2],LEFT)
		ded_lines.move_to(FRAME_WIDTH/5*LEFT+FRAME_HEIGHT/4*DOWN)
		#self.add(ded_lines)
		
		self.play(
			geo_group.animate.move_to(FRAME_WIDTH/5*LEFT+FRAME_HEIGHT/5*UP),
			Write(ded_lines[0], time_span=[0.5,1]))
		self.wait()
		self.play(Write(ded_lines[1]),run_time=2)
		self.wait(2)
		self.play(FadeIn(ded_lines[2]))
		self.wait(2)
		self.play(FadeIn(ded_lines[3]))
		self.wait(2)

	def transform(self):
		line, run, rise = self.line, self.run, self.rise
		run_label, rise_label = self.run_label, self.rise_label
		geo_group = self.geo_group
		org_slope_label = self.length_label
		grp_ctr_point = self.grp_ctr_point

		# copy 一份，挪动到屏幕右边
		# recall: geo_group = [line, run, rise]
		a, b = 1.5, 1.2
		geo_group_new = geo_group.copy()
		line_new, run_new, rise_new = geo_group_new

		geo_group_new.move_to(FRAME_WIDTH/5*RIGHT+FRAME_HEIGHT/5*UP)
		grp_ctr_point_new = line_new.get_center()
		run_label_tmp  = run_label.copy()
		rise_label_tmp = rise_label.copy()
		# make them dynamic as they'll be involved in animations
		run_label_tmp.clear_updaters()
		run_label_tmp.add_updater(lambda m: m.next_to(run_new, DOWN))
		rise_label_tmp.clear_updaters()
		rise_label_tmp.add_updater(lambda m: m.next_to(rise_new, RIGHT))
		self.add(run_label_tmp, rise_label_tmp)
		
		self.stop_skipping()
		self.play(TransformFromCopy(geo_group, geo_group_new))
		self.wait()
		
		# Transform on the new group
		tex_config = {'color': FML_COLOR}
		run_label_new  = Tex('a',r'\Delta x', **tex_config)
		rise_label_new = Tex('b',r'\Delta y', **tex_config)
		run_label_new. add_updater(lambda m: m.next_to(run_new, DOWN))
		rise_label_new.add_updater(lambda m: m.next_to(rise_new,RIGHT))

		#stretch(a, XDIM, about_point = grp_ctr_point).stretch(b, YDIM, about_point = grp_ctr_point)

		# "peek" to the new loc
		trans_kw = {'about_point': grp_ctr_point_new}
		run_label_new.next_to(run.copy().stretch(a, XDIM, about_point=grp_ctr_point), DOWN)
		self.play(
			geo_group_new.animate.stretch(a, XDIM, **trans_kw).stretch(b, YDIM, **trans_kw),
			FadeTransform(run_label_tmp, run_label_new),
			FadeTransform(rise_label_tmp, rise_label_new),
			run_time=2
		)

		self.wait(2)

		self.geo_group_new = geo_group_new

	def show_transformed_length_formula(self):
		geo_group_new = self.geo_group_new
		grp_ctr_point = self.grp_ctr_point

		isolate = ['l','a','b',r'\Delta x',r'\Delta y','=']
		t2c = {'a': BLUE, 'b': BLUE}
		tex_config = {
			'color': FML_COLOR, 
			'isolate': isolate, 
			'tex_to_color_map': t2c
		}; kw=tex_config

		length_fml = MTex("l'",**kw).next_to(self.geo_group_new[0].get_center(),UL)

		ded_lines = VGroup(
			MTex("l'", **kw),
			MTex(r"=\sqrt{(a\Delta x)^2+(b\Delta y)^2}", **kw),
			MTex(r"=\sqrt{(bk\Delta x)^2+(a\Delta x)^2}", **kw),
			MTex(r"=\sqrt{a^2+b^2k^2}\cdot\Delta x", **kw),
		)
		ded_lines[1].next_to(ded_lines[0],RIGHT)
		ded_lines[2].next_to(ded_lines[1],DOWN)
		ded_lines[2].align_to(ded_lines[1],LEFT)
		ded_lines[3].next_to(ded_lines[2],DOWN)
		ded_lines[3].align_to(ded_lines[2],LEFT)
		ded_lines.move_to(FRAME_WIDTH/4*RIGHT+FRAME_HEIGHT/4*DOWN)
		#self.add(ded_lines)
		
		self.play(Write(ded_lines[0]), FadeIn(length_fml), run_time=0.5)
		self.wait()
		self.play(Write(ded_lines[1]))
		self.wait(2)
		self.play(FadeIn(ded_lines[2]))
		self.wait(2)
		self.play(FadeIn(ded_lines[3]))
		self.wait(2)

	def show_curtain_and_compare(self):
		self.stop_skipping()
		curtain = Curtain(fill_opacity=0.9)
		self.play(FadeIn(curtain))

		isolate = ['a','b','k',r'\Delta x',r'\Delta y','=']
		t2c = {'a': BLUE, 'b': BLUE}
		tex_config = {
			'color': FML_COLOR, 
			'isolate': isolate, 
			'tex_to_color_map': t2c
		}; kw=tex_config
		cmp_fml = MTex(r"\frac{l'}{l}=\frac{\sqrt{a^2+b^2k^2}}{\sqrt{1+k^2}}", **kw)
		text = Text('与k有关！',font=文楷).shift(2*RIGHT)
		#VGroup(cmp_fml, text).arrange(RIGHT, buff=0.5)

		self.play(Write(cmp_fml))
		self.wait()
		self.play(ApplyMethod(cmp_fml.shift, LEFT*1.5), FadeIn(text, shift=RIGHT))
		self.wait()

	def fade_all(self, run_time=1):
		self.play(FadeIn(Curtain()), run_time=run_time)

def calc_line_intersection(l1_param, l2_param):
	A1, B1, C1 = l1_param
	A2, B2, C2 = l2_param
	det = A1*B2-A2*B1
	assert(det!=0)
	detx = (-C1)*B2-(-C2)*B1
	dety = (-C2)*A1-(-C1)*A2
	return (detx/det, dety/det)

def oval_tangent_line_ABC(a, b, theta):
	x0, y0 = a*np.cos(theta), b*np.sin(theta)
	return x0/a**2, y0/b**2, -1

class OvalCircumferenceProblem(OvalScene):
	def construct(self) -> None:
		self.setup_oval()
		self.construct_geometry_elements()
		self.show_geometry_elements()
		#self.interact()
		self.construct_ellipse_int_deduction_elements()
		self.show_ellipse_int_deduction()
		self.remove_all_elements()
	
	def setup_oval(self):
		self.init_axes()
		a, b = 2.6, 1.5
		self.init_oval(a, b)

		axes, oval = self.axes, self.oval
	
	def generate_enveloping_line_segments(self, nr_segmenet):
		a,b = self.a, self.b

		terminal_theta = np.linspace(0,2*PI,nr_segmenet+1)

		line_param = [] # in the form of (A,B,C) where Ax+By+C=0 is the line
		for i in range(nr_segmenet):
			line_param.append(oval_tangent_line_ABC(a,b, \
					   (terminal_theta[i]+terminal_theta[i+1])/2))

		line_segments = VGroup()
		for i in range(nr_segmenet):
			if i==0:
				A, B, C = line_param[i]
				start_LC = (-C/A,0)
			else:
				start_LC = calc_line_intersection(line_param[i-1],line_param[i])
			if i==nr_segmenet-1:
				A, B, C = line_param[-1]
				end_LC = (-C/A,0)
			else:
				end_LC = calc_line_intersection(line_param[i],line_param[i+1])
			line_segments.add(self.line(start_LC, end_LC, stroke_width=7))

		return line_segments

	def construct_geometry_elements(self):
		NR_SEGMENT = 10
		self.line_segments = self.generate_enveloping_line_segments(NR_SEGMENT)
		self.NR_SEGMENT = NR_SEGMENT

		t2c = {'S':BLUE,'a':BLUE_B,'b':BLUE_B,'C':YELLOW}

		area_fml      = MTex(r'S=\pi ab',tex_to_color_map=t2c,font_size=70)
		circ_area_part= MTex(r'\pi r^2',font_size=70)
		circum_fml    = MTex(r'C=\,\,\,?',tex_to_color_map=t2c,font_size=70)
		area_fml      .to_edge(UR,buff=1.2).shift(LEFT*.3)
		circ_area_part.next_to(area_fml[1],RIGHT).shift(UP*.1)
		circum_fml    .next_to(area_fml,DOWN,buff=MED_LARGE_BUFF).align_to(area_fml,LEFT)
		
		self.area_fml = area_fml
		self.circum_fml = circum_fml
		self.circ_area_part = circ_area_part
	
	def show_geometry_elements(self):
		axes, oval = self.axes, self.oval
		line_segments = self.line_segments
		NR_SEGMENT = self.NR_SEGMENT
		area_fml = self.area_fml
		circum_fml = self.circum_fml
		circ_area_part = self.circ_area_part
		
		self.play(Create(axes), Create(oval, time_span=[.5,1.5]))
		self.wait()

		# 椭圆的面积问题
		oval.set_fill(BLUE_E)
		self.play(FadeIn(area_fml),oval.animate.set_fill(BLUE_E,.8).set_anim_args(time_span=[.5,1.5]))
		self.play(FadeTransform(area_fml[2:],circ_area_part))
		self.wait()
		self.play(FadeTransform(circ_area_part,area_fml[2:]))
		self.play(oval.animate.set_fill(BLUE_E,.0))
		self.wait()

		# 周长问题就很难了
		self.play(FadeIn(circum_fml),oval.animate.set_stroke(YELLOW,8).set_anim_args(time_span=[0,1]))
		self.wait(2)
		self.play(oval.animate.set_stroke(WHITE,5).set_anim_args(time_span=[0,1]))
		self.wait(2)

		# 切分线段
		self.play(
			oval.animate.set_stroke(opacity=0.3),
			*[
				Write(
					line_segments[k], 
					time_span=0.6+overlap_timespan(k,3,NR_SEGMENT,0.7),
					rate_func=linear
				)
				for k in range(NR_SEGMENT)
			],
		)
		
		self.wait(0.5)
		self.play(FadeOut(line_segments))

		self.wait(.5)
		self.add(line_segments)
		line_segments.become(self.generate_enveloping_line_segments(4))
		self.wait(.8)
		line_segments.become(self.generate_enveloping_line_segments(6))
		self.wait(.5)
		line_segments.become(self.generate_enveloping_line_segments(10))
		self.wait(.5)
		line_segments.become(self.generate_enveloping_line_segments(16))
		self.NR_SEGMENT = 16
		self.wait()

		oval_circum_ext = MTex('\sum_{i=1}^n \Delta l_i').next_to(circum_fml[1],RIGHT)
		tmp = circum_fml[2:]
		self.play(FadeOut(area_fml),Transform(tmp,oval_circum_ext))
		self.remove(tmp); self.add(oval_circum_ext)
		self.wait()

		self.oval_circum_ext = oval_circum_ext

		'''
		# line segmeents highlight 1
		self.play(
			line_segments.animate.set_stroke(width=5),
			oval.animate.set_stroke(opacity=0.3)
		)
		self.wait()
		
		# line segmeents highlight 2 
		self.play(*[
			line_segments[k].animate.set_color(YELLOW).scale(1.1).set_stroke(width=5*1.2) \
				.set_anim_args(
					time_span=overlap_timespan(k,2,NR_SEGMENT,0.9),
					rate_func=there_and_back
				)
			for k in range(NR_SEGMENT)
		])
		self.wait()
		'''

	def construct_ellipse_int_deduction_elements(self):
		axes, oval = self.axes, self.oval
		line_segments = self.line_segments

		t2c = {
			'a': BLUE, 'b': BLUE, 'c': BLUE,
			'a^2': BLUE, 'b^2': BLUE, 'c^2': BLUE,
			r'C': YELLOW
		}
		isolate = ['=', 'a', 'b']
		tex_config = {
			'color': GREY_A,
			'font_size': 40,
			#'isolate': isolate,
			#'tex_to_color_map': t2c
		}; kw=tex_config

		tex_src = [
			r"""\frac{x^2}{a^2}+\frac{y^2}{b^2}=1\ 
			\longrightarrow\left\{\begin{aligned}x&=a\cos\theta\\ 
			y&=b\sin\theta\end{aligned}\right."""
		]
		top_line = MTex(tex_src[0],**kw)
		top_line.to_corner(UR, buff=MED_LARGE_BUFF).shift(LEFT*0.2)
		# 为了花括号，需要\begin{array}或类似环境，但这会导致
		# 其中的a被错误地分离出来，导致latex渲染失败。
		# 为此，我选择不在渲染时分离，而在后期花一点功夫手动调整。
		for idx in [3,9,18,25]:
			top_line[idx].set_color(BLUE)
		top_line[15].scale(0.86)

		#self.add(top_line)

		tex_config['isolate'] = isolate
		tex_config['tex_to_color_map'] = t2c

		tex_src = [
			r"C=\oint\mathrm dl=\int_0^{2\pi}\sqrt{\left(\frac{\mathrm dx}{\mathrm d\theta}\right)^2+\left(\frac{\mathrm dx}{\mathrm d\theta}\right)^2}\ \mathrm{d}\theta\\",
			r"=\int_0^{2\pi}\sqrt{(a\cos\theta)^2+(-b\sin\theta)^2}\ \mathrm d\theta\\",
			r"=\int_0^{2\pi}\sqrt{a^2-(a^2-b^2)\sin^2\theta}\ \mathrm d\theta\\",
			r"=a\cdot\int_0^{2\pi}\sqrt{1-c^2/a^2\sin^2\theta}\ \mathrm d\theta\\",
			r"=a\cdot \mathcal E(e,2\pi)"
		]
		ded_lines = VGroup(*[
			MTex(s, **kw) for s in tex_src
		])
		def next_line_by_equiv(row: MTex, prev_row: MTex):
			i = prev_row.get_submob_indices_lists_by_selector('=')[0][0]
			j =      row.get_submob_indices_lists_by_selector('=')[0][0]
			row.next_to(prev_row,DOWN, buff=SMALL_BUFF)
			# get_center返回的是mobject中bb变量的切片... 
			# 会产生变量纠缠问题。需要copy一下去除纠缠。
			r1=row[j].get_center().copy()
			row[j].align_to(prev_row[i],LEFT)
			r2=row[j].get_center()
			Δr=r2-r1
			row[j].shift(-Δr)
			row.shift(Δr)

		# layout
		ded_lines.arrange(DOWN)
		for row in range(1,len(ded_lines)):
			next_line_by_equiv(ded_lines[row],ded_lines[row-1])
		ded_lines.next_to(top_line,DOWN)
		# 微调
		ded_lines[0][10:-2].scale(0.8).shift(LEFT*0.5+DOWN*0.08) # 大根号调小一些
		ded_lines[0][-2:].shift(LEFT*.8+DOWN*0.08)
		ded_lines[-1].shift(DOWN*0.3)
		top_line.shift(LEFT*0.3)
		#self.add(ded_lines)

		text_config = {'font':文楷, 'color':YELLOW}
		'''
		hint_text = Text('离心率:', **text_config)
		hint_tex = MTex(r'e=\frac{c}{a}=\frac{\sqrt{a^2-b^2}}{a}',**kw)
		hint_tex.next_to(hint_text,RIGHT).shift(UP*0.1)
		hint = VGroup(hint_text, hint_tex).scale(0.7)
		hint.next_to(ded_lines[3],RIGHT)
		self.add(hint)
		'''

		# highlight
		ellipse_int_highlight = SurroundingRectangle(ded_lines[-1][3:])
		ellipse_int_label = Text('椭圆积分',**text_config)
		ellipse_int_label.next_to(ellipse_int_highlight,RIGHT,buff=0.6)
		#self.add(ellipse_int_highlight)
		#self.add(ellipse_int_label)

		self.top_line, self.ded_lines = top_line, ded_lines
		self.ellipse_int_highlight = ellipse_int_highlight
		self.ellipse_int_label = ellipse_int_label

	def show_ellipse_int_deduction(self):
		axes, oval = self.axes, self.oval
		line_segments = self.line_segments
		top_line, ded_lines = self.top_line, self.ded_lines
		ellipse_int_highlight = self.ellipse_int_highlight
		ellipse_int_label = self.ellipse_int_label
		org_circum_fml = self.circum_fml
		org_oval_circum_ext = self.oval_circum_ext

		
		# Σ Δl -> ∫dl
		self.play(*[
			m.animate.move_to(FRAME_WIDTH/4.5*LEFT)
			for m in [axes, oval, line_segments]
			],
			Transform(org_circum_fml[0:2],ded_lines[0][:2]),
			Transform(org_oval_circum_ext[0:5],ded_lines[0][2]),
			Transform(org_oval_circum_ext[5:],ded_lines[0][3:5]),
		)
		self.remove(*self.mobjects[-3:])
		detached_mobj = ded_lines[0][:5]; self.add(detached_mobj)

		# show deductions towards ellipse integral
		for i in range(5):
			ded_lines[0].replace_submobject(i,VMobject()) # detach
		all_mobj = [top_line]+[m for m in ded_lines]
		self.play(*[
			FadeIn(m, shift=UP/2, time_span=0.5+overlap_timespan(i,1.5,len(all_mobj),0.8))
			for i,m in enumerate(all_mobj)
		]); self.wait(0.5)
		for i in range(5):
			ded_lines[0].replace_submobject(i,detached_mobj[i]) # attach
		self.remove(detached_mobj); self.add(ded_lines) 
		
		# some highlights
		self.play(Create(ellipse_int_highlight), Write(ellipse_int_label, time_span=[0.6,2]))
		self.wait()

	def remove_all_elements(self):
		# all elements fade out
		axes, oval = self.axes, self.oval
		line_segments = self.line_segments
		top_line, ded_lines = self.top_line, self.ded_lines
		ellipse_int_highlight = self.ellipse_int_highlight
		ellipse_int_label = self.ellipse_int_label
		line_segments = self.line_segments
		NR_SEGMENT = self.NR_SEGMENT

		all_lines = [top_line]+[m for m in ded_lines]
		animations = []

		animations += [Uncreate(ellipse_int_highlight), FadeOut(ellipse_int_label)]
		animations += [
			FadeOut(m, shift=DOWN, time_span=0.5+overlap_timespan(i,1.5,len(all_lines),0.8))
			for i,m in enumerate(all_lines)
		]
		
		# Seems Uncreate is buggy with time_span, probably caused by
		# its rate_func settings. Hope this will be fixed in new versions.
		animations += [
			Uncreate(
				line_segments[NR_SEGMENT-1-k], 
				time_span=1+overlap_timespan(k,1.5,NR_SEGMENT,0.7),
				rate_func=lambda t: linear(1-t)
			)
			for k in range(NR_SEGMENT)
		]
		
		animations += [Uncreate(oval, time_span=[1,2])]
		animations += [FadeOut(axes, time_span=[1.8,3.3])]
		self.stop_skipping()
		self.play(*animations)
		
#!-------------------------------------------------------------------!#
#* Conclusion

class SummaryOnProblemSolving(StarskyScene):
	def construct(self) -> None:
		title = Text('椭圆的第零定义',font=文楷, isolate=['椭圆'], font_size=60).set_color_by_text('椭圆',YELLOW_B)
		points= VGroup(
			Text('+ 有效的解题方法',font=文楷),
			Text('· 填空、选择更好用',font=文楷,font_size=36),
			Text('· 大题需要说清变换关系',font=文楷,font_size=36),
			Text('· “把椭圆横向缩小a倍、纵向缩小b倍得到单位圆”',font=文楷,font_size=36),
			Text('+ 帮助理解椭圆的性质',font=文楷),
			Text('+ 短板：长度问题、双曲线问题',font=文楷),
		).arrange(DOWN)
		def align_on_left(M: VGroup):
			for m in M[1:]:
				m.align_to(M[0],LEFT)
		align_on_left(points)

		# 微调——我为什么不用ppt呢？
		for m in points[1:4]:
			m.shift(RIGHT*.6)
		points[3].set_color(GREY_B)
		points[3][0].set_opacity(0)
		
		points[1][1:6].set_color(TEAL)
		points[2][1:3].set_color(TEAL)
		points[2][-4:].set_color(YELLOW_B)

		all = VGroup(title,points).arrange(DOWN,buff=.7)
		align_on_left(all)
		all.to_edge(LEFT,buff=1.7)
		all.shift(UP*.2)

		points[-2].shift(DOWN*.15)
		points[-1].shift(DOWN*.24)

		# end weitiao——不要问我为什么用拼音
		self.play(FadeIn(title))
		self.wait(2)
		self.play(FadeIn(points[0],shift=UP/2))
		self.wait(2)
		self.play(Write(points[1]),run_time=2)
		self.wait(2)
		self.play(Write(points[2:4]),run_time=4)
		self.wait(2)
		self.play(FadeIn(points[4],shift=UP/2))
		self.wait(2)
		self.play(FadeIn(points[5],shift=UP/2))
		self.wait(2)
		self.play(FadeIn(Curtain()))

class MatrixDiagonalization(StarskyScene):
	def construct(self) -> None:
		canvas = ComplexPlane(width=4,height=4, x_range=[-2,2],y_range=[-2,2],axis_config={'stroke_color':BLUE_D})
		self.add(canvas)

		mat = np.array([[3,1],[1,3]])*0.5
		inv = np.linalg.inv(mat)
		eig_val, eig_vec = np.linalg.eig(mat)
		idx = 0 # 将要作为x轴的v的编号，0/1
		diag = np.array([[eig_val[idx],0],[0,eig_val[1-idx]]])

		axes = DataAxes(
			axis_align_towards_zero=True,
			include_numbers=False,axis_config={'include_ticks':False},
			x_range=[-3,3],width=6,
			y_range=[-3,3],height=6,
		)

		fml = VGroup(
			MTex(r'\frac 12\begin{bmatrix}3 & 1 \\ 1 & 3\end{bmatrix}'),
			MTex(r'\longrightarrow\begin{bmatrix}2 & 0 \\ 0 & 1\end{bmatrix}')
		).to_corner(UR)
		fml[0][:3].scale(.9)
		fml[1][-4:-2].set_color(GREY_C)

		# show matrix
		all = VGroup(canvas,axes)
		self.play(FadeIn(all),FadeIn(fml[0]))
		self.play(ApplyMatrix(mat, all),run_time=1)
		self.wait(.5)
		self.play(ApplyMatrix(inv, all),run_time=1)
		self.wait(.5)

		# effect of diagonalization
		new_axes = axes.copy().set_color(WHITE)
		xlabel = MTex('x'); ylabel = MTex('y')
		xlabel.add_updater(lambda m: m.next_to(new_axes.x_axis,DR).shift(LEFT*.5))
		ylabel.add_updater(lambda m: m.next_to(new_axes.y_axis,UL).shift(DOWN*.5))
		self.play(
			# Note: the vectors in eig_vec 是竖着排的，因此idx在第二个指标
			Rotate(all, -np.arctan2(eig_vec[0,idx],eig_vec[1,idx])),
			# Formula Diagonalization
			fml[0].animate.shift(LEFT*2.2),
			FadeIn(fml[1])
		)
		self.wait(.5)
		
		DARK = interpolate_color(GREY_C,GREY_D,0.7)
		#self.play(ApplyMatrix(diag, all))
		all.generate_target()
		all.target.stretch(eig_val[XDIM],XDIM).stretch(eig_val[YDIM],YDIM)
		all.target[1].set_color(DARK)
		new_axes.generate_target()
		γ=0.5
		new_axes.target.stretch(eig_val[XDIM]**γ,XDIM).stretch(eig_val[YDIM]**γ,YDIM)
		new_axes.set_opacity(0)
		self.add(new_axes)
		self.play(
			MoveToTarget(all),MoveToTarget(new_axes),
			FadeIn(xlabel),FadeIn(ylabel)
		)
		self.wait()

		self.play(FadeIn(Curtain()))

class PoissonEquation(StarskyScene):
	def construct(self) -> None:
		# parameter
		h = 1

		# tex
		tex_config = {
			'color': FML_COLOR,
			'tex_to_color_map':{r'\vec{E}':BLUE}
		}
		fml1 = MTex(r'\frac{\partial^2\varphi}{\partial x^2}+\frac{\partial^2\varphi}{\partial y^2}=-4\pi\rho_e',**tex_config)
		fml2 = MTex(r'\vec{E}=-\nabla\varphi',**tex_config)
		fml1[:15].scale(0.8).shift(RIGHT*0.2)
		fml2.next_to(fml1, DOWN, buff=MED_SMALL_BUFF)
		fml = VGroup(fml1, fml2).to_edge(DOWN, buff=1).to_edge(RIGHT, buff=2)

		# construct elements
		center_dot = Dot(UP*h)
		self.add(center_dot)

		ground = ParametricCurve(lambda t: RIGHT*t,[-5,5,0.1])

		NR_ARROWS = 8
		def z2dir(z):
			return RIGHT*z.real+UP*z.imag

		elec_field_baseline = VGroup()
		for i in range(NR_ARROWS):
			theta = (0.5+i)*TAU/NR_ARROWS
			elec_field_baseline.add(ParametricCurve(
				lambda t: z2dir(-(np.exp(1j*theta)*t+1)/(np.exp(1j*theta)*t-1)*h*1j),
				t_range = [0,1,0.005]
			))
		
		origin_arrow = ArrowTip(width=0.25,fill_color=BLUE)
		elec_field = VGroup(VMobject(color=BLUE),origin_arrow.copy())*NR_ARROWS
		alpha = ValueTracker(0)
		def geometry_controller(m):
			for i in range(NR_ARROWS):
				points = elec_field_baseline[i].get_points()
				buff = MED_SMALL_BUFF
				start, end = 0, points.shape[0]//3
				while get_norm(points[3*start]-points[0])<buff: start+=1
				while get_norm(points[3*(end-1)]-points[-1])<buff: end-=1
				if end<start: end=start
				buffered_points = points[3*start:3*end]
				elec_field[i][0].set_points(buffered_points)
			
				p = alpha.get_value()
				end_tangent = points[-1]-points[-2]
				# arrow tips
				elec_field[i][1].set_points(origin_arrow.get_points())
				elec_field[i][1].set_opacity(1)
				elec_field[i][1].scale((1-p)*(0.8+(i-3.5)**2*0.02)+p*0.8)
				elec_field[i][1].move_to(buffered_points[3*(-1)])
				elec_field[i][1].rotate(-np.arctan2(end_tangent[0],end_tangent[1])+PI/2)

		elec_field.add_updater(geometry_controller)
			
		elec_field_baseline.set_opacity(0)

		center_dot.add_updater(lambda m: m.move_to(elec_field_baseline[0].get_start()))

		charge_label_p = MTex('+Q').scale(0.8).next_to(center_dot, UP, buff=MED_LARGE_BUFF)
		charge_label_n = MTex('-Q').next_to(ground, DOWN)
		charge_labels = VGroup(charge_label_p, charge_label_n)

		def gamma_corr(func,γ):
			def wrapped_func(α):
				return func(α**γ)
			return wrapped_func
		
		self.play(
			FadeIn(center_dot),
			Create(ground),
			LaggedStart(*[
				Create(m,run_time=((i-NR_ARROWS/2)/NR_ARROWS)**4*6+1,rate_func=gamma_corr(linear,.4))
				for i,m in enumerate(elec_field)],
				lag_ratio=.1
			),
			FadeIn(charge_labels[0],time_span=[0,1]),
			FadeIn(charge_labels[1],time_span=[.5,1.5]),

			FadeIn(fml1),FadeIn(fml2)
		)
		self.wait() # to preserve partial animation video file order

		# 整理一下图层
		self.add(
			fml1,fml2,
			center_dot,ground,
			elec_field,elec_field_baseline,
			charge_labels
		)

		# transform
		unit_circ = Circle(color=WHITE)
		self.wait()
		self.play(
			FadeOut(charge_labels, time_span=[0,1]),
			ApplyComplexFunction(lambda z: (z-h*1j)/(z+h*1j), ground),
	   		ApplyComplexFunction(lambda z: (z-h*1j)/(z+h*1j), elec_field_baseline),
			alpha.animate.set_value(1),
			FadeIn(unit_circ, time_span=[2.5,3.5]),

			fml.animate.shift(RIGHT*0.8).set_anim_args(time_span=[1,2.5]),
			run_time=3
	    )
		self.wait()

		self.play(FadeIn(Curtain()))

#!-------------------------------------------------------------------!#
#* 封面特供
class SceneForCover(OvalScene):
	def construct(self) -> None:
		xmax=2.5
		self.init_axes(
			x_range= [-xmax,3*xmax], width=6*2,
			y_range= [-xmax*1.1,xmax*1.1], height=6*1.1,
			axis_config={'include_ticks':False}
		)
		self.axes.shift(ORIGIN)
		self.init_oval(2,1.4)

		axes = self.axes
		oval = self.oval
		circ = self.unit_circ

		oval.set_stroke(YELLOW,13)
		circ.set_stroke(GREY_A,10)

		self.add(axes, oval, circ)

		text = Text('椭圆化圆',font=文楷,color=GREY_A).scale(2.5).to_corner(UR,buff=1).shift(DOWN)
		text2= Text('降维打击',font=文楷,color=GREY_A).scale(2.5).to_corner(DR,buff=1).shift(UP)
		text.set_color(YELLOW_A)
		text[2].set_color(GREY_A)
		self.add(text,text2)