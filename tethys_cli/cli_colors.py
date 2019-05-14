# encoding: utf-8

# Copyright 2013 Diego Navarro Mellén. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this list of
#     conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice, this list
#     of conditions and the following disclaimer in the documentation and/or other materials
#     provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY DIEGO NAVARRO MELLÉN ''AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DIEGO NAVARRO MELLÉN OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those of the
# authors and should not be interpreted as representing official policies, either expressed
# or implied, of Diego Navarro Mellén.

# Special END separator
END = '0e8ed89a-47ba-4cdb-938e-b8af8e084d5c'

# Text attributes
ALL_OFF = '\033[0m'
BOLD = '\033[1m'
UNDERSCORE = '\033[4m'
BLINK = '\033[5m'
REVERSE = '\033[7m'
CONCEALED = '\033[7m'

# Foreground colors
FG_BLACK = '\033[30m'
FG_RED = '\033[31m'
FG_GREEN = '\033[32m'
FG_YELLOW = '\033[33m'
FG_BLUE = '\033[34m'
FG_MAGENTA = '\033[35m'
FG_CYAN = '\033[36m'
FG_WHITE = '\033[39m'

# Background colors
BG_BLACK = '\033[40m'
BG_RED = '\033[41m'
BG_GREEN = '\033[42m'
BG_YELLOW = '\033[43m'
BG_BLUE = '\033[44m'
BG_MAGENTA = '\033[45m'
BG_CYAN = '\033[46m'
BG_WHITE = '\033[49m'

# TerminalColors colors
TC_BLUE = '\033[94m'
TC_GREEN = '\033[92m'
TC_WARNING = '\033[93m'
TC_FAIL = '\033[91m'
TC_ENDC = '\033[0m'


class pretty_output:
    """
    Context manager for pretty terminal prints
    """

    def __init__(self, *attr):
        self.attributes = attr

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def write(self, msg):
        style = ''.join(self.attributes)
        print('{}{}{}'.format(style, str(msg).replace(END, ALL_OFF + style), ALL_OFF))


def write_pretty_output(msg, color=FG_WHITE, attributes=None):
    """Utility function to write output with the `pretty_output` context manager

    Args:
        msg(str, required):
            output to write
        color(constant, optional, default=FG_WHITE):
            constant representing color of the text
        attributes(list, optional, default=None):
            list of constants applying style attributes to `msg`

    Note:
        If a foreground color is specified in attributes it will override the `color` argument.
    """
    attributes = attributes or list()
    attributes.insert(0, color)
    with pretty_output(*attributes) as p:
        p.write(msg)


def write_msg(msg):
    write_pretty_output(msg)


def write_error(msg):
    write_pretty_output(msg, FG_RED)


def write_warning(msg):
    write_pretty_output(msg, FG_YELLOW)


def write_success(msg):
    write_pretty_output(msg, FG_GREEN)


def write_info(msg):
    write_pretty_output(msg, FG_BLUE)
