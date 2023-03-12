from rpsgame import RPSGame        

model = RPSGame(n_rock=5, n_paper=5, n_scissors=5, width=1)
# model.play()

model.set_frames(300)
model.set_hf(0.0005)
model.set_ha(0.002)
model.set_ht(0.003)
model.play()

# model.export('new.mp4')
