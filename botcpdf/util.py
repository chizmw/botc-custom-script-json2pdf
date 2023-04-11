"""Utility functions for botcpdf."""

import json


def load_data(filename: str):
    """Load data from a JSON file."""
    with open(filename) as f:
        data = json.load(f)
    return data


def load_role_data():
    """Load role data from a JSON file."""
    return load_data('roles.json')
