"""Shared route for Blender MCP terrain authors and texture painting.
Gameplay uses the same constants; geometry is modified only inside Blender.
"""
import math
START=-20.7
JOIN_A=-18.5
JOIN_B=-12.5
def old_path(x):return .4+math.sin(x*.25)*.44
def old_height(x,z):return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.10+max(0,-z-.3)*.23
START_Z=old_path(START)
START_Y=old_height(START,START_Z)
def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def hermite(a,b,da,db,t,length):return (2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*length*da+(-2*t**3+3*t*t)*b+(t**3-t*t)*length*db
def route(x):
    if x<=JOIN_A:return START_Z-(x-START)*5/9
    if x>=JOIN_B:return old_path(x)
    t=(x-JOIN_A)/(JOIN_B-JOIN_A)
    return hermite(START_Z-(JOIN_A-START)*5/9,old_path(JOIN_B),-5/9,.11*math.cos(JOIN_B*.25),t,JOIN_B-JOIN_A)
def deck_height(x):
    if x<=JOIN_A:return START_Y
    return old_height(x,route(x))+(START_Y-old_height(x,route(x)))*(1-smooth(JOIN_A,JOIN_B,x))
def road_half_width(x):return .82+.12*(1-smooth(-19,-14,x))
def deform_height(x,z,original):
    if x>=JOIN_B:return original
    across=1-smooth(1.10,3.1,abs(z-route(x)))
    extent=smooth(-24.65,-23.1,x)*(1-smooth(-13.3,JOIN_B,x))
    protect=smooth(.88,1.30,math.hypot(x+23,z+.06))
    return original+(deck_height(x)-original)*across*extent*protect
