// Optional local forest silhouette opening at the new terminal rocky coast.
uniform bool terminus_edge_enabled=false;
float terminal_forest_edge(vec3 p){
    if(!terminus_edge_enabled)return 1.0;
    return smoothstep(-66.0,-61.5,p.x+.55*sin(-p.z*.11));
}
