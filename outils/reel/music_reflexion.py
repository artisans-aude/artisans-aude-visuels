# Musique originale « réflexion » pour les réels Artisans Aude
# Simple, posée, en mineur : piano feutré, nappe douce, basse longue, pulsation discrète.
# 60 BPM (1 temps = 1 s, 1 mesure = 4 s) : les changements d'écran (multiples de 2 s) tombent sur les temps.
# Usage : python3 music_reflexion.py [duree_s]  -> musique.wav
import sys, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
D = float(sys.argv[1]) if len(sys.argv) > 1 else 42.0
N = int(SR * D)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)

def m(n): return 440 * 2 ** ((n - 69) / 12)

def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR)
    if i >= N: return
    j = min(N, i + len(sig)); s = sig[:j - i] * g
    L[i:j] += s * np.sqrt((1 - pan) / 2); R[i:j] += s * np.sqrt((1 + pan) / 2)

def lowpass(x, fc):
    return sosfilt(butter(2, fc, 'low', fs=SR, output='sos'), x)

def piano(f, dur=3.0, vel=1.0):
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for h, a in [(1, 1), (2, .45), (3, .18), (4, .08), (5, .04)]:
        s += a * np.exp(-t * (1.2 + 1.1 * h)) * np.sin(2 * np.pi * f * h * (1 + 0.0004 * h * h) * t)
    env = np.minimum(1, t / 0.012)
    return lowpass(s * env * vel, 2600)

def pad(notes, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for n in notes:
        f = m(n)
        for d in (-0.15, 0.15):
            ph = 2 * np.pi * f * (1 + d / 100) * t
            s += np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.2)
    return lowpass(s * env, 1200)

def bass(f, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)
    return s * np.minimum(1, t / 0.08) * np.exp(-t * 0.5)

def pulse():
    t = np.arange(int(0.5 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(40 + 30 * np.exp(-t * 25)) / SR) * np.exp(-t * 9)

# Am – F – Dm – E (la mineur, cadence en suspens)
prog = [(45, [57, 60, 64]), (41, [57, 60, 65]), (38, [57, 62, 65]), (40, [56, 59, 64])]
# mélodie simple, une note par temps fort, à partir de la 3e mesure
mel = {2: [(0, 76), (2, 74)], 3: [(0, 72), (2, 71)], 4: [(0, 72), (2, 76)], 5: [(0, 77), (2, 76)],
       6: [(0, 74), (2, 72)], 7: [(0, 71)], 8: [(0, 72), (2, 74)], 9: [(0, 72)]}
bar = 4.0
bars = int(np.ceil(D / bar))
for b in range(bars):
    t0 = b * bar; root, ch = prog[b % 4]
    last = b == bars - 1
    add(pad(ch, bar + 1.2), t0, 0, 0.035)
    add(bass(m(root), bar), t0, 0, 0.22)
    # arpège lent en croches (0,5 s) : grave -> aigu -> retour
    arp = [ch[0] - 12, ch[0], ch[1], ch[2], ch[1], ch[0], ch[1], ch[2]]
    for k, n in enumerate(arp):
        if last and k > 3: break
        add(piano(m(n), 2.5, 0.8 if k % 4 == 0 else 0.6), t0 + k * 0.5, -0.25 + 0.15 * (k % 3), 0.11)
    for (beat, n) in mel.get(b, []):
        add(piano(m(n), 3.5, 1.0), t0 + beat, 0.2, 0.13)
    # pulsation très discrète (temps 1 et 3), seulement au cœur du morceau
    if 1 <= b < bars - 1:
        add(pulse(), t0, 0, 0.18); add(pulse(), t0 + 2, 0, 0.12)

mix = np.stack([L, R])
# petite réverbération (bruit à décroissance exponentielle)
ir_t = np.arange(int(1.8 * SR)) / SR
for c in range(2):
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.2)
    ir = lowpass(ir, 3000); ir /= np.abs(ir).sum() / 6
    mix[c] = 0.78 * mix[c] + 0.22 * fftconvolve(mix[c], ir)[:N]
mix = np.stack([lowpass(mix[0], 5000), lowpass(mix[1], 5000)])
fade = np.ones(N); fi = int(1.0 * SR); fo = int(3.0 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= fade
# niveau moyen visé ≈ −19 dB (RMS), crête plafonnée
rms = np.sqrt(np.mean(mix ** 2)); mix *= 10 ** (-19 / 20) / rms
mix = np.clip(mix, -0.95, 0.95)
pcm = (mix.T * 32767).astype(np.int16)
with wave.open('musique.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', D, 's')
