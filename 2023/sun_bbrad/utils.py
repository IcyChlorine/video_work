import numpy as np
from manimlib import clip

def map_range(x, x_min, x_max, y_min, y_max):
	return (x-x_min)/(x_max-x_min)*(y_max-y_min)+y_min

def wavelength_to_rgb(wavelength):
  clip(wavelength, 380.0, 780.0)
  
  if ((wavelength >= 380.0) and (wavelength <= 410.0)):
    R =0.6-0.41*(410.0-wavelength)/30.0
    G = 0.0
    B = 0.39+0.6*(410.0-wavelength)/30.0
  elif ((wavelength >= 410.0) and (wavelength <= 440.0)):
    R =0.19-0.19*(440.0-wavelength)/30.0
    G = 0.0
    B = 1.0
  elif ((wavelength >= 440.0) and (wavelength<= 490.0)):
    R =0
    G = 1-(490.0-wavelength)/50.0
    B = 1.0
  elif ((wavelength >= 490.0) and (wavelength <= 510.0)):
    R =0
    G = 1
    B = (510.0-wavelength)/20.0
  elif ((wavelength >= 510.0) and (wavelength <= 580.0)):
    R =1-(580.0-wavelength)/70.0
    G = 1
    B = 0
  elif ((wavelength >= 580.0) and (wavelength<= 640.0)):
    R =1
    G = (640.0-wavelength)/60.0
    B = 0
  elif ((wavelength >= 640.0) and (wavelength <= 700.0)):
    R =1
    G = 0
    B = 0
  elif ((wavelength >= 700.0) and (wavelength<= 780.0)):
    R =0.35+0.65*(780.0-wavelength)/80.0
    G = 0
    B = 0
  
  return np.array([R,G,B])

def rgb_to_hsv(rgb):
  r = rgb[0]
  g = rgb[1]
  b = rgb[2]
  
  maxc = max(r, g, b)
  minc = min(r, g, b)
  v = maxc
  if minc == maxc:
    return 0.0, 0.0, v
  
  s = (maxc-minc) / maxc
  rc = (maxc-r) / (maxc-minc)
  gc = (maxc-g) / (maxc-minc)
  bc = (maxc-b) / (maxc-minc)
  
  if r == maxc:
    h = bc-gc
  elif g == maxc:
    h = 2.0+rc-bc
  else:
    h = 4.0+gc-rc
  h = (h/6.0) % 1.0
  
  return h, s, v
def hsv_to_rgb(h,s,v):
  
  i = int(h*6.0)
  f = (h*6.0)-i
  p = v*(1.0-s)
  q = v*(1.0-f*s)
  t = v*(1.0-(1.0-f)*s)
  
  if i%6 == 0:
    r = v
    g = t
    b = p
  elif i == 1:
    r = q
    g = v
    b = p
  elif i == 2:
    r = p
    g = v
    b = t
  elif i == 3:
    r = p
    g = q
    b = v
  elif i == 4:
    r = t
    g = p
    b = v
  elif i == 5:
    r = v
    g = p
    b = q
  
  return np.array([r,g,b])