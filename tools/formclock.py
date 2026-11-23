"""Form clock: where in the tune are we?  Pure Python, shared by TD and the tests.

    import formclock as fc
    song = fc.Song(chart, key='F', bpm=120)
    now = song.at(seconds_since_bar_1)      # -> Position(chorus, section, pass_, bar_in_section, bar, beat, chord, next_chord ...)

Time 0 is the downbeat of bar 1 (the end of the count-off). The form loops: chorus 1, 2, 3 ...
Negative time = still counting off (Position.counting_in, beats_left).
"""
import math
from dataclasses import dataclass

try:
    from . import chartlib as cl, harmony as h  # noqa: F401
except ImportError:
    import chartlib as cl
    import harmony as h


@dataclass
class Position:
    counting_in: bool
    beats_left: int           # count-off beats still to come (0 when playing)
    chorus: int               # 1-based
    section: str
    pass_: int                # 1-based pass through a repeated section
    bar_in_section: int       # 1-based
    bar: int                  # 1-based bar within the chorus
    beat: int                 # 1-based beat within the bar
    beat_phase: float         # 0..1 through the current beat
    bar_phase: float          # 0..1 through the current bar
    chord: object             # harmony.Chord sounding now
    chord_beats_left: float   # beats until the next chord
    next_chord: object        # harmony.Chord coming next
    chord_index: int          # increments on every chord change (handy for triggers)


class Song:
    def __init__(self, chart, key=None, bpm=None):
        self.chart = chart
        self.key = key or chart.get('default_key') or 'C'
        self.bpm = float(bpm or (chart.get('tempo') or {}).get('bpm') or 120)
        self.beats_per_bar = chart['rhythm']['meter']['beats']
        changes = h.realize(chart, self.key)
        if not changes:
            raise ValueError('%s has no changes yet (status: %s)' % (chart.get('id'), chart.get('status')))
        # Flatten the form into a list of chord events: (start beat, beats, chord, section, pass, bar_in_sec, bar)
        self.events = []
        beat = 0.0
        bar = 0
        for section, pass_, nbars in cl.form_plan(chart):
            sec_bars = changes[section]
            for b in range(nbars):
                bar += 1
                for ch, beats in sec_bars[b]:
                    self.events.append((beat, float(beats), ch, section, pass_, b + 1, bar))
                    beat += beats
        self.chorus_beats = beat
        self.chorus_bars = bar
        # Sections as played, for "where are we in the form": [(first bar, bars, section name), ...]
        self.spans = []
        start = 1
        for section, pass_, nbars in cl.form_plan(chart):
            self.spans.append((start, nbars, section))
            start += nbars

    def span_at(self, bar):
        """(index, first bar, bars, name) of the section containing chorus bar `bar`."""
        for i, (start, n, name) in enumerate(self.spans):
            if start <= bar < start + n:
                return i, start, n, name
        return 0, 1, self.spans[0][1], self.spans[0][2]

    @property
    def sec_per_beat(self):
        return 60.0 / self.bpm

    def count_in_seconds(self, bars=1):
        return bars * self.beats_per_bar * self.sec_per_beat

    def at(self, seconds):
        beats_total = seconds / self.sec_per_beat
        if beats_total < 0:
            first = self.events[0]
            return Position(True, int(math.ceil(-beats_total)), 0, first[3], 1, 1, 1, 0, 0.0, 0.0,
                            None, -beats_total, first[2], -1)
        chorus = int(beats_total // self.chorus_beats)
        b = beats_total - chorus * self.chorus_beats
        # find the event containing b (events are few; linear is fine and clear)
        idx = 0
        for i, ev in enumerate(self.events):
            if ev[0] <= b:
                idx = i
            else:
                break
        start, dur, ch, section, pass_, bis, bar = self.events[idx]
        nxt = self.events[(idx + 1) % len(self.events)][2]
        in_bar = b - (bar - 1) * self.beats_per_bar
        return Position(False, 0, chorus + 1, section, pass_, bis, bar, int(in_bar) + 1, in_bar % 1.0,
                        in_bar / self.beats_per_bar, ch, start + dur - b, nxt,
                        chorus * len(self.events) + idx)
