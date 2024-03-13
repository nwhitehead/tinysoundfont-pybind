//
// Python bindings for TinySoundFont
// https://github.com/nwhitehead/tinysoundfont-pybind
//
// Copyright (C) 2024 Nathan Whitehead
//
// This code is licensed under the MIT license (see LICENSE for details)
//

#include <pybind11/pybind11.h>

namespace py = pybind11;
using namespace pybind11::literals;

#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

// Include support for OGG Vorbis file format (detected automatically by TinySoundFont header)
#include "stb/stb_vorbis.c"

#define TSF_IMPLEMENTATION
#include "tsf/tsf.h"

#define TML_IMPLEMENTATION
#include "tsf/tml.h"

namespace {

inline const char* string_none_if_nullptr(const char* s) {
    return s ? s : "<None>";
}

} // end anonymous namespace

class SoundFont {
public:
    tsf* obj = nullptr;

    SoundFont(py::bytes bytes)
    {
        py::buffer_info info(py::buffer(bytes).request());
        obj = tsf_load_memory(info.ptr, info.size);
        if (!obj) {
            throw std::runtime_error(std::string("Could not load SoundFont from bytes"));
        }
    }

    SoundFont(const std::string& filename)
    {
        obj = tsf_load_filename(filename.c_str());
        if (!obj) {
            throw std::runtime_error(std::string("Could not load SoundFont file: ") + filename);
        }
    }

    SoundFont(const SoundFont &other) {
        obj = tsf_copy(other.obj);
        if (!obj) {
            throw std::runtime_error("Could not clone existing SoundFont object");
        }
    }

    ~SoundFont() {
        tsf_close(obj);
    }

    void reset() { tsf_reset(obj); }

    int get_preset_index(int bank, int number) { return tsf_get_presetindex(obj, bank, number); }

    int get_preset_count() { return tsf_get_presetcount(obj); }

    std::string get_preset_name(int index) { return string_none_if_nullptr(tsf_get_presetname(obj, index)); }

    std::string get_preset_name(int bank, int number) { return string_none_if_nullptr(tsf_bank_get_presetname(obj, bank, number)); }

    void set_output(enum TSFOutputMode output_mode, int samplerate, float global_gain_db) { tsf_set_output(obj, output_mode, samplerate, global_gain_db); }

    void set_volume(float global_gain) { tsf_set_volume(obj, global_gain); }

    void set_max_voices(int max_voices) { tsf_set_max_voices(obj, max_voices); }

    void note_on(int index, int key, float velocity) {
        if (!tsf_note_on(obj, index, key, velocity)) {
            throw std::runtime_error(std::string("Error in note_on"));
        }
    }

    void note_on(int bank, int number, int key, float velocity) {
        if (!tsf_bank_note_on(obj, bank, number, key, velocity)) {
            throw std::runtime_error("Error in note_on");
        }
    }

    void note_off() { tsf_note_off_all(obj); }

    void note_off(int index, int key) { tsf_note_off(obj, index, key); }

    void note_off(int bank, int number, int key) { tsf_bank_note_off(obj, bank, number, key); }

    void render(py::buffer buffer, bool mix) {
        py::buffer_info info = buffer.request();
        int output_channels = obj->outputmode == TSF_MONO ? 1 : 2;
        if (info.ndim == 1) {
            // 1D buffers must be contiguous byte arrays
            if (info.format != py::format_descriptor<unsigned char>::format()) {
                throw std::runtime_error("Incompatible buffer format, must be unsigned char");
            }
            if (info.shape[0] % (sizeof(float) * output_channels)) {
                throw std::runtime_error("Buffer length does not divide evenly into sample frames");
            }
            int samples = info.shape[0] / (sizeof(float) * output_channels);
            tsf_render_float(obj, static_cast<float *>(info.ptr), samples, mix ? 1 : 0);
            return;
        }
        if (info.format != py::format_descriptor<float>::format()) {
            throw std::runtime_error("Incompatible buffer format, must be float32");
        }
        if (info.ndim != 2) {
            throw std::runtime_error("Incompatible buffer dimension, must be 1 dimensional bytearray or 2 dimensional of size (samples, channels)");
        }
        if (info.shape[1] != output_channels) {
            throw std::runtime_error(std::string("Incompatible buffer length, channel size must be ") + std::string(output_channels == 1 ? "1 for mono" : "2 for stereo"));
        }
        int samples = info.shape[0];
        tsf_render_float(obj, static_cast<float *>(info.ptr), samples, mix ? 1 : 0);
        return;
    }

    void channel_set_preset_index(int channel, int index) {
        if (!tsf_channel_set_presetindex(obj, channel, index)) {
            throw std::runtime_error("Error in channel_set_preset_index");
        }
    }

