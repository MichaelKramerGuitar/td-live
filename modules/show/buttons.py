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
    elif name == 'btn_chart' and L().state() == 'idle':
        p = op.Song.par.Chart
        p.menuIndex = (p.menuIndex + 1) % len(p.menuNames)
        op.Song.op('setup').module.chart_changed()
    elif name == 'btn_key' and L().state() == 'idle':
        p = op.Song.par.Key
        p.menuIndex = (p.menuIndex + 1) % len(p.menuNames)
    elif name == 'btn_meter' and L().state() == 'idle':
        p = op.Song.par.Meter
        p.menuIndex = (p.menuIndex + 1) % len(p.menuNames)
    elif name == 'btn_tempo_down' and L().state() == 'idle':
        op.Song.par.Tempo = max(30, op.Song.par.Tempo.eval() - 2)
    elif name == 'btn_tempo_up' and L().state() == 'idle':
        op.Song.par.Tempo = min(400, op.Song.par.Tempo.eval() + 2)
    elif name == 'btn_tempo' and L().state() == 'idle':     # back to the chart's tempo
        op.Song.op('setup').module.chart_changed(keep_key=True)
    elif name == 'btn_me':                          # background styles, then corner tiles
        L_ = op.Visuals.op('landscape')
        combos = [('outline', 'background'), ('ghost', 'background'), ('negative', 'background'),
                  ('outline', 'top_left'), ('outline', 'top_right'), ('outline', 'bottom_left'),
                  ('outline', 'bottom_right')]                  # tiles use the outline look (Tile Look: styled)
        cur = (L_.par.Mestyle.eval(), L_.par.Meplace.eval())
        if cur[1] != 'background':
            cur = ('outline', cur[1])
        i = (combos.index(cur) + 1) % len(combos) if cur in combos else 0
        L_.par.Mestyle, L_.par.Meplace = combos[i]
    elif name in ('btn_clickv', 'btn_clicka'):        # toggle the visual / audio click (the window follows)
        S = op.Show
        v = S.par.Click.eval() in ('visual', 'both')
        a = S.par.Click.eval() in ('audio', 'both')
        if name == 'btn_clickv':
            v = not v
        else:
            a = not a
        S.par.Click = {(0, 0): 'off', (1, 0): 'visual', (0, 1): 'audio', (1, 1): 'both'}[(int(v), int(a))]
        win = op.Click.op('window')
        if name == 'btn_clickv':
            (win.par.winopen if v else win.par.winclose).pulse()
    elif name in ('btn_ncaption', 'btn_nmap', 'btn_nnames'):     # Notation mode toggles
        N = op.Visuals.op('notation')
        par = {'btn_ncaption': N.par.Labels, 'btn_nmap': N.par.Allchords, 'btn_nnames': N.par.Names}[name]
        par.val = not par.eval()
    elif name in ('btn_ggrid', 'btn_gtether', 'btn_gnames', 'btn_gcaption'):     # Harmony Galaxy toggles
        G = op.Visuals.op('galaxy')
        par = {'btn_ggrid': G.par.Grid, 'btn_gtether': G.par.Tether, 'btn_gnames': G.par.Names,
               'btn_gcaption': G.par.Labels}[name]
        par.val = not par.eval()
    elif name == 'btn_gprot':
        G = op.Visuals.op('galaxy')
        G.par.Protagonist = 'comet' if G.par.Protagonist == 'whisp' else 'whisp'
    elif name == 'btn_gview':
        G = op.Visuals.op('galaxy')
        names = list(G.par.View.menuNames)
        G.par.View = names[(names.index(G.par.View.eval()) + 1) % len(names)]
    elif name == 'btn_ndo':
        N = op.Visuals.op('notation')
        N.par.Do = 'fixed' if N.par.Do == 'movable' else 'movable'
    elif name == 'btn_nphrasing':
        N = op.Visuals.op('notation')
        names = list(N.par.Phrasing.menuNames)
        N.par.Phrasing = names[(names.index(N.par.Phrasing.eval()) + 1) % len(names)]
    elif name == 'btn_clickevery':
        S = op.Show
        names = list(S.par.Clickevery.menuNames)
        S.par.Clickevery = names[(names.index(S.par.Clickevery.eval()) + 1) % len(names)]
    elif name == 'btn_export' and L().state() == 'idle':
        op.Show.op('export').module.export_selected()
    elif name == 'btn_take' and L().state() == 'idle':
        op.Show.op('playback').module.select_next()
    elif name == 'btn_delete' and L().state() == 'idle':
        op.Show.op('playback').module.delete_selected()
    elif name == 'btn_play' and L().state() == 'idle':
        op.Show.op('playback').module.toggle()
    elif name == 'btn_format' and L().state() == 'idle':   # never change size mid-take
        C = op.Config
        C.par.Preset.menuIndex = (C.par.Preset.menuIndex + 1) % len(C.par.Preset.menuNames)
    return
