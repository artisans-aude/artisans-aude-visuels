import numpy as np, wave
from scipy.signal import butter, sosfilt
w=wave.open('src.wav'); sr=w.getframerate()
a=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,2)/32768
bar=60/104*4; D=42.0; t0=41.69
cuts=[(t0,t0+3*bar),(78.61+bar,78.61+8*bar),(152.45+2*bar,None)]
parts=[]
for s,e in cuts:
    if e is None: e=s+D-sum(len(p) for p in parts)/sr+0.2
    parts.append(a[int(s*sr):int(e*sr)])
xf=int(0.05*sr); out=parts[0]
for p in parts[1:]:
    r=np.linspace(0,1,xf)[:,None]
    out=np.concatenate([out[:-xf], out[-xf:]*(1-r)+p[:xf]*r, p[xf:]])
N=int(D*sr); out=out[:N].copy()
fade=np.ones(N); fi=int(0.6*sr); fo=int(2.5*sr)
fade[:fi]=np.linspace(0,1,fi); fade[-fo:]=np.linspace(1,0,fo)**1.5
out*=fade[:,None]
out*=10**(-19/20)/np.sqrt(np.mean(out**2)); out=np.clip(out,-0.98,0.98)
with wave.open('musique.wav','wb') as o:
    o.setnchannels(2);o.setsampwidth(2);o.setframerate(sr);o.writeframes((out*32767).astype(np.int16).tobytes())
m=out.mean(1); lo=sosfilt(butter(4,120,'low',fs=sr,output='sos'),m)
print('graves/2s',[round(20*np.log10(np.sqrt(np.mean(lo[i:i+2*sr]**2))+1e-9)) for i in range(0,N,2*sr)])
print('jonctions',[round(x,2) for x in np.cumsum([len(p)/sr for p in parts])[:2]], 'fin source', cuts[2][0]+D-sum(len(p) for p in parts[:2])/sr)
