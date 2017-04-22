# -*-coding:UTF-8-*-

from __future__ import absolute_import

import random
from captcha.image import ImageCaptcha

_chars = 'ABCDEFGHJKMNPRSTWXYZ23456789'  # 去除易混淆的字符


class Captcha(object):

    _image = ImageCaptcha()

    @staticmethod
    def get(session):
        chars = random.sample(_chars, 4)
        chars = ''.join(chars)
        session['captcha'] = chars
        return Captcha._image.generate(chars)

    @staticmethod
    def verify(captcha, session):
        chars = session.get('captcha', '')
        if chars:
            del session['captcha']
            if captcha == chars:
                return True
        return False


