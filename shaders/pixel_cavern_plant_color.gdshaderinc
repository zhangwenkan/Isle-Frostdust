// A shared, metre-scale colour field connects the grass blades to their floor.
// These broad zones are stationary; wind changes the silhouette, not the paint.
uniform vec4 meadow_green : source_color = vec4(0.53, 0.65, 0.36, 1.0);
uniform vec4 grove_green : source_color = vec4(0.31, 0.49, 0.43, 1.0);
uniform vec4 glade_green : source_color = vec4(0.65, 0.72, 0.41, 1.0);

vec3 cavern_grass_color(vec2 ground_position) {
    float patch = 0.50
        + 0.29 * sin(ground_position.x * 0.34 + sin(ground_position.y * 0.23) * 0.65)
        + 0.18 * cos(ground_position.y * 0.39 - ground_position.x * 0.12);
    vec3 colour = mix(grove_green.rgb, meadow_green.rgb, smoothstep(0.08, 0.64, patch));
    return mix(colour, glade_green.rgb, smoothstep(0.65, 0.97, patch) * 0.65);
}

float cavern_plant_diffuse(float facing) {
    // Broad transitions respect the Blender-authored clump normals.
    return 0.18 + 0.37 * smoothstep(0.12, 0.48, facing)
        + 0.45 * smoothstep(0.50, 0.90, facing);
}

vec3 cavern_plant_light_hue(float facing) {
    return mix(vec3(0.67, 0.92, 1.07), vec3(1.04, 1.01, 0.88), smoothstep(0.19, 0.84, facing));
}
