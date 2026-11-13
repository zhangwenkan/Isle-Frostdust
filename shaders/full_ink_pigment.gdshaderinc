// World-space pigment remains attached to the authored Blender surfaces.
uniform sampler2D cliff_paint : source_color, filter_linear_mipmap_anisotropic;
vec3 cliff_pigment(vec3 p,vec3 n){
    vec3 weights=pow(abs(normalize(n)),vec3(4.0));
    weights/=max(dot(weights,vec3(1.0)),.001);
    vec3 a=texture(cliff_paint,p.zy*vec2(.20,.22)).rgb;
    vec3 b=texture(cliff_paint,p.xz*vec2(.20,.22)).rgb;
    vec3 c=texture(cliff_paint,p.xy*vec2(.20,.22)).rgb;
    return a*weights.x+b*weights.y+c*weights.z;
}
float ink_sky_fill(vec3 n){return max(dot(normalize(n),normalize(vec3(-.65,.70,.45))),0.0);}
