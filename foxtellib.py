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


channels_url = 'https://watch.foxtel.com.au/en-AU/epg-fixture'

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
					datefmt='%Y-%m-%d:%H:%M:%S',
					level=logging.INFO)
logger = logging.getLogger(__name__)

SLEEP_TIME_IN_SECONDS = 6


class FoxtelWatcher:
	__slots__ = ('driver', 'FOXTEL_USERNAME', 'FOXTEL_PASSWORD', 'CHANNEL_GENRE', 'CHANNEL_NUMBER')

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


			self.FOXTEL_USERNAME = os.environ.get('FOXTEL_USERNAME')
			self.FOXTEL_PASSWORD = os.environ.get('FOXTEL_PASSWORD')
			self.CHANNEL_GENRE = os.environ.get('CHANNEL_GENRE')
			self.CHANNEL_NUMBER = os.environ.get('CHANNEL_NUMBER')
			if not self.FOXTEL_USERNAME or not self.FOXTEL_PASSWORD or not self.CHANNEL_GENRE or not self.CHANNEL_NUMBER:
				raise Exception(
					"FOXTEL_USERNAME, FOXTEL_PASSWORD, CHANNEL_GENRE or CHANNEL_NUMBER are not set in .env")
			
			#self.targetUrl = '';

		except Exception as e:
			logger.error(f"Unable to initialise FoxtelWatcher: {type(e)} {e}")
			raise(e)

   
	def checkState(self):
		#todo, not updated
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
		#self.targetUrl = url;
		time.sleep(SLEEP_TIME_IN_SECONDS)
		
	def play_channel(self):
		
		logger.info(f"Loading Channels...")
		self.navigate_to_url(channels_url)
		
		logger.info(f"Selecting Channel...")
		self.driver.find_element(By.CSS_SELECTOR, "button[aria-haspopup='listbox']").click()
		time.sleep(1)  # let the dropdown render
		self.driver.find_element(By.XPATH, f"//li[@role='option' and .//span[contains(text(), '{self.CHANNEL_GENRE}')]]").click()
		time.sleep(1)  # let the channel list render

		script = """
		const channelNumber = arguments[0];

		const logoContainer = document.getElementById('all-channel-logos');
		const rowContainer = document.getElementById('all-channel-content');

		const numbers = Array.from(logoContainer.querySelectorAll('span'))
			.filter(e => /^\\d+$/.test(e.textContent.trim()));

		const idx = numbers.findIndex(
			e => e.textContent.trim() === channelNumber
		);

		if (idx === -1) return false;

		const row = rowContainer.children[idx];
		const firstShow = row.querySelector('[class~="channel-list-item"]');

		if (!firstShow) return false;

		firstShow.click();
		return true;
		"""
		
		found = self.driver.execute_script(script, str(self.CHANNEL_NUMBER))
		time.sleep(SLEEP_TIME_IN_SECONDS)
		
		logger.info(f"Checking if muted...")
		unmute = self.driver.find_elements(
			By.CSS_SELECTOR,
			"button[data-test-id~='VOLUME_BUTTON_MUTED']"
		)
		
		
		if unmute:			
			unmute[0].click()
		
		if not found:
			raise Exception(f"Channel {self.CHANNEL_NUMBER} not found in logo list")  


	def go_fullscreen(self):
		try:
			logger.info(f"Going Fullscreen")
			btn = self.driver.find_element(By.CSS_SELECTOR, "#player-FULLSCREEN_BUTTON_TOOLTIP[aria-expanded='false']")
			self.driver.execute_script("arguments[0].click();", btn)
			time.sleep(1)
			
		except NoSuchElementException:
			pass
	
	def deregister_chrome(self):
		#has not been updated since ft ui change
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
		#has not been updated since ft ui change
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
		logger.info("Loading foxtel page and initiating login")
		self.driver.get(channels_url)
		time.sleep(SLEEP_TIME_IN_SECONDS)

		try:
			username = self.driver.find_element(
				By.XPATH, "//input[@type='email']")
			password = self.driver.find_element(
				By.XPATH, "//input[@type='password']")
			username.send_keys(self.FOXTEL_USERNAME)
			password.send_keys(self.FOXTEL_PASSWORD)
			self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
			time.sleep(SLEEP_TIME_IN_SECONDS)
		except NoSuchElementException:
			logger.info("A session appears to be active. Skipping login ....")

		if not self.driver.current_url.startswith(channels_url):
			raise Exception(f"Login failed, ended up at {self.driver.current_url}")
