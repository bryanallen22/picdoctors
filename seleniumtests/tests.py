"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

#from django.test import TestCase
from django.utils import unittest
from selenium import webdriver
from selenium.webdriver import ActionChains

import settings
from settings.functions import get_cfg_setting

import os
import time

def get_setting(name, default):
    return get_cfg_setting("seleniumtests/localsettings.cfg", name) or default

def set_input(driver, el_id, text):
    el = driver.find_element_by_id( el_id )
    el.click()
    el.send_keys( text )

class CreateSkaa(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30) # can take up to 30 seconds to do something
        self.email = get_setting('skaa_email', 'bryan+user@picdoctors.com')
        self.domain = get_setting('domain', 'http://localhost:8000')

    def test_create_user_and_job(self):
        driver = self.driver
        print "Going to %s" % self.domain
        driver.get( self.domain )
        self.assertIn("PicDoctors", driver.title)

        ######
        # Home page
        ######
        # Hide django toolbar
        driver.find_element_by_id("djHideToolBarButton").click()

        # Find the "Upload" button and click it
        driver.find_element_by_id("upload_button").click()

        ######
        # Upload page
        ######
        # upload an actual file
        el = driver.find_element_by_id("fileinput")
        el.send_keys(
            os.path.join(settings.PROJECT_ROOT,
                         'static/images/sm_botanical_before.jpg'))

        # Move on to the markup page
        driver.find_element_by_id("next").click()

        ######
        # Markup page
        ######

        # Create a markup. This doesn't work. I don't know why.
        # I'll have to come back to it.
        #action_chains = ActionChains(driver)
        #el = driver.find_element_by_class_name("markup_pic_container")
        #action_chains.drag_and_drop_by_offset(el, 100, 50)
        #action_chains.perform()

        # Add a general description
        el = driver.find_element_by_class_name( 'desc' )
        el.click()
        el.send_keys( 'some description' )

        # Click "next"
        driver.find_element_by_id('next').click()

        ######
        # Sign In page
        ######
        set_input(driver, 'email', self.email )
        set_input(driver, 'password', 'asdf')
        set_input(driver, 'confirm_password', 'asdf')

        driver.find_element_by_id("btnsubmit").click()

        ######
        # Sign In page
        ######
        set_input(driver, 'price', '4.00')
        # Fill in test card info:
        driver.find_element_by_id( 'btn-visa' ).click()
        # Submit the payment
        driver.find_element_by_id('submit_payment').click()

    def tearDown(self):
        self.driver.close()

