#include <pybind11/pybind11.h>
namespace py = pybind11;

#include <stdexcept>
#include <string>

#define TSF_IMPLEMENTATION
#include "tsf/tsf.h"

int add(int i, int j) {
    return i + j;
}

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
};

PYBIND11_MODULE(tinysoundfont, m) {
    m.doc() = "Tiny Sound Font module";

    m.def("add", &add, "A function that adds two numbers");
    m.def("tsf_load_filename", &tsf_load_filename, "Directly load a SoundFont from a .sf2 file path");
    py::class_<SoundFont>(m, "SoundFont")
        .def(py::init<const std::string &>());
}
