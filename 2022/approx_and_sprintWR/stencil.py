from manimlib import *

from OpenGL.GL import *

import os,sys
sys.path.append('C:\\StarSky\\Programming\\MyProjects\\')
from manimhub import *
sys.path.append(os.getcwd())

from typing import Optional

from sprintWR_data_frame import SprintWRDataFrame

class StencilGroup(Group):
	def __init__(self,stencil_mobject, *stenciled_mobjects):
		super().__init__()
		self.add(stencil_mobject)
		self.add(Group(*stenciled_mobjects))
		self.name_parts()

	def name_parts(self):
		self.stencil_mobject = self.submobjects[0]
		self.stenciled_mobjects = self.submobjects[1]
		return self

	def set_stencil_mobject(self, m):
		self.submobjects[0]=m
		self.stencil_mobject = self.submobjects[0]
		return self

	def add_stenciled(self, *mobjects):
		return self.stenciled_mobjects.add(mobjects)

	def copy(self, deep=False):
		copy_mobject = super().copy(deep=deep)
		copy_mobject.name_parts()
		return copy_mobject

STENCIL_DISABLED = 0
STENCIL_ENABLED = 1
STENCIL_WRITE = 2
STENCIL_CLIP = 3
class StencilCamera(Camera):
	CONFIG = {
		'stencil_enabled': False
	}
	
	# Rendering
	def capture(self, *mobjects: Mobject, **kwargs) -> None:
		self.refresh_perspective_uniforms()
		for mobject in mobjects:
			if isinstance(mobject, StencilGroup):
				self.set_stencil_mode(STENCIL_ENABLED)
				for RG in self.get_render_group_list(mobject.stencil_mobject):
					self.set_stencil_mode(STENCIL_WRITE)
					self.render(RG)
				for RG in self.get_render_group_list(mobject.stenciled_mobjects):
					self.set_stencil_mode(STENCIL_CLIP)
					self.render(RG)
				self.set_stencil_mode(STENCIL_DISABLED)
			else:
				for RG in self.get_render_group_list(mobject):
					self.render(RG)

	def set_stencil_mode(self, mode) -> None:
		if mode == STENCIL_DISABLED:
			glDisable(GL_STENCIL_TEST)
		elif mode == STENCIL_ENABLED:
			glEnable(GL_STENCIL_TEST)
		elif mode == STENCIL_WRITE:
			glClear(GL_STENCIL_BUFFER_BIT)
			glStencilFunc(GL_ALWAYS, 1, 0xFF)
			glStencilOp(GL_KEEP, GL_REPLACE, GL_REPLACE)
		elif mode == STENCIL_CLIP: 
			glStencilFunc(GL_EQUAL, 1, 0xFF) #只有模板值为1时才通过
			glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
		else:
			raise ValueError("Unknown mode to StencilCamera.set_stencil_mode(...)!")


	def init_context(self, ctx: Optional[moderngl.Context]=None) -> None:
		super().init_context(ctx)
		
		# attach stencil buffer to fbo_msaa
		# can't attach stencil buffer to fbo(framebuffer0, window) though,
		# that will cause GL_INVALID_OPERATION.
		depth_stencil_buffer = glGenRenderbuffers(1)
		glBindRenderbuffer(GL_RENDERBUFFER, depth_stencil_buffer)
		glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.pixel_width, self.pixel_height)

		glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.fbo_msaa.glo)
		glFramebufferRenderbuffer(GL_DRAW_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, depth_stencil_buffer)



class StencilScene(StarskyScene):
	CONFIG = {
		'camera_class': StencilCamera
	}
	# 由于修改了渲染时使用的fbo，这里要修改一下渲染管线（高层次的）
	def update_frame(self, dt: float = 0, ignore_skipping: bool = False) -> None:
		if self._should_restart(): 
			raise RestartScene()

		self.increment_time(dt)
		self.update_mobjects(dt)
		if self.skip_animations and not ignore_skipping:
			return

		if self.is_window_closing():
			raise EndScene()

		if self.window:
			self.window.clear()
			self.camera.fbo_msaa.use() # 由于PygletWindow.clear()会重新启用自己的fbo，这里需要显式启用自己的fbo
		self.camera.clear()
		self.camera.capture(*self.mobjects)

		if self.window:
			pw, ph = self.camera.pixel_width, self.camera.pixel_height
			gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.camera.fbo_msaa.glo)
			gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, self.camera.fbo.glo)
			gl.glBlitFramebuffer(0, 0, pw, ph, 0, 0, pw, ph, gl.GL_COLOR_BUFFER_BIT, gl.GL_LINEAR)

			self.window.swap_buffers()
			vt = self.time - self.virtual_animation_start_time
			rt = time.time() - self.real_animation_start_time
			if rt < vt:
				self.update_frame(0)



class TestStencil(StencilScene):
	def construct(self):
		area1 = Rectangle(FRAME_WIDTH/2,FRAME_HEIGHT, fill_opacity=0.001, stroke_opacity=0).align_on_border(LEFT,buff=0)
		axes = SprintWRDataFrame()
		left = StencilGroup(area1, axes)
		self.add(left)
		
		c=Circle()
		area2 = Rectangle(FRAME_WIDTH/2,FRAME_HEIGHT, fill_opacity=0.001, stroke_opacity=0).align_on_border(RIGHT,buff=0)
		right = StencilGroup(area2, c)
		self.add(right)

		left.stenciled_mobjects.add_updater(lambda m: m)
		axes.x_axis.morph_existing_number_labels = False
		axes.y_axis.morph_existing_number_labels = False
		
		self.play(area1.shift, LEFT*1.5, axes.scale,0.5, reorganize_mobjects=False)
		left.stenciled_mobjects.clear_updaters()

	def enable_and_write_stencil(self):
		glEnable(GL_STENCIL_TEST)

		glClear(GL_STENCIL_BUFFER_BIT)
		glStencilFunc(GL_ALWAYS, 1, 0xff)
		glStencilOp(GL_KEEP, GL_REPLACE, GL_REPLACE)

		area = Rectangle(FRAME_WIDTH/1.92,FRAME_HEIGHT, fill_opacity=0.001, stroke_opacity=0).align_on_border(RIGHT,buff=0)
		area.refresh_shader_data()
		area.refresh_shader_wrapper_id()
		self.camera.fbo_msaa.use()
		for render_group in self.camera.get_render_group_list(area):
			self.camera.render(render_group)

		glStencilFunc(GL_NOTEQUAL, 1, 0xff)
		glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)