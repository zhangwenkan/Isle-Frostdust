shader_type fog;
#include "res://shaders/sunset_sea_mist.gdshaderinc"

uniform vec3 cloud_color : source_color = vec3(0.77, 0.83, 0.82);
uniform float cloud_density = 0.075;
uniform vec3 sea_mist_color : source_color = vec3(0.49, 0.68, 0.74);
uniform float sunset_blend : hint_range(0.0,1.0) = 0.0;
uniform float cape_opening : hint_range(0.0,1.0) = 0.0;

float hash(vec3 p) {
    p = fract(p * 0.1031);
    p += dot(p, p.yzx + 33.33);
    return fract((p.x + p.y) * p.z);
}
float soft_noise(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(hash(i), hash(i + vec3(1,0,0)), f.x),
                   mix(hash(i + vec3(0,1,0)), hash(i + vec3(1,1,0)), f.x), f.y),
               mix(mix(hash(i + vec3(0,0,1)), hash(i + vec3(1,0,1)), f.x),
                   mix(hash(i + vec3(0,1,1)), hash(i + vec3(1,1,1)), f.x), f.y), f.z);
}
void fog() {
    vec3 p = WORLD_POSITION;
    float broad = soft_noise(vec3(p.x * 0.033 + TIME * 0.0013, p.y * 0.08, p.z * 0.038));
    float detail = soft_noise(vec3(p.x * 0.085 - TIME * 0.002, p.y * 0.14, p.z * 0.070));
    // Discrete low ribbons cover valley floors; clear air remains above each band.
    float front_center = -0.25 + (broad - 0.5) * 3.8 + sin(p.x * 0.09 + TIME * 0.016) * 0.65;
    float height_mask = exp(-pow((p.y - front_center) / 1.25, 2.0));
    float middle_center = 2.0 + (broad - 0.5) * 4.2;
    float middle_height = exp(-pow((p.y - middle_center) / 1.9, 2.0));
    float far_center = 4.7 + (broad - 0.5) * 4.8;
    float far_height = exp(-pow((p.y - far_center) / 2.4, 2.0));
    float saddle_height = 6.2 + sin(p.x * 0.042 + TIME * 0.012) * 1.6;
    float saddle_wisp = exp(-pow((p.y - saddle_height) / 0.7, 2.0))
        * exp(-pow((p.z + 151.0) / 14.0, 2.0))
        * smoothstep(0.37, 0.66, broad);
    float depth = -p.z;
    // The near edge follows broad cloud bays and projecting tongues. A fixed
    // distance cutoff would flatten every ribbon into the same horizontal line.
    float cloud_bay = sin(p.x * 0.047 + 0.3) * 13.0
        + sin(p.x * 0.109 + 1.6) * 6.0 + (broad - 0.5) * 8.0;
    float front_depth = 72.0 + cloud_bay;
    float foreground_clear = smoothstep(front_depth - 35.0, front_depth - 3.0, depth);
    float bottom_mask = smoothstep(-14.0, -5.0, p.y);
    float side_mask = smoothstep(0.0, 0.06, UVW.x) * (1.0 - smoothstep(0.94, 1.0, UVW.x));
    float wisps = smoothstep(0.18, 0.77, broad * 0.62 + detail * 0.38);
    float front_bank = exp(-pow((p.z + front_depth) / 22.0, 2.0));
    float middle_bank = exp(-pow((p.z + 117.0 + sin(p.x * 0.039) * 10.0) / 15.0, 2.0));
    float far_bank = exp(-pow((p.z + 183.0 + sin(p.x * 0.033) * 12.0) / 21.0, 2.0));
    float banks = front_bank * height_mask * 1.35 + middle_bank * middle_height * 1.6 + far_bank * far_height * 1.8;
    // Clear water first becomes translucent sea haze, then denser mountain mist.
    float low_height = -2.6 + sin(p.x * 0.052 + TIME * 0.012) * 1.35 + (broad - 0.5) * 2.4;
    float low_cloud = exp(-max(p.y - low_height, 0.0) / 1.4)
        * (front_bank * 0.65 + middle_bank * 0.60 + far_bank * 0.45);
    // Separate low tongues extend into the clear sea at unequal distances;
    // their soft boundaries interrupt the otherwise uniform line of the bank.
    float tongue_a = exp(-pow((p.x + 19.0 - TIME * 0.025) / 13.0, 2.0)
        -pow((p.z + 51.0) / 13.0, 2.0)) * exp(-pow((p.y + 0.1) / 1.6, 2.0));
    float tongue_b = exp(-pow((p.x - 43.0 + TIME * 0.018) / 19.0, 2.0)
        -pow((p.z + 66.0) / 15.0, 2.0)) * exp(-pow((p.y - 0.6) / 2.1, 2.0));
    float sea_haze = 0.0018 * exp(-pow((p.y + 1.6) / 2.8, 2.0));
    float far_haze = smoothstep(150.0, 250.0, depth) * 0.002;
    DENSITY = ((cloud_density * banks * mix(0.28, 1.45, wisps) + saddle_wisp * 0.018 + low_cloud + sea_haze + far_haze) * foreground_clear
        + tongue_a * 0.060 + tongue_b * 0.045) * bottom_mask * side_mask;
    // A connected cloud sea hides the mountain roots. Its front advances and
    // recedes in bays; three elevated layers give it depth above the open water.
    float sunset_patches=sunset_mist_patches(p.xz,TIME);
    float sunset_front=89.0+sin(p.x*.052+.7)*21.0+sin(p.x*.109+2.0)*9.0;
    float cloud_lobes=soft_noise(vec3(p.x*.069+TIME*.007,p.y*.19,p.z*.075));
    float upper_lobes=soft_noise(vec3(p.x*.13+TIME*.012,p.y*.27,p.z*.11));
    float sunset_floor=-.8+sin(p.x*.069+.8)*.9+(cloud_lobes-.5)*2.6;
    float sunset_front_height=exp(-pow((p.y-sunset_floor)/1.6,2.0))
        *(1.0-smoothstep(2.0,4.0,p.y));
    float sunset_middle_height=exp(-pow((p.y-1.2-(cloud_lobes-.5)*3.8)/1.8,2.0))
        *(1.0-smoothstep(3.5,6.0,p.y));
    float sunset_far_height=exp(-pow((p.y-2.8-(cloud_lobes-.5)*3.8)/2.0,2.0))
        *(1.0-smoothstep(5.0,7.0,p.y));
    float sunset_front_bank=exp(-pow((depth-sunset_front)/17.0,2.0));
    float sunset_middle_bank=exp(-pow((depth-137.0-sin(p.x*.047)*15.0)/22.0,2.0));
    float sunset_far_bank=exp(-pow((depth-196.0-sin(p.x*.033+1.2)*19.0)/28.0,2.0));
    float sunset_body=(sunset_front_bank*sunset_front_height*.10
        +sunset_middle_bank*sunset_middle_height*.085
        +sunset_far_bank*sunset_far_height*.07)
        *mix(.38,1.45,smoothstep(.25,.72,cloud_lobes*.75+upper_lobes*.25));
    float sunset_tendrils=sunset_patches*exp(-pow((p.y+.1)/1.1,2.0))*.018;
    float near_left=exp(-pow((p.x+4.0+sin(depth*.085)*3.0)/12.0,2.0)
        -pow((depth-52.0)/12.0,2.0))
        *exp(-pow((p.y+.65-(cloud_lobes-.5)*2.1)/1.5,2.0));
    float near_right=exp(-pow((p.x-28.0+sin(depth*.065)*3.0)/17.0,2.0)
        -pow((depth-74.0)/16.0,2.0))
        *exp(-pow((p.y-.2-(cloud_lobes-.5)*2.2)/1.8,2.0));
    float sunset_density=(sunset_body+sunset_tendrils+near_left*.070+near_right*.065
        +far_haze*.4)*bottom_mask*side_mask;
    DENSITY=mix(DENSITY,sunset_density,sunset_blend);
    DENSITY*=1.0-cape_opening*.98;
    float airy_cloud = smoothstep(45.0, 130.0, depth) * 0.65 + smoothstep(0.0, 6.0, p.y) * 0.35;
    vec3 mist_tint = mix(sea_mist_color, cloud_color, airy_cloud);
    float cloud_top=smoothstep(-1.8,4.0,p.y-sunset_floor*.35);
    float warm_air=smoothstep(65.0,205.0,depth)*.52+cloud_top*.48;
    vec3 sunset_tint=mix(sea_mist_color,cloud_color,warm_air);
    mist_tint=mix(mist_tint,sunset_tint,sunset_blend);
    ALBEDO = mist_tint;
    EMISSION = mist_tint * mix(.20,.20+cloud_top*.08,sunset_blend);
}
