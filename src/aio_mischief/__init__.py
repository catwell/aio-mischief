import asyncio
import ctypes
import linecache
import traceback
from typing import Any

# For PyObject see `struct _object` in object.h
# For PyAsyncGenASend see `struct PyAsyncGenASend` in genobject.c


class PyObject(ctypes.Structure):
    pass


PyObject._fields_ = [
    ("ob_refcnt", ctypes.c_ssize_t),
    ("ob_type", ctypes.POINTER(PyObject)),
]


class PyAsyncGenASend(PyObject):
    _fields_ = [("ags_gen", ctypes.POINTER(PyObject))]


def extract_generator(async_gen_asend: Any):
    async_gen = PyAsyncGenASend.from_address(id(async_gen_asend)).ags_gen
    r: dict[str, Any] = {}
    ctypes.pythonapi.PyDict_SetItem(
        ctypes.cast(id(r), ctypes.POINTER(PyObject)),
        ctypes.cast(id("k"), ctypes.POINTER(PyObject)),
        async_gen,
    )
    return r["k"]


def get_an_attr(o: Any, ks: list[str]) -> Any:
    for k in ks:
        if (r := getattr(o, k, None)) is not None:
            return r


def extract_stack_from_task(task: "asyncio.Task[Any]") -> list[traceback.FrameSummary]:
    frames: list[Any] = []
    coro = task._coro  # type: ignore
    while coro:
        frame = get_an_attr(coro, ["cr_frame", "gi_frame", "ag_frame"])
        if frame is not None:
            frames.append(frame)

        coro = get_an_attr(coro, ["cr_await", "gi_yieldfrom", "ag_await"])
        if type(coro).__name__ == "async_generator_asend":
            coro = extract_generator(coro)

    extracted_list = []
    checked: set[str] = set()
    for f in frames:
        lineno = f.f_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        if filename not in checked:
            checked.add(filename)
            linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        extracted_list.append(traceback.FrameSummary(filename, lineno, name, line=line))
    return extracted_list


def patch() -> None:
    from aiomonitor import monitor as aio_monitor
    from aiomonitor import utils as aio_utils

    aio_utils._extract_stack_from_task = extract_stack_from_task
    aio_monitor._extract_stack_from_task = extract_stack_from_task
