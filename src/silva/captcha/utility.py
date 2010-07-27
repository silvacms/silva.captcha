# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from plone.keyring.interfaces import IKeyManager
from plone.keyring.keyring import Keyring
from zope.interface import implements

from OFS.SimpleItem import SimpleItem


class SilvaKeyManager(SimpleItem):

    implements(IKeyManager)

    meta_type = 'Silva Key Manager'
    __keyrings = {}

    def __init__(self):
        SimpleItem.__init__(self)
        self.__keyrings["system"] = Keyring()
        self.__keyrings["system"].rotate()

    def clear(self, ring="system"):
        if ring is None:
            for ring in self.values():
                ring.clear()
        else:
            self.__keyrings[ring].clear()

    def rotate(self, ring="system"):
        if ring is None:
            for ring in self.values():
                ring.rotate()
        else:
            self.__keyrings[ring].rotate()

    def secret(self, ring="system"):
        return self.__keyrings[ring].current
