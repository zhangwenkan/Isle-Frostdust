// Adapted from Sumiro's publicly served ink_material-UyOP6egx.js (2026-11-07).
// Upstream provenance and licence status: assets/sumiro/PROVENANCE.md.
shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
uniform sampler2D look_map : filter_linear_mipmap_anisotropic, repeat_enable;
uniform bool has_map = true;
uniform bool use_paint = true;
uniform bool foliage = false;
uniform bool grass = false;
uniform bool ground_project = false;
uniform bool base_ground = false;
uniform vec3 base_color = vec3(1.0);
uniform float material_scale = 1.0;
uniform float alpha_cut = 0.0;
uniform float wash_amount = 0.0;
uniform vec3 wash_color = vec3(.6,.56,.47);
varying vec3 ink_world;
varying vec3 ink_normal;
varying vec3 ink_camera;
varying float leaf_weight;
void vertex(){
    ink_camera = CAMERA_POSITION_WORLD;
    vec3 p = (MODEL_MATRIX * vec4(VERTEX,1.0)).xyz;
    if(foliage){
        float ph = p.x*1.3+p.z*.9+p.y*.7;
        float w = sin(TIME*.9+ph)+.5*sin(TIME*1.7+ph*2.1);
        VERTEX.xz += vec2(.018,.012)*w*UV2.x;
    }
    if(grass){
        float ph=p.x*1.1+p.z*.8;
        VERTEX.xz+=vec2(.035,.018)*(sin(TIME*1.1+ph)*.6+sin(TIME*2.3+ph*1.7)*.25)*UV2.x;
    }
    ink_world = (MODEL_MATRIX * vec4(VERTEX,1.0)).xyz;
    ink_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
}

uniform sampler3D tInkNoise : filter_linear, repeat_enable;
float vnoise(vec3 p) {
  vec3 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return texture(tInkNoise, (i + f + 0.5) / 64.0).r;
}
float fbm3(vec3 p) {
  return 0.5333 * vnoise(p) + 0.2667 * vnoise(p * 2.03 + 11.7) + 0.2 * vnoise(p * 4.01 + 3.1);
}
// Noise whose features stay lambdaPx wide on screen at any distance. Octaves cross-fade, so it
// never aliases into speckle and never pops. mpp is metres per reference pixel. World-locked, static.
// An octave keeps its offset whichever side of the fade it is on, or every change of octave is a seam, a line at one distance from the
// camera that travels over the stone as he moves. A half-way blend of two noises is flatter than either, which would leave a pale band,
// empty of marks, travelling with it: so the contrast is held level across the fade, at what the blend averaged before.
float pxNoise(vec3 p, vec3 stretch, float lambdaPx, float mpp, float seed) {
  float l = log2(max(lambdaPx * mpp, 1e-4));
  float k = floor(l);
  float f = l - k;
  vec3 q = p * stretch;
  float a = vnoise(q / pow(2.0, k) + seed + 5.7 * mod(k, 2.0));
  float b = vnoise(q / pow(2.0, k + 1.0) + seed + 5.7 * mod(k + 1.0, 2.0));
  return 0.5 + (mix(a, b, f) - 0.5) * 0.82 / sqrt(f * f + (1.0 - f) * (1.0 - f));
}
// Broad fields decide where a wash stops, and that edge is a hard threshold. If a field morphs as the camera comes closer, the edge
// slides over the stone as a pale stripe. So within playing distance a broad field stays one size in metres, locked to the stone,
// the size it had at 12 m. Past 64 m, where little moves on screen, it holds a size on screen instead.
const float INK_LOCK_K = 12.0 / 64.0;
float inkLockMpp(float dist, float pxToRad) { return max(dist, 64.0) * pxToRad; }

