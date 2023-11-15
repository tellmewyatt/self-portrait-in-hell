import ly
from fractions import Fraction
from math import floor, random
def get_seq_beats():
    return floor(seq_time*tempo/60)
chords = ["ees c aes", "d bes g", "d aes ges", "des aes e", "des aes ees"]
# 1 => 3 2 => 1 3 => 2
pattern_beats = 11 # How long before the pattern repeats
interval_sequence = [[1, 2, 1], [0, 2, 1], [1, 0, 2], [0, 0, 1]]
tempo = 45
tempo_string = f"\\tempo 4={tempo}"
seq_time = 7*60 # 7 minutes
octave_rate = 33 # Each voice takes 3 repetitions to change octave
repetitions = floor(get_seq_beats()/pattern_beats)
bars = [Fraction(4,4) for i in range(0, round(get_seq_beats()/4))]
parts = ["ees''", "c''", "aes''"]
def generate_sequence(num):
    interval_sequence_copy = [intervals.copy() for intervals in interval_sequence]
    for intervals in interval_sequence_copy:
        ex = False
        while not(ex):
            rand = floor(random()*3)
            interval = intervals[rand]
            if(interval > 0):
                
                for p in parts: 
                    p = ly.add_note(p, ly.find_notes(p)[-1].group("name")+"~")
                parts[rand-num%3] = ly.transpose(ly.find_notes(p)[-1])
                intervals[rand] = interval-1
                ex = all([not(i) for i in intervals])
def generate_music():
    for i in range(0, repetitions):
        generate_sequence(i)
