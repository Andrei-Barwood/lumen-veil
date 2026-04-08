#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <math.h>

/*
 * Lumen Veil native field propagator.
 *
 * This engine models abstract field influence:
 * positions, exposure, attenuation, and temporary subsystem degradation.
 */

typedef struct {
    double x;
    double y;
    double reach;
    double intensity;
    double falloff;
    double bias;
} ward_node_t;

static int unpack_doubles(PyObject *sequence, Py_ssize_t expected, double *out) {
    PyObject *fast = PySequence_Fast(sequence, "expected a sequence");
    Py_ssize_t index;
    if (fast == NULL) {
        return -1;
    }
    if (PySequence_Fast_GET_SIZE(fast) != expected) {
        PyErr_SetString(PyExc_ValueError, "unexpected tuple width");
        Py_DECREF(fast);
        return -1;
    }
    for (index = 0; index < expected; index++) {
        out[index] = PyFloat_AsDouble(PySequence_Fast_GET_ITEM(fast, index));
        if (PyErr_Occurred()) {
            Py_DECREF(fast);
            return -1;
        }
    }
    Py_DECREF(fast);
    return 0;
}

static PyObject *propagate(PyObject *self, PyObject *args) {
    PyObject *vessels_obj;
    PyObject *nodes_obj;
    PyObject *vessels_fast;
    PyObject *nodes_fast;
    PyObject *result;
    Py_ssize_t vessel_count;
    Py_ssize_t node_count;
    Py_ssize_t i;
    Py_ssize_t j;
    double dt;

    (void)self;

    if (!PyArg_ParseTuple(args, "OOd", &vessels_obj, &nodes_obj, &dt)) {
        return NULL;
    }

    vessels_fast = PySequence_Fast(vessels_obj, "vessels must be a sequence");
    if (vessels_fast == NULL) {
        return NULL;
    }
    nodes_fast = PySequence_Fast(nodes_obj, "nodes must be a sequence");
    if (nodes_fast == NULL) {
        Py_DECREF(vessels_fast);
        return NULL;
    }

    vessel_count = PySequence_Fast_GET_SIZE(vessels_fast);
    node_count = PySequence_Fast_GET_SIZE(nodes_fast);
    result = PyList_New(vessel_count);
    if (result == NULL) {
        Py_DECREF(vessels_fast);
        Py_DECREF(nodes_fast);
        return NULL;
    }

    for (i = 0; i < vessel_count; i++) {
        PyObject *vessel_obj = PySequence_Fast_GET_ITEM(vessels_fast, i);
        PyObject *row;
        double vessel[14];
        double x;
        double y;
        double vx;
        double vy;
        double ax;
        double ay;
        double susceptibility;
        double shielding;
        double comms;
        double navigation;
        double sensors;
        double control_link;
        double hardpoint_sync;
        double exposure;
        double pressure = 0.0;

        if (unpack_doubles(vessel_obj, 14, vessel) != 0) {
            Py_DECREF(vessels_fast);
            Py_DECREF(nodes_fast);
            Py_DECREF(result);
            return NULL;
        }

        x = vessel[0];
        y = vessel[1];
        vx = vessel[2];
        vy = vessel[3];
        ax = vessel[4];
        ay = vessel[5];
        susceptibility = vessel[6];
        shielding = vessel[7];
        comms = vessel[8];
        navigation = vessel[9];
        sensors = vessel[10];
        control_link = vessel[11];
        hardpoint_sync = vessel[12];
        exposure = vessel[13];

        vx += ax * dt;
        vy += ay * dt;
        x += vx * dt;
        y += vy * dt;

        for (j = 0; j < node_count; j++) {
            PyObject *node_obj = PySequence_Fast_GET_ITEM(nodes_fast, j);
            double raw_node[6];
            ward_node_t node;
            double dx;
            double dy;
            double distance;
            double attenuation;
            double effect;

            if (unpack_doubles(node_obj, 6, raw_node) != 0) {
                Py_DECREF(vessels_fast);
                Py_DECREF(nodes_fast);
                Py_DECREF(result);
                return NULL;
            }

            node.x = raw_node[0];
            node.y = raw_node[1];
            node.reach = raw_node[2];
            node.intensity = raw_node[3];
            node.falloff = raw_node[4];
            node.bias = raw_node[5];

            dx = x - node.x;
            dy = y - node.y;
            distance = sqrt(dx * dx + dy * dy);
            if (distance > node.reach) {
                continue;
            }

            attenuation = exp(-node.falloff * (distance / fmax(node.reach, 1e-6)));
            effect = node.intensity * attenuation * susceptibility * fmax(0.05, 1.0 - shielding) * node.bias;
            pressure += effect;
            comms -= effect * 0.025 * dt * node.bias;
            navigation -= effect * 0.018 * dt * (1.0 + node.bias * 0.2);
            sensors -= effect * 0.021 * dt;
            control_link -= effect * 0.014 * dt * node.bias;
            hardpoint_sync -= effect * 0.031 * dt;
            exposure += effect * dt;
        }

        if (comms < 0.0) comms = 0.0;
        if (comms > 1.0) comms = 1.0;
        if (navigation < 0.0) navigation = 0.0;
        if (navigation > 1.0) navigation = 1.0;
        if (sensors < 0.0) sensors = 0.0;
        if (sensors > 1.0) sensors = 1.0;
        if (control_link < 0.0) control_link = 0.0;
        if (control_link > 1.0) control_link = 1.0;
        if (hardpoint_sync < 0.0) hardpoint_sync = 0.0;
        if (hardpoint_sync > 1.0) hardpoint_sync = 1.0;

        row = Py_BuildValue(
            "(ddddddddddd)",
            x,
            y,
            vx,
            vy,
            comms,
            navigation,
            sensors,
            control_link,
            hardpoint_sync,
            exposure,
            pressure
        );
        if (row == NULL) {
            Py_DECREF(vessels_fast);
            Py_DECREF(nodes_fast);
            Py_DECREF(result);
            return NULL;
        }
        PyList_SET_ITEM(result, i, row);
    }

    Py_DECREF(vessels_fast);
    Py_DECREF(nodes_fast);
    return result;
}

static PyMethodDef lumen_methods[] = {
    {"propagate", propagate, METH_VARARGS, "Advance the abstract field model by one step."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef lumen_module = {
    PyModuleDef_HEAD_INIT,
    "_lumen_native",
    "Native Lumen Veil field propagation.",
    -1,
    lumen_methods
};

PyMODINIT_FUNC PyInit__lumen_native(void) {
    return PyModule_Create(&lumen_module);
}
