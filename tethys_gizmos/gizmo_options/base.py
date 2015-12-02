"""
********************************************************************************
* Name: base.py
* Author: Nathan Swain and Ezra Rice
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import re
import shlex

class TethysGizmoOptions(dict):
    """
    Base class for Tethys Gizmo Options objects.
    """

    def __init__(self, attributes={}, classes=''):
        """
        Constructor for Tethys Gizmo Options base.
        """
        # Initialize super class
        super(TethysGizmoOptions, self).__init__()

        # Dictionary magic
        self.__dict__ = self

        if isinstance(attributes, basestring):
            # 'key="value" key2="value with spaces"'
            pattern = '(\w+)='
            pairs = re.split(pattern, attributes)
            if pairs:
                pairs = [x.strip().strip('\'').strip('\"') for x in pairs]
                attributes = dict()
                for i in range(1, len(pairs), 2):
                    attributes[pairs[i]] = pairs[i+1]
                    print attributes
        self.attributes = attributes
        self.classes = classes


class SecondaryGizmoOptions(dict):
    """
    Base class for Secondary Tethys Gizmo Options objects.
    """

    def __init__(self):
        """
        Constructor for Tethys Gizmo Options base.
        """
        # Initialize super class
        super(SecondaryGizmoOptions, self).__init__()

        # Dictionary magic
        self.__dict__ = self