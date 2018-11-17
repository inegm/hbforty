"""Implements base40 pitches and intervals."""

__version__ = '0.0.1'

from collections import namedtuple
from itertools import chain
from math import copysign


def validate_pitch_name(name):
    """Pitch name validation

    Pitch names are written as a combination of the uppercase pitch note class
    letter, a maximum of two accidentals of the same type, and an integer
    representing the octave. Sharps are represented by the '#' symbols and
    flats by 'b'. Pitch names are case sensitive.

    :param name: Pitch name
    :type name: str

    :returns: None if valid

    :raises: ValueError if invalid

    **Examples**

    >>> validate_pitch_name('C#4')

    >>> validate_pitch_name('D')
    Traceback (most recent call last):
     ...
    ValueError: invalid pitch name "D"
    """
    msg = 'invalid pitch name "{}"'.format(name)
    if name[0] not in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        raise ValueError(msg)
    if (name.count('#') > 2) or (name.count('b')) > 2:
        raise ValueError('accepts a maximum of two accidentals')
    try:
        int(name.replace('#', '').replace('b', '')[1:])
    except ValueError:
        raise ValueError(msg)


def validate_interval_name(name):
    """Interval name validation

    Interval names are written as a combination of direction, quality, and
    quantity. They are case sensitive.

    Direction is represented by the '+' for ascending intervals and by
    the '-' symbol for descending intervals.

    Qualities are represented as follows :

        - Diminished : 'd'
        - Minor : 'm'
        - Perfect : 'P'
        - Major : 'M'
        - Augmented : 'A'

    Quantity is represented by its equivalent integer.

    :param name: Interval name
    :type name: str

    :returns: None if valid

    :raises: ValueError if invalid

    **Examples**

    >>> validate_interval_name('+M9')

    >>> validate_interval_name('d1')
    Traceback (most recent call last):
     ...
    ValueError: invalid interval name "d1"
    """
    msg = 'invalid interval name "{}"'.format(name)
    if name[0] not in ['+', '-']:
        raise ValueError(msg)
    if name[1] not in ['d', 'm', 'P', 'M', 'A']:
        raise ValueError(msg)
    try:
        int(name[2:])
    except ValueError:
        raise ValueError(msg)


def pitch_name_to_lilypond(name):
    """Pitch name to Lilypond text string conversion

    :param name: Pitch name
    :type name: str

    :returns: Lilypond pitch string
    :rtype: str

    >>> pitch_name_to_lilypond('C4')
    "c'"
    >>> pitch_name_to_lilypond('Gb2')
    'ges,'
    """
    validate_pitch_name(name)
    octave = int(name.replace('#', '').replace('b', '')[1:])
    ref_octave = 3
    if octave > ref_octave:
        octave_str = '\'' * (octave - ref_octave)
    elif octave < ref_octave:
        octave_str = ',' * abs(octave - ref_octave)
    else:
        octave_str = ''
    name = name[:name.index(str(octave))] + octave_str
    return name.replace('#', 'is').replace('b', 'es').lower()


def letter_to_base40(letter):
    """Pitch letter name to Base40 pitch number conversion.

    :param letter: Pitch letter
    :type letter: str

    :returns: Base40 pitch number
    :rtype: int

    **Examples**

    >>> letter_to_base40('F')
    20
    """
    letters = {'C': 3, 'D': 9, 'E': 15, 'F': 20, 'G': 26, 'A': 32, 'B': 38}
    if letter not in letters.keys():
        raise ValueError('invalid letter \'{}\''.format(letter))
    return letters[letter]


def pitch_name_to_base40(name):
    """Pitch string to Base40 pitch number.

    :param name: Pitch name
    :type name: str

    :returns: Base40 pitch number
    :rtype: int

    **Examples**

    >>> pitch_name_to_base40('Cb6')
    242
    """
    validate_pitch_name(name)
    base40 = letter_to_base40(name[0])
    base40 += name.count('#') - name.count('b')
    base40 += int(name.replace('#', '').replace('b', '')[1:]) * 40
    return base40


