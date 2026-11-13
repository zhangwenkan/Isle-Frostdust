"""Monotonic layout remap, shared by Blender authoring and runtime ports."""
SHIFT=5.5
def compact_x(x):
    if x<=-19:return x+SHIFT
    if x>=-11:return x
    t=x+19
    integral=.5*t*t if t<1 else t-.5 if t<7 else 6.5+(t-7)-.5*(t-7)**2
    return x+SHIFT-SHIFT/7*integral
def source_x(x):
    if x<=-13.5:return x-SHIFT
    if x>=-11:return x
    a,b=-19.,-11.
    for _ in range(28):
        m=(a+b)/2
        if compact_x(m)<x:a=m
        else:b=m
    return (a+b)/2