    void channel_set_preset_number(int channel, int number, bool drum) {
        if (!tsf_channel_set_presetnumber(obj, channel, number, drum ? 1 : 0)) {
            throw std::runtime_error("Error in channel_set_preset_number");
        }
    }

    void channel_set_bank(int channel, int bank) {
        if (!tsf_channel_set_bank(obj, channel, bank)) {
            throw std::runtime_error("Error in channel_set_bank");
        }
    }

    void channel_set_bank_preset(int channel, int bank, int number) {
        if (!tsf_channel_set_bank_preset(obj, channel, bank, number)) {
            throw std::runtime_error("Error in channel_set_bank_preset");
        }
    }

    void channel_set_pan(int channel, float pan) {
        if (!tsf_channel_set_pan(obj, channel, pan)) {
            throw std::runtime_error("Error in channel_set_pan");
        }
    }

    void channel_set_volume(int channel, float volume) {
        if (!tsf_channel_set_volume(obj, channel, volume)) {
            throw std::runtime_error("Error in channel_set_volume");
        }
    }

    void channel_set_pitch_wheel(int channel, int pitch_wheel) {
        if (!tsf_channel_set_pitchwheel(obj, channel, pitch_wheel)) {
            throw std::runtime_error("Error in channel_set_pitch_wheel");
        }
    }

    void channel_set_pitch_range(int channel, float range) {
        if (!tsf_channel_set_pitchrange(obj, channel, range)) {
            throw std::runtime_error("Error in channel_set_pitch_range");
        }
    }

    void channel_set_tuning(int channel, float tuning) {
        if (!tsf_channel_set_tuning(obj, channel, tuning)) {
            throw std::runtime_error("Error in channel_set_tuning");
        }
    }

    void channel_note_on(int channel, int key, float velocity) {
        if (!tsf_channel_note_on(obj, channel, key, velocity)) {
            throw std::runtime_error(std::string("Error in channel_note_on"));
        }
    }

    void channel_note_off(int channel, int key) { tsf_channel_note_off(obj, channel, key); }

    void channel_note_off(int channel) { tsf_channel_note_off_all(obj, channel); }

    void channel_sounds_off(int channel) { tsf_channel_sounds_off_all(obj, channel); }

    void channel_midi_control(int channel, int controller, int control_value) {
        if (!tsf_channel_midi_control(obj, channel, controller, control_value)) {
            throw std::runtime_error(std::string("Error in channel_midi_control"));
        }
    }

    int channel_get_preset_index(int channel) { return tsf_channel_get_preset_index(obj, channel); }

    int channel_get_preset_bank(int channel) { return tsf_channel_get_preset_bank(obj, channel); }

    int channel_get_preset_number(int channel) { return tsf_channel_get_preset_number(obj, channel); }

    float channel_get_pan(int channel) { return tsf_channel_get_pan(obj, channel); }

    float channel_get_volume(int channel) { return tsf_channel_get_volume(obj, channel); }

    int channel_get_pitch_wheel(int channel) { return tsf_channel_get_pitchwheel(obj, channel); }

    float channel_get_pitch_range(int channel) { return tsf_channel_get_pitchrange(obj, channel); }

    float channel_get_tuning(int channel) { return tsf_channel_get_tuning(obj, channel); }
};

enum class MidiMessageType {
    NOTE_OFF = 0x80,
    NOTE_ON = 0x90,
    KEY_PRESSURE = 0xA0,
    CONTROL_CHANGE = 0xB0,
    PROGRAM_CHANGE = 0xC0,
    CHANNEL_PRESSURE = 0xD0,
    PITCH_BEND = 0xE0,
    SET_TEMPO = 0x51
};


