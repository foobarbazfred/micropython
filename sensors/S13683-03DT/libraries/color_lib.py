#
# Color convert Libraries
#

CW_BLACK_LEVEL_BRIGHTNESS = 0.19
CW_WHITE_LEVEL_BRIGHTNESS = 0.8
CW_WHITE_LEVEL_SATURATION = 0.1

#
# convert (r, g, b) to (Hue, Saturation, Value(Brightness) )
#
def rgb2hsv(r, g, b):
    max_val = max((r, g, b))
    min_val = min((r, g, b))

    if max_val == min_val:
       print('Error, max_val == min_val')
       return None

    if min_val == b:
         h = 60 * (g - r)/(max_val - min_val) + 60
    elif min_val == r:
         h = 60 * (b - g)/(max_val - min_val) + 180
    elif min_val == g:
         h = 60 * (r - b)/(max_val - min_val) + 300
    else:
         print('internal Error')
         h = None

    s = (max_val - min_val)/max_val
    v = max_val
    
    return (h, s, v)


#
# convert Hue to Color Name (in japanese Katakana)
# Adjusting the Hue value for sensor calibration (ST13683-03DT)in the COLOR_NAME_LIST
#
COLOR_NAME_LIST = (
  (10, 'aka'), (28, 'daidai'), (60, 'kiiro'),
  (100, 'kimidori'), (150, 'midori'), (180, 'aomidori'),
  (200, 'mizuiro'), (230, 'aoiro'), (270, 'aomurasaki'),
  (330, 'murasaki'), (340, 'akamurasaki'), (360, 'aka'),
)


#
# convert (h, s, v) to color name
#
def hsv2color_name(h, s, v):

  # check black
  if v < CW_BLACK_LEVEL_BRIGHTNESS:     # if brightness is lower than 0.1 then black
     return('kuro')

  # check white
  if s < CW_WHITE_LEVEL_SATURATION  and v > CW_WHITE_LEVEL_BRIGHTNESS:
     return(f'siro')

  for color_pair in COLOR_NAME_LIST:
      (level, name) = color_pair
      if h <= level:
           return name

