#  coding=utf-8
#
#  PyPWA, a scientific analysis toolkit.
#  Copyright (C) 2016 JLab
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import importlib
import sys
from pathlib import Path
from typing import Any, Callable

import logging

_LOGGER = logging.getLogger(__file__)


def load(file: Path, name: str) -> Callable[[Any], Any]:
    """
    Loads a single function from a provided python file.
    """

    # We need the absolute path for the PythonPath
    file = file.absolute()

    # Check to make sure the path isn't already in PtyhonPath
    if file.parent not in sys.path:
        sys.path.append(str(file.parent))

    # Import the module
    try:
        module = importlib.import_module(file.stem)
    except ModuleNotFoundError:
        _LOGGER.error(f"{file.stem} not found!")
        raise ImportError(f"Can not find {file.stem} with {file}")

    # Extract the function
    try:
        found = getattr(module, name)
    except AttributeError:
        _LOGGER.error(f"{name} not found in {file.name}!")
        raise ImportError

    return found
