# Execute DAT on /project1/show: the clock. Runs the state machine once per frame.
def onFrameStart(frame):
    op.Show.op('logic').module.tick()
    return
