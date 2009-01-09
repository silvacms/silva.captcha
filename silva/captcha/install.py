# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Five.site.localsite import enableLocalSiteHook, FiveSite
from Products.Five.site.interfaces import IFiveSiteManager

from zope.app.component.interfaces import ISite
from zope.app.component.hooks import setSite
from zope.component import queryUtility

from plone.keyring.interfaces import IKeyManager

from utility import SilvaKeyManager


def install(context):
    """Install Captcha Support.
    """
    if not ISite.providedBy(context):
        enableLocalSiteHook(context)
        setSite(context)
    sm = context.getSiteManager()
    # Yes. Five people are clever.
    if IFiveSiteManager.providedBy(sm):
        sm.registerUtility(IKeyManager, SilvaKeyManager())
    else:
        sm.registerUtility(SilvaKeyManager(), IKeyManager)

def uninstall(context):
    """Uninstall Captcha Support.
    """
    sm = context.getSiteManager()
    utility = sm.queryUtility(IKeyManager)
    if IFiveSiteManager.providedBy(sm):
        parent = utility.aq_parent
        parent.manage_delObjects(['IKeyManager'])
    else:
        sm.unregisterUtility(utility, IKeyManager)

def is_installed(context):
    return not (queryUtility(IKeyManager) is None)



