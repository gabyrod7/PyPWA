#    PyPWA, a scientific analysis toolkit.
#    Copyright (C) 2016  JLab
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This file is the main file for all of PyPWA. This file takes a
configuration file, processes it, then contacts the main module that is
requested to determine what information is needed to be loaded and how it
needs to be structured to be able to function in the users desired way.
"""

import argparse
import logging
import sys

from PyPWA import VERSION, LICENSE, STATUS
from PyPWA.core_libs import initial_logging

__author__ = ["Mark Jones"]
__credits__ = ["Mark Jones"]
__maintainer__ = ["Mark Jones"]
__email__ = "maj@jlab.org"
__status__ = STATUS
__license__ = LICENSE
__version__ = VERSION


class StartProgram(object):
    def __init__(self, builder, *args):
        """
        This is the wrapping object for the entry points, it takes the
        object as a input, parses it, and sends the result to the builder
        along with any arguments received for the builder.

        Args:
            builder (PyPWA.configurator.Configurator): The object that
                will build the main from the plugins and execute it to
                begin the actual processing.
            *args: The arguments received from the wrapper.
        """
        self.builder = builder(*args)

    def __call__(self, function):
        """
        The method that will be passed the function when the function is
        called.

        Args:
            function (function): The simple function that contains
                whatever default logic that is needed for the program to
                work.

        Returns:
            The final value of the wrapped function.
        """
        def decorated_builder(*args):
            application_configuration = function(args)
            if application_configuration["extras"]:
                print(
                    "[INFO] Caught something unaccounted for, "
                    "this should be reported, caught: "
                    "{}".format(application_configuration["extras"])
                )

            arguments = self.parse_arguments(
                application_configuration["description"]
            )

            self._return_logging_level(arguments.verbose)

            if arguments.WriteConfig:
                self.write_config(application_configuration)

            sys.stdout.write("\x1b[2J\x1b[H")

            self.builder.run(
                application_configuration, arguments.configuration
            )

        return decorated_builder()

    @staticmethod
    def parse_arguments(description):
        """
        Parses the standard arguments for the PyPWA program.

        Args:
            description (str): Description for the .

        Returns:
            The parsed arguments.
        """
        parser = argparse.ArgumentParser(
            description=description
        )

        parser.add_argument(
            "configuration", type=str, default="", nargs="?"
        )
        parser.add_argument(
            "--WriteConfig", "-wc", action="store_true",
            help="Write an example configuration to the current working "
                 "directory"
        )

        parser.add_argument(
            "--Version", "-V", action="version",
            version="%(prog)s (version " + __version__ + ")"
        )

        parser.add_argument(
            "--verbose", "-v", action="count",
            help="Adds logging, defaults to errors, then setups up on "
                 "from there. -v will include warning, -vvv will show "
                 "debugging."
        )

        arguments = parser.parse_args()

        if not arguments.WriteConfig and arguments.configuration == "":
            parser.print_help()

        return arguments

    @staticmethod
    def _return_logging_level(count):
        """
        Sets the logging level for the program.

        Args:
            count (int): The count of the logging counter.
        """
        if count == 1:
            initial_logging.define_logger(logging.WARNING)
        elif count == 2:
            initial_logging.define_logger(logging.INFO)
        elif count >= 3:
            initial_logging.define_logger(logging.DEBUG)
        else:
            initial_logging.define_logger(logging.ERROR)

    def write_config(self, application_settings):
        """
        Writes the configuration files for the program.

        Args:
            application_settings (dict): The settings received from the
                start function.
        """
        self.builder.make_config(application_settings)

