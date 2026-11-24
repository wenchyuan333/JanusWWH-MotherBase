import math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

OUT = os.path.expanduser("~/storage/pictures/")
os.makedirs(OUT, exist_ok=True)

def gamma(v): return 1.0 / math.sqrt(max(1e-9, 1 - v*v))
def rapidity(v): return math.atanh(max(-0.9999, min(0.9999, abs(v))))

# ═══════════════════════════════════════════════════════════════
# GIF 1  first_person.gif
# ═══════════════════════════════════════════════════════════════
N1=96; DT1=12.0/N1; V_MAX=0.95

def v_sched(f):
    t=f/N1
    if t<0.4: return V_MAX*t/0.4
    if t<0.6: return V_MAX
    return V_MAX*(1-(t-0.6)/0.4)

fig1,axes1=plt.subplots(1,3,figsize=(13,4.2))
fig1.patch.set_facecolor("#080818")

axA=axes1[0]; axA.set_facecolor("#080818")
axA.set_xlim(-2.6,2.6); axA.set_ylim(-2.6,2.6); axA.set_aspect("equal")
axA.set_title("Metric (coordinate view)\nLorentz distortion of unit sphere",color="white",fontsize=8.5)
for sp in axA.spines.values(): sp.set_edgecolor("#222")
axA.tick_params(colors="#444"); axA.axhline(0,color="#222",lw=.5); axA.axvline(0,color="#222",lw=.5)
axA.text(2.2,.1,"x",color="#555",fontsize=8); axA.text(.1,2.2,"ct",color="#555",fontsize=8)
axA.add_patch(plt.Circle((0,0),1,color="#333",fill=False,lw=1,ls="--"))
axA.text(-2.4,2.2,"proper frame: always unit circle",color="#666",fontsize=7)
mell=patches.Ellipse((0,0),2,2,color="#2255ff",fill=False,lw=2.5)
axA.add_patch(mell)
varr=axA.annotate("",xy=(.8,0),xytext=(0,0),
    arrowprops=dict(arrowstyle="->",color="#ff5522",lw=2.5))
mlbl=axA.text(-2.4,-2.4,"v=0.00c  g=1.000",color="#aaa",fontsize=8)

axB=axes1[1]; axB.set_facecolor("#080818")
axB.set_xlim(-1.6,1.6); axB.set_ylim(-1.6,1.6); axB.set_aspect("equal")
axB.set_title("Order parameter psi=exp(i*tau)\nU(1) phase of proper time",color="white",fontsize=8.5)
for sp in axB.spines.values(): sp.set_edgecolor("#222")
axB.tick_params(colors="#444"); axB.axhline(0,color="#222",lw=.5); axB.axvline(0,color="#222",lw=.5)
axB.add_patch(plt.Circle((0,0),1,color="#333",fill=False,lw=1.5))
axB.text(0,1.3,"Im",color="#555",fontsize=7,ha="center")
axB.text(1.4,0,"Re",color="#555",fontsize=7,va="center")
odA,=axB.plot([1],[0],"o",color="#2255ff",ms=11,label="A rest",zorder=5)
odB,=axB.plot([1],[0],"o",color="#ff3322",ms=11,label="B moving",zorder=5)
otA,=axB.plot([],[],"-",color="#2255ff",lw=1.2,alpha=0.5)
otB,=axB.plot([],[],"-",color="#ff3322",lw=1.2,alpha=0.5)
axB.legend(loc="lower right",fontsize=7.5,facecolor="#111",labelcolor="white")
oblbl=axB.text(-1.5,-1.45,"tA=0.00  tB=0.00  D=0.00",color="#aaa",fontsize=7.5)

