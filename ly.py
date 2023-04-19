import re
from re import Match
from fractions import Fraction
noter = re.compile("(?P<name>[a-z,']*)(?P<durint>[0-9])(?P<durdots>[\.]*)(?P<tie>~?)")
barliner = re.compile("|")
def find_notes(string):
    notes = noter.finditer(string)
    notes = [n for n in notes if(len(n.group("name")) > 0)]
    return notes
def get_dur_as_frac(note: Match):
    i = int(note.group("durint"))
    dots = note.group("durdots")
    value = Fraction(i, 4)
    n_dots = len(dots)
    value_with_dots = value
    for d in range(0, n_dots):
        value_with_dots += Fraction(1, (d+1)*(i*2))
    return value_with_dots
