// Blender-authored float UV=root.xz, UV2=root.y/main bend.
// COLOR.rg=local tip weight/phase. Never encode world pivots in GPU 8-bit colors.
uniform float wind_kind = 0.0;
uniform float wind_strength : hint_range(0.0, 2.0) = 1.0;
// Negative uses the same engine clock in visible, shadow and occlusion passes.
uniform float vegetation_time = -1.0;
uniform vec4 hero_position = vec4(0.0);
uniform vec2 movement_direction = vec2(1.0, 0.0);
uniform vec4 trample_points[12]; // xyz world foot position, w remaining pressure.
uniform float trample_radius : hint_range(0.2, 1.2) = 0.62;

vec3 vegetation_rotate(vec3 value, vec3 axis, float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return value * c + cross(axis, value) * s + axis * dot(axis, value) * (1.0 - c);
}

float vegetation_gust(vec3 point, float t) {
    // Travelling fronts have rises and quiet gaps; not one global oscillator.
    float front = sin(dot(point.xz, vec2(0.18, 0.11)) - t * 0.62);
    float envelope = smoothstep(-0.22, 0.82, front);
    float slower = 0.64 + 0.36 * sin(t * 0.27 + point.z * 0.065);
    return 0.15 + envelope * slower;
}

vec2 vegetation_wind(vec3 point, float t) {
    float gust = vegetation_gust(point, t);
    vec2 direction = normalize(vec2(0.94 + 0.14 * sin(t * 0.21), 0.32 + 0.18 * sin(t * 0.17 + 0.8)));
    float wave = sin(t * 1.42 - dot(point.xz, vec2(0.14, 0.09)));
    return direction * gust * (0.48 + 0.52 * wave) * wind_strength;
}

float vegetation_pressure(vec3 root, vec4 stamp) {
    float distance_to_foot = length(root.xz - stamp.xz);
    float vertical = 1.0 - smoothstep(0.22, 0.52, abs(root.y - stamp.y));
    return stamp.w * vertical * (1.0 - smoothstep(0.08, trample_radius, distance_to_foot));
}

void vegetation_deform(inout vec3 point, inout vec3 normal, vec2 root_xz, vec2 weights, vec4 attachment, float t) {
    if (wind_kind < 0.5) { return; }
    float main_weight = clamp(weights.y, 0.0, 1.0);
    float leaf_weight = clamp(attachment.r, 0.0, 1.0);
    vec3 pivot = vec3(root_xz.x,weights.x,root_xz.y);
    vec2 wind = vegetation_wind(point, t);
    float phase = attachment.g * 6.2831853;

    if (wind_kind < 1.5) {
        // Grounded blades bend around their own root. Roots never translate.
        float pressure = vegetation_pressure(pivot, hero_position);
        vec2 push = pivot.xz - hero_position.xz;
        for (int i = 0; i < 12; i++) {
            float candidate = vegetation_pressure(pivot, trample_points[i]);
            if (candidate > pressure) {
                pressure = candidate;
                push = pivot.xz - trample_points[i].xz;
            }
        }
        push = length(push) > 0.045 ? normalize(push) : normalize(movement_direction + vec2(0.001, 0.0));
        vec2 root_wind = vegetation_wind(pivot, t);
        float flutter = sin(t * 2.45 + phase) * 0.035 * vegetation_gust(pivot, t);
        vec2 lean = root_wind * 0.36 + vec2(0.72, 0.28) * flutter;
        lean += push * pressure * 1.20;
        float angle = min(length(lean), 1.32) * pow(main_weight, 0.72);
        vec2 direction = normalize(lean + vec2(0.00001, 0.0));
        vec3 axis = vec3(direction.y, 0.0, -direction.x);
        point = pivot + vegetation_rotate(point - pivot, axis, angle);
        normal = normalize(vegetation_rotate(normal, axis, angle));
        return;
    }

    // Continuous spatial field and authored main weights keep branch / leaf
    // junctions together. Per-cluster phase affects only the attached leaf tip.
    float amplitude = 0.24;
    if (wind_kind > 3.5 && wind_kind < 4.5) { amplitude = 0.27; }
    if (wind_kind > 4.5 && wind_kind < 5.5) { amplitude = 0.24; }
    if (wind_kind > 5.5) { amplitude = 0.11; }
    vec2 bend = wind * amplitude * main_weight * main_weight;
    point.xz += bend;
    point.y -= length(bend) * 0.07;
    vec2 direction = normalize(wind + vec2(0.00001, 0.0));
    vec3 main_axis = vec3(direction.y, 0.0, -direction.x);
    normal = normalize(vegetation_rotate(normal, main_axis, length(bend) * 0.20));

    // Branch wood has no local leaf flutter. Stem vertices use COLOR.a = 0.
    if (wind_kind > 2.5 && wind_kind < 3.5) { return; }
    float tip_wave = sin(t * 2.15 + phase - dot(pivot.xz, vec2(0.12, 0.08)));
    float tip_amplitude = wind_kind > 4.5 && wind_kind < 5.5 ? 0.11 : 0.085;
    float tip_angle = tip_wave * tip_amplitude * vegetation_gust(pivot, t) * leaf_weight * wind_strength;
    vec3 local_tip = vegetation_rotate(point - pivot - vec3(bend.x, -length(bend) * 0.07, bend.y), main_axis, tip_angle);
    point = pivot + local_tip + vec3(bend.x, -length(bend) * 0.07, bend.y);
    normal = normalize(vegetation_rotate(normal, main_axis, tip_angle));
}
