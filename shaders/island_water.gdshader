shader_type spatial;
render_mode cull_disabled, specular_schlick_ggx;

uniform vec4 deep_color : source_color = vec4(0.055, 0.34, 0.44, 1.0);
uniform vec4 shallow_color : source_color = vec4(0.10, 0.60, 0.58, 1.0);
varying vec3 world_pos;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p); f = f*f*(3.0-2.0*f);
    return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y);
}
void vertex() { world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
    vec2 p = floor(world_pos.xz * 14.0) / 14.0;
    float t = TIME * 0.42;
    float coast = min(length((p-vec2(-6.0,-0.3))/vec2(17.0,6.8)), length((p-vec2(19.0,-0.4))/vec2(6.0,5.5)));
    float shallow = (1.0-smoothstep(0.85, 1.8, coast))*0.83;
    float n = noise(p*0.33+vec2(t*0.2,0)) * 0.6 + noise(p*1.1-vec2(t*0.25,t*0.12))*0.4;
    vec3 col = mix(deep_color.rgb, shallow_color.rgb, shallow + n*0.22);
    float wave = sin(p.y*8.0 + sin(p.x*1.7+t)*1.7 + t*2.2);
    float wave2 = sin(p.y*3.3-p.x*0.7-t);
    float broken_ripple = step(0.60,noise(p*vec2(1.8,3.7)+vec2(t*.2,0.0)));
    col += vec3(0.012,0.035,0.04) * smoothstep(0.88,0.99,wave)*broken_ripple;
    float sunpath = exp(-pow((p.x-1.0+p.y*0.28)/9.0, 2.0));
	float glint = step(0.96, wave) * step(0.66, wave2) * step(0.55, noise(p*vec2(2.5,8.0)+t*0.4));
    col = mix(col, vec3(0.92,1.0,0.88), glint*(0.22+sunpath*0.76));
	float haze = smoothstep(12.0,115.0,-world_pos.z);
	col = mix(col, vec3(0.38,0.62,0.65), haze);
    ALBEDO = col;
    ROUGHNESS = 0.35;
    SPECULAR = 0.32;
}
void light() {
    // Keep maritime ambient color and allow bridge/rock shadows on the sea.
    DIFFUSE_LIGHT += ALBEDO*LIGHT_COLOR*ATTENUATION*0.30;
}