axC=axes1[2]; axC.set_facecolor("#080818")
axC.set_xlim(-0.02,1.0); axC.set_ylim(-0.1,3.2)
axC.set_title("Gauge field: rapidity eta=arctanh(v)\n(additive under boosts, like a U(1) potential)",color="white",fontsize=8.5)
axC.set_xlabel("v/c",color="#aaa",fontsize=8); axC.set_ylabel("eta",color="#aaa",fontsize=8)
for sp in axC.spines.values(): sp.set_edgecolor("#222")
axC.tick_params(colors="#444")
vr=[i*0.01 for i in range(100)]
axC.plot(vr,[math.atanh(v) for v in vr],color="#444",lw=1.5,ls="--")
axC.text(0.62,2.7,"eta=arctanh(v)",color="#555",fontsize=7)
gdot,=axC.plot([0],[0],"o",color="#ffaa22",ms=12,zorder=5)
gline=axC.axhline(0,color="#ffaa22",lw=1,alpha=0.4)
glbl=axC.text(0.04,2.85,"eta=0.000",color="#ffaa22",fontsize=8)

tauA=0.0; tauB=0.0
trAx=[]; trAy=[]; trBx=[]; trBy=[]; TRAIL=25

def upd1(f):
    global tauA,tauB
    v=v_sched(f); g=gamma(v); eta=rapidity(v)
    tauA+=DT1; tauB+=DT1/g
    phA=2*math.pi*(tauA%1.0); cA,sA=math.cos(phA),math.sin(phA)
    trAx.append(cA); trAy.append(sA)
    if len(trAx)>TRAIL: trAx.pop(0); trAy.pop(0)
    phB=2*math.pi*(tauB%1.0); cB,sB=math.cos(phB),math.sin(phB)
    trBx.append(cB); trBy.append(sB)
    if len(trBx)>TRAIL: trBx.pop(0); trBy.pop(0)
    odA.set_data([cA],[sA]); odB.set_data([cB],[sB])
    otA.set_data(trAx,trAy); otB.set_data(trBx,trBy)
    oblbl.set_text(f"tA={tauA:.2f}  tB={tauB:.2f}  D={tauA-tauB:.2f}")
    mell.set_width(2.0/g); mell.set_height(2.0*g)
    mell.set_edgecolor(plt.cm.plasma(v/V_MAX))
    vx=min(v*2.2,2.2); varr.xy=(vx,0)
    mlbl.set_text(f"v={v:.2f}c  g={g:.3f}")
    gdot.set_data([v],[eta]); gline.set_ydata([eta,eta])
    glbl.set_text(f"eta={eta:.3f}")
    return [mell,varr,mlbl,odA,odB,otA,otB,oblbl,gdot,gline,glbl]

ani1=animation.FuncAnimation(fig1,upd1,frames=N1,interval=70,blit=False)
fig1.suptitle("First-person: metric / order-parameter / gauge field",
              color="white",fontsize=10,y=1.01)
fig1.tight_layout(pad=0.4)
ani1.save(OUT+"first_person.gif",writer=animation.PillowWriter(fps=13))
plt.close(fig1)
print("saved first_person.gif")

# ═══════════════════════════════════════════════════════════════
# GIF 2  twin_diverge.gif
# ═══════════════════════════════════════════════════════════════
N2=90; T_MAX=10.0; V_B=0.80; G_B=gamma(V_B)

fig2,ax2=plt.subplots(1,3,figsize=(13,4.8))
fig2.patch.set_facecolor("#080818")

axW=ax2[0]; axW.set_facecolor("#080818")
axW.set_xlim(-0.5,9); axW.set_ylim(-0.5,T_MAX+.5)
axW.set_xlabel("x",color="#aaa"); axW.set_ylabel("T (coordinate)",color="#aaa")
axW.set_title("Spacetime worldlines\n(third-person frame)",color="white",fontsize=9)
for sp in axW.spines.values(): sp.set_edgecolor("#222")
axW.tick_params(colors="#444")
axW.plot([0,T_MAX],[0,T_MAX],color="#333",lw=.8,ls=":",label="light")
wlA,=axW.plot([0,0],[0,0],color="#2255ff",lw=2.5,label="A (rest)")
wlB,=axW.plot([0],[0],color="#ff3322",lw=2.5,label=f"B (v={V_B}c)")
nowL=axW.axhline(0,color="white",lw=.7,ls="--",alpha=0.4)
dA,=axW.plot([0],[0],"o",color="#2255ff",ms=9,zorder=5)
dB,=axW.plot([0],[0],"o",color="#ff3322",ms=9,zorder=5)
axW.legend(loc="upper left",fontsize=8,facecolor="#111",labelcolor="white")
Tlbl=axW.text(0.2,T_MAX+.1,"T=0.00",color="white",fontsize=9)

