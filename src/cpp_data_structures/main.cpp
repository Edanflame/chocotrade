#include <pybind11/pybind11.h>
#include <iostream>
#include "data_structures.h"

namespace py = pybind11;


PYBIND11_MODULE(cpp_data_structures, m){
  py::class_<CtQueue>(m, "CtQueue")
    .def(py::init<int>(), py::arg("qz") = 10)
    .def("is_empty", &CtQueue::is_empty)
    .def("is_full", &CtQueue::is_full)
    .def("count", &CtQueue::count)
    .def("enqueue", &CtQueue::enqueue)
    .def("dequeue", [](CtQueue & q){
        Item item;
        bool ok = q.dequeue(item);
        return py::make_tuple(ok,item);
    });
}

