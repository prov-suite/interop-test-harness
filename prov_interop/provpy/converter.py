"""Manages invocation of ProvPy ``prov-convert`` script.
"""
# Copyright (c) 2015 University of Southampton
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions: 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.  

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os.path
import subprocess

from prov_interop import standards
from prov_interop.component import CommandLineComponent
from prov_interop.component import ConfigError
from prov_interop.converter import ConversionError
from prov_interop.converter import Converter

class ProvPyConverter(Converter, CommandLineComponent):
  """Manages invocation of ProvPy ``prov-convert`` script."""

  FORMAT = "FORMAT"
  """str or unicode: token for output format in command-line specification"""

  INPUT = "INPUT"
  """str or unicode: token for input file in command-line specification"""

  OUTPUT = "OUTPUT"
  """str or unicode: token for output file in command-line specification"""

  LOCAL_FORMATS = {
    standards.PROVX: "xml"
  }
  """dict: mapping from formats in :mod:`prov_interop.standards` to
  formats understood by ``prov-convert``
  """

  def __init__(self):
    """Create converter.
    """
    super(ProvPyConverter, self).__init__()

  def configure(self, config):
    """Configure converter. The configuration must hold:

    - :class:`prov_interop.converter.Converter` configuration
    - :class:`prov_interop.component.CommandLineComponent` configuration

    ``arguments`` must have tokens ``FORMAT``, ``INPUT``, ``OUTPUT``,
    which are place-holders for the output format, input file and
    output file. 

    A valid configuration is::

      {
         "executable": "prov-convert"
         "arguments": "-f FORMAT INPUT OUTPUT"
         "input-formats": ["json"]
         "output-formats": ["provn", "provx", "json"]
      }

    :param config: Configuration
    :type config: dict
    :raises ConfigError: if `config` does not hold the above entries
    """
    super(ProvPyConverter, self).configure(config)
    for token in [ProvPyConverter.FORMAT,
                  ProvPyConverter.INPUT, 
                  ProvPyConverter.OUTPUT]:
      if token not in self._arguments:
        raise ConfigError("Missing token " + token)

  def convert(self, in_file, out_file):
    """Convert input file into output file. 

    - Input and output formats are derived from `in_file` and
      `out_file` file extensions.  
    - A check is done to see that `in_file` exists and that the input
      and output format are in ``input-formats`` and
      ``output-formats`` respectively. 
    - ``executable`` and ``arguments`` are used to create a
      command-line invocation, with ``FORMAT``, ``INPUT`` and
      ``OUTPUT`` being replaced with the output format, `in_file`, and
      `out_file`  
    - If the output format is ``provx`` then ``xml`` is used as
      ``FORMAT`` (as ``prov-convert`` does not recognise ``provx``).
    - A check is done to see that `out_file` exists.

    An example command-line invocation is::

      prov-convert -f xml testcase1.json testcase1.provx

    :param in_file: Input file
    :type in_file: str or unicode
    :param out_file: Output file
    :type out_file: str or unicode
    :raises ConversionError: if the input file cannot be found, or
      the exit code of ``prov-convert`` is non-zero
    :raises OSError: if there are problems invoking the converter
      e.g. the script is not found
    """
    super(ProvPyConverter, self).convert(in_file, out_file)
    in_format = os.path.splitext(in_file)[1][1:]
    out_format = os.path.splitext(out_file)[1][1:]
    super(ProvPyConverter, self).check_formats(in_format, out_format)
    local_format = out_format
    if (out_format in ProvPyConverter.LOCAL_FORMATS):
      local_format = ProvPyConverter.LOCAL_FORMATS[out_format]
    command_line = list(self._executable)
    command_line.extend(self._arguments)
    command_line = [local_format if x==ProvPyConverter.FORMAT else x 
                    for x in command_line]
    command_line = [in_file if x==ProvPyConverter.INPUT else x 
                    for x in command_line]
    command_line = [out_file if x==ProvPyConverter.OUTPUT else x 
                    for x in command_line]
    print((" ".join(command_line)))
    return_code = subprocess.call(command_line)
    if return_code != 0:
      raise ConversionError(" ".join(command_line) + \
                              " returned " + str(return_code))
    if not os.path.isfile(out_file):
      raise ConversionError("Output file not found: " + out_file)
