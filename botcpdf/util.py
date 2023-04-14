"""Utility functions for botcpdf."""

import json


def load_data(filename: str):
    """Load data from a JSON file."""
    with open(filename, encoding="utf-8") as fhandle:
        data = json.load(fhandle)
    return data


def load_role_data():
    """Load role data from a JSON file."""
    return load_data("gameinfo/roles-bra1n.json")