py::list midi_load_memory(py::bytes bytes) {
    py::buffer_info info(py::buffer(bytes).request());
    // Parse contents using TML
    tml_message *parsed = tml_load_memory(info.ptr, info.size);
    if (!parsed) {
        throw std::runtime_error(std::string("Could not load MIDI data"));
    }
    py::list result{};
    int count = tml_get_info(parsed, nullptr, nullptr, nullptr, nullptr, nullptr);
    tml_message *pos = parsed;
    double current_bpm = 10.0;
    while (pos) {
        double t = (pos->time) * 0.001f;
        py::dict d;
        d["t"] = t;
        d["type"] = static_cast<MidiMessageType>(pos->type);
        d["channel"] = static_cast<int>(pos->channel);
        switch (pos->type) {
            case TML_NOTE_OFF:
                // Fallthrough
            case TML_NOTE_ON:
                d["key"] = static_cast<int>(pos->key);
                d["velocity"] = static_cast<int>(pos->velocity);
                break;
            case TML_KEY_PRESSURE:
                d["key"] = static_cast<int>(pos->key);
                d["key_pressure"] = static_cast<int>(pos->key_pressure);
                break;
            case TML_CONTROL_CHANGE:
                d["control"] = static_cast<int>(pos->control);
                d["control_value"] = static_cast<int>(pos->control_value);
                break;
            case TML_PROGRAM_CHANGE:
                d["program"] = static_cast<int>(pos->program);
                break;
            case TML_CHANNEL_PRESSURE:
                d["channel_pressure"] = static_cast<int>(pos->channel_pressure);
                break;
            case TML_PITCH_BEND:
                d["pitch_bend"] = static_cast<int>(pos->pitch_bend);
                break;
            case TML_SET_TEMPO:
                // No payload, updates bpm field for this and subsequent events
                break;
            default:
                // Unknown events don't get any payload
                break;
        }
        // Update bpm on tempo change
        if (pos->type == TML_SET_TEMPO) {
            double microseconds_per_beat = tml_get_tempo_value(pos);
            current_bpm = 60e6 / microseconds_per_beat;
        }
        d["bpm"] = current_bpm;
        pos = pos->next;
        result.append(d);
    }
    tml_free(parsed);
    return result;
}

