Copyright (c) 2008, Infrae. All rights reserved.
See also LICENSE.txt

This is a captcha support for Silva. It works with the help of
``collective.captcha``, and ``plone.keyring``.

After installing the extension, you either use a formlib widget, or
use it directly.

You can get a captcha in your template the following way::

   <tal:captcha tal:define="captcha nocall:here/@@captcha"
                tal:content="structure captcha/image_tag">
   </tal:captcha>

This is going to display an image with the captcha. After, in your
code, you can validate an captcha entry like this::

   from zope.component import getMultiAdapter


   captcha = getMultiAdapter((self.context, self.request), name='captcha')
   if not captcha.verify(input):
       # Bad value
   else:
       # Good value

