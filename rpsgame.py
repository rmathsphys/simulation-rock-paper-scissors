import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim


class RPSGame():
    def __init__(self, n_rock=9, n_paper=9, n_scissors=9, width=1):
        self.nr = n_rock
        self.np = n_paper
        self.ns = n_scissors
        self.nt = self.nr + self.np + self.ns
        self.w = width

        self._id_to_label = ['Rock', 'Paper', 'Scissors']
        
        self.threshold = 0.015
        self.hf = 0.0003
        self.ha = 0.0021
        self.ht = 0.0031
        self.fq = 1.15
        self.fc = '#1e1e1e'
        self.fr = '#0088aa'
        self.fp = '#d4aa00'
        self.fs = '#ff0066'
        self.frames = 1000

        self._re_init()


    def play(self):
        print('Running the simulation.')
        self._run_sim(export=False)
        print('Task completed.')

    def export(self, fname):
        print('Running the simulation.')
        print(f'The output will be saved to {fname}')
        self._run_sim(export=True, fname=fname)
        print('Task completed.')

    def set_hf(self, val):
        self.hf = val

    def set_ha(self, val):
        self.ha = val

    def set_ht(self, val):
        self.ht = val

    def set_frames(self, val):
        self.frames = val

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
        self._dm = np.array([np.sum((self.pos - self.pos[j])**2, axis=-1) for j in range(self.nt)])
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
                rf = rf / max(1e-18, np.sum(rf**2))
            else:
                rf = 0
            
            if np.any(self.cat == ((self.cat[j]+1)%3)):
                arr_a = self.pos[self.cat == ((self.cat[j]+1)%3)]
                dist_a = np.sum((arr_a - self.pos[j])**2, axis=-1)
                ra = arr_a[np.argmin(dist_a)] - self.pos[j]
                ra = ra / max(1e-18, np.sum(ra**2))
            else:
                ra = 0
            
            if np.any(self.cat == ((self.cat[j]+2)%3)):
                arr_t = self.pos[self.cat == ((self.cat[j]+2)%3)]
                dist_t = np.sum((arr_t - self.pos[j])**2, axis=-1)
                rt = arr_t[np.argmin(dist_t)] - self.pos[j]
                rt = rt / max(1e-18, np.sum(rt**2))
            else:
                rt = 0

            r = (self.ht * rt) - (self.ha * ra) - (self.hf * rf)
            self._temp_pos[j] = self.pos[j] + r

            self._temp_pos = np.where(self._temp_pos > self.w, self.w - 0.25*self.threshold, self._temp_pos)
            self._temp_pos = np.where(self._temp_pos < -self.w, 0.25*self.threshold - self.w, self._temp_pos)

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

    def _display_scene(self):
        ''' For debugging purposes only '''
        wq = self.fq * self.w
        ms = 50

        fig, ax = plt.subplots(figsize=(4.5, 4.7), facecolor=self.fc, num='The Arena', layout='constrained')
        ax.set(aspect=True, xlim=(-wq, wq), ylim=(-wq, wq))
        ax.axis(False)

        dt_r = self.pos[self.cat == 0]
        dt_p = self.pos[self.cat == 1]
        dt_s = self.pos[self.cat == 2]

        _ = ax.scatter(dt_r[:,0], dt_r[:,1], s=ms, marker=r'$R$', c=self.fr)
        _ = ax.scatter(dt_p[:,0], dt_p[:,1], s=ms, marker=r'$P$', c=self.fp)
        _ = ax.scatter(dt_s[:,0], dt_s[:,1], s=ms, marker=r'$S$', c=self.fs)

        msg = ''
        for j in range(3):
            msg += f'{self._id_to_label[j]}: {(self.cat == j).sum():>2}, '
        msg = msg[:-2]
        status = ax.text(0.5, 1, msg, ha='center', va='top', transform=ax.transAxes,
            fontsize=10, fontweight='medium', color='#e6e6e6')
        
        plt.show()
        self._re_init()

    def _run_sim(self, export=False, fname='output.mp4'):
        wq = self.fq * self.w
        ms = 50

        fig, ax = plt.subplots(figsize=(4.5, 4.7), facecolor=self.fc, num='The Arena', layout='constrained')
        ax.set(aspect=True, xlim=(-wq, wq), ylim=(-wq, wq))
        ax.axis(False)

        sc_r = ax.scatter([], [], s=ms, marker=r'$R$', c=self.fr)
        sc_p = ax.scatter([], [], s=ms, marker=r'$P$', c=self.fp)
        sc_s = ax.scatter([], [], s=ms, marker=r'$S$', c=self.fs)

        msg = ''
        for j in range(3):
            msg += f'{self._id_to_label[j]}: {(self.cat == j).sum()}, '
        msg = msg[:-2]
        status = ax.text(0.5, 1, msg, ha='center', va='top', transform=ax.transAxes,
            fontsize=10, fontweight='medium', color='#e6e6e6')
        
        def updater(k):
            if len(np.unique(self.cat)) == 1:
                status.set(text=f'The winner is: {self._id_to_label[int(self.cat[0])]}')
                return sc_r, sc_p, sc_s, status

            self.pos, self.cat = self._step_sim()
            
            dt_r = self.pos[self.cat == 0]
            dt_p = self.pos[self.cat == 1]
            dt_s = self.pos[self.cat == 2]
            
            sc_r.set_offsets(dt_r)
            sc_p.set_offsets(dt_p)
            sc_s.set_offsets(dt_s)

            msg = f''
            for j in range(3):
                msg += f'{self._id_to_label[j]}: {(self.cat == j).sum()}, '
            msg = msg[:-2]
            status.set(text=msg)

            return sc_r, sc_p, sc_s, status
        
        if export:
            ani = anim.FuncAnimation(fig, updater, frames=self.frames, interval=40, repeat=False, blit=False)
            writer = anim.FFMpegWriter(fps=30)
            ani.save(f'{fname}', dpi=256, writer=writer, savefig_kwargs={'facecolor':self.fc})
        else:
            ani = anim.FuncAnimation(fig, updater, frames=self.frames, interval=40, repeat=False, blit=False)
            plt.show()

        self._re_init()        
