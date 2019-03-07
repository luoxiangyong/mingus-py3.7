从mingus 0.5.2中导入代码，主要修改文件如下：

    修改：     mingus/containers/__init__.py
    修改：     mingus/containers/bar.py
    修改：     mingus/containers/composition.py
    修改：     mingus/containers/instrument.py
    修改：     mingus/containers/note.py
    修改：     mingus/containers/note_container.py
    修改：     mingus/containers/suite.py
    修改：     mingus/containers/track.py
    修改：     mingus/core/chords.py
    修改：     mingus/core/intervals.py
    修改：     mingus/core/keys.py
    修改：     mingus/core/notes.py
    修改：     mingus/core/progressions.py
    修改：     mingus/core/scales.py
    修改：     mingus/extra/__init__.py
    修改：     mingus/extra/lilypond.py
    修改：     mingus/extra/musicxml.py
    修改：     mingus/extra/tunings.py
    修改：     mingus/midi/__init__.py
    修改：     mingus/midi/fluidsynth.py
    修改：     mingus/midi/midi_events.py
    修改：     mingus/midi/midi_file_in.py
    修改：     mingus/midi/midi_file_out.py
    修改：     mingus/midi/midi_track.py
    修改：     mingus/midi/pyfluidsynth.py
    修改：     mingus/midi/win32midi.py


修改的地方包括：

- 包的导入方法
- byte的字面量表示方法
- 十六进制字符到byte的转换
- fluidsytn的导入动态库
- midi文件的读写
- 异常的语法
- print函数的语法
- 八进制数的表示方法
- 修正从midi文件读取在写入时的部分错误