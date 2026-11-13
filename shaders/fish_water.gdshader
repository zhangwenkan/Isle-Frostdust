shader_type spatial;
#include "res://shaders/sunset_sea_mist.gdshaderinc"
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform sampler2D screen_color : hint_screen_texture, filter_linear_mipmap, repeat_disable;
uniform sampler2D screen_depth : hint_depth_texture, filter_nearest, repeat_disable;
uniform sampler2D wave_slopes : filter_linear_mipmap_anisotropic, repeat_enable;
uniform vec3 deep_color : source_color = vec3(0.055, 0.40, 0.46);
uniform vec3 shallow_color : source_color = vec3(0.12, 0.62, 0.55);
uniform float wave_strength = 0.36;
uniform vec3 reflected_horizon : source_color = vec3(0.50, 0.69, 0.75);
uniform vec3 reflected_zenith : source_color = vec3(0.26, 0.49, 0.65);
uniform float sun_elevation_sine = 0.62;
uniform float sunset_haze : hint_range(0.0,1.0) = 0.0;
uniform float cape_opening : hint_range(0.0,1.0) = 0.0;
uniform float overhead_intro : hint_range(0.0,1.0) = 0.0;
varying vec3 world_position;
varying vec3 water_plane_normal;
varying float water_specular;

vec3 display_to_scene(vec3 c) {
    vec3 y=mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));
    vec3 a=2.51-2.43*y,b=.03-.59*y;
    return max((-b+sqrt(b*b+4.0*a*.14*y))/(2.0*a),vec3(0.0));
}

vec3 view_position(vec2 uv, float depth, mat4 inverse_projection) {
    vec4 p = inverse_projection * vec4(uv * 2.0 - 1.0, depth, 1.0);
    return p.xyz / p.w;
}

void vertex() {
    world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    water_plane_normal = normalize((VIEW_MATRIX * vec4(0.0,1.0,0.0,0.0)).xyz);
}

