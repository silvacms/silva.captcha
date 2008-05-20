# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.ExtensionRegistry import extensionRegistry

import install

def initialize(context):
    extensionRegistry.register(
        'silva.captcha', 'Silva Captcha', context, [],
        install, depends_on='Silva')

