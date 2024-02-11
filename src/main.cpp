#include <pybind11/pybind11.h>
namespace py = pybind11;

#include <stdexcept>
#include <string>

#define TSF_IMPLEMENTATION
#include "tsf/tsf.h"

class SoundFont {
private:
    tsf* obj = nullptr;
public:
    SoundFont(const std::string& filename)
    {
        obj = tsf_load_filename(filename.c_str());
        if (!obj) {
            throw std::runtime_error("Could not load SoundFont file: " + filename);
        }
    }
    ~SoundFont() {
        tsf_close(obj);
    }
    void reset() { tsf_reset(obj); }
    int get_preset_index(int bank, int preset) { return tsf_get_presetindex(obj, bank, preset); }
    int get_preset_count() { return tsf_get_presetcount(obj); }
    std::string get_preset_name(int index) { return std::string(tsf_get_presetname(obj, index)); }
};

PYBIND11_MODULE(tinysoundfont, m) {
    m.doc() = "Tiny Sound Font module";
    py::class_<SoundFont>(m, "SoundFont")
        .def(py::init<const std::string &>(),
            "Directly load a SoundFont from a .sf2 filename",
            py::arg("filename"))
        .def("reset", &SoundFont::reset,
            "Stop all playing notes immediately and reset all channel parameters")
        .def("get_preset_index", &SoundFont::get_preset_index,
            "Returns the preset index from a bank and preset number, or -1 if it does not exist in the loaded SoundFont",
            py::arg("bank"), py::arg("preset"))
        .def("get_preset_count", &SoundFont::get_preset_count,
            "Returns the number of presets in the loaded SoundFont")
        .def("get_preset_name", &SoundFont::get_preset_name,
            "Returns the name of a preset index >= 0 and < get_preset_count()",
            py::arg("index"))
    ;
}
