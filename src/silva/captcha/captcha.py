# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import os.path
import random
import hashlib
import sys
import time

from skimpyGimpy import skimpyAPI

from five import grok
from silva.core.services.interfaces import ISecretService
from zope.interface import Interface
from zope.component import getUtility
from zope.traversing.browser import absoluteURL

CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
# note: no 0/o/O and i/I/1 confusion

COOKIE_ID = 'silva_captcha'
WORDLENGTH = 7

WAVSOUNDS = os.path.join(os.path.dirname(__file__), 'waveIndex.zip')
FONTPATH = os.path.join(os.path.dirname(__file__), 'arevmoit.bdf')

_TEST_TIME = None


class RenderedCaptcha(object):

    def __init__(self, context, request, word):
        self.context = context
        self.request = request
        self.word = word

    def set_headers(self, type):
        response = self.request.response
        response.setHeader('content-type', type)
        # no caching please
        response.setHeader('cache-control', 'no-cache, no-store')
        response.setHeader('pragma', 'no-cache')
        response.setHeader('expires', 'now')

    def __call__(self):
        raise NotImplementedError


class ImageCaptcha(RenderedCaptcha):
    """Image version of the captcha.
    """

    def __call__(self):
        self.set_headers('image/png')
        return skimpyAPI.Png(self.word, speckle=0.5, fontpath=FONTPATH).data()


class AudioCaptcha(RenderedCaptcha):
    """Audio version of the captcha.
    """

    def __call__(self):
        self.set_headers('audio/wav')
        return skimpyAPI.Wave(self.word, WAVSOUNDS).data()


CAPTCHA_RENDERERS = {
    'image.png': ImageCaptcha,
    'audio.wav': AudioCaptcha}


class Captcha(grok.View):
    grok.context(Interface)

    _session_id = None

    def _setcookie(self, value):
        """Set the session cookie"""
        response = self.request.response
        if COOKIE_ID in response.cookies:
            # clear the cookie first, clearing out any expiration cookie
            # that may have been set during verification
            del response.cookies[COOKIE_ID]
        response.setCookie(COOKIE_ID, value, path='/')

    def _generate_session(self):
        """Create a new session id"""
        if self._session_id is None:
            value = hashlib.sha1(str(random.randrange(sys.maxint))).hexdigest()
            self._session_id = value
            self._setcookie(value)

    def _verify_session(self):
        """Ensure session id and cookie exist"""
        if not self.request.has_key(COOKIE_ID):
            if self._session_id is None:
                # This may happen e.g. when the user clicks the back button
                self._generate_session()
            else:
                # This may happen e.g. when the user does not accept the cookie
                self._setcookie(self._session_id)
            # Put the cookie value into the request for immediate consumption
            self.request.cookies[COOKIE_ID] = self._session_id

    def _generate_words(self):
        """Create words for the current session

        We generate one for the current 5 minutes, plus one for the previous
        5. This way captcha sessions have a livespan of 10 minutes at most.

        """
        session = self.request[COOKIE_ID]
        nowish = int((_TEST_TIME or time.time()) / 300)
        service = getUtility(ISecretService)
        seeds = [
            service.digest(session, nowish),
            service.digest(session, nowish - 1)]

        words = []
        for seed in seeds:
            word = []
            for i in range(WORDLENGTH):
                index = ord(seed[i]) % len(CHARS)
                word.append(CHARS[index])
            words.append(''.join(word))
        return words

    def _url(self, filename):
        return '%s/@@%s/%s' % (
            absoluteURL(self.context, self.request), self.__name__, filename)

    def image_tag(self):
        self._generate_session()
        return '<img src="%s" alt="captcha"/>' % (self._url('image.png'),)

    def audio_url(self):
        self._generate_session()
        return self._url('audio.wav')

    def render(self):
        return self.image_tag()

    def verify(self, input):
        if not input:
            return False
        result = False
        try:
            for word in self._generate_words():
                result = result or input.upper() == word.upper()
            # Delete the session key, we are done with this captcha
            self.request.response.expireCookie(COOKIE_ID, path='/')
        except KeyError:
            pass  # No cookie

        return result

    def publishTraverse(self, request, name):
        if name in CAPTCHA_RENDERERS:
            self._verify_session()
            return CAPTCHA_RENDERERS[name](
                self.context,
                request,
                self._generate_words()[0])
        return super(Captcha, self).publishTraverse(request, name)