uniform vec3 uSunDir = vec3(0.3,0.8,0.5);
uniform vec3 uShadowMul = vec3(0.42,0.47,0.55);
uniform float uWrap = .5;
uniform float uSkyFill = .8;
uniform float uWashFreq = .7;
uniform float uWashWarp = .03;
uniform float uCavityK = .3;
uniform float uDryAmt = .85;
uniform float uDryFreq = 1.6;
uniform float uGrainAmp = .07;
uniform float uGrainFreq = 7.0;
uniform float uBlotchAmp = .02;
uniform float uBlotchFreq = 9.0;
uniform float uStreakAmp = .01;
uniform float uUseRamp = 1.0;
uniform float uLookMap = 1.0;
uniform float uFlat = 0.0;
uniform float uRampBias = 0.0;
uniform float uRampScale = 1.0;
uniform float uPoolAmt = 1.0;
uniform float uStep = 0.0;
uniform float uBrushEdge = .05;
uniform float uHueAmt = .15;
uniform float uFacetAmt = 0.0;
uniform float uFacetFreq = 1.1;
uniform float uFacetStretch = .42;
uniform float uCrackAmt = 0.0;
uniform float uCrackW = 1.6;
uniform float uCrackGate = .62;
uniform float uFacetBevel = .2;
uniform float uBrushAmt = .02;
uniform float uBrushLean = .24;
uniform float uPitAmt = 0.0;
uniform float uScumble = 0.0;
uniform float uStainAmt = 0.0;
uniform float uStainFreq = .5;
uniform float uSpeckAmt = 0.0;
uniform float uPxScale = 1.0;
uniform float uPxToRad = 0.0010340063473471656;
uniform float uGouge = 0.0;
uniform mat3 uNoiseFrame = mat3(1.0);
uniform vec3 uTint = vec3(1.012,1.0,.975);
uniform vec3 uShadeTint = vec3(.56,.56,.58);
uniform vec3 uDryCol = vec3(.552,.546,.486);
uniform vec3 uPoolCol = vec3(.024,.031,.034);
uniform vec3 uPoolDeep = vec3(.0075,.0103,.0116);
uniform vec3 uInkLine = vec3(.0044,.004,.003);
uniform float uLineWeight = 1.0;
uniform float uLitClean = .6;
uniform float uZones = 0.0;
uniform float uZoneA = .38;
uniform float uZoneB = .68;
uniform float uZoneWander = 1.0;
uniform float uZoneSoft = .15;
uniform vec3 uZoneVals = vec3(.2,.52,.92);
uniform float uDryDirect = 1.0;
uniform float uPoolTear = .35;
uniform float uCoolDark = .12;
uniform float uInkBold = 1.0;
uniform float uBoldMat = 1.0;
uniform float uInkShape = 1.0;

// style.md section 5, widened at both ends by eye: darks a little bluer and lights a little higher,
// as the stone in the reference runs near paper on lit edges and into slate in shadow. t = 1 lands
// on the 178 stop, and only t above 1, such as a pale look map on sunlit stone, reaches the last.
const int RAMP_N = 10;
const vec3 RAMP[RAMP_N] = {
  vec3(13.0, 16.0, 20.0) / 255.0,
  vec3(25.0, 33.0, 40.0) / 255.0,
  vec3(45.0, 52.0, 58.0) / 255.0,
  vec3(69.0, 72.0, 73.0) / 255.0,
  vec3(90.0, 90.0, 87.0) / 255.0,
  vec3(110.0, 109.0, 104.0) / 255.0,
  vec3(132.0, 131.0, 124.0) / 255.0,
  vec3(155.0, 154.0, 146.0) / 255.0,
  vec3(178.0, 177.0, 168.0) / 255.0,
  vec3(203.0, 202.0, 193.0) / 255.0
};

vec3 rampLookup(float t) {
  float x = clamp(t * 8.0, 0.0, 9.0);
  int i = int(floor(x));
  int j = min(i + 1, RAMP_N - 1);
  return mix(RAMP[i], RAMP[j], smoothstep(0.0, 1.0, x - float(i)));
}

vec3 inkHash33(vec3 p) {
  p = fract(p * vec3(0.1031, 0.1030, 0.0973));
  p += dot(p, p.yxz + 33.33);
  return fract((p.xxy + p.yxx) * p.zyx);
}

// Distance to the nearest cell border in lattice units, plus that cell's random vector.
float inkVoronoi(vec3 p, out vec3 cell) {
  vec3 i = floor(p), f = fract(p);
  vec3 near = vec3(0.0), r0 = vec3(0.0);
  float best = 8.0;
  for (int z = -1; z <= 1; z++) for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) {
    vec3 g = vec3(float(x), float(y), float(z));
    vec3 r = g + inkHash33(i + g) - f;
    float d = dot(r, r);
    if (d < best) { best = d; r0 = r; near = g; }
  }
  float border = 8.0;
  for (int z = -1; z <= 1; z++) for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) {
    vec3 g = near + vec3(float(x), float(y), float(z));
    vec3 r = g + inkHash33(i + g) - f;
    vec3 diff = r - r0;
    float len2 = dot(diff, diff);
    if (len2 > 1e-5) border = min(border, dot(0.5 * (r0 + r), diff) / sqrt(len2));
  }
  cell = inkHash33(i + near + 91.7);
  return border;
}


