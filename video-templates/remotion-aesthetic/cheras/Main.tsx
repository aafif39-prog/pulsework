import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, Easing} from 'remotion';
import data from '../public/captions.json';

// I-SIHAT Cheras Invisalign - "aesthetic explainer" style (frosted cards, blur-in captions, step progress, PiP).
// Meta-safe: everything between y=262 and y=1240.
export const FPS = 30, W = 1080, H = 1920;
const SPEECH = data.speech;
const END_LEN = 4;
export const TOTAL_FRAMES = Math.round((SPEECH + END_LEN) * FPS);
const C = {teal: '#2E9C93', deep: '#083441', gold: '#F2BB44', ink: '#10202A', muted: '#7A8794', wa: '#25D366'};
const PHONE = '017-744 6302';
const INTRO_END = 3.6;
const PIP_IN = 28.75, PIP_OUT = 33.08;
const STEPS: [number, string][] = [
  [0, 'INVISALIGN'], [8.52, 'CLEAR TRAYS'], [28.75, 'VS METAL BRACES'], [33.08, '5 REASONS'], [73.57, 'TREATMENT COST'],
];

const font = (n: string, f: string, fmt = 'opentype') => `@font-face{font-family:'${n}';src:url(${staticFile(f)}) format('${fmt}');}`;
const FONTS = font('InterM', 'Inter-Medium.otf') + font('InterSB', 'Inter-SemiBold.otf') + font('InterB', 'Inter-Bold.otf') +
  font('InterXB', 'Inter-ExtraBold.otf') + font('InterBlack', 'Inter-Black.otf') + font('Serif', 'serif-italic.woff2', 'woff2') +
  font('Mono', 'mono.ttf', 'truetype');

const useT = () => useCurrentFrame() / FPS;
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const sp = (t: number, t0: number, cfg = {damping: 15, stiffness: 140, mass: 0.8}) =>
  spring({frame: Math.round((t - t0) * FPS), fps: FPS, config: cfg});
// blur-in / blur-out visibility helper
const reveal = (t: number, a: number, b: number, inD = 0.35, outD = 0.25) => {
  const i = interpolate(t, [a, a + inD], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const o = interpolate(t, [b - outD, b], [1, 0], clamp);
  return Math.min(i, o);
};
const fx = (v: number, dy = 24) => ({opacity: v, filter: `blur(${(1 - v) * 12}px)`, transform: `translateY(${(1 - v) * dy}px)`});

// ---------------- footage + PiP ----------------
const Footage: React.FC = () => {
  const t = useT();
  const pin = sp(t, PIP_IN - 0.05, {damping: 18, stiffness: 110, mass: 0.9});
  const pout = sp(t, PIP_OUT - 0.25, {damping: 18, stiffness: 110, mass: 0.9});
  const p = t < PIP_IN - 0.05 ? 0 : t < PIP_OUT - 0.25 ? pin : 1 - pout;
  const full = {x: 0, y: 0, w: W, h: H, r: 0}, card = {x: 70, y: 345, w: 940, h: 560, r: 46};
  const L = (k: keyof typeof full) => full[k] + (card[k] - full[k]) * p;
  const drift = 1 + 0.025 * ((t % 12) / 12);
  return (
    <AbsoluteFill>
      {/* dark aesthetic stage, only visible while the footage is a card */}
      <AbsoluteFill style={{background: 'radial-gradient(120% 70% at 50% 30%, #0F4A4F 0%, #072328 55%, #041417 100%)', opacity: p}} />
      <div style={{position: 'absolute', left: L('x'), top: L('y'), width: L('w'), height: L('h'), borderRadius: L('r'), overflow: 'hidden',
        boxShadow: p > 0.01 ? `0 30px 80px rgba(0,0,0,${0.5 * p})` : 'none', border: p > 0.01 ? `${2 * p}px solid rgba(255,255,255,0.25)` : 'none'}}>
        <OffthreadVideo src={staticFile('src.mp4')} muted
          style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: `50% ${50 - 16 * p}%`, transform: `scale(${drift})`}} />
      </div>
    </AbsoluteFill>
  );
};

