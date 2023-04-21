import re
from re import Match
from fractions import Fraction
import subprocess
import os
noter = re.compile("(?=\\b)(?P<name>[abcdefg](?:is|es)?(?:[',]*)?)(?:(?P<durint>[0-9]))?(?:(?P<durdots>[\.]*))?(?:(?P<tie>~?))?")
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
    def has_dur(note):
        i = int(note.group("durint"))
        dots = note.group("durdots")
        value = Fraction(1, i)
        n_dots = len(dots)
        value_with_dots = value
        for d in range(0, n_dots):
            value_with_dots += Fraction(1, (d+1)*(i*2))
        return value_with_dots
    if(note.group("durint")):
        return has_dur(note)
    else:
        notes = find_notes(note.string[:note.start()])
        for n in range(len(notes), 0):
            if(n.group("durint")):
                return has_dur(note)
        return Fraction(1,4)
def get_dur_from_frac(fraction):
    remainder = fraction%1
    if(remainder.numerator == 3):
        return f"{fraction.denominator}."
    if(remainder.numerator == 1):
        return f"{fraction.denominator}"
    if(remainder.numerator == 7):
        return f"{remainder.denominatoor}.."
    else: return "1"
def insert_at_index(string, index, item):
    return string[:index]+item+string[index:]
def remove_at_index(string, start, end):
    return string[:start]+string[end:]
def add_barlines(string, bars):
    notes = find_notes(string)
    note_n = 0
    inserted = 0
    new_string = string
    for b in bars:
        total = 0
        while(total < b and note_n < len(notes)):
            note = notes[note_n]
            note_val = get_dur_as_frac(notes[note_n])
            total += note_val
            if(total == b):
                barline = " |"
                new_string = insert_at_index(new_string, note.end()+inserted,barline)
                inserted += len(barline)
            if(total > b):
                print("Bar overflow!")
            note_n += 1
    print("Added barlines:"+new_string)
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
    print("Added time signatures:"+new_string)
    return new_string
def consolidate_ties(string, pos=0):
    tier = re.compile("(\w+~+\s+)+(?:([abcdefgis0-9,\.']+))?")
    new_string = string
    t = tier.search(string, pos)
    if(t == None):
        return string
    inserted = 0
    total_l = 0
    notes = find_notes(t.group())
    total_l = sum(get_dur_as_frac(n) for n in notes)
    prev_dur = get_dur_from_frac(get_dur_as_frac(notes[-1]))
    total_dur = get_dur_from_frac(total_l)
    # Replace Tie
    insert_note = notes[0].group("name")+total_dur+notes[-1].group("tie")+" "
    new_string = insert_at_index(new_string, inserted+t.end(), insert_note)
    new_string = remove_at_index(new_string, t.start()+inserted, t.end()+inserted)
    inserted += len(insert_note)-len(t.group())
    # Replace Next note
    next_note = noter.search(new_string, t.end()+inserted)
    if(not(next_note.group("durint"))):
        insert_next_note = ""+next_note.group("name")+prev_dur+next_note.group("tie")+" "
        new_string = insert_at_index(new_string, next_note.end(), insert_next_note)
        new_string = remove_at_index(new_string, next_note.start(), next_note.end())
    return consolidate_ties(new_string, pos+inserted+t.end())
    # Returns tie groups
def run_ly(string, outDir, filename):
    outputFile = os.path.join(outDir, filename)
    with open(outputFile, "w") as lyfile:
        lyfile.write(string)
    subprocess.run(["lilypond", "-o", outDir, outputFile], shell=True)
def to_variable(name, expression):
    return f"{name} = {expression}"
def to_staff(instrumentName, shortInstrumentName, expression):
    return "\\new Staff \with { instrumentName = \"#NAME\" shortInstrumentName = \"#SHORTNAME\" } { #MUSIC }"\
    .replace("#SHORTNAME", shortInstrumentName).replace("#NAME", instrumentName).replace("#MUSIC", expression)
def to_score(vars, staves):
    return """
    \\version "2.22.2"
    \\header { }

    #VARS
    \\score { 
        << #STAVES >> 
        \\layout { }
    }""".replace("#STAVES", "\n".join(staves)).replace("#VARS", "\n".join(vars))
test_bars =[ Fraction(4,4), Fraction(4,4), Fraction(3, 4), Fraction(2,4)]
test_expression = "{ a4~ a~ a~ a~ a~ a e f g a~ a b c~ c~ c b c d e f g a b c } "
viola_var = to_variable("violamusic", consolidate_ties(\
    add_timesignatures(\
    add_barlines(test_expression, test_bars), test_bars)))
viola_staff = to_staff("Viola", "Vla.", "\\violamusic")
score = to_score([viola_var],[viola_staff])
run_ly(score, "./output", "test.ly")
