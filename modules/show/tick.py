# Execute DAT on /project1/show: the clock. Runs the state machine once per frame,
# and opens the TDlive window when the project starts.
def onStart():
    run("op.Show.par.Openwindow.pulse()", delayFrames=30)
    return


def onFrameStart(frame):
    op.Show.op('logic').module.tick()
    return