// ---------------- intro title ----------------
const Intro: React.FC = () => {
  const t = useT();
  if (t > INTRO_END) return null;
  const a = reveal(t, 0.1, INTRO_END), b = reveal(t, 0.35, INTRO_END), c = reveal(t, 0.75, INTRO_END);
  const glow = '0 0 28px rgba(255,255,255,0.85), 0 0 2px rgba(255,255,255,0.9)';
  return (
    <div style={{position: 'absolute', top: 300, left: 80, right: 80}}>
      <div style={{position: 'absolute', left: -60, right: -60, top: -40, bottom: -50, borderRadius: 120, opacity: Math.max(a, b) * 0.9,
        background: 'radial-gradient(closest-side, rgba(255,255,255,0.78), rgba(255,255,255,0.55) 60%, rgba(255,255,255,0))', filter: 'blur(14px)'}} />
      <div style={{...fx(a), position: 'relative', fontFamily: 'InterSB', fontSize: 50, color: '#5B6B76', letterSpacing: -1, textShadow: glow}}>let's learn about</div>
      <div style={{...fx(b, 40), position: 'relative', display: 'flex', alignItems: 'center', gap: 18, marginTop: -6}}>
        <Img src={staticFile('tooth.png')} style={{height: 120, filter: 'drop-shadow(0 0 18px rgba(255,255,255,0.9))'}} />
        <span style={{fontFamily: 'InterBlack', fontSize: 150, color: C.deep, letterSpacing: -7, lineHeight: 1, textShadow: glow}}>Invisalign</span>
      </div>
      <div style={{...fx(c), position: 'relative', textAlign: 'right', marginTop: -4, marginRight: 30}}>
        <span style={{fontFamily: 'InterSB', fontSize: 50, color: '#5B6B76', textShadow: glow}}>the </span>
        <span style={{fontFamily: 'Serif', fontSize: 72, color: C.teal, textShadow: glow}}>almost invisible</span>
        <span style={{fontFamily: 'InterSB', fontSize: 50, color: '#5B6B76', textShadow: glow}}> braces</span>
      </div>
    </div>
  );
};

// ---------------- step progress ----------------
const Progress: React.FC = () => {
  const t = useT();
  if (t < INTRO_END - 0.2 || t > SPEECH) return null;
  const v = reveal(t, INTRO_END - 0.2, SPEECH + 0.01, 0.4, 0.3);
  let cur = 0;
  STEPS.forEach(([s], i) => { if (t >= s) cur = i; });
  const segW = (940 - 6 * 8) / 7;
  const next = cur + 1 < STEPS.length ? STEPS[cur + 1][0] : SPEECH;
  const prog = interpolate(t, [STEPS[cur][0], next], [0, 1], clamp);
  const pillIn = sp(t, Math.max(STEPS[cur][0], INTRO_END - 0.2));
  return (
    <div style={{position: 'absolute', top: 274, left: 70, width: 940, opacity: v, filter: 'drop-shadow(0 2px 6px rgba(0,0,0,0.35))'}}>
      <div style={{display: 'flex', gap: 8}}>
        {STEPS.map((_, i) => (
          <div key={i} style={{width: segW, height: 5, borderRadius: 3, background: 'rgba(255,255,255,0.35)', overflow: 'hidden'}}>
            <div style={{height: '100%', width: `${i < cur ? 100 : i === cur ? prog * 100 : 0}%`, background: i < cur ? '#FFFFFF' : C.teal}} />
          </div>
        ))}
      </div>
      <div style={{display: 'flex', gap: 10, marginTop: 14, alignItems: 'center', opacity: pillIn, transform: `translateX(${(1 - pillIn) * -20}px)`}}>
        <span style={{fontFamily: 'Mono', fontSize: 21, color: '#fff', background: C.teal, borderRadius: 8, padding: '5px 12px', letterSpacing: 1}}>
          STEP {String(cur + 1).padStart(2, '0')} / {String(STEPS.length).padStart(2, '0')}</span>
        <span style={{fontFamily: 'Mono', fontSize: 21, color: '#fff', background: 'rgba(8,30,40,0.55)', borderRadius: 8, padding: '5px 12px', letterSpacing: 2}}>
          {STEPS[cur][1]}</span>
      </div>
    </div>
  );
};

