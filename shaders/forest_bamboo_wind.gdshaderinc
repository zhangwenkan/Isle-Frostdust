// Smooth irregular gusts. One root and seed bind each culm to its painted sprays.
float bamboo_hash(float n){return fract(sin(n*127.1+311.7)*43758.5453);}
float bamboo_noise(float n,float seed){
    float i=floor(n);float f=fract(n);f=f*f*(3.0-2.0*f);
    return mix(bamboo_hash(i+seed),bamboo_hash(i+seed+1.0),f)*2.0-1.0;
}
vec3 bamboo_bend(vec3 p,vec3 root,float height,float seed,float t,float amplitude,float flex){
    float q=clamp((p.y-root.y)/max(height,.1),0.0,1.12);
    float envelope=.24+.95*smoothstep(.16,.83,bamboo_noise(t*.19,seed+43.0)*.5+.5);
    float wave=.62*bamboo_noise(t*.31+root.x*.017,seed*.31);
    wave+=.27*sin(t*(.74+bamboo_hash(seed)*.37)+seed);
    wave+=.11*sin(t*1.41+seed*.63);
    float dx=wave*envelope*amplitude*q*q;
    float dz=bamboo_noise(t*.23,seed+87.0)*envelope*amplitude*q*q*.30;
    float flutter=sin(t*(1.7+bamboo_hash(seed+7.0)*.6)+p.x*2.1+p.z*.8);
    dx+=flutter*flex*flex*envelope*q*q*.11;
    return vec3(dx,-(dx*dx+dz*dz)/max(2.0*height,.2)*q,dz);
}
