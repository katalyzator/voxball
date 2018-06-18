# -*- coding: utf-8 -*-
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging
import os
import requests
import StringIO
import urlparse

logger = logging.getLogger(__name__)


def get_cdn_url(image):
    return urlparse.urljoin(settings.MEDIA_URL, image.name)
#    return urlparse.urljoin(settings.AWS_CDN_URL, image.name)


def get_image_info(image):
    if not image:
        return None
    else:
        return {
            'url': image.url,
            'width': image.width,
            'height': image.height
        }


def get_resized_image(image, left, top, width, height,
                      new_size=settings.POLL_IMG_SIZE):
    cropped = Image.open(image).crop((left, top, width, height,))
    resized = cropped.resize(new_size, Image.ANTIALIAS)
    # needed not to create an instance of file in local filesystem
    thumb_io = StringIO.StringIO()
    resized.save(thumb_io, format='JPEG')
    thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg', 'image/jpeg',
                                      thumb_io.len, None)
    return thumb_file


def facebook_crop(image):
    width = image.size[0]
    height = image.size[1]
    if 2 * height >= width:
        new_height = width / 2
        up = (height - new_height) / 2
        down = height - up - new_height
        image = image.crop((0, up, width, height - down))
    else:
        new_width = height * 2
        left = (width - new_width) / 2
        right = width - left - new_width
        image = image.crop((left, 0, width - right, height))
    image = image.resize((1200, 630))
    return image


def split_text(text, row_size=28):
    result = []
    current = []
    for word in text.split():
        if not word:
            continue
        new_current = list(current)
        new_current.append(word)
        if len(" ".join(new_current)) > row_size:
            result.append(" ".join(current))
            current = []
        current.append(word)
    if len(current) > 0:
        result.append(" ".join(current))
    return result


def get_texted_image(image, text):
    try:
        logger.info("Received image type: {0}".format(type(image)))
        image = Image.open(image)

        image = facebook_crop(image)

        width = image.size[0]
        height = image.size[1]

        black_image = Image.new(image.mode, size=(width, height), color=(0, 0, 0))

        result = Image.blend(black_image, image, alpha=0.2)

        draw = ImageDraw.Draw(result)

        try:
            font = ImageFont.truetype(os.path.join(settings.BASE_DIR,
                                      "utils/fonts/Roboto-Regular.ttf"), 64)
        except Exception as e:
            logger.error(str(e))
            return None

        rows = split_text(text)

        UP = (height - 80 * len(rows)) / 2
        for row in rows:
            text_w, text_h = draw.textsize(row, font=font)
            draw.text(((width - text_w) / 2, UP), row, (255, 255, 255), font=font)
            UP += 80

        # needed not to create an instance of file in local filesystem
        thumb_io = StringIO.StringIO()
        result.save(thumb_io, format='JPEG')
        thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg', 'image/jpeg',
                                          thumb_io.len, None)
        return thumb_file
    except Exception as e:
        logger.error(str(e))
        return None


def get_favicon(url):
    try:
        icon_url = settings.FAVICON_URL.format(url=url)
        response = requests.get(icon_url)
        if response.status_code == 200:
            thumb_io = StringIO.StringIO()
            image = Image.open(BytesIO(response.content))
            image.save(thumb_io, format='PNG')
            thumb_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpg', 'image/jpeg',
                                              thumb_io.len, None)
            return thumb_file
    except Exception as e:
        logger.error(str(e))
        return None