axB2=ax2[1]; axB2.set_facecolor("#080818")
axB2.set_xlim(-.6,1.6); axB2.set_ylim(0,T_MAX+.8)
axB2.set_title("Proper time (internal clock)\nsame T, different tau",color="white",fontsize=9)
axB2.set_xticks([0,1]); axB2.set_xticklabels(["A (rest)",f"B ({V_B}c)"],color="white",fontsize=9)
for sp in axB2.spines.values(): sp.set_edgecolor("#222")
axB2.tick_params(colors="#444"); axB2.axhline(0,color="#333",lw=.5)
barA=axB2.bar([0],[0],width=0.6,color="#2255ff",alpha=0.85)
barB=axB2.bar([1],[0],width=0.6,color="#ff3322",alpha=0.85)
lblA=axB2.text(0,.3,"0.00",ha="center",color="white",fontsize=10,fontweight="bold")
lblB=axB2.text(1,.3,"0.00",ha="center",color="white",fontsize=10,fontweight="bold")
coordLbl=axB2.text(.5,T_MAX+.4,"T=0.00",ha="center",color="#aaa",fontsize=9)

axGap=ax2[2]; axGap.set_facecolor("#080818")
GAP_MAX=T_MAX*(1-1/G_B)+.3
axGap.set_xlim(0,T_MAX); axGap.set_ylim(-0.05,GAP_MAX)
axGap.set_xlabel("coordinate time T",color="#aaa")
axGap.set_ylabel("tau_A - tau_B",color="#aaa",fontsize=8.5)
axGap.set_title(f"Accumulating time gap\n(v_B={V_B}c, gamma={G_B:.3f})",color="white",fontsize=9)
for sp in axGap.spines.values(): sp.set_edgecolor("#222")
axGap.tick_params(colors="#444")
T_ref=[i*.1 for i in range(101)]
axGap.plot(T_ref,[(t-t/G_B) for t in T_ref],color="#444",lw=1.2,ls="--")
gapL,=axGap.plot([],[],color="#ffaa22",lw=2.5)
gapD,=axGap.plot([],[],"o",color="#ffaa22",ms=8)
gapTxt=axGap.text(.5,.05,"gap=0.000",color="#ffaa22",fontsize=9)

ghT=[]; ghG=[]

def upd2(f):
    T=(f+1)/N2*T_MAX
    tA=T; tB=T/G_B; xB=V_B*T
    wlA.set_data([0,0],[0,T]); wlB.set_data([0,xB],[0,T])
    nowL.set_ydata([T,T]); dA.set_data([0],[T]); dB.set_data([xB],[T])
    Tlbl.set_text(f"T={T:.2f}")
    barA[0].set_height(tA); barB[0].set_height(tB)
    lblA.set_text(f"{tA:.2f}"); lblA.set_y(tA+.15)
    lblB.set_text(f"{tB:.2f}"); lblB.set_y(tB+.15)
    coordLbl.set_text(f"T={T:.2f}")
    gap=tA-tB; ghT.append(T); ghG.append(gap)
    gapL.set_data(ghT,ghG); gapD.set_data([T],[gap])
    gapTxt.set_text(f"gap={gap:.3f}"); gapTxt.set_position((.4,gap+.05))
    return [wlA,wlB,nowL,dA,dB,Tlbl,
            barA[0],barB[0],lblA,lblB,coordLbl,
            gapL,gapD,gapTxt]

ani2=animation.FuncAnimation(fig2,upd2,frames=N2,interval=65,blit=False)
fig2.suptitle(f"Twin separation: A stays, B moves at v={V_B}c",
              color="white",fontsize=10,y=1.01)
fig2.tight_layout(pad=0.4)
ani2.save(OUT+"twin_diverge.gif",writer=animation.PillowWriter(fps=14))
plt.close(fig2)
print("saved twin_diverge.gif")

os.system(f"termux-media-scan {OUT}first_person.gif")
os.system(f"termux-media-scan {OUT}twin_diverge.gif")
print("all done.")
