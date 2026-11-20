shader_type spatial;
render_mode diffuse_lambert, specular_disabled, cull_disabled;

#include "res://shaders/pixel_cavern_vegetation.gdshaderinc"
#include "res://shaders/pixel_cavern_plant_color.gdshaderinc"

uniform vec4 base_color : source_color = vec4(0.35, 0.48, 0.25, 1.0);
varying vec3 vegetation_world_normal;
varying vec3 leaf_light_point;
varying float grass_tip_weight;

void vertex() {
    vec3 point = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    vec3 surface_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
    vec3 resting_normal = surface_normal;
    float t = vegetation_time >= 0.0 ? vegetation_time : TIME;
    vegetation_deform(point, surface_normal, UV, UV2, COLOR, t);
    VERTEX = (inverse(MODEL_MATRIX) * vec4(point, 1.0)).xyz;
    NORMAL = normalize(inverse(MODEL_NORMAL_MATRIX) * surface_normal);
    // Grass inherits the ground/clump light. Bending its tips must not turn
    // every blade into a separate flashing highlight.
    bool grass = wind_kind > 0.5 && wind_kind < 1.5;
    vegetation_world_normal = grass ? normalize(mix(resting_normal, surface_normal, 0.08)) : surface_normal;
    leaf_light_point = vec3(UV.x,UV2.x,UV.y);
    grass_tip_weight = COLOR.r;
}

void fragment() {
    bool grass = wind_kind > 0.5 && wind_kind < 1.5;
    ALBEDO = grass ? cavern_grass_color(leaf_light_point.xz) : base_color.rgb;
    // A restrained 6% root-to-tip interval retains blades within a shared mass.
    if (grass) ALBEDO *= mix(0.97, 1.03, smoothstep(0.08, 0.90, grass_tip_weight));
    ROUGHNESS = 0.96;
    NORMAL = normalize((VIEW_MATRIX * vec4(vegetation_world_normal, 0.0)).xyz);
    if (grass || wind_kind > 1.5 && (wind_kind < 2.5 || wind_kind > 4.5 && wind_kind < 5.5)) {
        // Grass samples its actual floor shadow; leaves sample their attachment.
        // Crown shadow proxies provide broad patches, not individual leaf stripes.
        vec3 light_point = leaf_light_point;
        if (grass) light_point.y += 0.035;
        LIGHT_VERTEX = (VIEW_MATRIX * vec4(light_point,1.0)).xyz;
    }
}

void light() {
    float n = max(dot(NORMAL, LIGHT), 0.0);
    float band = cavern_plant_diffuse(n);
    vec3 hue = cavern_plant_light_hue(n);
    DIFFUSE_LIGHT += LIGHT_COLOR * band * hue * ATTENUATION / 3.14159265;
}