// ---------------- captions: blur-in word by word ----------------
const Captions: React.FC = () => {
  const t = useT();
  const line = data.lines.find((l) => t >= l.s && t < l.e);
  if (!line) return null;
  const inPip = t >= PIP_IN + 0.4 && t < PIP_OUT - 0.2;
  const out = interpolate(t, [line.e - 0.15, line.e], [1, 0], clamp);
  const pos = inPip ? {top: 935} : {bottom: H - 1240};
  return (
    <div style={{position: 'absolute', left: 40, right: 110, ...pos, textAlign: 'center', whiteSpace: 'nowrap', opacity: out, filter: `blur(${(1 - out) * 6}px)`}}>
      {line.words.map((w, i) => {
        const v = interpolate(t, [w.s, w.s + 0.28], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
        const serif = w.style === 'serif', key = w.style === 'key';
        return (
          <span key={i} style={{display: 'inline-block', marginRight: 14, ...fx(v, 14),
            fontFamily: serif ? 'Serif' : key ? 'InterB' : 'InterSB', fontSize: serif ? 72 : 58, lineHeight: 1.2, whiteSpace: 'nowrap' as const,
            color: key ? C.gold : '#FFFFFF', letterSpacing: serif ? 0 : -0.5,
            textShadow: '0 4px 22px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.4)'}}>{w.t}</span>
        );
      })}
    </div>
  );
};

// ---------------- frosted glass UI ----------------
const Glass: React.FC<{a: number; b: number; top: number; children: React.ReactNode}> = ({a, b, top, children}) => {
  const t = useT();
  if (t < a || t > b) return null;
  const s = sp(t, a);
  const o = interpolate(t, [b - 0.25, b], [1, 0], clamp);
  const v = Math.min(s, o);
  return (
    <div style={{position: 'absolute', top, left: 90, right: 90, opacity: v, filter: `blur(${(1 - v) * 10}px)`,
      transform: `translateY(${(1 - s) * 50}px) scale(${0.94 + 0.06 * s})`,
      background: 'rgba(255,255,255,0.84)', backdropFilter: 'blur(26px) saturate(1.4)', border: '1.5px solid rgba(255,255,255,0.75)',
      borderRadius: 32, boxShadow: '0 24px 70px rgba(6,30,36,0.28)', padding: '22px 24px 24px'}}>
      {children}
    </div>
  );
};
const Head: React.FC<{text: string}> = ({text}) => (
  <div style={{fontFamily: 'Mono', fontSize: 19, letterSpacing: 2.5, color: C.muted, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 10}}>
    <span style={{width: 9, height: 9, borderRadius: 5, background: C.teal, display: 'inline-block'}} />{text}
  </div>
);
const Check: React.FC<{v: number; size?: number}> = ({v, size = 40}) => (
  <div style={{width: size, height: size, borderRadius: size / 2, background: C.teal, transform: `scale(${v})`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
    <svg width={size * 0.55} height={size * 0.55} viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="#fff" strokeWidth={3.2} strokeLinecap="round" strokeLinejoin="round" /></svg>
  </div>
);
const Row: React.FC<{sel: number; icon?: React.ReactNode; children: React.ReactNode; strike?: boolean; h?: number; right?: React.ReactNode}> =
  ({sel, icon, children, strike, h = 76, right}) => (
  <div style={{height: h, borderRadius: 20, display: 'flex', alignItems: 'center', gap: 16, padding: '0 18px', marginTop: 10,
    background: `rgba(232,246,244,${sel})`, border: `3px solid rgba(46,156,147,${sel})`}}>
    {icon}
    <span style={{flex: 1, fontFamily: 'InterSB', fontSize: h > 60 ? 33 : 30, color: strike ? C.muted : C.ink,
      textDecoration: strike ? 'line-through' : 'none', textDecorationThickness: 3}}>{children}</span>
    {right}
  </div>
);
const IconCircle: React.FC<{bg: string; children: React.ReactNode; size?: number}> = ({bg, children, size = 44}) => (
  <div style={{width: size, height: size, borderRadius: size / 2, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0}}>{children}</div>
);
const Xmark = () => <svg width="20" height="20" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" stroke="#fff" strokeWidth="3.2" strokeLinecap="round" /></svg>;
const Cal = () => <svg width="24" height="24" viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="15" rx="3" fill="none" stroke="#fff" strokeWidth="2.2" /><path d="M3.5 10h17M8 3v4M16 3v4" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" /></svg>;
const Pin = () => <svg width="20" height="20" viewBox="0 0 24 24"><path d="M12 22s7-7.2 7-12.2A7 7 0 0 0 5 9.8C5 14.8 12 22 12 22z" fill="none" stroke="#fff" strokeWidth="2.4" /><circle cx="12" cy="10" r="2.6" fill="#fff" /></svg>;
const WaIcon = () => <svg width="26" height="26" viewBox="0 0 24 24"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3z" fill="none" stroke="#fff" strokeWidth="2" /><path d="M8.6 8.4c.3-.6.6-.6.9-.6h.6c.2 0 .4 0 .6.5l.8 1.9c.1.2 0 .4-.1.6l-.5.6c-.1.2-.2.3 0 .6.6 1 1.4 1.8 2.5 2.4.3.2.5.1.6-.1l.7-.8c.2-.2.4-.2.6-.1l1.8.9c.3.1.4.3.4.5 0 .6-.3 1.5-1.4 1.8-.9.3-2.3.2-4.4-1-2-1.2-3.4-3.3-3.7-4.1-.4-.9-.5-1.9.6-3.1z" fill="#fff" /></svg>;

const Cards: React.FC = () => {
  const t = useT();
  const sel = (t0: number) => interpolate(t, [t0, t0 + 0.3], [0, 1], clamp);
  const ck = (t0: number) => sp(t, t0 + 0.1, {damping: 10, stiffness: 200, mass: 0.6});
  const Tick = <IconCircle bg={C.teal}><svg width="22" height="22" viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="#fff" strokeWidth={3.2} strokeLinecap="round" strokeLinejoin="round" /></svg></IconCircle>;
  const dot = (t0: number) => <IconCircle bg={t >= t0 ? C.teal : '#B9C2C9'}><svg width="16" height="16" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6" fill="#fff" /></svg></IconCircle>;
  return (
    <>
      {/* 01 what is Invisalign */}
      <Glass a={INTRO_END} b={8.45} top={372}>
        <Head text="WHAT IS INVISALIGN" />
        <Row sel={sel(4.15)} icon={dot(4.15)} right={<Check v={ck(4.15)} />}>A set of plastic trays</Row>
        <Row sel={sel(7.69)} icon={dot(7.69)} right={<Check v={ck(7.69)} />}>Gently moves your teeth</Row>
      </Glass>
      {/* 02 clear trays (over the aligner B-roll) */}
      <Glass a={8.6} b={19.5} top={372}>
        <Head text="CLEAR TRAYS" />
        <Row h={66} sel={sel(10.11)} icon={dot(10.11)} right={<Check v={ck(10.11)} />}>Transparent</Row>
        <Row h={66} sel={sel(11.6)} icon={dot(11.6)} right={<Check v={ck(11.6)} />}>Light passes through</Row>
        <Row h={66} sel={sel(17.93)} icon={dot(17.93)} right={<Check v={ck(17.93)} />}>Almost invisible</Row>
      </Glass>
      {/* 03 metal braces vs Invisalign (inside PiP) */}
      <Glass a={PIP_IN + 0.7} b={PIP_OUT - 0.1} top={1000}>
        <Head text="METAL BRACES VS INVISALIGN" />
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: 12}}>
          <Row h={64} sel={0} strike icon={<IconCircle size={36} bg="#B9C2C9"><Xmark /></IconCircle>}>Metal braces</Row>
          <Row h={64} sel={sel(30.0)} icon={<IconCircle size={36} bg={C.teal}><svg width="18" height="18" viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="#fff" strokeWidth={3.4} strokeLinecap="round" strokeLinejoin="round" /></svg></IconCircle>}>Invisalign</Row>
        </div>
      </Glass>
      {/* 05 cost */}
      <Glass a={73.7} b={SPEECH} top={372}>
        <Head text="TREATMENT COST" />
        <Row sel={sel(76.36)} icon={dot(76.36)} right={<Check v={ck(76.36)} />}>Depends on no. of trays</Row>
        <Row sel={sel(82.9)} icon={dot(82.9)} right={<Check v={ck(82.9)} />}>Fewer trays, lower cost</Row>
      </Glass>
    </>
  );
};

// ---------------- 03-04 number tiles ----------------
const Tiles: React.FC = () => {
  const t = useT();
  const a = 33.0, b = 73.45;
  if (t < a || t > b) return null;
  const items: [string, string, number][] = [['1', 'AESTHETIC', 33.08], ['2', 'EASY CLEAN', 34.78], ['3', 'EAT ANYTHING', 45.66],
    ['4', 'PREDICTABLE', 56.47], ['5', 'FEWER VISITS', 65.72]];
  return (
    <div style={{position: 'absolute', top: 372, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 14}}>
      {items.map(([n, lab, t0], i) => {
        const inV = sp(t, a + i * 0.08);
        const out = interpolate(t, [b - 0.25, b], [1, 0], clamp);
        const nextT = i + 1 < items.length ? items[i + 1][2] : 1e9;
        const act = t >= t0 && t < nextT, done = t >= nextT;
        const ap = act ? sp(t, t0, {damping: 12, stiffness: 180, mass: 0.6}) : 0;
        const dk = done ? sp(t, nextT, {damping: 10, stiffness: 200, mass: 0.6}) : 0;
        const v = Math.min(inV, out);
        return (
          <div key={n} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, opacity: v,
            filter: `blur(${(1 - v) * 10}px)`, transform: `translateY(${(1 - inV) * 40}px) scale(${0.96 + 0.1 * ap})`}}>
            <div style={{position: 'relative', width: 166, height: 166, borderRadius: 30, border: `3px ${act || done ? 'solid' : 'dashed'} rgba(255,255,255,${act ? 1 : 0.85})`,
              background: act ? `rgba(46,156,147,${0.6 + 0.3 * ap})` : 'rgba(8,52,65,0.45)', backdropFilter: 'blur(18px)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 18px 44px rgba(0,0,0,0.25)'}}>
              <span style={{fontFamily: 'Serif', fontSize: 116, color: '#fff', lineHeight: 1, marginTop: 8, opacity: done ? 0.75 : 1}}>{n}</span>
              {done && <div style={{position: 'absolute', top: -10, right: -10}}><Check v={dk} size={40} /></div>}
            </div>
            <span style={{fontFamily: 'Mono', fontSize: 16, color: '#fff', letterSpacing: 1.2, padding: '5px 9px', borderRadius: 8,
              background: act ? C.teal : 'rgba(8,30,40,0.6)', whiteSpace: 'nowrap'}}>{lab}</span>
          </div>
        );
      })}
    </div>
  );
};

