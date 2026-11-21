# Execute DAT on /project1/show: the clock. Runs the state machine once per frame,
# and opens the TDlive window when the project starts.
def onStart():
    op('/').time.play = True                                  # the rig needs the timeline running
    op.Show.op('logic').module.later(lambda: op.Show.par.Openwindow.pulse(), 30)
    op.Show.op('logic').module.later(lambda: op.Show.op('playback').module.retry_deletes(), 60)   # last session
    return


def onFrameStart(frame):
    op.Show.op('logic').module.tick()
    return
