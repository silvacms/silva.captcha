
from Products.Five import zcml
from Products import Five
zcml.load_config('meta.zcml', Five)
zcml.load_config('configure.zcml', Five)

from Products.Silva.tests import SilvaTestCase
from Testing import ZopeTestCase as ztc

from zope.component import queryMultiAdapter

from silva.captcha import formulator
from Products.Formulator import Form
from Products.Formulator import Errors

class Container(dict):
    """ dict with getattr access to items
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError, e:
            raise AttributeError(e)

class FormulatorFieldTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        """After set up, install the extension.
        """
        root = self.getRoot()
        root.service_extensions.install('silva.captcha')

    def test_functional(self):
        root = self.getRoot()
        captcha = queryMultiAdapter((root, root.REQUEST), name='captcha')
        captcha._generate_session()
        root.REQUEST['captchasessionid'] = root.REQUEST.response.cookies[
            'captchasessionid']['value']

        root.manage_addProduct['Formulator'].manage_add('form', 'Test form')
        form = root.form
        form.manage_addProduct['Formulator'].manage_addField(
            'captcha_field', 'Test Captcha Field', 'CaptchaField')
        
        # i don't think it ever generates 'foo', but still...
        words = captcha._generate_words()
        teststr = 'foo'
        while teststr in words:
            teststr += 'o'
        self.assertRaises(
            Form.FormValidationError, form.validate_all,
            {'field_captcha_field': teststr})

        form.validate_all({'field_captcha_field': words[0]})


from Testing.ZopeTestCase.layer import onsetup as ZopeLiteLayerSetup

@ZopeLiteLayerSetup
def installPackage(name):
    # plone sux0rZ
    ztc.installPackage(name)

import unittest
def test_suite():

    # Load the Zope Product
    installPackage('silva.captcha')

    # Load our ZCML, which add the extension as a Product
    from silva import captcha
    zcml.load_config('configure.zcml', captcha)

    # Run tests
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FormulatorFieldTestCase))
    return suite
