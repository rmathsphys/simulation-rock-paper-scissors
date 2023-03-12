from rpsgame import RPSGame        

model = RPSGame(n_rock=8, n_paper=8, n_scissors=8)

# Option settings: (the default values are shown here)
# model.set_frames(1000) # Tweak this if the animation ends too quickly
# model.set_hf(0.0003)
# model.set_ha(0.0021)
# model.set_ht(0.0030)

# model.play() # Live display

# The arena is automatically reset to a new random configuration
# before simulating again

model.export('out-02k.mp4') # Export to a file


