#include <pybind11/pybind11.h>
#include "test.h"

namespace py = pybind11;


PYBIND11_MODULE(my_module1, m) {
    m.doc() = "Example pybind11 module";
    m.def("add", &add, "A function that adds two numbers");
}
