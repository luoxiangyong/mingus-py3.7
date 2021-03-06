#!/usr/bin/python
# -*- coding: utf-8 -*-

#    mingus - Music theory Python package, midi_track module.
#    Copyright (C) 2008-2009, Bart Spaans
#    Copyright (C) 2011, Carlo Stemberger
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Methods for working with MIDI data as bytes.

The MIDI file format specification I used can be found here:
http://www.sonicspot.com/guide/midifiles.html
"""

from binascii import a2b_hex
from struct import pack, unpack
from math import log
from .midi_events import *
from mingus.core.keys import Key, major_keys, minor_keys
from mingus.containers.note import Note

class MidiTrack(object):

    """A class used to generate MIDI events from the objects in
    mingus.containers."""

    track_data = b''
    delta_time = b'\x00'
    delay = 0
    bpm = 120
    change_instrument = False
    instrument = 1

    def __init__(self, start_bpm=120):
        self.track_data = b''
        self.set_tempo(start_bpm)

    def end_of_track(self):
        """Return the bytes for an end of track meta event."""
        return b"\x00\xff\x2f\x00"

    def play_Note(self, note):
        """Convert a Note object to a midi event and adds it to the
        track_data.

        To set the channel on which to play this note, set Note.channel, the
        same goes for Note.velocity.
        """
        velocity = 64
        channel = 1
        if hasattr(note, 'dynamics'):
            if 'velocity' in note.dynamics:
                velocity = note.dynamics['velocity']
            if 'channel' in note.dynamics:
                channel = note.dynamics['channel']
        if hasattr(note, 'channel'):
            channel = note.channel
        if hasattr(note, 'velocity'):
            velocity = note.velocity
        if self.change_instrument:
            self.set_instrument(channel, self.instrument)
            self.change_instrument = False
        print("*"*80,int(note))
        print('midi_track::play_Note channel note velocity',channel,note,velocity)
        print('midi_track::play_Note',self.track_data,len(self.track_data))
        res = self.note_on(channel, int(note) + 12, velocity)
        print('midi_track::play_Note',self.track_data,len(self.track_data))
        print('>>>>midi_track::play_Note res=',res)
        self.track_data += res
        

    def play_NoteContainer(self, notecontainer):
        """Convert a mingus.containers.NoteContainer to the equivalent MIDI
        events and add it to the track_data.

        Note.channel and Note.velocity can be set as well.
        """
        if len(notecontainer) <= 1:
            [self.play_Note(x) for x in notecontainer]
        else:
            self.play_Note(notecontainer[0])
            self.set_deltatime(0)
            [self.play_Note(x) for x in notecontainer[1:]]

    def play_Bar(self, bar):
        """Convert a Bar object to MIDI events and write them to the
        track_data."""
        self.set_deltatime(self.delay)
        self.delay = 0
        self.set_meter(bar.meter)
        self.set_deltatime(0)
        self.set_key(bar.key)

        print('B'*80)
        print('midi_track::play_Bar')
        print('midi_track::play_Bar',self.track_data,len(self.track_data))
        
        for x in bar:
            tick = int(round((1.0 / x[1]) * 288))
            print("tick:",tick)
            print("x[2]:",x[2])
            if x[2] is None or len(x[2]) == 0:
                self.delay += tick
            else:
                self.set_deltatime(self.delay)
                self.delay = 0
                if hasattr(x[2], 'bpm'):
                    self.set_deltatime(0)
                    self.set_tempo(x[2].bpm)
                    print("x[2].bpm",x[2].bpm)
                print('midi_track::play_Bar',self.track_data,len(self.track_data))
                self.play_NoteContainer(x[2])
                print('midi_track::play_Bar',self.track_data,len(self.track_data))
                r = self.int_to_varbyte(tick)
                print("int_to_varbyte",r)
                self.set_deltatime(r)
                print('midi_track::play_Bar',self.track_data,len(self.track_data))
                self.stop_NoteContainer(x[2])
                
        print('B'*80)

    def play_Track(self, track):
        """Convert a Track object to MIDI events and write them to the
        track_data."""
        if hasattr(track, 'name'):
            self.set_track_name(track.name)
        self.delay = 0
        instr = track.instrument
        if hasattr(instr, 'instrument_nr'):
            self.change_instrument = True
            self.instrument = instr.instrument_nr
        for bar in track:
            self.play_Bar(bar)
        print('~'*80)
        print('midi_track::play_Track')
        print("self",self.track_data)
        print('~'*80)

    def stop_Note(self, note):
        """Add a note_off event for note to event_track."""
        velocity = 64
        channel = 1
        if hasattr(note, 'dynamics'):
            if 'velocity' in note.dynamics:
                velocity = note.dynamics['velocity']
            if 'channel' in note.dynamics:
                channel = note.dynamics['channel']
        if hasattr(note, 'channel'):
            channel = note.channel
        if hasattr(note, 'velocity'):
            velocity = note.velocity
        print('midi_track::stop_Note velocity channel',velocity,channel)
        note_off_res = self.note_off(channel, int(note) + 12, velocity)
        print('midi_track::stop_Note note_off_res',note_off_res)
        print('stop_Note::play_Track',self.track_data,len(self.track_data))
        self.track_data += note_off_res
        print('stop_Note::play_Track',self.track_data,len(self.track_data))

    def stop_NoteContainer(self, notecontainer):
        """Add note_off events for each note in the NoteContainer to the
        track_data."""
        # if there is more than one note in the container, the deltatime should
        # be set back to zero after the first one has been stopped

        print("stop_NoteContainer::notecontainer",notecontainer,len(notecontainer))
        if len(notecontainer) <= 1:
            [self.stop_Note(x) for x in notecontainer]
        else:
            self.stop_Note(notecontainer[0])
            self.set_deltatime(0)
            [self.stop_Note(x) for x in notecontainer[1:]]

    def set_instrument(self, channel, instr, bank=1):
        """Add a program change and bank select event to the track_data."""
        self.track_data += self.select_bank(channel, bank)
        self.track_data += self.program_change_event(channel, instr)

    def header(self):
        """Return the bytes for the header of track.

        The header contains the length of the track_data, so you'll have to
        call this function when you're done adding data (when you're not
        using get_midi_data).
        """
        #SOLO:
        #chunk_size = a2b_hex('%08x' % (len(self.track_data)
        #                      + len(self.end_of_track())))
        chunk_size = bytes.fromhex('%08x' % (len(self.track_data)
                              + len(self.end_of_track())))

        print("-"*80)
        print("MidiTrack:header")
        print("self.track_data:", self.track_data,len(self.track_data))
        print("self.end_of_track():", self.end_of_track(),len(self.end_of_track()))
        print("chunk_size value:",(len(self.track_data)
                              + len(self.end_of_track())))
        print("chunk_size byte:",chunk_size)
        print("-"*80)

        return TRACK_HEADER.encode() + chunk_size

    def get_midi_data(self):
        """Return the MIDI data in bytes for this track.

        Include header, track_data and the end of track meta event.
        """

        print("-"*80)
        print("MidiTrack:get_midi_data")
        print(self.header(), len(self.header()))
        print(self.track_data,len(self.track_data))
        print(self.end_of_track())
        print("-"*80)
        
        return self.header() + self.track_data + self.end_of_track()

    def midi_event(self, event_type, channel, param1, param2=None):
        """Convert and return the paraters as a MIDI event in bytes."""
        assert event_type < 0x80 and event_type >= 0
        assert channel < 16 and channel >= 0
        #SOLO: tc = a2b_hex('%x%x' % (event_type, channel))
        tc = bytes.fromhex('%x%x' % (event_type, channel))
        if param2 is None:
            #SOLO: params = a2b_hex('%02x' % param1)
            params = bytes.fromhex('%02x' % param1)
        else:
            #SOLO: params = a2b_hex('%02x%02x' % (param1, param2))
            params = bytes.fromhex('%02x%02x' % (param1, param2))
        print("-------------",self.delta_time,tc,params) 

        my_delta_time=b''
        if type(self.delta_time).__name__ == 'str':
             my_delta_time = self.delta_time.encode()
        else:
            my_delta_time = self.delta_time
        
        res = my_delta_time + tc + params
        print("midi_event res:",res)
        return res

    def note_off(self, channel, note, velocity):
        """Return bytes for a 'note off' event."""
        return self.midi_event(NOTE_OFF, channel, note, velocity)

    def note_on(self, channel, note, velocity):
        """Return bytes for a 'note_on' event."""
        res = self.midi_event(NOTE_ON, channel, note, velocity)
        print("midi_track:note_on", res)
        return res

    def controller_event(self, channel, contr_nr, contr_val):
        """Return the bytes for a MIDI controller event."""
        return self.midi_event(CONTROLLER, channel, contr_nr, contr_val)

    def reset(self):
        """Reset track_data and delta_time."""
        self.track_data = b''
        self.delta_time = b'\x00'

    def set_deltatime(self, delta_time):
        """Set the delta_time.

        Can be an integer or a variable length byte.
        """
        if type(delta_time) == str:
            delta_time = delta_time.encode()
        if type(delta_time) == int:
            delta_time = self.int_to_varbyte(delta_time)
        print("---set_deltatime", delta_time)   
        self.delta_time = delta_time

    def select_bank(self, channel, bank):
        """Return the MIDI event for a select bank controller event."""
        return self.controller_event(BANK_SELECT, channel, bank)

    def program_change_event(self, channel, instr):
        """Return the bytes for a program change controller event."""
        return self.midi_event(PROGRAM_CHANGE, channel, instr)

    def set_tempo(self, bpm):
        """Convert the bpm to a midi event and write it to the track_data."""
        self.bpm = bpm
        self.track_data += self.set_tempo_event(self.bpm)

    def set_tempo_event(self, bpm):
        """Calculate the microseconds per quarter note."""
        ms_per_min = 60000000
        ###:solo_lxy modified
        #SOLO:mpqn = a2b_hex('%06x' % (ms_per_min // bpm))
        mpqn = bytes.fromhex('%06x' % (ms_per_min // bpm))
        #print("____________ms_per_min / bpm = %d/%d = %d" % (ms_per_min , bpm, ms_per_min //bpm ))
        #print(mpqn)
        print("+"*80)
        print("MidiTrack:set_tempo_event")
        print("self.delta_time:",self.delta_time)
        print("META_EVENT:",META_EVENT)
        print("SET_TEMPO:",SET_TEMPO)
        print("mpqn:",mpqn)
        print(self.delta_time + META_EVENT + SET_TEMPO + b'\x03' + mpqn)
        print("+"*80)

        return self.delta_time + META_EVENT + SET_TEMPO + b'\x03' + mpqn

    def set_meter(self, meter=(4, 4)):
        """Add a time signature event for meter to track_data."""
        self.track_data += self.time_signature_event(meter)

    def time_signature_event(self, meter=(4, 4)):
        """Return a time signature event for meter."""

        #SOLO:
        #numer = a2b_hex('%02x' % meter[0])
        #denom = a2b_hex('%02x' % int(log(meter[1], 2)))
        #return self.delta_time + META_EVENT + TIME_SIGNATURE + '\x04' + numer\
        #     + denom + '\x18\x08'

        numer = bytes.fromhex('%02x' % meter[0])
        denom = bytes.fromhex('%02x' % int(log(meter[1], 2)))
        return self.delta_time + META_EVENT + TIME_SIGNATURE + b'\x04' + numer\
             + denom + b'\x18\x08'

    def set_key(self, key='C'):
        """Add a key signature event to the track_data."""
        if isinstance(key, Key):
            key = key.name[0]
        self.track_data += self.key_signature_event(key)

    def key_signature_event(self, key='C'):
        """Return the bytes for a key signature event."""
        if key.islower():
            val = minor_keys.index(key) - 7
            mode = b'\x01'
        else:
            val = major_keys.index(key) - 7
            mode = b'\x00'
        if val < 0:
            val = 256 + val

        print('key_signature_event val',val)
        
        #SOLO:
        #key = a2b_hex('%02x' % val)
        #return '{0}{1}{2}\x02{3}{4}'.format(self.delta_time, META_EVENT,
        #        KEY_SIGNATURE, key, mode)
        key = bytes.fromhex('%02x' % val)
        print('key_signature_event key',key)
        res = self.delta_time + META_EVENT + KEY_SIGNATURE + b'\x02' \
                + key + mode
        print('key_signature_event res',res)
        return res

    def set_track_name(self, name):
        """Add a meta event for the track."""
        self.track_data += self.track_name_event(name)

    def track_name_event(self, name):
        """Return the bytes for a track name meta event."""
        l = self.int_to_varbyte(len(name))
        return b'\x00' + META_EVENT + TRACK_NAME + l + name.encode()

    def int_to_varbyte(self, value):
        """Convert an integer into a variable length byte.

        How it works: the bytes are stored in big-endian (significant bit
        first), the highest bit of the byte (mask 0x80) is set when there
        are more bytes following. The remaining 7 bits (mask 0x7F) are used
        to store the value.
        """
        # Warning: bit kung-fu ahead. The length of the integer in bytes
        length = int(log(max(value, 1), 0x80)) + 1

        # Remove the highest bit and move the bits to the right if length > 1
        my_bytes = [value >> i * 7 & 0x7F for i in range(length)]
        my_bytes.reverse()

        # Set the first bit on every one but the last bit.
        for i in range(len(my_bytes) - 1):
            my_bytes[i] = my_bytes[i] | 0x80
        return pack('%sB' % len(my_bytes), *my_bytes)

