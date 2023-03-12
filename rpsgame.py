import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim


class RPSGame():
    def __init__(self, n_rock=10, n_paper=10, n_scissors=10, width=1):
        self.nr = n_rock
        self.np = n_paper
        self.ns = n_scissors
        self.nt = self.nr + self.np + self.ns
        self.w = width
        
        self.threshold = 0.015
        self.hf = 0.0005
        self.ha = 0.002
        self.ht = 0.003
        self.fq = 1.15
        self.fc = '#f5fffa'
        self.fr = '#002e63'
        self.fp = '#ffa700'
        self.fs = '#ae0c00'

        self._re_init()

    def _re_init(self):
        while True:
            self.rng = np.random.default_rng()
            self.pos = self.rng.uniform(-self.w, self.w, (self.nt, 2))
            self.cat = np.concatenate((0+np.zeros(self.nr),
                1+np.zeros(self.np),
                2+np.zeros(self.ns)))
            self.rng.shuffle(self.cat)
            if not self._warm_up_check():
                break

    def _warm_up_check(self):
        ''' Initial repelling and error handling to make sure
        that no two elements are 'too' close to each other '''
        self._dm = np.array(
            [np.sum((self.pos - self.pos[j])**2, axis=-1) for j in range(self.nt)]
            )
        return np.any(np.less(self._dm[self._dm>0], 1.2*self.threshold))

    def _step_sim(self):
        self._temp_pos = np.zeros_like(self.pos)
        self._temp_cat = np.zeros_like(self.cat)

        for j in range(self.nt):
            if np.any(self.cat == ((self.cat[j]+0)%3)):
                arr_f = self.pos[self.cat == ((self.cat[j]+0)%3)]
                dist_f = np.sum((arr_f - self.pos[j])**2, axis=-1)
                dist_f = np.where(dist_f == 0, np.max(dist_f)+1, dist_f)
                rf = arr_f[np.argmin(dist_f)] - self.pos[j]
                rf = rf / max(1e-8, np.sum(rf**2))
            else:
                rf = 0
            
            if np.any(self.cat == ((self.cat[j]+1)%3)):
                arr_a = self.pos[self.cat == ((self.cat[j]+1)%3)]
                dist_a = np.sum((arr_a - self.pos[j])**2, axis=-1)
                ra = arr_a[np.argmin(dist_a)] - self.pos[j]
                ra = ra / max(1e-8, np.sum(ra**2))
            else:
                ra = 0
            
            if np.any(self.cat == ((self.cat[j]+2)%3)):
                arr_t = self.pos[self.cat == ((self.cat[j]+2)%3)]
                dist_t = np.sum((arr_t - self.pos[j])**2, axis=-1)
                rt = arr_t[np.argmin(dist_t)] - self.pos[j]
                rt = rt / max(1e-8, np.sum(rt**2))
            else:
                rt = 0

            r = (self.ht * rt) - (self.ha * ra) - (self.hf * rf)
            self._temp_pos[j] = self.pos[j] + r

            if self._temp_pos[j,0] > self.w: self._temp_pos[j,0] = (self.w + 0.5*self.threshold)
            if self._temp_pos[j,0] < -self.w: self._temp_pos[j,0] = -(self.w + 0.5*self.threshold)
            if self._temp_pos[j,1] > self.w: self._temp_pos[j,1] = (self.w + 0.5*self.threshold)
            if self._temp_pos[j,1] < -self.w: self._temp_pos[j,1] = -(self.w + 0.5*self.threshold)

            # CAN GO OUT OF THE SCREEN. NEEDS TO BE FIXED!

        
        for j in range(self.nt):
            if np.any(self.cat == ((self.cat[j]+1)%3)):
                arr_a = self.pos[self.cat == ((self.cat[j]+1)%3)]
                dist_a = np.sum((arr_a - self.pos[j])**2, axis=-1)
                if np.min(dist_a) < self.threshold:
                    self._temp_cat[j] = ((self.cat[j]+1)%3)
                else:
                    self._temp_cat[j] = self.cat[j]
            else:
                self._temp_cat[j] = self.cat[j]

        return self._temp_pos, self._temp_cat

    def _display_scene(self, pos_dt, cat_dt):
        wq = self.fq * self.w
        ms = 50

        _, ax = plt.subplots(figsize=(4.5, 4.5), facecolor=self.fc, num='The Arena')
        ax.set(aspect=True, xlim=(-wq, wq), ylim=(-wq, wq))
        ax.axis(False)

        _ = ax.scatter(pos_dt[cat_dt == 0][:,0], pos_dt[cat_dt == 0][:,1],
            s=ms, marker=r'$R$', c=self.fr)
        _ = ax.scatter(pos_dt[cat_dt == 1][:,0], pos_dt[cat_dt == 1][:,1],
            s=ms, marker=r'$P$', c=self.fp)
        _ = ax.scatter(pos_dt[cat_dt == 2][:,0], pos_dt[cat_dt == 2][:,1],
            s=ms, marker=r'$S$', c=self.fs)

        plt.show()

    def _run_sim(self, export=False, fname='output.mp4'):
        wq = self.fq * self.w
        ms = 50

        fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor=self.fc, num='The Arena')
        ax.set(aspect=True, xlim=(-wq, wq), ylim=(-wq, wq))
        ax.axis(False)

        sc_r = ax.scatter([], [], s=ms, marker=r'$R$', c=self.fr)
        sc_p = ax.scatter([], [], s=ms, marker=r'$P$', c=self.fp)
        sc_s = ax.scatter([], [], s=ms, marker=r'$S$', c=self.fs)
        # status = ax.text(0, self.w, 'Status', ha='center')
        
        def updater(k):
            if len(np.unique(self.cat)) == 1:
                # status.set(text=f'The winner is: {self.cat[0]}')
                return sc_r, sc_p, sc_s#, status

            self.pos, self.cat = self._step_sim()
            
            dt_r = self.pos[self.cat == 0]
            dt_p = self.pos[self.cat == 1]
            dt_s = self.pos[self.cat == 2]
            
            sc_r.set_offsets(dt_r)
            sc_p.set_offsets(dt_p)
            sc_s.set_offsets(dt_s)

            return sc_r, sc_p, sc_s
        
        if export:
            ani = anim.FuncAnimation(fig, updater, frames=1000, interval=30, repeat=False, blit=True)
            writer = anim.FFMpegWriter(fps=35)
            ani.save(f'{fname}', dpi=256, writer=writer, savefig_kwargs={'facecolor':self.fc})
        else:
            ani = anim.FuncAnimation(fig, updater, frames=1000, interval=30, repeat=False, blit=True)

        plt.show()
        self._re_init()

    def play(self):
        self._run_sim(export=False)

    def export(self, fname):
        print('Running the simulation.')
        print(f'The output will be saved to {fname}')
        self._run_sim(export=True, fname=fname)
        print('Task completed.')
        
