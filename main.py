import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim

rng = np.random.default_rng()
target = [2, 0, 1] # 0: rock, 1: paper, 2: scissors

N = 10 # number of players in each team
smax = 1 # controls the size of the field (FUTURE: expand to other shapes)
dmin = 0.015 # distance threshold to register a hit

d = lambda x1, y1, x2, y2: (x1-x2)**2 + (y1-y2)**2

def step_attack(h=0.05):
    pos_new = 0*pos
    
    for i in range(3*N):
        x1, y1 = pos[i, :]
        c = cat[i]
        t = target[c]
        d0_a = 10*smax
        d0_r = 10*smax
        val_a = i
        val_r = i
        for j in range(3*N):
            if cat[j] == t:
                x2, y2 = pos[j, :]
                dist = d(x1, y1, x2, y2)
                if dist <= d0_a:
                    d0_a = dist
                    val_a = j
            elif cat[j] != c:
                x2, y2 = pos[j, :]
                dist = d(x1, y1, x2, y2)
                if dist <= d0_r:
                    d0_r = dist
                    val_r = j
        
        v_a = pos[val_a, :] - pos[i, :]
        u_a = np.sqrt(np.sum(v_a * v_a))
        w_a = v_a/u_a if u_a > 1e-4 else v_a/1e-4
        v_r = pos[val_r, :] - pos[i, :]
        u_r = np.sqrt(np.sum(v_r * v_r))
        w_r = v_r/u_r if u_r > 1e-4 else v_r/1e-4
        
        di = (h*(w_a + (-0.8*w_r)))
        rn = rng.normal(0,0.01/3, size=2)
        prop = pos[i, :] + di + rn
        if abs(prop[0]) > smax: prop[0] = x1
        if abs(prop[1]) > smax: prop[1] = y1
        pos_new[i, :] = prop        
    
    for i in range(3*N):
        x1, y1 = pos_new[i, :]
        t = target[cat[i]]
        for j in range(3*N):
            if cat[j] == t:
                x2, y2 = pos_new[j, :]
                dist = d(x1, y1, x2, y2)
                if dist <= dmin:
                    cat[j] = cat[i]
    pos[:,:] = pos_new[:,:]


pos = rng.uniform(low=-smax, high=smax, size=(3*N, 2))
cat = np.array([i//N for i in range(3*N)])
rng.shuffle(cat)

q = 1.15
fc = '#f5fffa'
fig, ax = plt.subplots(figsize=(4.5,4.5), facecolor=fc)
ax.set(aspect=True, xlim=(-smax*q,smax*q), ylim=(-smax*q,smax*q))
ax.axis(False)

sc_r = ax.scatter([], [], s=50, marker=r'$R$', c='#002e63')
sc_p = ax.scatter([], [], s=50, marker=r'$P$', c='#ffa700')
sc_s = ax.scatter([], [], s=50, marker=r'$S$', c='#ae0c00')

def updater(k):
    step_attack(0.0085)
    
    x = pos[:,0]
    y = pos[:,1]

    u_r = np.c_[[x[k] for k in range(3*N) if cat[k]==0], [y[k] for k in range(3*N) if cat[k]==0]]
    u_p = np.c_[[x[k] for k in range(3*N) if cat[k]==1], [y[k] for k in range(3*N) if cat[k]==1]]
    u_s = np.c_[[x[k] for k in range(3*N) if cat[k]==2], [y[k] for k in range(3*N) if cat[k]==2]]
        
    sc_r.set_offsets(u_r)
    sc_p.set_offsets(u_p)
    sc_s.set_offsets(u_s)
    return sc_r, sc_p, sc_s

def gen_func():
    while True:
        if len(np.unique(cat)) > 1: yield 0
        
ani = anim.FuncAnimation(fig, updater, gen_func(), interval=30, repeat=False)

# ani = anim.FuncAnimation(fig, updater, 800, interval=30, repeat=False)
# writer = anim.FFMpegWriter(fps=35)
# ani.save('output.mp4', dpi=256, writer=writer, savefig_kwargs={'facecolor':fc})

plt.show()