def interval_name_to_base40(name):
    """Interval name to Base40 number conversion.

    :param name: Interval name
    :type name: str

    :returns: Base40 interval number
    :rtype: int

    **Examples**

    >>> interval_name_to_base40('+M9')
    46
    """
    if name[0] not in ['+', '-']:
        name = '+' + name
    validate_interval_name(name)
    direction = name[0]
    quality = name[1]
    try:
        octave, quantity = divmod(int(name[2:]), 7)
    except TypeError:
        msg = 'invalid quantity "{}"'.format(name[2:])
    if quantity == 1:
        applicable_qualities = ['P', 'A']
        if quality not in applicable_qualities:
            msg = 'invalid quality "{}" for quantity "{}"'.format(
                quality, quantity
            )
            raise ValueError(msg)
        ascending = applicable_qualities.index(quality) + octave * 40
        if direction == 'descending':
            base40 = ascending * -1
        else:
            base40 = ascending
    elif quantity in [2, 3, 6, 7]:
        if quality == 'P':
            msg = 'invalid quality "{}" for quantity "{}"'.format(
                quality, quantity
            )
            raise ValueError(msg)
        quantity_roots = [None, 4, 10, None, None, 27, 33]
        quality_offsets = ['d', 'm', 'M', 'A']
        ascending = (
            quantity_roots[quantity - 1] +
            quality_offsets.index(quality) +
            octave * 40
        )
        if direction == '-':
            base40 = ascending * -1
        else:
            base40 = ascending
    elif quantity in [4, 5]:
        applicable_qualities = ['d', 'P', 'A']
        if quality not in applicable_qualities:
            msg = 'invalid quality "{}" for quantity "{}"'.format(
                quality, quantity
            )
            raise ValueError(msg)
        quantity_roots = [None, None, None, 16, 22]
        quality_offsets = ['d', 'P', 'A']
        ascending = (
            quantity_roots[quantity - 1] +
            quality_offsets.index(quality) +
            octave * 40
        )
        if direction == '-':
            base40 = ascending * -1
        else:
            base40 = ascending
    elif quantity == 8:
        applicable_qualities = ['d', 'P']
        if quality not in applicable_qualities:
            msg = 'invalid quality "{}" for quantity "{}"'.format(
                quality, quantity
            )
            raise ValueError(msg)
        octave_root = 40
        ascending = (
            octave_root + applicable_qualities.index('quality') - 1 +
            octave * 40
        )
        if direction == '-':
            base40 = ascending * -1
        else:
            base40 = ascending
    else:
        raise ValueError('something fell through the cracks...')
    return base40


def base40_to_pitch_name(base40):
    """Pitch string to Base40 pitch number.

    :param base40: Base40 pitch number
    :type base40: int

    :returns: Pitch name
    :rtype: str

    **Examples**

    >>> base40_to_pitch_name(242)
    'Cb6'
    """
    if base40 < 1:
        raise ValueError('note integers must be greater than 0')
    octave, pitch = divmod(base40 - 1, 40)
    pitch += 1
    pitches = [None]
    for pletter in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
        pitches += [pletter] * 5 + [None]
    del pitches[18]
    letter = pitches[pitch]
    if letter is None:
        msg = '{} has no valid pitch representation'.format(base40)
        raise ValueError(msg)
    note = letter_to_base40(letter)
    acc = pitch - note
    if acc > 0:
        name = letter + '#' * acc + str(octave)
    elif acc < 0:
        name = letter + 'b' * abs(acc) + str(octave)
    else:
        name = letter + str(octave)
    return name


def base40_to_interval_name(base40):
    """Base40 number to interval name conversion

    :param base40: Base40 interval number
    :type base40: int

    :returns: Interval name
    :rtype: str

    **Examples**

    >>> base40_to_interval_name(46)
    '+M9'
    """
    direction = '-' if base40 < 0 else '+'
    octave, interval = divmod(abs(base40), 40)
    names = [
        'P1', 'A1', None, None,
        'd2', 'm2', 'M2', 'A2', None, None,
        'd3', 'm3', 'M3', 'A3', None, None,
        'd4', 'P4', 'A4', None, None, None,
        'd5', 'P5', 'A5', None, None,
        'd6', 'm6', 'M6', 'A6', None, None,
        'd7', 'm7', 'M7', 'A7', None, None,
        'd8', 'P8',
    ]
    name = names[interval]
    if octave:
        name = name.replace(name[1], str(octave * 8 + int(name[1]) - 1))
    return ''.join([direction, name])


