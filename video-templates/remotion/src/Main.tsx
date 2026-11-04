import React from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing,
} from 'remotion';
import {C, SAFE, W, H, FPS, BANNER_TOP, BELOW_BANNER, CAPTION_BOTTOM, PHONE, WEBSITE, LOCATION} from './theme';
import data from '../public/captions.json';

// ---------- per-video config: "Metal vs Ceramic Braces" (Meta-safe v5) ----------
const SPEECH = data.speech; // seconds of cut voice
const END_LEN = 3.5;
export const TOTAL_FRAMES = Math.round((SPEECH + END_LEN) * FPS);
const HOOK_END = 2.5;
const CLIPS = [ // [srcStart, srcEnd] kept from the source video (same as KEEP in prep_v2.py)
  [0.3, 5.6],
  [21.2, 57.3],
];
const FOOTAGE_SHIFT = -60; // px; face sits between the top banner and the captions
const HOOK = {l1: 'Metal or Ceramic?', l2: ['Which one is', 'right for you?']};
const CHIPS = [
  {from: 5.46, to: 16.4, text: 'METAL BRACES'},
  {from: 16.6, to: 26.4, text: 'CERAMIC BRACES'},
];
const ZOOMS: [number, number][] = [ // [time, scale] emphasis punch-ins
  [0, 1.0], [5.46, 1.08], [10.24, 1.0], [16.6, 1.08], [18.64, 1.0],
  [26.52, 1.06], [30.68, 1.0], [33.34, 1.08], [35.0, 1.0], [38.9, 1.08],
];
// B-roll: 'full' = full-screen cutaway, 'card' = close-up card over dimmed speaker, 'compare' = metal vs ceramic
// capTop: true -> captions move up (just under the banner) for this shot
const BROLL: {from: number; to: number; kind: 'full' | 'card' | 'compare'; src?: string; label?: string; capTop?: boolean}[] = [
  {from: 5.46, to: 7.42, kind: 'full', src: 'b_wire.mp4'},
  {from: 7.42, to: 10.24, kind: 'full', src: 'b_place.mp4'},
  {from: 16.6, to: 20.44, kind: 'card', src: 'c_ceramic.mp4', label: 'CERAMIC BRACES'},
  {from: 26.52, to: 30.68, kind: 'compare'},
  {from: 30.68, to: 35.0, kind: 'full', src: 'b_model.mp4'},
  {from: 35.0, to: 38.9, kind: 'full', src: 'b_clinic.mp4', capTop: true},
];
const END = {l1: 'Your new smile', l2: 'starts here.', price: 'Braces from RM150/month', btn: 'WhatsApp to book'};
// Banner artwork = public/banner.png (compact top card, made by build3_metasafe.py)
// ------------------------------------------------------------------------------

const font = (name: string, file: string) => `@font-face{font-family:'${name}';src:url(${staticFile(file)}) format('opentype');}`;
const FONTS = font('InterXB', 'Inter-ExtraBold.otf') + font('InterBlack', 'Inter-Black.otf') +
  font('InterBold', 'Inter-Bold.otf') + font('InterSB', 'Inter-SemiBold.otf') + font('InterDisp', 'InterDisplay-ExtraBold.otf');
const shadow = '0 8px 24px rgba(0,0,0,0.28)';
const useT = () => useCurrentFrame() / FPS;

