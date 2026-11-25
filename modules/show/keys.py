# CHOP Execute DAT on /project1/show/keyboard: computer keys.
#   Space = start the armed mode (Rehearse or Record) / stop.   Esc = stop.
#   R = arm Record, H = arm reHearse (arming doesn't start anything; Space does).
#   End keys (show › Keys › End Keys, default 'e pagedown'): play the ending - this chorus becomes the last one
#   (the chart's endings replace the turnaround, the last chord rings a bar, then it stops). Again = cancel.
#   Most Bluetooth page-turner pedals send PageDown / arrow keys, so a pedal works as an End key.
# Keys only arrive while a TouchDesigner window has focus. Use the TDlive window: in the network editor,
# Space also plays/pauses the timeline.
def L():
    return op.Show.op('logic').module


def onOffToOn(channel, sampleIndex, val, prev):
    n = channel.name
    if n.endswith('space'):
        L().toggle()
        run("op('/').time.play = True", delayMilliSeconds=60)   # Space in the editor also pauses the timeline
    elif n.endswith('esc'):
        L().stop()
    elif any(n.endswith(k) for k in op.Show.par.Endkeys.eval().split()) and L().state() != 'idle':
        op.Song.op('engine').module.arm_ending()
    elif n.endswith('r') and L().state() == 'idle':
        op.Show.par.Armed = 'record'
    elif n.endswith('h') and L().state() == 'idle':
        op.Show.par.Armed = 'rehearse'
    return
