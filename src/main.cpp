#include <pybind11/pybind11.h>

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(tinysoundfont, m) {
    m.doc() = "Tiny Sound Font module";

    m.def("add", &add, "A function that adds two numbers");
}