def base40_to_midi(base40):
    """Hewlett Base40 pitch number to MIDI note number conversion.

    :param base40: Hewlett Base40 pitch number
    :type base40: int

    :returns: MIDI note number
    :rtype: int

    .. note::

        Returns None if pitch is outside of the valid MIDI range.

    **Examples**

    >>> base40_to_midi(242)
    83
    """
    mapping = list(
        chain.from_iterable([
            list(range(dbl_b, dbl_b + 5)) + [None] for
            dbl_b in [10, 12, 14, 15, 17, 19, 21]
        ]))
    del mapping[17]
    octave, pitch = divmod(base40 - 1, 40)
    pitch += 1
    midi = mapping[pitch - 1] + octave * 12
    if 0 > midi > 127:
        return None
    return midi


class Base40Pitch():
    """Implementation of Hewlett's Base40 pitch numbering system."""

    def __init__(self, value):
        """Initializes a Base40Pitch

        The Base40Pitch can be constructed in one of two ways :

            - from a pitch name (see :func:`validate_pitch_name`)
            - from a Base40 pitch number

        :param value: Either a pitch name or a Base40 pitch number
        :type value: str or int

        **Examples**

        >>> Base40Pitch('Cb4')
        Base40Pitch("Cb4", 162)

        >>> Base40Pitch(162)
        Base40Pitch("Cb4", 162)
        """
        self._name = None
        self._base40 = None
        if isinstance(value, str):
            self.name = value.strip()
            self.base40 = pitch_name_to_base40(self.name)
        elif isinstance(value, int):
            self.base40 = value
            self.name = base40_to_pitch_name(self.base40)
        else:
            raise ValueError('invalid note value')

    @property
    def base40(self):
        """Base40 integer value.

        :param value: Base40 value
        :type value: int

        :rtype: int

        **Examples**

        >>> pitch = Base40Pitch('Cb4')
        >>> pitch.base40
        162

        >>> pitch.base40 = 140
        >>> print(pitch)
        Base40Pitch("F3", 140)
        """
        return self._base40

    @base40.setter
    def base40(self, value):
        """Sets the pitch's Base40 value."""
        self._base40 = value
        self._name = base40_to_pitch_name(value)

    @property
    def name(self):
        """Base40Pitch name.

        :param value: Base40Pitch name
        :type value: str

        :rtype: str

        **Examples**

        >>> pitch = Base40Pitch('Cb4')
        >>> pitch.name
        'Cb4'

        >>> pitch.name = 'F3'
        >>> print(pitch)
        Base40Pitch("F3", 140)
        """
        return self._name

    @name.setter
    def name(self, value):
        """Sets Base40Pitch name."""
        name = value.lower().capitalize()
        validate_pitch_name(name)
        self._name = name
        self._base40 = pitch_name_to_base40(name)

    @property
    def midi(self):
        """Base40Pitch MIDI note value.

        :rtype: int

        **Examples**

        >>> Base40Pitch('A4').midi
        69
        """
        return base40_to_midi(self.base40)

    @property
    def lilypond(self):
        """Base40Pitch Lilypond string.

        :rtype: str

        **Examples**

        >>> Base40Pitch('Cb2').lilypond
        'ces,'
        """
        return pitch_name_to_lilypond(self.name)

    def interval(self, pitch):
        """Returns the interval distance between the two pitches.

        :param pitch: Another pitch
        :type pitch: :class:`Base40Pitch`

        :rtype: :class:`Base40Interval`

        **Examples**

        >>> Base40Pitch('C4').interval(Base40Pitch('Eb4'))
        Base40Interval("+m3", 11)

        >>> Base40Pitch('C4').interval(Base40Pitch('D#4'))
        Base40Interval("+A2", 7)
        """
        return Base40Interval(self, pitch)

    def inverted(self, index):
        """Invert around another pitch (the index).

        :param index: Base40Pitch around which to invert
        :type index: Base40Pitch

        :returns: inverted
        :rtype: Base40Pitch

        **Examples**

        >>> Base40Pitch('C4').inverted(Base40Pitch('C5'))
        Base40Pitch("C6", 243)
        """
        interval = self.interval(index)
        return index + interval

    def __repr__(self):
        """repr(self)"""
        return '{}("{}", {})'.format(
            self.__class__.__name__,
            self.name,
            self.base40)

    def __add__(self, other):
        """Returns a higher pitch at a distance of the other interval.

        :param other: An interval to add
        :type other: :class:`Base40Interval`

        **Examples**

        >>> Base40Pitch('C4') + Base40Interval('P5')
        Base40Pitch("G4", 186)
        """
        return Base40Pitch(self.base40 + other.base40)

    def __sub__(self, other):
        """Returns a lower pitch at a distance of the other interval

        :param other: An interval to substract
        :type other: :class:`Base40Interval`

        **Examples**

        >>> Base40Pitch('Eb4') - Base40Interval('m3')
        Base40Pitch("C4", 163)
        """
        return Base40Pitch(self.base40 - other.base40)

    def __eq__(self, other):
        """self == other"""
        return self.base40 == other.base40

    def __gt__(self, other):
        """self > other"""
        return self.base40 > other.base40

    def __gte__(self, other):
        """self >= other"""
        return self.base40 >= other.base40

    def __lt__(self, other):
        """self < other"""
        return self.base40 < other.base40

    def __lte__(self, other):
        """self <= other"""
        return self.base40 <= other.base40


