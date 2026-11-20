# CHOP Execute DAT on /project1/show/keyboard: computer keys.
#   Space = start the armed mode (Rehearse or Record) / stop.   Esc = stop.
#   R = arm Record, H = arm reHearse (arming doesn't start anything; Space does).
# Keys only arrive while a TouchDesigner window has focus. Use the TDlive window: in the network editor,
# Space also plays/pauses the timeline.
def L():
    return op.Show.op('logic').module


def onOffToOn(channel, sampleIndex, val, prev):
    n = channel.name
    if n.endswith('space'):
        L().toggle()
    elif n.endswith('esc'):
        L().stop()
    elif n.endswith('r') and L().state() == 'idle':
        op.Show.par.Armed = 'record'
    elif n.endswith('h') and L().state() == 'idle':
        op.Show.par.Armed = 'rehearse'
    return
