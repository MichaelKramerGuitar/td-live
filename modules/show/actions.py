# Parameter Execute DAT on /project1/show: the custom parameters' pulses.
def L():
    return op.Show.op('logic').module


def onPulse(par):
    n = par.name
    if n == 'Rehearse':
        L().start('rehearse')
    elif n == 'Record':
        L().start('record')
    elif n == 'Stop':
        L().stop()
    elif n == 'Openwindow':
        op.Show.op('window').par.winopen.pulse()
    elif n == 'Closewindow':
        op.Show.op('window').par.winclose.pulse()
    return