PYBIND11_MODULE(_tinysoundfont, m) {
    m.doc() = "TinySoundFont module";
    py::enum_<enum TSFOutputMode>(m, "OutputMode")
        .value("StereoInterleaved", TSF_STEREO_INTERLEAVED)
        .value("StereoUnweaved", TSF_STEREO_UNWEAVED)
        .value("Mono", TSF_MONO)
    ;
    py::enum_<enum MidiMessageType>(m, "MidiMessageType")
        .value("NOTE_OFF", MidiMessageType::NOTE_OFF, "Turn off note")
        .value("NOTE_ON", MidiMessageType::NOTE_ON, "Turn on note")
        .value("KEY_PRESSURE", MidiMessageType::KEY_PRESSURE, "Change pressure of existing note (not handled by tinysoundfont)")
        .value("CONTROL_CHANGE", MidiMessageType::CONTROL_CHANGE, "Change value for controller")
        .value("PROGRAM_CHANGE", MidiMessageType::PROGRAM_CHANGE, "Change the chosen program for a channel")
        .value("CHANNEL_PRESSURE", MidiMessageType::CHANNEL_PRESSURE, "Change the pressure of channels of existing note (not handled by tinysoundfont)")
        .value("PITCH_BEND", MidiMessageType::PITCH_BEND, "Change pitch of existing notes")
        .value("SET_TEMPO", MidiMessageType::SET_TEMPO, "Change tempo of playback")
    ;
    m.def("_midi_load_memory", &midi_load_memory, "Load MIDI file data in Standard MIDI File format");
    py::class_<SoundFont>(m, "SoundFont")
        // Need bytes constructor first, otherwise bytes would be converted and match string constructor
        .def(py::init<py::bytes>(),
            "Load a SoundFont from a memory buffer",
            "bytes"_a)
        .def(py::init<const std::string &>(),
            "Load a SoundFont from a .sf2 filename",
            "filename"_a)
        .def(py::init<const SoundFont &>(),
            "Clone existing SoundFont. This allows loading a soundfont only once, but using it for multiple independent playbacks.",
            "other"_a)
        .def("reset", &SoundFont::reset,
            "Stop all playing notes immediately and reset all channel parameters")
        .def("get_preset_index", &SoundFont::get_preset_index,
            "Returns the preset index from a bank and preset number, or -1 if it does not exist in the loaded SoundFont",
            "bank"_a, "preset"_a)
        .def("get_preset_count", &SoundFont::get_preset_count,
            "Returns the number of presets in the loaded SoundFont")
        .def("get_preset_name", py::overload_cast<int>(&SoundFont::get_preset_name),
            "Returns the name of a preset index >= 0 and < get_preset_count()",
            "index"_a)
        .def("get_preset_name", py::overload_cast<int, int>(&SoundFont::get_preset_name),
            "Returns the name of a preset by bank and preset number",
            "bank"_a, "number"_a)
        .def("set_output", &SoundFont::set_output,
            "Setup the parameters for the voice render methods",
            "output_mode"_a, "samplerate"_a, "global_gain_db"_a)
        .def("set_volume", &SoundFont::set_volume,
            "Set the global gain as a volume factor (1.0 is normal 100%)",
            "global_gain"_a)
        .def("set_max_voices", &SoundFont::set_max_voices,
            "Set the maximum number of voices to play simultaneously. Depending on the soundfond, one note can cause many new voices to be started, so don't keep this number too low or otherwise sounds may not play.",
            "max_voices"_a)
        .def("note_on", py::overload_cast<int, int, float>(&SoundFont::note_on),
            "Start playing a note",
            "index"_a, "key"_a, "velocity"_a)
        .def("note_on", py::overload_cast<int, int, int, float>(&SoundFont::note_on),
            "Start playing a note",
            "bank"_a, "number"_a, "key"_a, "velocity"_a)
        .def("note_off", py::overload_cast<>(&SoundFont::note_off),
            "Stop playing all notes")
        .def("note_off", py::overload_cast<int, int>(&SoundFont::note_off),
            "Stop playing a note",
            "index"_a, "key"_a)
        .def("note_off", py::overload_cast<int, int, int>(&SoundFont::note_off),
            "Stop playing a note",
            "bank"_a, "number"_a, "key"_a)
        .def("render", &SoundFont::render,
            "Render output samples into a buffer",
            "buffer"_a,
            "mix"_a = false)
        .def("channel_set_preset_index", &SoundFont::channel_set_preset_index,
            "Set preset index for a channel",
            "channel"_a, "index"_a)
        .def("channel_set_preset_number", &SoundFont::channel_set_preset_number,
            "Set preset number for a channel, with drum flag that applies MIDI drum rules",
            "channel"_a, "number"_a, "drum"_a)
        .def("channel_set_bank", &SoundFont::channel_set_bank,
            "Set bank for a channel",
            "channel"_a, "bank"_a)
        .def("channel_set_pan", &SoundFont::channel_set_pan,
            "Set stereo pan for a channel, value from 0.0 (left) to 1.0 (right) (default 0.5 center)",
            "channel"_a, "pan"_a)
        .def("channel_set_volume", &SoundFont::channel_set_volume,
            "Set volume for a channel, linear scale (default 1.0)",
            "channel"_a, "volume"_a)
        .def("channel_set_pitch_wheel", &SoundFont::channel_set_pitch_wheel,
            "Set pitch wheel for a channel, position 0 to 16383 (default 8192 unpitched)",
            "channel"_a, "pitch_wheel"_a)
        .def("channel_set_pitch_range", &SoundFont::channel_set_pitch_range,
            "Set pitch range of channel in semitones (default 2.0, total +/- 2 semitones)",
            "channel"_a, "range"_a)
        .def("channel_set_tuning", &SoundFont::channel_set_tuning,
            "Set pitch tuning for channel of all playing voices, in semitones (default 0.0, standard (A440) tuning)",
            "channel"_a, "tuning"_a)
        .def("channel_note_on", &SoundFont::channel_note_on,
            "Play note on channel (preset must already be set for channel)",
            "channel"_a, "key"_a, "velocity"_a)
        .def("channel_note_off", py::overload_cast<int, int>(&SoundFont::channel_note_off),
            "Stop note on channel",
            "channel"_a, "key"_a)
        .def("channel_note_off", py::overload_cast<int>(&SoundFont::channel_note_off),
            "Stop all notes on channel",
            "channel"_a)
        .def("channel_sounds_off", &SoundFont::channel_sounds_off,
            "Stop all sounds entirely on channel",
            "channel"_a)
        .def("channel_midi_control", &SoundFont::channel_midi_control,
            "Apply a MIDI control change to the channel (not all controllers are supported!)",
            "channel"_a, "controller"_a, "control_value"_a)
        .def("channel_get_preset_index", &SoundFont::channel_get_preset_index,
            "Get current preset index set on the channel",
            "channel"_a)
        .def("channel_get_preset_bank", &SoundFont::channel_get_preset_bank,
            "Get current preset bank set on the channel",
            "channel"_a)
        .def("channel_get_preset_number", &SoundFont::channel_get_preset_number,
            "Get current preset number set on the channel",
            "channel"_a)
        .def("channel_get_pan", &SoundFont::channel_get_pan,
            "Get current pan value set on the channel",
            "channel"_a)
        .def("channel_get_volume", &SoundFont::channel_get_volume,
            "Get current volume value set on the channel",
            "channel"_a)
        .def("channel_get_pitch_wheel", &SoundFont::channel_get_pitch_wheel,
            "Get current pitch wheel value set on the channel, 0 to 16383 (8192 is unpitched)",
            "channel"_a)
        .def("channel_get_pitch_range", &SoundFont::channel_get_pitch_range,
            "Get current pitch range value set on the channel, in semitones",
            "channel"_a)
        .def("channel_get_tuning", &SoundFont::channel_get_tuning,
            "Get current tuning value set on the channel, in semitones, (0.0 is standard A440 tuning)",
            "channel"_a)
    ;
}
