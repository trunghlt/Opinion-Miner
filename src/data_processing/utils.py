#!/usr/bin/env python
#
# Copyright 2011 Trung Huynh
#
# Licnesed under GNU GPL, Version 3.0; you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.gnu.org/licenses/gpl.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A util module for text processing

"""
def erase(sub, string, char="_"):
    """Find ``sub`` and replace them by a string including only ``char`` with 
    same length as ``sub`` in ``string``.
    
    >>erase("Hello", "Hello world", "-")
    >>---- world

    """
    return string.replace(sub, char*len(sub))

