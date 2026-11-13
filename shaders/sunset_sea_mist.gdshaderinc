// Shared world-space air masses. Unequal depths leave open water between wisps.
float sunset_patch(vec2 p,vec2 center,vec2 spread){
    vec2 q=(p-center)/spread;
    return exp(-dot(q,q)*1.6);
}

float sunset_mist_patches(vec2 p,float seconds){
    p.x+=sin(p.y*.031+seconds*.006)*4.0;
    p.y+=sin(p.x*.045+1.3)*6.0;
    return clamp(
        sunset_patch(p,vec2(-55.0,-76.0),vec2(24.0,24.0))*.85
        +sunset_patch(p,vec2(2.0,-139.0),vec2(35.0,25.0))*.72
        +sunset_patch(p,vec2(55.0,-101.0),vec2(23.0,32.0))*.88
        +sunset_patch(p,vec2(112.0,-183.0),vec2(38.0,29.0))*.70
        +sunset_patch(p,vec2(-137.0,-171.0),vec2(32.0,23.0))*.75,
        0.0,1.0);
}

float sunset_valley_height(vec2 p){
    return sin(p.x*.061+p.y*.014)*1.7
        +sin(p.x*.133-p.y*.031+1.7)*.8;
}
