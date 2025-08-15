import os
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "BreadCrumbs",
        url="https://seal-app-c5ety.ondigitalocean.app",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("BreadCrumbs", path=build_dir)

def BreadCrumbs(activeLink,pages,key=None):
    component_value = _component_func(activeLink=activeLink,pages=pages,key=key, default=0)
    return component_value
