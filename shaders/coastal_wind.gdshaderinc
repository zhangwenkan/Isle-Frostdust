// A travelling gust rises and settles over several seconds, shared by vegetation.
float coastal_gust(vec3 world, float time) {
    float phase = time * 0.48 - world.x * 0.15 + world.z * 0.10;
    float swell = pow(0.5 + 0.5 * sin(phase), 2.0);
    return 0.22 + swell * (0.55 + 0.23 * sin(time * 0.17 + 0.8));
}
vec2 coastal_bend(vec3 world, float time) {
    float gust = coastal_gust(world, time);
    float sway = sin(time * 1.15 - world.x * 0.16 + world.z * 0.12);
    return vec2(0.55 + sway * 0.6, 0.24 + sin(time * 0.86 + world.x * 0.12) * 0.23) * gust;
}
