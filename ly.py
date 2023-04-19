import re
from re import Match
from fractions import Fraction
import subprocess
import os
noter = re.compile("(?P<name>[a-z,']*)(?:(?P<durint>[0-9]))?(?:(?P<durdots>[\.]*))?(?:(?P<tie>~?))?")
barliner = re.compile("\|")
timesignaturer = re.compile("\\\\time (?P<numerator>[0-9]*)\/(?P<denominator>[0-9]*)")
def find_notes(string):
    notes = noter.finditer(string)
    notes = [n for n in notes if(len(n.group("name")) > 0)]
    return notes
def find_barlines(string):
    barlines = barliner.finditer(string)
    return [b for b in barlines]
def find_timesignatures(string):
    timesignatures = timesignaturer.finditer(string)
    return [b for b in timesignatures]

def get_dur_as_frac(note: Match):
    if(note.group("durint")):
        i = int(note.group("durint"))
        dots = note.group("durdots")
        value = Fraction(1, i)
        n_dots = len(dots)
        value_with_dots = value
        for d in range(0, n_dots):
            value_with_dots += Fraction(1, (d+1)*(i*2))
        return value_with_dots
    else: return None
    
def insert_at_index(string, index, item):
    return string[:index]+item+string[index:]
def remove_at_index(string, start, end):
    return string[:start]+string[end:]
def add_barlines(string, bars):
    notes = find_notes(string)
    note_n = 0
    inserted = 0
    new_string = string
    current_dur = Fraction(1, 4)
    for b in bars:
        total = 0
        while(total < b and note_n < len(notes)):
            note = notes[note_n]
            note_val = get_dur_as_frac(notes[note_n]) or current_dur
            current_dur = note_val
            total += note_val
            if(total == b):
                barline = " |"
                new_string = insert_at_index(new_string, note.end()+inserted,barline)
                inserted += len(barline)
            if(total > b):
                print("Bar overflow!")
            note_n += 1
    return new_string
def add_timesignatures(string, bars):
    timesigs = find_timesignatures(string)
    new_string = string
    removed = 0
    for t in timesigs:
        new_string = remove_at_index(new_string, t.start()-removed, t.end()-removed)
        removed += t.end() - t.start()
    barlines = find_barlines(new_string)
    notes = find_notes(new_string)
    # First one attached to first note
    timesig =f"\\time {bars[0].numerator}/{bars[0].denominator}"
    new_string = insert_at_index(new_string, notes[0].start()-1, timesig)
    inserted = len(timesig)
    current_time = bars[0]
    for i, b in enumerate(barlines[:-1]):
        timesig = f"\\time {bars[i+1].numerator}/{bars[i+1].denominator}"
        if(bars[i+1] != current_time):
            new_string = insert_at_index(new_string, b.end()+inserted, timesig)
            inserted += len(timesig)
            current_time = bars[i+1]
    return new_string
def run_ly(string, outDir, filename):
    outputFile = os.path.join(outDir, filename)
    with open(outputFile, "w") as lyfile:
        lyfile.write(string)
    subprocess.run(["lilypond", "-o", outDir, outputFile], shell=True)
test_bars =[ Fraction(4,4), Fraction(4,4), Fraction(3, 4), Fraction(2,4)]
test_expression = "{ a4 b c d e f g a b c d e f g a b c }"
run_ly(add_timesignatures(add_barlines(test_expression, test_bars), test_bars), "./output", "test.ly")
