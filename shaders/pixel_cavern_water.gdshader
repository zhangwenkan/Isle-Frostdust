shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never;
uniform sampler2D scene_depth:hint_depth_texture,repeat_disable,filter_nearest;
varying vec3 wp;
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1)).xyz;}
void fragment(){
    vec4 p=INV_PROJECTION_MATRIX*vec4(SCREEN_UV*2.0-1.0,texture(scene_depth,SCREEN_UV).r,1);
    float gap=max(0.0,-p.z/p.w+VERTEX.z);
    vec2 grid=floor(wp.xz*13.0)/13.0;
    float a=sin(grid.x*1.35+grid.y*1.8+TIME*.55)+.45*sin(grid.x*2.0-grid.y*.9-TIME*.43);
    float b=sin(grid.x*.4-grid.y*.6+TIME*.19);
    float glint=smoothstep(1.22,1.40,a)*smoothstep(.25,.8,b);
    vec3 col=mix(vec3(.20,.43,.39),vec3(.065,.23,.28),smoothstep(.4,7.5,gap));
    col=mix(col,vec3(.43,.61,.56),glint*.29);
    float foam=(1.0-smoothstep(.13,.38,gap))*step(.05,gap)*smoothstep(-.7,.7,sin(grid.x*3.1+grid.y*2.4+TIME*.7));
    col=mix(col,vec3(.75,.82,.71),foam*.70);
    ALBEDO=col;ALPHA=mix(.47,.94,smoothstep(.2,5.0,gap));
}
