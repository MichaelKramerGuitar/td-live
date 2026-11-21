# Song setup helpers (Text DAT /project1/song/setup, synced to this file).
def refresh_menu():
    """Fill Song › Chart with the charts in charts/ that can be clocked."""
    E = op.Song.op('engine').module
    items = E.chart_menu()
    p = op.Song.par.Chart
    cur = p.eval()
    p.menuNames = ['none'] + [i for i, _ in items]
    p.menuLabels = ['(no chart)'] + [t for _, t in items]
    p.val = cur if cur in p.menuNames else ('blues_jazz' if 'blues_jazz' in p.menuNames else 'none')


def chart_changed(keep_key=False):
    """A new chart: key back to the chart's default, tempo to the chart's tempo."""
    E = op.Song.op('engine').module
    if not keep_key:
        op.Song.par.Key = 'default'
    if not E.active():
        return
    import os
    c = E.cl.load_chart(os.path.join(project.folder, 'charts', op.Song.par.Chart.eval() + '.yaml'))
    bpm = (c.get('tempo') or {}).get('bpm')
    if bpm:
        op.Song.par.Tempo = bpm
