# Panel Execute DAT on the TDlive window's buttons. Each button is a small Container COMP;
# its name says what it does.
def L():
    return op.Show.op('logic').module


def onOffToOn(panelValue):
    name = panelValue.owner.name
    S = op.Show
    if name == 'btn_rehearse':
        L().stop() if L().state() != 'idle' else L().start('rehearse')
    elif name == 'btn_record':
        L().stop() if L().state() != 'idle' else L().start('record')
    elif name == 'btn_mode':
        S.par.Mode.menuIndex = (S.par.Mode.menuIndex + 1) % len(S.par.Mode.menuNames)
    elif name == 'btn_camera':
        S.par.Camerainshot = not S.par.Camerainshot.eval()
    elif name == 'btn_format' and L().state() == 'idle':   # never change size mid-take
        C = op.Config
        C.par.Preset.menuIndex = (C.par.Preset.menuIndex + 1) % len(C.par.Preset.menuNames)
    return
