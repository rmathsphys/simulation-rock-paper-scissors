from rpsgame import RPSGame        

model = RPSGame(n_rock=5, n_paper=5, n_scissors=5, width=1)
model.play()
model.set_frames(100)
model.set_hf(0.005)
model.set_ha(0.02)
model.set_ht(0.03)
model.play()
# model.export('new.mp4')
