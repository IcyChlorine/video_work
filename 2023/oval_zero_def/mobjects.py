from manimlib import *
__manimhub_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__manimhub_path__)
from manimhub import *

# 直角标记（“∟”） 
class RightAngleMark(VMobject):
	def __init__(self, A,O,B, **kwargs):
		super().__init__(**kwargs)
		OA = normalize(A-O)*0.2
		OB = normalize(B-O)*0.2
		self.vertices = [O+OA, O+OA+OB, O+OB]
		self.set_points_as_corners(self.vertices)

class LengthMark(VGroup):
	CONFIG = {
		'mark_len': 0.2
	}
	def __init__(self, 
		start=DOWN, 
		end=UP,
	):
		super().__init__()
		mark_len = self.mark_len
		self.start, self.end = start, end
		dir = normalize(end-start)
		norm = np.array([-dir[1],dir[0],0])

		self.line = Line(start, end)
		self.start_mark = Line(
			start+norm*mark_len/2, 
			start-norm*mark_len/2)
		self.end_mark = Line(
			end+norm*mark_len/2, 
			end-norm*mark_len/2)

		self.add(self.line, self.start_mark, self.end_mark)

	def set_start_and_end(self, start, end):
		if get_norm(end-start)==0: # prevent numerical disaster
			original_dir = normalize(self.end-self.start)
			eps=1e-6; end=start+original_dir*eps
		
		mark_len = self.mark_len
		self.start, self.end = start, end

		dir = normalize(end-start)
		norm = np.array([-dir[1],dir[0],0])

		self.line.put_start_and_end_on(start, end)
		self.start_mark.put_start_and_end_on(
			start+norm*mark_len/2, 
			start-norm*mark_len/2)
		self.end_mark.put_start_and_end_on(
			end+norm*mark_len/2,
			end-norm*mark_len/2)
		return self
	
	def set_start(self, start):
		return self.set_start_and_end(start, self.end)

	def set_end(self, end):
		return self.set_start_and_end(self.start, end)
	
	# to facilitate animation
	def shrink_to_start(self):
		return self.set_end(self.start)

	def shrink_to_middle(self):
		mid = (self.start+self.end)/2
		return self.set_start_and_end(mid, mid)

	def refresh_attr(self):
		self.start, self.end = self.line.get_start_and_end()
		return self

GROW_FROM_START = 0
GROW_FROM_MIDDLE = 1
class GrowLengthMark(Transform):
	FadeIn
	def __init__(self, length_mark: LengthMark, from_start_or_middle=GROW_FROM_START, **kwargs):
		if not (isinstance(length_mark, LengthMark) 
	  		and from_start_or_middle in [GROW_FROM_START, GROW_FROM_MIDDLE]):
			raise ValueError('invalid arg!')
		self.from_start_or_middle = from_start_or_middle
		super().__init__(length_mark, **kwargs)

	def create_target(self) -> Mobject:
		return self.mobject

	def create_starting_mobject(self) -> Mobject:
		mobj = super().create_starting_mobject()
		start, end = mobj.start, mobj.end
		if get_norm(end-start)>0:
			dir = normalize(end-start)
		else:
			dir = RIGHT
		mid = (start+end)/2
		if self.from_start_or_middle == GROW_FROM_START:
			mobj.set_start_and_end(start, start+dir*1e-6)
		elif self.from_start_or_middle == GROW_FROM_MIDDLE:
			mobj.set_start_and_end(mid, mid+dir*1e-6)
		return mobj

# resemble Tex behaviour from Text——used in TrigAreaTransform only
class TextGroup(VGroup):
	def __init__(self, *text_strs, **kwargs):
		super().__init__()
		for s in text_strs:
			mobj = Text(s, font=文楷, color=FML_COLOR)
			if len(self.submobjects)>0: mobj.next_to(self.submobjects[-1])
			self.add(mobj)
