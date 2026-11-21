# Parameter Execute DAT on /project1/config.
def onPulse(par):
    if par.name == 'Findinput':
        op.Sources.op('findinput').module.start()
    return
