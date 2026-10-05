from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from string import Template
import logging
import os
import time
import json
import re

channels_url = 'https://watch.foxtel.com.au/en-AU/epg-fixture'

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
					datefmt='%Y-%m-%d:%H:%M:%S',
					level=logging.INFO)
logger = logging.getLogger(__name__)

SLEEP_TIME_IN_SECONDS = 6
URL_FILTERS = ["mpd", "lic"]


class FoxtelWatcher:
	__slots__ = ('driver', 'FOXTEL_USERNAME', 'FOXTEL_PASSWORD', 'FOXTEL_URL', 'targetUrl')

	def __init__(self):    
		

		try:
			CHROME_PORT = os.environ.get("CHROME_PORT", "9222")
			logger.info(f"Loading chromer driver on port {CHROME_PORT}")
			chromeOptions = webdriver.ChromeOptions()
			chromeOptions.add_experimental_option(
				"debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
			chromeOptions.set_capability(
				"goog:loggingPrefs", {"performance": "ALL"})

			self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
										   options=chromeOptions)

			self.FOXTEL_URL = os.environ.get(
				'FOXTEL_URL', "https://watch.foxtel.com.au/app/")
			self.FOXTEL_USERNAME = os.environ.get('FOXTEL_USERNAME')
			self.FOXTEL_PASSWORD = os.environ.get('FOXTEL_PASSWORD')
			if not self.FOXTEL_USERNAME or not self.FOXTEL_PASSWORD:
				raise Exception(
					"FOXTEL_USERNAME and FOXTEL_PASSWORD are not set")
			
			self.targetUrl = '';

		except Exception as e:
			logger.error(f"Unable to initialise FoxtelWatcher: {type(e)} {e}")
			raise(e)

   
	def checkState(self):
		logger.info("checking state...")
		try:

			if self.driver.current_url != self.targetUrl:
				logger.info(f"Correcting Url")
				self.navigate_to_url(self.targetUrl)
				
			try:    
				loadingSpinner = self.driver.find_element(By.CSS_SELECTOR, ".loading-indicator-container")
		   
				if loadingSpinner:
					logger.info("Player stuck, reloading");
					self.refresh();
			except NoSuchElementException:
				pass
		   
			playButton = self.driver.find_element(By.CSS_SELECTOR, ".play-toggle")
			playTitle = playButton.find_element(By.CSS_SELECTOR, "desc").get_attribute("innerHTML")
			
			if playTitle == 'Play Button':
				logger.info("Playing Video")
				playButton.click()
				
			#check fullscreen ?
				
		except Exception as e:
			logger.info(f"{e.msg}")
			
			logger.info(f'refreshing');
			time.sleep(10);
			self.refresh();


	def refresh(self):
		'''
		This routine performs a web page refresh
		:return:
		'''
		self.driver.refresh()
		time.sleep(SLEEP_TIME_IN_SECONDS)

	def navigate_back(self):
		'''
		This routine navigates back to previous page
		:return:
		'''
		self.driver.execute_script("window.history.go(-1)")
		time.sleep(SLEEP_TIME_IN_SECONDS)

	def navigate_to_url(self, url):
		'''
		This routine navigates to a provided url
		:param url:
		:return:
		'''
		self.driver.get(url)
		self.targetUrl = url;
		time.sleep(SLEEP_TIME_IN_SECONDS)
		
	def play_channel(self, genre, channel_num):
		
		logger.info(f"Loading Channels...")
		self.navigate_to_url(channels_url)
		
		logger.info(f"Selecting Channel...")
		self.driver.find_element(By.CSS_SELECTOR, "button[aria-haspopup='listbox']").click()
		time.sleep(1)  # let the dropdown render
		self.driver.find_element(By.XPATH, f"//li[@role='option' and .//span[contains(text(), '{genre}')]]").click()
		time.sleep(1)  # let the channel list render

		script = """
		const logos = Array.from(document.querySelectorAll('.channelLogo__channel-number-text___XmDaM'));
		const idx = logos.findIndex(e => e.textContent.trim() === arguments[0]);
		if (idx === -1) return false;
		const channelRows = document.querySelectorAll('.channel__single-channel___26Las');
		channelRows[idx].querySelector('.channel-list-item').click();
		return true;
		"""
		found = self.driver.execute_script(script, str(channel_num))
		time.sleep(SLEEP_TIME_IN_SECONDS)
		
		if not found:
			raise Exception(f"Channel {channel_num} not found in logo list")  


	def go_fullscreen(self):
		try:
			logger.info(f"Going Fullscreen")
			btn = self.driver.find_element(By.CSS_SELECTOR, "#player-FULLSCREEN_BUTTON_TOOLTIP[aria-expanded='false']")
			self.driver.execute_script("arguments[0].click();", btn)
			time.sleep(1)
			
		except NoSuchElementException:
			pass
	
	def deregister_chrome(self):
		try:
			logger.info("Deregister Chrome ...")
			self.open_app_settings()
			devices = self.driver.find_elements(By.XPATH, "//div[@class='device-line']")

			chrome_deregister = None
			for d in devices:
				span = d.find_element(By.XPATH, ".//span[@class='device-name']")
				if "(This device)" in span.text:
					chrome_deregister = d.find_element(By.XPATH, ".//button[@class='settings-button']")
					break

			if chrome_deregister:
				chrome_deregister.click()
				time.sleep(SLEEP_TIME_IN_SECONDS)
				modal = self.driver.find_element(By.XPATH, "//div[@class='modal']")
				buttons = modal.find_elements(By.XPATH, "//button[@class='settings-button']")
				for b in buttons:
					if b.text == "Yes, do it":
						logger.info("Chrome device is being de-registered!")
						b.click()
						return

		except NoSuchElementException as e:
			logger.error(f"Unable to access app settings")
			raise(e)


	def open_app_settings(self):
		try:
			logger.info("App Settings ...")
			self.driver.find_element(
				By.XPATH, "//div[@class='icon settings-icon']").click()
			self.driver.find_element(
				By.XPATH, "//span[@aria-label='App Settings']").click()
			time.sleep(SLEEP_TIME_IN_SECONDS)
		except NoSuchElementException as e:
			logger.error(f"Unable to access app settings")
			raise(e)

	def logout(self):
		'''
		Logout user automatically once automation is complete
		:return:
		'''
		try:
			logger.info("Logging out with deregistered chrome session ...")
			self.deregister_chrome()
		except NoSuchElementException as e:
			logger.error(f"Unable to logout session")
			raise(e)

	def load_and_login(self):
		'''
		Loads the FOXTEL website and automatically logs in user.
		This requires environment variables FOXTEL_USERNAME and FOXTEL_PASSWORD to be set
		:return:
		'''
		try:
			logger.info("Loading foxtel page and initiating login")
			self.driver.get(self.FOXTEL_URL)
			time.sleep(SLEEP_TIME_IN_SECONDS)

			username = self.driver.find_element(
				By.XPATH, "//input[@type='email']")
			password = self.driver.find_element(
				By.XPATH, "//input[@type='password']")
			username.send_keys(self.FOXTEL_USERNAME)
			password.send_keys(self.FOXTEL_PASSWORD)
			self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
			time.sleep(SLEEP_TIME_IN_SECONDS)
		except NoSuchElementException as e:
			logger.info(f"A session appears to be active. Skipping login ....")
			try:
				self.driver.find_element(By.CSS_SELECTOR, "span[fallback='Log out']")#check logged in
			except Exception as e:
				logger.error(f"Something is not right: {e}")
				raise(e)
