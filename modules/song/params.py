# Parameter Execute DAT on /project1/song.
def onValueChange(par, prev):
    if par.name == 'Chart':
        op.Song.op('setup').module.chart_changed()
    return


def onPulse(par):
    if par.name == 'Reloadcharts':
        op.Song.op('setup').module.refresh_menu()
    return