class Base40Interval():
    """Implementation of Hewlett's Base40 interval numbering system."""

    CompoundInterval = namedtuple(
        'CompoundInterval',
        ['octave', 'simple']
    )

    def __init__(self, val, pitch=None):
        """Initialize a Base40Interval.

        The interval representation can be constructed in one of two ways :

            - from an interval name (see :func:`validate_interval_name`)
            - from two Base40Pitch objects

        :param val: Either an interval name or the first Base40Pitch object
        :type val: str or Base40Pitch
        :param pitch: The second Base40Pitch object
        :type pitch: Base40Pitch

        .. note::

            If no direction is provided, it is assumed that the interval is
            an *ascending* interval.

        **Examples**

        >>> Base40Interval('m3')
        Base40Interval("+m3", 11)

        >>> Base40Interval(-11)
        Base40Interval("-m3", -11)
        """
        self._base40 = None
        self._name = None
        self._compound = None
        try:
            self.base40 = self._from_two_pitches(val, pitch)
        except AttributeError:
            if isinstance(val, str):
                if val[0] not in ['+', '-']:
                    val = '+' + val
                self.name = val
            elif isinstance(val, int):
                self.base40 = val
            else:
                raise ValueError('invalid interval value "{}"'.format(val))

    @property
    def base40(self):
        """Base40 integer value.

        :param value: Base40 value
        :type value: int

        :rtype: int

        **Examples**

        >>> interval = Base40Interval('P5')
        >>> interval.base40
        23

        >>> interval.base40 = 11
        >>> print(interval)
        Base40Interval("+m3", 11)
        """
        return self._base40

    @base40.setter
    def base40(self, base40):
        """Sets the interval's Base40 value."""
        self._base40 = base40
        self._name = base40_to_interval_name(self.base40)
        self._compound = self._split_compound(self.base40)

    @property
    def name(self):
        """Base40Interval name.

        :param value: Base40Interval name
        :type value: str

        :rtype: str

        **Examples**

        >>> interval = Base40Interval(11)
        >>> interval.name
        '+m3'

        >>> interval.name = '+P5'
        >>> print(interval)
        Base40Interval("+P5", 23)
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets Base40Interval name."""
        self._base40 = interval_name_to_base40(name)
        self._name = name
        self._compound = self._split_compound(self.base40)

    @property
    def inverted(self):
        """The inverted interval.

        :rtype: :class:`Base40Interval`

        .. note::

            Returns a copy.

        **Examples**

        >>> Base40Interval(23).inverted
        Base40Interval("-P4", -17)
        """
        octave, interval = divmod(abs(self.base40), 40)
        inverted = int(copysign(40 - interval + 40 * octave, self.base40)) * -1
        return Base40Interval(inverted)

    @property
    def compound(self):
        """Splits a compound interval into its octave and simple form.

        :rtype: namedtuple

        **Examples**

        >>> Base40Interval('+M9').compound
        CompoundInterval(octave=1, simple=6)
        """
        return self._compound

    def _from_two_pitches(self, npitch, mpitch):
        return mpitch.base40 - npitch.base40

    def _split_compound(self, base40):
        octave, simple = divmod(base40, 40)
        return self.CompoundInterval(octave, simple)

    def __add__(self, other):
        """self + other.

        **Examples**

        >>> Base40Interval('+m3') + Base40Interval('+M3')
        Base40Interval("+P5", 23)
        """
        return Base40Interval(self.base40 + other.base40)

    def __sub__(self, other):
        """self - other.

        **Examples**

        >>> Base40Interval('+P8') - Base40Interval('+P4')
        Base40Interval("+P5", 23)
        """
        return Base40Interval(self.base40 - other.base40)

    def __repr__(self):
        """repr(self)"""
        return '{}("{}", {})'.format(
            self.__class__.__name__,
            self.name,
            self.base40)
