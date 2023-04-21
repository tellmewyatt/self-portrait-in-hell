import re
class Scale:
    def __init__(self, one_octave):
        self.pitches = []
        self.one_octave = []
        for octave in range(0, 10):
            for deg in one_octave:
                self.pitches.append({ "name": deg, "octave": octave-1 })
    def to_lilypond(self, index):
        pitch = self.pitches[index]
        displacement = pitch["octave"]-3
        octave_string = ""
        if(displacement < 0):
            octave_string = "," * displacement
        else:
            octave_string = "\'" * displacement
        return f"{pitch['name']}{octave_string}"
    def from_lilypond(self, note: str):
        noter = re.compile("(?P<name>[a-z]*)(?P<octave>[,']*)")
        vals = noter.match(note)
        octave_str = vals.group("octave")
        name = vals.group("name")
        octave = 3
        if("," in octave_str):
            octave -= len(octave_str)
        if("\'" in octave_str):
            octave += len(octave_str)
        return self.pitches.index({ "name": name, "octave": octave })


chromatic = Scale(["c", "des", "d", "ees", "e", "f", "ges", "g", "aes", "a", "bes", "b"])