void fragment() {
    vec2 p = world_position.xz;
    mat2 turn = mat2(vec2(0.8, 0.6), vec2(-0.6, 0.8));
    vec2 swell = texture(wave_slopes, p * 0.062 + TIME * vec2(-0.008, 0.004)).rg * 2.0 - 1.0;
    vec2 ripple = texture(wave_slopes, turn * p * 0.145 + TIME * vec2(0.012, -0.008)).rg * 2.0 - 1.0;
    float pixel_span = max(length(dFdx(p)), length(dFdy(p)));
    float resolved = 1.0 - smoothstep(0.22, 1.5, pixel_span);
    float distance_fade = 1.0 - smoothstep(18.0, 85.0, length(VERTEX));
    vec2 slope = (swell + turn * ripple * 0.48) * wave_strength * mix(0.035, 1.0, resolved * distance_fade);
    vec3 world_normal = normalize(vec3(slope.x, 1.0, slope.y));
    NORMAL = normalize((VIEW_MATRIX * vec4(world_normal, 0.0)).xyz);

    float raw = texture(screen_depth, SCREEN_UV).r;
    vec3 behind = view_position(SCREEN_UV, raw, INV_PROJECTION_MATRIX);
    vec3 world_behind = (INV_VIEW_MATRIX * vec4(behind, 1.0)).xyz;
    float depth = max(0.0, world_position.y - world_behind.y);
    if (raw < 0.00001) { depth = 40.0; }
    // Refraction stays on the submerged side of silhouettes.
    vec2 projected_slope = (VIEW_MATRIX * vec4(slope.x, 0.0, slope.y, 0.0)).xy;
    vec2 offset = projected_slope * 0.011 * smoothstep(0.0, 1.8, depth);
    vec2 sample_uv = clamp(SCREEN_UV + offset, vec2(0.001), vec2(0.999));
    vec3 refracted = view_position(sample_uv, texture(screen_depth, sample_uv).r, INV_PROJECTION_MATRIX);
    if (refracted.z > VERTEX.z) { sample_uv = SCREEN_UV; }
    float optical_depth = min(depth / max(dot(VIEW, normalize((VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz)), 0.32), 45.0);
    vec3 transmission = exp(-vec3(0.28, 0.085, 0.065) * optical_depth);
    // Distant shallows lose bottom visibility through the long sea-haze path.
    // This keeps submerged mountain skirts from shining through the fog banks.
    float bottom_visibility = 1.0 - smoothstep(28.0, 62.0, length(VERTEX));
    transmission *= bottom_visibility;
    vec3 bottom = textureLod(screen_color, sample_uv, clamp((depth - 2.8) * 0.20, 0.0, 2.5)).rgb;
    // The opaque buffer lights the seabed in air. Account for the sunlight's
    // underwater path as well as the outgoing path to the camera.
    bottom *= exp(-vec3(0.18, 0.045, 0.035) * depth / max(sun_elevation_sine, 0.25));
    // Soft moving underwater light helps read fixed shells through moving refraction.
    vec2 bed_uv = world_behind.xz;
    vec2 caustic_flow = texture(wave_slopes, bed_uv * 0.31 + TIME * vec2(-0.021, 0.016)).rg;
    float caustic = pow(1.0 - abs(sin(bed_uv.x * 3.2 + caustic_flow.x * 4.8 + TIME * 0.43)
        * sin(bed_uv.y * 3.6 + caustic_flow.y * 4.2 - TIME * 0.31)), 14.0);
    bottom *= 1.0 + caustic * 0.16 * exp(-depth * 0.25) * bottom_visibility;
    vec3 sea = mix(shallow_color, deep_color, smoothstep(0.5, 10.0, depth));
    sea = mix(deep_color, sea, bottom_visibility);
    // A vertical view sees water depth, not the dark grazing-angle reflection.
    // Keep the original low-amplitude waves instead of forcing sparkles with
    // steep micro-normals, which made the overhead sea look like thick paint.
    float cape_sea=cape_opening*(1.0-overhead_intro);
    sea=mix(sea,vec3(.012,.075,.105),cape_sea*smoothstep(1.5,7.0,depth));
    // Filter the broad Fresnel lobe separately from fine sun-reflecting waves.
    // Otherwise tiny slopes turn the whole grazing-angle ocean into pale blotches.
    vec3 calm_normal = normalize((VIEW_MATRIX * vec4(normalize(vec3(slope.x * 0.12, 1.0, slope.y * 0.12)), 0.0)).xyz);
    float fresnel = 0.02 + 0.98 * pow(1.0 - clamp(dot(calm_normal, VIEW), 0.0, 1.0), 5.0);
    vec3 world_view = normalize((INV_VIEW_MATRIX * vec4(VIEW, 0.0)).xyz);
    vec3 reflected_ray = reflect(-world_view, world_normal);
    vec3 reflected_sky = mix(reflected_horizon, reflected_zenith, smoothstep(0.0, 0.85, reflected_ray.y));
    reflected_sky=mix(reflected_sky,vec3(.05,.20,.29),cape_sea*.45);

    // Captured bottom already contains lighting and cast shadows.
    // Only transmitted radiance is emitted; water scattering remains lit.
    EMISSION = bottom * transmission * (1.0 - fresnel) + reflected_sky * fresnel * 0.55;
    ALBEDO = sea * (vec3(1.0) - transmission) * (1.0 - fresnel);
    // A smooth sky lobe avoids reflecting a tiny cubemap sun twice. The direct
    // DirectionalLight still supplies GGX highlights with actual shadowing.
    RADIANCE = vec4(0.0, 0.0, 0.0, 1.0);
    ROUGHNESS = mix(0.28, 0.14, resolved * distance_fade);
    SPECULAR = 0.25; // Water dielectric F0 ~ 0.02; highlight uses the real scene light
    SPECULAR*=mix(1.0,.50,cape_sea);
    ROUGHNESS=mix(ROUGHNESS,.23,cape_sea);

    // Narrow broken wash around real contacts, never a sea-wide grid.
    float wash = 0.5 + 0.5 * sin(TIME * 1.0 + swell.x * 3.0 + p.x * 0.35 + p.y * 0.24);
    float shore = 1.0 - smoothstep(0.07, 0.22 + wash * 0.14, depth);
    float foam = shore * smoothstep(-0.20, 0.34, swell.x + ripple.y) * 0.65 * bottom_visibility;
    ALBEDO = mix(ALBEDO, vec3(0.66, 0.76, 0.70), foam);
    EMISSION *= 1.0 - foam;
    ROUGHNESS = mix(ROUGHNESS, 0.65, foam);

    // Long atmospheric paths blend the distant sea into the sunset foothills.
    // Clear water and all underwater detail near the bridge keep their original shading.
    float mist_patches=sunset_mist_patches(world_position.xz,TIME);
    float distant_haze=sunset_haze*smoothstep(34.0,82.0,-world_position.z)
        *(.12*smoothstep(120.0,320.0,-world_position.z)+mist_patches*.22);
    vec3 horizon_haze=display_to_scene(mix(vec3(.63,.73,.75),vec3(.70,.744,.733),smoothstep(65.0,230.0,-world_position.z)));
    ALBEDO*=1.0-distant_haze;
    EMISSION=mix(EMISSION,horizon_haze,distant_haze);
    SPECULAR*=1.0-distant_haze;
    water_specular=SPECULAR;
}

void light() {
    // Water's volume scatters broad light. Tiny surface slopes govern reflection,
    // not stone-like diffuse bumps across every wavelet in the overhead view.
    vec3 scatter_normal=normalize(mix(NORMAL,water_plane_normal,overhead_intro*.78));
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(scatter_normal,LIGHT),0.0)/PI;
    float nl=max(dot(NORMAL,LIGHT),0.0);
    float nv=max(dot(NORMAL,VIEW),.001);
    vec3 halfway=normalize(LIGHT+VIEW);
    float nh=max(dot(NORMAL,halfway),0.0);
    float vh=max(dot(VIEW,halfway),0.0);
    float alpha=max(.002,ROUGHNESS*ROUGHNESS);
    float alpha2=alpha*alpha;
    float denominator=nh*nh*(alpha2-1.0)+1.0;
    float distribution=alpha2/(PI*denominator*denominator);
    float k=(ROUGHNESS+1.0)*(ROUGHNESS+1.0)/8.0;
    float visibility=(nl/(nl*(1.0-k)+k))*(nv/(nv*(1.0-k)+k));
    float fresnel=.08*water_specular+(1.0-.08*water_specular)*pow(1.0-vh,5.0);
    SPECULAR_LIGHT+=LIGHT_COLOR*ATTENUATION*distribution*visibility*fresnel*.48/max(4.0*nv,.001);
}
