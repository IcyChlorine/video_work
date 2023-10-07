from manimlib import *
from manimhub import * 
import os, sys; sys.path.append(os.path.dirname(__file__))
from set_output_path import set_output_path

#* 木块从光滑固定斜面上划下的模拟&渲染.
#* 绝大多数复杂性来自于转角处...
class SmoothSlope(StarskyScene):
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
		
		#* 几何参数
		theta = 30*DEGREES
		slope_width = 2
		slides_size = 0.7
		ground_color = interpolate_color(GREY_C,GREY_B,0.5)

		#* ground
		upper  = Rectangle(width=FRAME_WIDTH-2,height=0.3) \
				.set_fill(color=ground_color,opacity=1) \
				.set_stroke(width=0) \
				.shift(DOWN*0.5)
		lower = upper.copy().stretch(0.8,1).next_to(upper,DOWN,buff=0)
		color = color_to_rgb(ground_color)
		rgba_trans = [*color,0]; rgba_solid = [*color,1]
		lower.set_rgba_array(
			[rgba_solid]*6 + [rgba_trans]*6
		)
		# 3 = nr_points_per_curve_node
		ground = VGroup(lower,upper).shift(DOWN*0.5)
		
		#* slope
		
		slope  = Polygon(ORIGIN,RIGHT*slope_width,UP*slope_width*np.tan(theta)).scale(2) \
				.set_fill(color=YELLOW_E,opacity=1) \
				.set_stroke(color=YELLOW_A) \
				.next_to(ground,UP,buff=0) 
		
		slides = Square(slides_size) \
				.set_fill(color=TEAL,opacity=1) \
				.set_stroke(color=BLUE_A)
	
		connected = VGroup(slope,slides)
		slope.rotate(theta)
		slides.next_to(slope,UP,buff=0.04) # buff by stroke width
		connected.rotate(-theta)
		connected.next_to(ground,UP,buff=0.02)
		
		#add(ground,slope,slides)
		
		#* rigid body simulation
		slides.vx = 0; slides.vy = 0; slides.w = 0
		def slides_RB_sim(_, dt):
			O = slope.data['points'][3] + (RIGHT*np.sin(theta)+UP*np.cos(theta))*0.04 # 修正
			A = slides.data['points'][3]
			B = slides.data['points'][6]
			C = slides.data['points'][9]
			D = slides.data['points'][0]

			sim_slowdown = 2
			dt /= sim_slowdown

			g = 9.8
			m = 1
			d = slides_size
			I = m*d**2/6
			if C[0] <= O[0]:
				slides.ax = np.cos(theta)*g
				slides.ay =-np.sin(theta)*g
				slides.vx+= slides.ax*dt
				slides.vy+= slides.ay*dt
			elif B[0] > O[0]+0.1/sim_slowdown: # add 0.1 to get one more frame of 
				slides.vy = 0
				slides.w  = 0
			else: # sth really complicated's about to happen!
				# prepare for the calculation
				#dt = dt/10
				CD = D-C
				angle = np.arctan2(CD[1],CD[0])
				gamma = PI/2 - angle
				alpha = theta - gamma
				if slides.w == 0:
					# The problem arises from the model, inherently.
					# so a init omega is needed, manually.
					# To handle the problem, suppose a brief impulse is exerted by ground (UP)
					# to give a proper initial angular velocity, so that vx remains unchanged
					# when entering the junction.
					# The impulse need not be calculated, though. Just set w properly.
					
					# This is physically correct(reasoned from above)
					#slides.w = slides.vx / d / (-np.cos(gamma)*np.cos(theta)/np.sin(theta) + np.cos(gamma-PI/4)/np.sqrt(2))
					#slides.w *= -1

					# But this is more visually satisfying, so I'll use this as I'm doing a visual project
					slides.w = slides.vy / d / (-np.cos(gamma)+np.cos(gamma-PI/4)/np.sqrt(2))
					slides.w /= g # why??

				# solve for Ns Ng
				Ns = 0
				Ng = 0
				a11 = np.sin(theta)/m
				a12 = 0
				a21 = np.cos(theta)/m
				a22 = 1/m
				b1 = d/np.sqrt(2)/I*np.sin(alpha-PI/4)
				b2 = d/np.sqrt(2)/I*np.sin(PI/4-gamma)
				c1 = d*            (np.cos(gamma)*np.cos(theta)/np.sin(theta) + np.sin(gamma-PI/4)/np.sqrt(2))
				c2 = d*            (-np.cos(gamma)                            + np.cos(gamma-PI/4)/np.sqrt(2))
				d1 = d*slides.w**2*(np.cos(gamma)*np.cos(theta)/np.sin(theta) - np.cos(gamma-PI/4)/np.sqrt(2))
				d2 = d*slides.w**2*(-np.sin(gamma)                            + np.sin(gamma-PI/4)/np.sqrt(2)) + g

				AA = np.zeros((2,2),dtype=np.float64)
				bb = np.zeros((2,),dtype=np.float64)
				AA[0,0] = a11 - c1*b1
				AA[0,1] = a12 - c1*b2
				AA[1,0] = a21 - c2*b1
				AA[1,1] = a22 - c2*b2
				bb[0] = d1
				bb[1] = d2

				res = np.linalg.solve(AA,bb)
				Ns = res[0]
				Ng = res[1]
				#print(f'Ns = {Ns:.3f}, Ng = {Ng:.3f}')

				# update variables; a.k.a. step forward differential equations.
				beta = (d/np.sqrt(2)/I*( \
					+Ng*np.sin(PI/4-theta+alpha) \
					-Ns*np.sin(PI/4-alpha)
				))
				
				# update velocity: velocity constraint based (f(v,w)=0)
				slides.vx = d*slides.w*(np.cos(gamma)*np.cos(theta)/np.sin(theta) + np.sin(gamma-PI/4)/np.sqrt(2))
				slides.vy = d*slides.w*(-np.cos(gamma)                            + np.cos(gamma-PI/4)/np.sqrt(2))
				# update velocity: update based (dv/dt=a)
				#slides.vx += dt * Ns*np.sin(theta)/m
				#slides.vy += dt * ((Ns*np.cos(theta)+Ng)/m - g)

				slides.w += dt * beta

			slides.shift((slides.vx*RIGHT + slides.vy*UP)*dt)
			slides.rotate(slides.w*dt)

			# Fade out to the right
			fade_x = 4.5
			if B[0] > fade_x:
				slides.set_opacity(1-(B[0]-fade_x))

		def slides_RB_sim_Lagrange(_, dt):
			'''Another method, using Lagrange equation for the constraint motion equation at the junction.
			this method results in 1)lower dimension of freedom and 2)simpler equations & easier equation solving.'''
			O = slope.data['points'][3] + (RIGHT*np.sin(theta)+UP*np.cos(theta))*0.04 # 修正
			A = slides.data['points'][3]
			B = slides.data['points'][6]
			C = slides.data['points'][9]
			D = slides.data['points'][0]

			sim_slowdown = 2
			dt /= sim_slowdown

			g = 9.8
			d = slides_size 
			if C[0] <= O[0]:
				slides.ax = np.cos(theta)*g
				slides.ay =-np.sin(theta)*g
				slides.vx+= slides.ax*dt
				slides.vy+= slides.ay*dt
			elif B[0] > O[0] - 0.1/sim_slowdown: # add 0.1 to get one more frame of 
				#TODO: This section is not properly handled yet;
				# the vx acuired at the junction(next 'else' section) is not passed to this section, yet.
				slides.vy = 0
				slides.w  = 0
			else: # sth really complicated's about to happen!
				# prepare for the calculation
				#dt = dt/10
				CD = D-C
				angle = np.arctan2(CD[1],CD[0])
				gamma = PI/2 - angle
				gamma_prev = gamma

				if slides.w == 0:
					# The problem arises from the model, inherently.
					# so a init omega is needed, manually.
					# To make up for this, suppose a brief impulse is exerted by ground (UP)
					# to give a proper initial angular velocity, so that vx remains unchanged
					# when entering the junction.
					# The impulse need not be calculated, though. Just set w properly.
					slides.w = slides.vx / d / (-np.cos(gamma)*np.cos(theta)/np.sin(theta) + np.cos(gamma-PI/4)/np.sqrt(2))
					slides.w *= -1
					
					#slides.w = 0

					slides.w = slides.vy / d / (-np.cos(gamma)+np.cos(gamma-PI/4)/np.sqrt(2))
					slides.w /= g # why??

				#*************#
				ga = gamma
				gd = -slides.w
				gdd = 0
				#*******************************************************************#
				#* Derived by Euler-Lagrange Equation under geometric constraint,  *#
				#*                  picking γ as the main generalized coordinate.  *#
				cot = 1/np.tan(theta)
				A = np.sin(theta)**(-2) - 1 - cot
				B = cot - 1

				# define f(γ) as follows, and df/dγ
				fg  = A*np.cos(gamma)**2 + B*np.sin(2*gamma)/2 + 1/2
				dfg = -A*np.sin(2*gamma) + B*np.cos(2*gamma)
				gdd = gd**2*dfg/(fg+1/6)/2 # Ultimate simplified form! Independant of mass and length (m,d) parameters!
				
				gd += dt * gdd
				ga += dt * gd
				#*******************************************************************#
				slides.w = -gd
				gamma = ga
				#*************#

				print(gamma)
				x = d*(-np.sin(gamma)*np.cos(theta)/np.sin(theta) + np.cos(PI/4-gamma)/np.sqrt(2))
				y = d*( np.sin(gamma)                             + np.sin(PI/4-gamma)/np.sqrt(2))
				#print('x,y=',x,y)

				slides.rotate(+gamma_prev)
				slides.move_to(O+x*RIGHT+y*UP)
				slides.rotate(-gamma)

				return

			slides.shift((slides.vx*RIGHT + slides.vy*UP)*dt)
			slides.rotate(slides.w*dt)

			fade_x = 4.5
			if B[0] > fade_x:
				slides.set_opacity(1-(B[0]-fade_x))

		self.stop_skipping()
		play(FadeIn(ground),FadeIn(slope),FadeIn(slides))
		wait()
		slides.add_updater(slides_RB_sim)
		wait(10)