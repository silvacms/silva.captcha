from Products.Formulator import Validator
from Products.Formulator import Widget
from Products.Formulator import Field
from Products.Formulator import StandardFields
from Products.Formulator import DummyField
from Products.Formulator.i18n import translate as _
from zope.component import queryMultiAdapter

class CaptchaValidator(Validator.Validator):
    """ validate the captcha
    """
    message_names = Validator.Validator.message_names + [
        'required_not_found', 'captcha_invalid']
    required_not_found = _('Input is required but no input given.')
    captcha_invalid = _('The verification entry is not valid.')

    def validate(self, field, key, REQUEST):
        value = REQUEST.get(key, '')
        if value == '':
            self.raise_error('required_not_found', field)
        root = field.get_root() # XXX not sure
        captcha = queryMultiAdapter((field, field.REQUEST), name='captcha')
        if not captcha.verify(value):
            self.raise_error('captcha_invalid', field)
        return True # we don't need to return the value, it doesn't matter


CaptchaValidatorInstance = CaptchaValidator()


class CaptchaWidget(Widget.Widget):
    """ the widget for the captcha

        renders the image and an input field
    """
    
    default = DummyField.fields.StringField(
        'default',
        title='Default',
        description='',
        value='',
        hidden=True,
        required=0)

    display_width = DummyField.fields.IntegerField(
        'display_width', title='Display width',
        description="The width in characters. Required.",
        default=20, required=1)

    def render(self, field, key, value, REQUEST):
        """ render the widget
        """
        root = field.get_root() # XXX not sure
        captcha = queryMultiAdapter((field, field.REQUEST), name='captcha')
        image = captcha.image_tag()
        input = Widget.render_element(
            "input", type="text", name=key,
            css_class=field.get_value('css_class'),
            value=value)
        return '<div class="form-captcha">' + image + input + '</div>'

    def render_view(self, field, value):
        return ''


CaptchaWidgetInstance = CaptchaWidget()


class CaptchaField(Field.ZMIField):
    meta_type = 'CaptchaField'
    widget = CaptchaWidgetInstance
    validator = CaptchaValidatorInstance
