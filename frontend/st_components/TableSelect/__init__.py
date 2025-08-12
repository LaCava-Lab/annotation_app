import os
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "TableSelect",
        url="https://seal-app-c5ety.ondigitalocean.app",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("TableSelect", path=build_dir)


def TableSelect(header,buttons, columns, key=None):
    component_value = _component_func(header=header,buttons=buttons,columns=columns, key=key, default={})
    return component_value
