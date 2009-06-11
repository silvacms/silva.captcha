# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Five.site.interfaces import IFiveSiteManager

from zope.app.component.interfaces import ISite
from zope.app.component.hooks import setSite
from zope.component import queryUtility

from plone.keyring.interfaces import IKeyManager
from five.localsitemanager import make_objectmanager_site

from utility import SilvaKeyManager


def clean_old_five_sm(context, create=True):
    """Disable the old Five sucky SM.
    """
    from Products.Five.site.localsite import disableLocalSiteHook
    disableLocalSiteHook(context)
    if not create:
        return None
    make_objectmanager_site(context)
    setSite(context)
    return context.getSiteManager()


def install(context):
    """Install Captcha Support.
    """
    if not ISite.providedBy(context):
        make_objectmanager_site(context)
        setSite(context)
    sm = context.getSiteManager()
    if IFiveSiteManager.providedBy(sm):
        clean_old_five_sm(context, create=True)
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