const zoomAt = (t: number) => {
  let s = ZOOMS[0][1];
  for (let i = 1; i < ZOOMS.length; i++) {
    const [zt, zs] = ZOOMS[i];
    if (t >= zt) {
      const prev = ZOOMS[i - 1][1];
      s = interpolate(t, [zt, zt + 0.22], [prev, zs], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
    }
  }
  return s * (1 + 0.012 * Math.sin(t / 3));
};

const Footage: React.FC = () => {
  const t = useT();
  let off = 0;
  return (
    <AbsoluteFill style={{transform: `translateY(${FOOTAGE_SHIFT}px) scale(${1.08 * zoomAt(t)})`, transformOrigin: '50% 30%'}}>
      {CLIPS.map(([a, b], i) => {
        const from = Math.round(off * FPS);
        const dur = Math.round((b - a) * FPS);
        off += b - a;
        return (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <OffthreadVideo src={staticFile('src.mp4')} startFrom={Math.round(a * FPS)} muted
              style={{width: W, height: H, objectFit: 'cover', filter: 'contrast(1.05) saturate(1.06) brightness(1.02)'}} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

const Vignette = () => (
  <AbsoluteFill style={{background: 'radial-gradient(ellipse 75% 60% at 50% 45%, rgba(0,0,0,0) 55%, rgba(5,15,40,0.38) 100%)'}} />
);

const Box: React.FC<{bg: string; fg: string; size: number; font: string; children: React.ReactNode}> = ({bg, fg, size, font, children}) => (
  <div style={{background: bg, color: fg, fontFamily: font, fontSize: size, lineHeight: 1.12, padding: '16px 34px 20px',
    borderRadius: 24, boxShadow: shadow, display: 'inline-block', letterSpacing: -0.5}}>{children}</div>
);

const pop = (frame: number, fps: number, delay: number) =>
  spring({frame: frame - delay, fps, config: {damping: 13, stiffness: 180, mass: 0.7}});

const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (frame > HOOK_END * fps) return null;
  const out = interpolate(frame, [HOOK_END * fps - 8, HOOK_END * fps], [1, 0], {extrapolateLeft: 'clamp'});
  const a = pop(frame, fps, 2), b = pop(frame, fps, 10), l = pop(frame, fps, 0);
  return (
    <>
      <div style={{position: 'absolute', top: SAFE.top - 10, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: out * l}}>
        <div style={{background: 'rgba(255,255,255,0.96)', borderRadius: 24, padding: '14px 26px', boxShadow: shadow}}>
          <Img src={staticFile('logo.png')} style={{width: 230, display: 'block'}} />
        </div>
      </div>
      <div style={{position: 'absolute', top: 915, left: SAFE.left, right: SAFE.right - 80, display: 'flex', flexDirection: 'column',
        alignItems: 'center', gap: 14, opacity: out}}>
        <div style={{transform: `translateY(${(1 - a) * 40}px) scale(${0.85 + 0.15 * a})`, opacity: a}}>
          <Box bg={C.white} fg={C.navy} size={62} font="InterXB">{HOOK.l1}</Box>
        </div>
        <div style={{transform: `translateY(${(1 - b) * 40}px) scale(${0.85 + 0.15 * b})`, opacity: b, textAlign: 'center'}}>
          <Box bg={C.lime} fg={C.navy} size={76} font="InterBlack">{HOOK.l2.map((l, i) => <div key={i}>{l}</div>)}</Box>
        </div>
      </div>
    </>
  );
};

const Chips: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const inCard = BROLL.some((b) => b.kind !== 'full' && t >= b.from && t < b.to);
  if (inCard) return null;
  return <>{CHIPS.filter((c) => t >= c.from && t < c.to).map((c) => {
    const p = pop(frame, fps, c.from * fps);
    const o = interpolate(t, [c.to - 0.25, c.to], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    return (
      <div key={c.text} style={{position: 'absolute', top: BELOW_BANNER, left: SAFE.left, opacity: o * p,
        transform: `translateX(${(1 - p) * -60}px)`}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 14, background: C.navy, borderRadius: 999, padding: '12px 28px 12px 16px', boxShadow: shadow}}>
          <div style={{width: 20, height: 20, borderRadius: 10, background: C.lime}} />
          <span style={{fontFamily: 'InterBlack', fontSize: 36, color: C.white, letterSpacing: 1}}>{c.text}</span>
        </div>
      </div>
    );
  })}</>;
};

const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const chunk = data.chunks.find((c) => t >= c[0].s && t < c[c.length - 1].e && c[0].s >= HOOK_END - 0.1);
  if (!chunk || t < HOOK_END) return null;
  const p = pop(frame, fps, chunk[0].s * fps);
  const top = BROLL.some((b) => b.capTop && t >= b.from && t < b.to);
  const pos = top ? {top: BELOW_BANNER + 10} : {bottom: H - CAPTION_BOTTOM};
  return (
    <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, ...pos, textAlign: 'center',
      transform: `scale(${0.9 + 0.1 * p})`, opacity: Math.min(1, p * 1.5)}}>
      <span style={{fontFamily: 'InterXB', fontSize: 70, lineHeight: 1.18, color: C.white,
        WebkitTextStroke: `9px ${C.navy}`, wordSpacing: 6, paintOrder: 'stroke fill', textShadow: '0 6px 18px rgba(0,0,0,0.45)'}}>
        {chunk.map((w, i) => {
          const active = t >= w.s && (i === chunk.length - 1 || t < chunk[i + 1].s);
          return <React.Fragment key={i}>{i > 0 ? ' ' : ''}<span style={{color: active ? C.cyan : C.white, display: 'inline-block',
            transform: active ? 'scale(1.06)' : 'none'}}>{w.t}</span></React.Fragment>;
        })}
      </span>
    </div>
  );
};

const Banner: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  if (t < HOOK_END || t >= SPEECH) return null;
  // compact top card (public/banner.png) - drops in from above and fades in after the hook
  const p = spring({frame: frame - HOOK_END * fps, fps, config: {damping: 16, stiffness: 120}});
  return <Img src={staticFile('banner.png')} style={{position: 'absolute', top: BANNER_TOP, left: '50%',
    transform: `translateX(-50%) translateY(${(1 - p) * -60}px)`, opacity: Math.min(1, p * 1.4)}} />;
};

const Card: React.FC<{src: string; label: string; w: number; delay: number; rate?: number}> = ({src, label, w, delay, rate = 0.8}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = pop(frame, fps, delay);
  return (
    <div style={{transform: `scale(${0.8 + 0.2 * p}) translateY(${(1 - p) * 40}px)`, opacity: p}}>
      <div style={{position: 'relative', width: w, height: w * 774 / 880, borderRadius: 32, overflow: 'hidden', border: `7px solid ${C.white}`,
        boxShadow: '0 18px 50px rgba(0,0,0,0.45)'}}>
        <OffthreadVideo src={staticFile(src)} muted playbackRate={rate} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        <div style={{position: 'absolute', left: 18, top: 16, background: C.navy, color: C.white, fontFamily: 'InterBlack', fontSize: 28,
          padding: '8px 20px', borderRadius: 999, display: 'flex', alignItems: 'center', gap: 10}}>
          <div style={{width: 16, height: 16, borderRadius: 8, background: C.lime}} />{label}
        </div>
      </div>
    </div>
  );
};

const BRollLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <>{BROLL.map((b, i) => {
    const from = Math.round(b.from * fps), dur = Math.round((b.to - b.from) * fps);
    return (
      <Sequence key={i} from={from} durationInFrames={dur}>
        {b.kind === 'full' ? (
          <AbsoluteFill style={{opacity: interpolate(frame - from, [0, 3], [0, 1], {extrapolateRight: 'clamp'})}}>
            <OffthreadVideo src={staticFile(b.src!)} muted
              style={{width: W, height: H, objectFit: 'cover', transform: `scale(${interpolate(frame - from, [0, dur], [1.0, 1.06])})`}} />
          </AbsoluteFill>
        ) : (
          <AbsoluteFill>
            <AbsoluteFill style={{background: 'rgba(8,22,56,0.62)', backdropFilter: 'blur(14px)',
              opacity: interpolate(frame - from, [0, 6], [0, 1], {extrapolateRight: 'clamp'})}} />
            <div style={{position: 'absolute', top: BELOW_BANNER + 10, left: SAFE.left, right: SAFE.left, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
              {b.kind === 'card' ? <Card src={b.src!} label={b.label!} w={620} delay={0} /> : <div style={{display: 'flex', gap: 18, marginTop: 20}}>
                <Card src="c_metal.mp4" label="METAL" w={420} delay={0} rate={1} />
                <Card src="c_ceramic.mp4" label="CERAMIC" w={420} delay={8} rate={0.8} />
              </div>}
            </div>
          </AbsoluteFill>
        )}
      </Sequence>
    );
  })}</>;
};

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const f = frame - Math.round(SPEECH * fps);
  if (f < 0) return null;
  const fade = interpolate(f, [0, 10], [0, 1], {extrapolateRight: 'clamp'});
  const item = (d: number) => {
    const p = pop(f, fps, d);
    return {opacity: p, transform: `translateY(${(1 - p) * 30}px)`};
  };
  // everything between y=280 and y=1240 (Meta safe area)
  return (
    <AbsoluteFill style={{opacity: fade}}>
      <OffthreadVideo src={staticFile('src.mp4')} startFrom={Math.round(40 * FPS)} muted
        style={{width: W, height: H, objectFit: 'cover', filter: 'blur(26px) brightness(0.8) saturate(0.7)', transform: 'scale(1.1)'}} />
      <AbsoluteFill style={{background: 'rgba(8,22,56,0.55)'}} />
      <div style={{position: 'absolute', top: 285, left: SAFE.left, right: SAFE.left, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center'}}>
        <div style={{...item(0), background: 'rgba(255,255,255,0.96)', borderRadius: 40, padding: '30px 46px', boxShadow: shadow}}>
          <Img src={staticFile('logo.png')} style={{width: 430, display: 'block'}} />
        </div>
        <div style={{...item(5), fontFamily: 'InterDisp', fontSize: 62, color: C.white, marginTop: 40, lineHeight: 1.15}}>{END.l1}<br />{END.l2}</div>
        <div style={{...item(9), fontFamily: 'InterBold', fontSize: 42, color: C.lime, marginTop: 16}}>{END.price}</div>
        <div style={{...item(13), background: C.lime, borderRadius: 40, padding: '16px 56px 20px', marginTop: 28, boxShadow: shadow}}>
          <div style={{fontFamily: 'InterBold', fontSize: 40, color: C.navy}}>{END.btn}</div>
          <div style={{fontFamily: 'InterBlack', fontSize: 50, color: C.navy}}>{PHONE}</div>
        </div>
        <div style={{...item(17), fontFamily: 'InterSB', fontSize: 36, color: C.white, marginTop: 26}}>{WEBSITE}</div>
        <div style={{...item(19), fontFamily: 'InterSB', fontSize: 32, color: '#D7E1F0', marginTop: 4}}>{LOCATION}</div>
        <div style={{...item(22), fontFamily: 'InterSB', fontSize: 34, color: C.lime, marginTop: 22}}>Follow for more dental tips</div>
      </div>
    </AbsoluteFill>
  );
};

export const Main: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <style>{FONTS}</style>
    <Footage />
    <Vignette />
    <BRollLayer />
    <Chips />
    <Hook />
    <Captions />
    <Banner />
    <EndCard />
  </AbsoluteFill>
);