// ---------------- end card ----------------
const EndCard: React.FC = () => {
  const t = useT();
  if (t < SPEECH - 0.05) return null;
  const f = interpolate(t, [SPEECH - 0.05, SPEECH + 0.45], [0, 1], clamp);
  const it = (d: number) => fx(interpolate(t, [SPEECH + d, SPEECH + d + 0.45], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)}), 30);
  return (
    <AbsoluteFill style={{opacity: f}}>
      <Sequence from={0}>
        <OffthreadVideo src={staticFile('src.mp4')} startFrom={Math.round((SPEECH - END_LEN - 0.05) * FPS)} muted
          style={{width: W, height: H, objectFit: 'cover', filter: 'blur(34px) saturate(0.9)', transform: 'scale(1.15)'}} />
      </Sequence>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(246,251,250,0.86) 0%, rgba(226,244,241,0.9) 100%)'}} />
      <div style={{position: 'absolute', top: 360, left: 80, right: 80, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center'}}>
        <Img src={staticFile('logo.png')} style={{width: 470, ...it(0.1)}} />
        <div style={{...it(0.3), fontFamily: 'InterBlack', fontSize: 140, color: C.deep, letterSpacing: -7, lineHeight: 1, marginTop: 60}}>Invisalign</div>
        <div style={{...it(0.5), marginTop: 6}}>
          <span style={{fontFamily: 'InterSB', fontSize: 52, color: '#4E5F6A'}}>almost </span>
          <span style={{fontFamily: 'Serif', fontSize: 92, color: C.teal}}>invisible.</span>
          <div style={{fontFamily: 'InterSB', fontSize: 46, color: '#4E5F6A', marginTop: 2}}>Fully removable.</div>
        </div>
        <div style={{...it(0.75), marginTop: 46, display: 'flex', alignItems: 'center', gap: 16, background: C.deep, borderRadius: 999, padding: '20px 40px 20px 22px',
          boxShadow: '0 18px 40px rgba(8,52,65,0.3)'}}>
          <IconCircle bg={C.wa} size={56}><WaIcon /></IconCircle>
          <span style={{fontFamily: 'InterB', fontSize: 40, color: '#fff'}}>WhatsApp {PHONE}</span>
        </div>
        <div style={{...it(0.95), marginTop: 34, fontFamily: 'Mono', fontSize: 23, letterSpacing: 3, color: C.muted}}>I-SIHAT DENTAL CARE · CHERAS</div>
      </div>
    </AbsoluteFill>
  );
};

export const Main: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <style>{FONTS}</style>
    <Footage />
    <Intro />
    <Tiles />
    <Cards />
    <Captions />
    <Progress />
    <EndCard />
  </AbsoluteFill>
);
