float cape_source_x(float x){
    if(x<=-13.5)return x-5.5;
    if(x>=-11.0)return x;
    if(x<-12.89285714)return -19.0+(1.0-sqrt(max(0.0,1.0-1.57142857143*(x+13.5))))/.785714285714;
    if(x<-11.60714286)return -18.0+(x+12.89285714)/.214285714286;
    return -12.0+(-.214285714286+sqrt(.045918367347+1.57142857143*(x+11.60714286)))/.785714285714;
}

// Invert the Blender-authored western extension for the cape's existing paint.
// The rear forest retains cape_source_x because its geometry has not moved.
float extended_cape_source_x(float x){
    if(x>=-11.0)return cape_source_x(x);
    if(x<=-24.0)return cape_source_x(x+9.0);
    float lo=-15.0;
    float hi=-11.0;
    for(int i=0;i<16;i++){
        float m=(lo+hi)*.5;
        float mapped=m-9.0*(1.0-smoothstep(-15.0,-11.0,m));
        if(mapped<x)lo=m;else hi=m;
    }
    return cape_source_x((lo+hi)*.5);
}
