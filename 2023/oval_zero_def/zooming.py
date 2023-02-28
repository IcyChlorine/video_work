from manimlib import *

from OpenGL.GL import *

import os,sys
sys.path.append('C:\\StarSky\\Programming\\MyProjects\\')
from manimhub import *
sys.path.append(os.getcwd())

from typing import Optional

class CompositionCamera(Camera):

	# Rendering
	def capture(self, *mobjects: Mobject, **kwargs) -> None:
		self.refresh_perspective_uniforms()
		for mobject in mobjects:

			if isinstance(mobject, VMobject) and hasattr(self, 'stroke_sf'):
				for sub in mobject.get_family():
					if not hasattr(sub, '_fxxx_mark'):
						sub.unlock_data()
						sub.data['stroke_width'] *= self.stroke_sf
						# do not inject vars starting with two underscore
						# see https://stackoverflow.com/questions/14671487/what-is-the-difference-in-python-attributes-with-underscore-in-front-and-back
						sub._fxxx_mark=1

			for RG in self.get_render_group_list(mobject):
				self.render(RG)

			if isinstance(mobject, VMobject) and hasattr(self, 'stroke_sf'):
				for sub in mobject.get_family():
					if hasattr(sub, '_fxxx_mark'):
						sub.data['stroke_width'] /= self.stroke_sf
						del sub._fxxx_mark

	def get_render_group_list(self, mobject: Mobject) -> Iterable[dict[str]]:
		return self.generate_render_group_list(mobject)	
	
	def generate_render_group_list(self, mobject: Mobject) -> Iterable[dict[str]]:
		return (
			self.get_render_group(sw, single_use=True)
			for sw in mobject.get_shader_wrapper_list()
		)
	
	# composition试验
	def set_shader_uniforms(
		self,
		shader: moderngl.Program,
		shader_wrapper: ShaderWrapper
	) -> None:
		for name, path in shader_wrapper.texture_paths.items():
			if hasattr(shader_wrapper, 'fbo'): 
				if self.n_textures == 15:  # I have no clue why this is needed
					self.n_textures += 1
				tid = self.n_textures
				self.n_textures += 1
				texture=shader_wrapper.fbo.color_attachments[0]
				texture.use(location=tid)
				
			else: tid = self.get_texture_id(path)

			shader[name].value = tid
			
		for name, value in it.chain(self.perspective_uniforms.items(), shader_wrapper.uniforms.items()):
			try:
				if isinstance(value, np.ndarray) and value.ndim > 0:
					value = tuple(value)
				shader[name].value = value
			except KeyError:
				pass

# composition试验
class CameraCapture(ImageMobject):
	CONFIG = {
		'camera_class': CompositionCamera
	}
	def __init__(self, give_me_the_fxxx_mgl_ctx, **kwargs):
		filename='tmp.png'
		self.set_image_path(get_full_raster_image_path(filename))
		self.path = '$'
		self.texture_paths['Texture']='$'

		Mobject.__init__(self, **kwargs)

		self.camera = self.camera_class(ctx=give_me_the_fxxx_mgl_ctx)
		# bind fbo to shader_wrapper so camera can find it as texture later on
		self.shader_wrapper.fbo = self.camera.fbo_msaa

class TestComposition(StarskyScene):
	CONFIG = {
		'camera_class': CompositionCamera
	}

	def construct(self) -> None:
		self.stop_skipping()
		#dots = VGroup(*[Dot() for i in range(5)]).arrange(RIGHT).shift(3*LEFT)
		#self.add(dots)
		#arrow = Arrow().add_updater(lambda m: m.put_start_and_end_on(dots[2].get_center()+DOWN, dots[2].get_center()))
		#self.add(arrow)
		vlines = VGroup(*[Line(DOWN, UP) for i in range(5)]).arrange(RIGHT, buff=0.15).shift(LEFT*3)
		self.add(vlines)

		detail = CameraCapture(self.camera.ctx).shift(RIGHT*3)
		bb=SurroundingRectangle(detail, buff=0).add_updater(lambda m:m.surround(detail, stretch=True, buff=0))	
		detail.refresh_shader_data()
		#detail.set_width(4, stretch=True)

		#detail.camera.capture(*self.mobjects)

		upper=1; down=0; left=0; right=1
		def updater(m: CameraCapture):
			m.camera.fbo_msaa.use(); 
			m.camera.fbo_msaa.clear()
			m.camera.capture(*self.mobjects)

		self.add(bb,detail)

		detail.add_updater(updater)
		detail.data['im_coords']=np.array([(left, upper), (left, down), (right, upper), (right, down)])

		#self.play(dots.animate.shift(UP*3), run_time=1)

		detail.camera.frame.move_to(vlines.get_center())
		#detail.camera.frame.scale(0.2)

		self.wait()

		zoomin_scale = ValueTracker(1) # should be synced with detail.camera
		def stroke_sf_notifier(m):
			detail.camera.stroke_sf=zoomin_scale.get_value()
		detail.add_updater(stroke_sf_notifier)

		#detail.camera.stroke_sf=5
		self.play(
			detail.camera.frame.animate.scale(0.5, about_point=vlines.get_center()),
			zoomin_scale.animate.set_value(2)
			)

		# Urghhhh. Caching issues again.
		# This shouldn't be necessay, but things don't work without this.
		# It seems that camera will resort to the old render group
		# which is cached before self.play() after an animation is over
		# and mobjects will fall back to the state before animation.
		# I'm sure it's related to the render group caching mechanism
		# in camera, but not clear why the old render groups are not cleared.
		# Uddate: in the latest versions of manimgl master, 
		# rendering is put to Mobject and ShaderWrapper
		# so the caching mechanism in camera will NO LONGER EXIST.
		# So I'll just keep the trick and lose some performance
		# for the time being, never mind.
		detail.camera.refresh_static_mobjects()

		self.play(vlines.animate.stretch(1.5, 0))
		#self.wait(15)