// paint is COLOR_0 (environment.md 3.1): R cavity and value, G dry brush, B ink pool, A line.
vec3 inkSurface(vec3 P, vec3 N, vec3 albedo, vec4 paint, float shadow) {
  if (uFlat > 0.5) return albedo * mix(uShadowMul, vec3(1.0), shadow);

  // Metres per reference pixel: everything that must hold a steady size on screen reads this.
  // Small marks use a noise frame. On ground seen at a grazing angle it squeezes the view axis,
  // so a pit is round on screen and not a dash lying across the view.
  vec3 Pq = uNoiseFrame * P;
  float mpp = max(max(length(dFdx(Pq)), length(dFdy(Pq))), 1e-4) * uPxScale;
  float mppB = inkLockMpp(length(P - ink_camera), uPxToRad);
  #define BROAD(q, stretch, lambda, seed) pxNoise(q, stretch, (lambda) * INK_LOCK_K, mppB, seed)


  float bristle = pxNoise(Pq, vec3(1.0, 0.2, 1.0), 2.3, mpp, 3.0);
  float bristleWide = pxNoise(Pq, vec3(1.0, 0.3, 1.0), 6.5, mpp, 11.0);
  float blotch = 0.6 * BROAD(Pq, vec3(1.0), 13.0, 17.0) + 0.4 * BROAD(Pq, vec3(1.0), 27.0, 23.0);
  float grain = 0.65 * pxNoise(Pq, vec3(1.0), 2.0, mpp, 29.0) + 0.35 * pxNoise(Pq, vec3(1.0), 4.3, mpp, 31.0);

  // Planes. Any mesh gets hewn, by tilting the normal per warped Voronoi cell. The tilt eases
  // to nothing at a border, so one plane rolls into the next as a soft edge, not a toon step.
  float borderPx = 1e3;
  vec3 cell = vec3(0.5);
  vec3 NF = N;
  if (uFacetAmt > 0.001 || uCrackAmt > 0.001) {
    vec3 sp = P * vec3(1.0, uFacetStretch, 1.0) * uFacetFreq;
    vec3 warp = vec3(vnoise(sp * 0.9 + 3.0), vnoise(sp * 0.9 + 13.0), vnoise(sp * 0.9 + 23.0)) - 0.5;
    vec3 warp2 = vec3(vnoise(sp * 3.7 + 33.0), vnoise(sp * 3.7 + 43.0), vnoise(sp * 3.7 + 53.0)) - 0.5;
    float border = inkVoronoi(sp + warp * 0.95 + warp2 * 0.22, cell);
    borderPx = border / (uFacetFreq * mpp);
    NF = normalize(N + (cell - 0.5) * 2.0 * uFacetAmt * smoothstep(0.0, uFacetBevel, border));
  }

  float ndl = dot(NF, uSunDir);
  float wrapped = clamp((ndl + uWrap) / (1.0 + uWrap), 0.0, 1.0);
  float sky = NF.y * 0.5 + 0.5;
  float light = mix(wrapped, sky, uSkyFill);

  // Wash warps the terminator. Stretched vertically so bleeds run downhill.
  vec3 wp = vec3(P.x, P.y * 0.45, P.z) * uWashFreq;
  float warpW = vnoise(wp * 0.53 + 7.0) - 0.5;
  float wash = fbm3(wp + warpW * 1.4);
  float t = light + (wash - 0.5) * uWashWarp;
  float tBase = t;

  // Ink on paper: value is decided in big shapes, so the even all-over tooth is turned well down.
  float bold = uInkBold * uBoldMat;
  float calm = 1.0 - 0.55 * bold;

  // Soft blotches: rock texture energy peaks at 8 to 16 px (style.md section 5).
  t += (blotch - 0.5) * uBlotchAmp * 2.0 * calm;

  // Fall-line streaks fade out on flat tops, where they would turn to speckle.
  float steep = 1.0 - smoothstep(0.55, 0.92, abs(N.y));
  t += (bristleWide - 0.5) * uStreakAmp * 2.0 * steep * calm;

  // Brush strokes. Each cell has its own frame: on steep planes strokes lean off the fall line,
  // on flat ones they lie at the cell's own heading. The frame is constant inside a cell, so the
  // strokes stay locked to the stone and there is no per-pixel swirl.
  float s1 = 0.5, s2 = 0.5, s3 = 0.5;
  if (uBrushAmt > 0.001) {
    vec3 lean = vec3(cell.x - 0.5, 0.0, cell.z - 0.5) * uBrushLean;
    vec3 a = normalize(vec3(lean.x, 1.0, lean.z));
    vec3 b = normalize(cross(a, vec3(0.31, 0.2, 0.93)));
    vec3 c = cross(a, b);
    float az = cell.y * 6.283;
    vec3 a2 = vec3(cos(az), 0.0, sin(az));
    vec3 b2 = vec3(-a2.z, 0.0, a2.x);
    vec3 qSteep = vec3(dot(Pq, a) * 0.13, dot(Pq, b), dot(Pq, c));
    vec3 qFlat = vec3(dot(Pq, a2) * 0.2, Pq.y, dot(Pq, b2));
    float sw = smoothstep(0.62, 0.88, abs(N.y));
    if (sw < 0.999) {
      s1 = pxNoise(qSteep, vec3(1.0), 2.8, mpp, 41.0);
      s2 = pxNoise(qSteep, vec3(1.0), 8.0, mpp, 47.0);
      s3 = pxNoise(qSteep, vec3(1.0), 1.9, mpp, 83.0);
    }
    if (sw > 0.001) {
      s1 = mix(s1, pxNoise(qFlat, vec3(1.0), 2.8, mpp, 41.0), sw);
      s2 = mix(s2, pxNoise(qFlat, vec3(1.0), 8.0, mpp, 47.0), sw);
      s3 = mix(s3, pxNoise(qFlat, vec3(1.0), 1.9, mpp, 83.0), sw);
    }
    t += ((s2 - 0.5) * 0.62 + (s1 - 0.5) * 0.4) * uBrushAmt * calm;
  }

  // Big soft stains, world-locked. On pale ground they are what makes it read as stained paper.
  float stainMask = 0.0;
  if (uStainAmt > 0.001) {
    vec3 st = P * uStainFreq;
    float swarp = vnoise(st * 0.61 + 91.0) - 0.5;
    float big = fbm3(st + swarp * 1.8 + 77.0);
    float mid = fbm3(st * 2.9 + swarp * 2.4 + 37.0);
    stainMask = smoothstep(0.44, 0.66, big * 0.7 + mid * 0.3);
    t -= stainMask * uStainAmt * 0.2;
    t -= (mid - 0.5) * uStainAmt * 0.12;
  }

  // Lit planes stay nearly clean. Surface noise belongs to the shade, where it reads as pigment.
  float litClean = uLitClean * smoothstep(0.3, 0.72, tBase);
  t = mix(t, tBase, litClean);

  vec3 look = vec3(0.5, 0.0, 0.0);
  if (uLookMap > 0.5) {
    look = albedo;
    t += (look.r - 0.5) * 1.1;
  }

  // Ink pools in cavities.
  t *= mix(1.0, paint.r, uCavityK);

  vec3 col;
  if (uUseRamp > 0.5) {
    // A continuous wash, with a few wandering wet edges where a glaze stopped. These are irregular
    // and uneven in strength, so they read as bleeds and not as a run of equal toon bands.
    float v = t * uRampScale + uRampBias;
    float wet = smoothstep(0.38, 0.72, vnoise(P * uWashFreq * 2.1 + 41.0));
    float q = 0.11;
    float wetEdge = 0.0;
    for (int i = 0; i < 4; i++) {
      float fi = float(i);
      float th = 0.22 + fi * 0.2 + (fract(fi * 0.73 + 0.41) - 0.5) * 0.07;
      float n = mix(bristle, bristleWide, fract(fi * 0.381 + 0.17)) - 0.5;
      float wander = (wash - 0.5) * 0.3 + (blotch - 0.5) * 0.9;
      float edge = mix(0.09, 0.2, wet * fract(fi * 0.618 + 0.3));
      float cov = smoothstep(th - edge, th + edge, v + n * uBrushEdge + wander * uBrushEdge * 1.6);
      q += 0.22 * cov;
      wetEdge += cov * (1.0 - cov) * 4.0 * (1.0 - wet) * fract(fi * 0.37 + 0.2);
    }
    float stepped = q + (v - q) * 0.45 - wetEdge * 0.016;

    // Border bleed: a dark side and a pale lip on each stroke, which chisels the plane.
    float crackFade = 1.0 - smoothstep(0.12, 0.3, mpp * uFacetFreq);
    if (uCrackAmt > 0.001) {
      float bleed = exp(-borderPx / 6.0) * crackFade * (0.45 + (s2 - 0.5) * 1.8);
      stepped += bleed * (cell.y > 0.5 ? -0.07 : 0.05) * uCrackAmt;
    }
    float vw = mix(v, stepped, uStep);

    // Wash zones: pale top, a mid wash, a cool dark. Each boundary is where a glaze stopped, hard in
    // one place and bleeding in the next. A little of the continuous ramp stays inside each zone.
    if (uZones > 0.001) {
      float slow = BROAD(P, vec3(1.0, 0.5, 1.0), 46.0, 151.0);
      float wetZ = smoothstep(0.32, 0.68, BROAD(P, vec3(1.0), 70.0, 157.0));
      float wan = ((slow - 0.5) * 0.34 + (wash - 0.5) * 0.3 + (bristleWide - 0.5) * 0.05) * uZoneWander;
      float ea = mix(0.03, uZoneSoft, wetZ);
      float eb = mix(uZoneSoft, 0.035, wetZ);
      float zDark = smoothstep(uZoneA - ea, uZoneA + ea, v + wan);
      float zPale = smoothstep(uZoneB - eb, uZoneB + eb, v + wan);
      float zoned = mix(mix(uZoneVals.x, uZoneVals.y, zDark), uZoneVals.z, zPale);
      zoned += (v - mix(mix(0.5 * uZoneA, 0.5 * (uZoneA + uZoneB), zDark), 0.5 * (uZoneB + 1.0), zPale)) * 0.3;
      vw = mix(vw, zoned, uZones);
    }

    // Notan: lit faces go to pale paper and shade drops to slate, across one wandering wet edge, in
    // place of a smooth 3D gradient through mid grey.
    if (bold > 0.001) {
      float slowN = BROAD(P, vec3(1.0, 0.4, 1.0), 60.0, 171.0);
      float wanN = (slowN - 0.5) * 0.3 + (wash - 0.5) * 0.3 + (bristleWide - 0.5) * 0.05;
      float wetN = smoothstep(0.35, 0.65, BROAD(P, vec3(1.0), 90.0, 177.0));
      float eN = mix(0.015, 0.07, wetN);
      float paperN = smoothstep(0.46 - eN, 0.46 + eN, vw + wanN);
      float shade = 0.08 + 0.42 * smoothstep(0.0, 0.46, vw);
      // Lit stone keeps big soft washes, or it reads as a blank card.
      // They are laid by a brush, so each stops at a dragged edge instead of fading out like an airbrush.
      float washN = (wash - 0.5) * 0.22 + (slowN - 0.5) * 0.34;
      float dragN = washN + ((bristleWide - 0.5) * 0.5 + (bristle - 0.5) * 0.4 + (blotch - 0.5) * 0.3) * 0.17;
      float laid = 0.085 * (smoothstep(-0.075, -0.05, dragN) + smoothstep(0.035, 0.06, dragN) - 1.0);
      float pale = 0.75 + 0.2 * smoothstep(0.55, 1.05, vw) + mix(washN, laid, 0.8);
      vw = mix(vw, mix(shade, pale, paperN), 0.85 * bold);
    }
    col = rampLookup(vw) * uTint;
    // The lit stone is the paper showing through: warm, not neutral grey.
    col = mix(col, col * vec3(1.035, 1.012, 0.97), bold * smoothstep(0.62, 0.95, vw));

    // Shadow goes to slate. The ramp's own darks are only faintly blue, and a warm tint cancels them.
    col *= mix(vec3(1.0), vec3(0.88, 0.98, 1.12), (1.0 - smoothstep(0.1, 0.6, vw)) * uCoolDark);

    // Pigment drifts warm and blue-grey in big patches.
    float hue = vnoise(P * uWashFreq * 0.8 + 61.0) - 0.5 + (blotch - 0.5) * 0.5;
    col *= 1.0 + max(hue, -0.16) * vec3(0.07, 0.0, -0.08) * uHueAmt;

    // Pale scumble: the brush skips over lit planes and leaves dragged, broken flecks.
    if (uScumble > 0.001) {
      float scum = smoothstep(0.585, 0.70, s1 * 0.6 + s3 * 0.4 + (v - 0.68) * 0.34) * (1.0 - litClean * 0.8);
      col = mix(col, uDryCol, scum * uScumble);
    }

    // Dry brush from the mask. Strokes feather its edge: a low mask gives sparse dragged flecks and
    // a high mask pale stone, with no one outline around the whole patch.
    float dryMask = max(paint.g, look.g);
    if (dryMask > 0.01) {
      float strokes = (uBrushAmt > 0.001 ? s1 * 0.45 + s2 * 0.2 + bristleWide * 0.35 : bristle * 0.62 + bristleWide * 0.38);
      float dry = smoothstep(0.47, 0.67, strokes + (dryMask - 0.5) * 0.8) * smoothstep(0.02, 0.22, dryMask);
      // A look map that paints its own torn edges does not want bristles laid over them, which read as hatching.
      dry = mix(dry, dryMask, uDryDirect);
      // Bare stone still carries its grain, or a painted tear reads as a flat label.
      vec3 dryTex = uDryCol * (1.0 + uDryDirect * ((blotch - 0.5) * 0.26 + (grain - 0.5) * 0.2));
      col = mix(col, dryTex, dry * mix(uDryAmt, 0.95, smoothstep(0.55, 1.0, dryMask)));
    }

    // Blue-black pools with a torn edge (environment.md 3.1). The edge is thresholded
    // against noise, so a soft mask paints as a brush mark and not a gradient.
    float poolMask = max(paint.b * uPoolAmt, look.b);
    if (poolMask > 0.001) {
      float tear = (blotch - 0.5) * 0.9 + (bristle - 0.5) * 0.65 + (s2 - 0.5) * 0.5;
      // A slow gradient against fine noise is what breaks into speckle, so a bold edge takes less of it.
      // Thresholds only drop for a fully bold chapter: on chapter 1's thin painted masks a lower one turns to leopard spots.
      float boldP = smoothstep(0.5, 1.0, bold);
      // On a wall a full mask is too big a shape for solid black: it pulls in and goes to slate, dry at the edges.
      float wallP = boldP * (1.0 - smoothstep(0.35, 0.65, abs(N.y)));
      poolMask = max(poolMask - wallP * (0.16 + (bristleWide - 0.5) * 0.3), 0.0);
      float pool = smoothstep(mix(0.42, 0.3, boldP), mix(0.56, 0.37, boldP), poolMask + tear * 0.5 * uPoolTear * mix(1.0, 0.3, bold));
      col *= 1.0 - 0.5 * boldP * smoothstep(0.08, 0.34, poolMask + (blotch - 0.5) * 0.1);
      // A thin mask paints a translucent wash, a full one goes down as solid ink.
      float load = smoothstep(0.15, 0.9, poolMask);
      vec3 inkCol = mix(mix(uPoolCol, uPoolDeep, smoothstep(0.7, 0.92, poolMask)), vec3(0.035, 0.04, 0.045), bold * 0.9);
      // Painted crack lines sit at the very top of the mask and are warm black, unlike wash.
      inkCol = mix(inkCol, vec3(0.085, 0.105, 0.13), wallP);
      float lineInk = smoothstep(0.78, 0.86, look.b);
      inkCol = mix(inkCol, uInkLine, lineInk);
      pool = mix(pool, smoothstep(0.78, 0.95, look.b), lineInk);
      col = mix(col, inkCol, pool * mix(mix(0.55, 0.98, load), 0.97, bold) * (1.0 - wallP * 0.4 * smoothstep(0.54, 0.7, s1 * 0.5 + bristle * 0.5)));
    }

    // Big ink shapes on anything steep: long falling bands, as a loaded brush draws down a cliff, gathered
    // where the face is turned from the light. A soft wet bleed, then a core of real black inside it.
    float inkAmt = bold * bold * uInkShape * (1.0 - smoothstep(0.42, 0.72, abs(N.y)));
    if (inkAmt > 0.001) {
      vec3 qi = vec3(P.x, P.y * 0.055, P.z) * 0.42;
      float warpI = vnoise(qi * 0.7 + 201.0) - 0.5;
      float bandI = fbm3(qi + warpI * 1.3 + 211.0);
      // From the true normal: a facet's tilt here would cut the shape into the cell mosaic.
      float lightI = mix(clamp((dot(N, uSunDir) + uWrap) / (1.0 + uWrap), 0.0, 1.0), N.y * 0.5 + 0.5, uSkyFill);
      float mI = bandI + (0.5 - lightI) * 0.3 + (paint.r - 1.0) * 0.3 + (vnoise(vec3(P.x, P.y * 0.05, P.z) * 3.4 + 221.0) - 0.5) * 0.07;
      // The field moves slowly on a near wall: fine noise here would make felt, not a torn edge.
      float bleedI = smoothstep(0.53, 0.64, mI + (blotch - 0.5) * 0.03);
      float coreI = smoothstep(0.665, 0.685, mI + (blotch - 0.5) * 0.05 + (bristleWide - 0.5) * 0.03);
      col = mix(col, col * vec3(0.36, 0.43, 0.5), bleedI * inkAmt * 0.85);
      // Slate, not black, with the dry brush skipping in it: the black belongs to the lines.
      col = mix(col, vec3(0.085, 0.105, 0.13), coreI * inkAmt * (0.97 - 0.4 * smoothstep(0.54, 0.7, s1 * 0.5 + bristle * 0.5)));
    }

    // Gouges: where two planes meet, ink sometimes runs into the seam as a short tapered notch. The
    // width comes from a slow field, so a notch swells and thins out to nothing along the border.
    if (uGouge > 0.001) {
      float reach = smoothstep(0.58, 0.82, BROAD(Pq, vec3(1.0, 0.6, 1.0), 19.0, 97.0));
      float gw = 0.6 + 3.4 * reach;
      float gouge = (1.0 - smoothstep(gw * 0.5, gw, borderPx + (bristle - 0.5) * 2.0)) * reach;
      gouge *= step(0.5, cell.z);
      col = mix(col, mix(uPoolCol, uPoolDeep, reach), gouge * uGouge);
    }

    // Granite: a pen's stipple gathers in loose patches and toward the shade, with bare stone between them.
    if (bold > 0.001) {
      float gather = smoothstep(0.38, 0.68, BROAD(Pq, vec3(1.0), 34.0, 191.0) + (0.55 - vw) * 0.5);
      float dot1 = smoothstep(0.6, 0.7, pxNoise(Pq, vec3(1.0), 1.7, mpp, 193.0));
      float dot2 = smoothstep(0.62, 0.74, pxNoise(Pq, vec3(1.0), 3.4, mpp, 197.0));
      col *= 1.0 - bold * gather * (0.26 * dot1 + 0.2 * dot2);
      // The brush skipped a little on the lit stone, too.
      col = mix(col, col * vec3(1.13, 1.12, 1.09), bold * smoothstep(0.66, 0.78, s3) * (1.0 - gather) * 0.55);
    }

    // Pits and chisel ticks, in loose clusters. Dark and small, and they follow the plane.
    if (uPitAmt > 0.001) {
      float cluster = smoothstep(0.38, 0.64, BROAD(Pq, vec3(1.0), 22.0, 53.0));
      float tick = smoothstep(0.69, 0.79, s3) * cluster;
      float pit = smoothstep(0.70, 0.82, pxNoise(Pq, vec3(1.0), 2.4, mpp, 59.0)) * mix(0.3, 1.0, cluster);
      col *= 1.0 - uPitAmt * (0.42 * tick + 0.42 * pit) * (1.0 - litClean);
    }

    // Ink specks settle in the stains.
    if (uSpeckAmt > 0.001) {
      float speck = smoothstep(0.73, 0.84, pxNoise(Pq, vec3(1.0), 2.1, mpp, 73.0));
      speck *= smoothstep(0.42, 0.68, BROAD(Pq, vec3(1.0), 38.0, 79.0) + stainMask * 0.22);
      col = mix(col, vec3(0.2, 0.19, 0.17), speck * uSpeckAmt * 0.62);
    }

    // Cracks: long strokes on the cell borders, with pressure along them. Only some borders carry
    // one, gated on a slow field, and pressure takes each down to nothing before it ends.
    if (uCrackAmt > 0.001) {
      float pressure = BROAD(Pq, vec3(1.0, 0.3, 1.0), 42.0, 67.0);
      float wPx = uCrackW * smoothstep(0.32, 0.8, pressure);
      float gate = smoothstep(uCrackGate - 0.03, uCrackGate + 0.03, vnoise(P * uFacetFreq * vec3(0.8, 0.8 * uFacetStretch, 0.8) + 71.0));
      float crack = 1.0 - smoothstep(max(wPx * 0.5 - 0.6, 0.0), wPx * 0.5 + 0.6, borderPx);
      crack *= gate * crackFade * smoothstep(0.12, 0.9, wPx);
      col = mix(col, uInkLine, crack * uCrackAmt);
    }
  } else {
    float lit = smoothstep(0.10, 0.62, t + (bristleWide - 0.5) * 0.08);
    col = albedo * mix(uShadeTint, vec3(1.0), lit);
    col *= mix(1.0, 1.25, smoothstep(0.82, 1.0, t));
  }

  // Cast shadow, multiplied. A brush lays it, so its edge breaks up instead of tracing the map.
  float sEdge = shadow * (1.0 - shadow) * 4.0;
  float s = smoothstep(0.3, 0.7, clamp(shadow + (bristleWide - 0.5) * 0.7 * sEdge + (blotch - 0.5) * 0.5 * sEdge, 0.0, 1.0));
  // On a bold chapter it is cool slate with the brush skipping through it, not a flat brown pane.
  float boldS = uInkBold * uBoldMat * step(0.5, uUseRamp);
  float skip = smoothstep(0.54, 0.7, bristleWide * 0.55 + blotch * 0.45);
  col *= mix(uShadowMul * mix(vec3(1.0), vec3(0.74, 0.82, 0.96) * (1.0 + skip * 0.34), boldS), vec3(1.0), s);

  // Granulation and world-locked tooth, luminance only. Pigment settles in the darks.
  float lum = dot(col, vec3(0.2126, 0.7152, 0.0722));
  float g = (grain - 0.5) * 2.0;
  col *= 1.0 + g * uGrainAmp * mix(2.2, 1.0, smoothstep(0.1, 0.65, lum)) * (1.0 - 0.3 * uInkBold * uBoldMat);

  return col;
}
vec3 display_to_scene(vec3 c){
    vec3 y = mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));
    vec3 a = 2.51-2.43*y;
    vec3 b = .03-.59*y;
    return max((-b+sqrt(b*b+4.0*a*.14*y))/(2.0*a),vec3(0.0));
}
void fragment(){
    vec2 uv = UV;
    if(ground_project){
        float path_z=.4+sin(ink_world.x*.25)*.44;
        uv=vec2(clamp((ink_world.z-path_z+5.0)/10.0,.025,.975),(ink_world.x+21.0)/48.0);
    }
    vec4 tex = has_map ? texture(look_map,uv) : vec4(base_color,1.0);
    if(foliage){
        vec2 dx=dFdx(uv)*2048.0,dy=dFdy(uv)*2048.0;
        float lod=.5*log2(max(max(dot(dx,dx),dot(dy,dy)),.000001));
        if(tex.a<mix(.42,.1,smoothstep(2.0,5.5,lod))){
            if(texture(look_map,uv,2.4).a<.42)discard;
            tex.rgb=vec3(.075,.085,.078);
        }
    }else if(tex.a<alpha_cut){discard;}
    vec4 paint = use_paint ? COLOR : vec4(1.0,0.0,0.0,1.0);
    if(!use_paint&&!base_ground)tex.rgb*=COLOR.rgb;
    if(base_ground)paint=vec4(1.0,0.0,0.0,1.0);
    vec3 col=inkSurface(ink_world*material_scale,normalize(ink_normal),tex.rgb,paint,1.0);
    col=mix(col,wash_color,wash_amount);
    ALBEDO=display_to_scene(clamp(col,vec3(0.0),vec3(.96)));
}
