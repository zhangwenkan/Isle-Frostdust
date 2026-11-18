shader_type fog;
#include "res://shaders/forest_sun_field.gdshaderinc"
uniform float density=0.025;
uniform vec3 pocket_center=vec3(0.0);
uniform vec3 pocket_half_size=vec3(1.0);
uniform mat4 author_world_to_local=mat4(1.0);
void fog(){
    vec3 p=(author_world_to_local*vec4(WORLD_POSITION,1.0)).xyz;
    vec3 q=(p-pocket_center)/pocket_half_size;
    float envelope=pow(max(1.0-dot(q,q),0.0),2.0);
    float drift=.72+sin(p.x*.21+p.z*.17+TIME*.035)*.15;
    drift+=sin(p.x*.37-p.z*.24+p.y*.29-TIME*.024)*.10;
    DENSITY=density*envelope*drift;
    float sun=forest_aperture(p,TIME);
    ALBEDO=mix(vec3(.48,.55,.46),vec3(.28,.38,.31)+forest_sun_tint.rgb*sun*.24,forest_light_strength);
    EMISSION=forest_sun_tint.rgb*sun*.012*forest_light_strength;
}
