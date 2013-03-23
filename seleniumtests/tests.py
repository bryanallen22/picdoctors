"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

#from django.test import TestCase
from django.utils import unittest
from selenium import webdriver

import settings
from settings.functions import get_cfg_setting

import os
import time

def get_setting(name):
    return get_cfg_setting("seleniumtests/localsettings.cfg", name)

class CreateSkaa(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30) # can take up to 30 seconds to do something
        self.email = get_setting('skaa_email')
        self.domain = get_setting('domain')

    def test_create_user_and_job(self):
        driver = self.driver
        driver.get( self.domain )
        self.assertIn("PicDoctors", driver.title)

        # Hide django toolbar
        driver.find_element_by_id("djHideToolBarButton").click()

        # Find the "Upload" button and click it
        driver.find_element_by_id("upload_button").click()

        # upload an actual file
        el = driver.find_element_by_id("fileinput")
        el.send_keys(
            os.path.join(settings.PROJECT_ROOT,
                         'static/images/sm_botanical_before.jpg'))

        # Move on to the markup page
        driver.find_element_by_id("next").click()

        import ipdb; ipdb.set_trace()

    def tearDown(self):
        self.driver.close()

