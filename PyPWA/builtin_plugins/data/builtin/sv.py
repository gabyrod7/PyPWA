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
Handles SV to / from memory.

The objects in this file are dedicated to reading SV files to memory and
writing data to SV to disk. This is the preferred and default method of
handling data to disk as of version PyPWA 2.0.0
"""

import collections
import csv
import io
import logging

import numpy
from PyPWA import VERSION, LICENSE, STATUS
from PyPWA.core.templates import interface_templates
from PyPWA.builtin_plugins.data import data_templates
from PyPWA.builtin_plugins.data import exceptions

__author__ = ["Mark Jones"]
__credits__ = ["Mark Jones"]
__maintainer__ = ["Mark Jones"]
__email__ = "maj@jlab.org"
__status__ = STATUS
__license__ = LICENSE
__version__ = VERSION

HEADER_SEARCH_BITS = 1024  # type: int


class SvMemory(data_templates.TemplateMemory):
    """
    Object for reading and writing delimiter separated data files.
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.addHandler(logging.NullHandler())

    def parse(self, file_location):
        """
        Reads a delimiter separated file containing data from disk.

        Args:
            file_location (str): The file that contain the data to be
                read.
        Returns:
            numpy.ndarray: The tuple containing the data parsed in from
                the file.
        """
        with io.open(file_location, "rt") as stream:
            for line_count, throw in enumerate(stream):
                pass

        with io.open(file_location, "rt") as stream:
            dialect = csv.Sniffer().sniff(
                stream.read(HEADER_SEARCH_BITS), delimiters=[",", "\t"]
            )

            stream.seek(0)

            sv = csv.reader(stream, dialect)

            elements = next(sv)

            types = []
            for element in elements:
                types.append((element, "f8"))

            self._logger.debug("Types: " + repr(types))
            parsed = numpy.zeros(line_count, types)
            self._logger.debug("Line count: " + repr(line_count))

            for index, row in enumerate(sv):
                for count in range(len(row)):
                    parsed[elements[count]][index] = row[count]
        return parsed

    def write(self, file_location, data):
        """
        Writes the data from memory to file.

        Args:
            file_location  (str): Where to write the data to.
            data (numpy.ndarray): Dictionary of the arrays
                containing the data.
        """
        extension = file_location.split(".")[-1]

        if extension == "tsv":
            the_dialect = csv.excel_tab
        else:
            the_dialect = csv.excel

        with open(file_location, "wt") as stream:
            field_names = list(data.dtype.names)

            writer = csv.DictWriter(
                stream, fieldnames=field_names, dialect=the_dialect
            )
            writer.writeheader()

            for index in range(len(data[field_names[0]])):
                temp = {}
                for field in field_names:
                    temp[field] = repr(data[field][index])
                writer.writerow(temp)


class SvReader(interface_templates.ReaderInterfaceTemplate):

    def __init__(self, file_location):
        """
        This reads in SV Files a single event at a time from disk, then
        puts the contents into a GenericEvent Container.

        Args:
            file_location (str): The location of the file to read in.
        """
        super(SvReader, self).__init__(file_location)
        self._previous_event = None  # type: collections.namedtuple
        self._reader = False  # type: csv.DictReader
        self._file = False  # type: io.TextIOBase
        self._types = False  # type: list[tuple]
        self._elements = False  # type: list[str]
        self._file_location = file_location

        self._start_input()

    def _start_input(self):
        """
        Starts the input and configures the reader. Detects the files
        dialect and plugs the header information into the GenericEvent.
        """
        if self._file:
            self._file.close()

        self._file = io.open(self._file_location)
        dialect = csv.Sniffer().sniff(
            self._file.read(HEADER_SEARCH_BITS), delimiters=[",", "\t"]
        )
        self._file.seek(0)

        self._reader = csv.reader(self._file, dialect)

        self._elements = next(self._reader)
        self._types = []
        for element in self._elements:
            self._types.append((element, "f8"))

    def reset(self):
        """
        Calls the _start_input method to properly close then reopen the
        file handle and restart the CSV process.
        """
        self._start_input()

    @property
    def next_event(self):
        """
        Simple read method that takes the list that is received from the
        CSV reader, translates it from text to numpy.float64, then returns
        the final data

        Returns:
            numpy.ndarray: The data read in from the event.
        """
        non_parsed = list(next(self._reader))
        parsed = numpy.zeros(1, self._types)

        for index, element in enumerate(self._elements):
            parsed[element][0] = non_parsed[index]

        self._previous_event = parsed

        return self.previous_event

    @property
    def previous_event(self):
        return self._previous_event

    def close(self):
        self._file.close()


class SvWriter(interface_templates.WriterInterfaceTemplate):

    def __init__(self, file_location):
        """
        Object writes data to file in either a tab separated sheet or a
        comma separated sheet.

        Args:
            file_location (str): Location to  write the data to.
        """
        super(SvWriter, self).__init__(file_location)
        self._file = open(file_location, "w")
        extension = file_location.split(".")[-1]

        if extension == "tsv":
            self._dialect = csv.excel_tab
        else:
            self._dialect = csv.excel

        self._writer = False  # type: cvs.DictWriter
        self._field_names = False  # type: list[str]

    def _writer_setup(self, data):
        if not self._writer:
            self._field_names = list(data.dtype.names)

            self._writer = csv.DictWriter(
                self._file,
                fieldnames=self._field_names,
                dialect=self._dialect
            )

            self._writer.writeheader()

    def write(self, data):
        """
        Writes the data to a SV Sheet a single event at a time.

        Args:
            data (numpy.ndarray): The tuple containing the data
                that needs to be written.
        """
        self._writer_setup(data)

        dict_data = {}
        for field_name in self._field_names:
            dict_data[field_name] = repr(data[0][field_name])

        self._writer.writerow(dict_data)

    def close(self):
        """
        Properly closes the file handle.
        """
        self._file.close()


class SvDataTest(data_templates.ReadTest):

    def quick_test(self, file_location):
        self._check_header(file_location)

    def full_test(self, file_location):
        self._check_header(file_location)

    @staticmethod
    def _check_header(text_file):
        """
        Simple test to see if the header for the file is a valid
        CSV Header.
        """
        the_file = io.open(text_file)

        if not csv.Sniffer().has_header(
                the_file.read(HEADER_SEARCH_BITS),
        ):
            raise exceptions.IncompatibleData(
                "CSV Module failed to find the files header in " +
                str(HEADER_SEARCH_BITS) + " characters!"
            )


class SvDataPlugin(data_templates.TemplateDataPlugin):

    @property
    def plugin_name(self):
        return "Delimiter Separated Variable sheets"

    def get_plugin_memory_parser(self):
        return SvMemory

    def get_plugin_reader(self):
        return SvReader

    def get_plugin_writer(self):
        return SvWriter

    def get_plugin_read_test(self):
        return SvDataTest()

    @property
    def plugin_supported_extensions(self):
        return [".tsv", ".csv"]

    @property
    def plugin_supports_flat_data(self):
        return True

    @property
    def plugin_supports_gamp_data(self):
        return False