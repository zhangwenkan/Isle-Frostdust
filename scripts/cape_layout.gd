extends RefCounted
## Inverse of the Blender-authored compact western layout; contains no geometry.
static func source_x(x: float) -> float:
	if x<=-13.5:return x-5.5
	if x>=-11.0:return x
	if x<-12.8928571429:
		return -19.0+(1.0-sqrt(maxf(0.0,1.0-1.57142857143*(x+13.5))))/.785714285714
	if x<-11.6071428571:return -18.0+(x+12.8928571429)/.214285714286
	return -12.0+(-.214285714286+sqrt(.045918367347+1.57142857143*(x+11.6071428571)))/.785714285714
