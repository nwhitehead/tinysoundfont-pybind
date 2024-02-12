#include <pybind11/pybind11.h>
namespace py = pybind11;
using namespace pybind11::literals;

#include <stdexcept>
#include <string>

#define TSF_IMPLEMENTATION
#include "tsf/tsf.h"

class SoundFont {
public:
    tsf* obj = nullptr;
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
    std::string get_preset_name(int index) { return std::string(tsf_get_presetname(obj, index)); }
    std::string get_preset_name(int bank, int number) { return tsf_bank_get_presetname(obj, bank, number); }
    void set_output(enum TSFOutputMode output_mode, int samplerate, float global_gain_db) { tsf_set_output(obj, output_mode, samplerate, global_gain_db); }
    void set_volume(float global_gain) { tsf_set_volume(obj, global_gain); }
    void set_max_voices(int max_voices) { tsf_set_max_voices(obj, max_voices); }
    void note_on(int index, int key, float velocity) { 
        if (!tsf_note_on(obj, index, key, velocity)) {
            throw std::runtime_error(std::string("Error in note_on, allocation of new voice failed"));
        }
    }
    void note_on(int bank, int number, int key, float velocity) { 
        if (!tsf_bank_note_on(obj, bank, number, key, velocity)) {
            throw std::runtime_error(std::string("Error in note_on, preset does not exist or allocation of new voice failed"));
        }
    }
    void note_off() { tsf_note_off_all(obj); }
    void note_off(int index, int key) { tsf_note_off(obj, index, key); }
    void note_off(int bank, int number, int key) { tsf_bank_note_off(obj, bank, number, key); }
    void render(py::buffer buffer) {
        py::buffer_info info = buffer.request();
        int output_channels = obj->outputmode == TSF_MONO ? 1 : 2;
        if (info.ndim != 2) {
            throw std::runtime_error("Incompatible buffer dimension, must be 2 dimensional (samples, channels)");
        }
        if (info.format != py::format_descriptor<float>::format()) {
            throw std::runtime_error("Incompatible buffer format, must be float32");
        }
        if (info.shape[1] != output_channels) {
            throw std::runtime_error(std::string("Incompatible buffer length, channel size must be ") + std::string(output_channels == 1 ? "1 for mono" : "2 for stereo"));
        }
        int samples = info.shape[0];
        tsf_render_float(obj, static_cast<float *>(info.ptr), samples, 0);
    }
};

PYBIND11_MODULE(tinysoundfont, m) {
    m.doc() = "Tiny Sound Font module";
    py::enum_<enum TSFOutputMode>(m, "OutputMode")
        .value("StereoInterleaved", TSF_STEREO_INTERLEAVED)
        .value("StereoUnweaved", TSF_STEREO_UNWEAVED)
        .value("Mono", TSF_MONO)
    ;
    py::class_<SoundFont>(m, "SoundFont")
        .def(py::init<const std::string &>(),
            "Directly load a SoundFont from a .sf2 filename",
            "filename"_a)
        .def(py::init<const SoundFont &>(),
            "Clone existing SoundFont. This allows loading a soundfont only once, but using it for multiple independent playbacks.")
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
            "buffer"_a)
    ;
}
