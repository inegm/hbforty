# hbforty (Hewlett's Base 40) #

An implementation of Walter Hewlett's base40 musical pitch and interval
numbering system.

## Documentation ##

### Base40Pitch ###

These can be initialized in one of two ways:

From a pitch name, where pitch names are written with an uppercase note letter, up to two accidentals of the same type, and an octave number.
```
>>> Base40Pitch('Cb4')
Base40Pitch("Cb4", 162)
```
Or from a base40 number value.
```
>>> Base40Pitch(162)
Base40Pitch("Cb4", 162)
```
You can get MIDI values from it:
```
>>> Base40Pitch('A4').midi
69
```
You can get a lilypond (absolute octave reference) string from it:
```
>>> Base40Pitch('Cb2').lilypond
'ces,'
```
You can get the interval distance between two of them:
```
>>> Base40Pitch('C4').interval(Base40Pitch('Eb4'))
Base40Interval("+m3", 11)
```
It's worth trying that again with an enharmonic equivalent:
```
>>> Base40Pitch('C4').interval(Base40Pitch('D#4'))
Base40Interval("+A2", 7)
```
Magic. Because:
```
>>> Base40Pitch('D#4') == Base40Pitch('Eb4')
False
```
Rather:
```
>>> Base40Pitch('D#4') < Base40Pitch('Eb4')
True
```
You can invert a note around another note:
```
>>> Base40Pitch('C4').inverted(Base40Pitch('C5'))
Base40Pitch("C6", 243)
```
If you add an interval to one, you get what you'd expect:
```
>>> Base40Pitch('C4') + Base40Interval('P5')
Base40Pitch("G4", 186)
```
If you subtract an interval from one, you get what you'd expect:
```
>>> Base40Pitch('Eb4') - Base40Interval('m3')
Base40Pitch("C4", 163)
```

### Base40Interval ###

These can be initialized in one of two similar ways:

From an interval name, with interval names written beginning with a `+` (for an ascending interval) or a `-` (for a descending interval), followed by an case-sensitive quality letter, and a quality integer.

The qualities are as follows:


|    quality | letter |
|-----------:|--------|
| Diminished | d      |
|      Minor | m      |
|    Perfect | P      |
|      Major | M      |
|  Augmented | A      |

```
>>> Base40Interval('+m3')
Base40Interval("+m3", 11)
```
Or from a base40 number value.
```
>>> Base40Interval(-11)
Base40Interval("-m3", -11)
```
They can be inverted:
```
>>> Base40Interval(23).inverted
Base40Interval("-P4", -17)
```
And they can be split into octave and simple form compounds (Note: that the simple value is a base40 number):
```
>>> Base40Interval('+M9').compound
CompoundInterval(octave=1, simple=6)
```
They are well behaved when you add them:
```
>>> Base40Interval('+m3') + Base40Interval('+M3')
Base40Interval("+P5", 23)
```
and subtract them from one another:
```
>>> Base40Interval('+P8') - Base40Interval('+P4')
Base40Interval("+P5", 23)
```

## References ##

Walter B. Hewlett - [A Base-40 Number-line Representation of Musical Pitch Notation](http://www.ccarh.org/publications/reprints/base40/).
