import logging
from dotenv import load_dotenv
from foxtellib import FoxtelWatcher
import time

load_dotenv()

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
					datefmt='%Y-%m-%d:%H:%M:%S',
					level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
	proc = None
	try:

		scraper = FoxtelWatcher()
		scraper.load_and_login()		
		scraper.play_channel()
		scraper.go_fullscreen()
		
		logger.info(f"Starting Monitor")
		while True:
			# todo as need	
			#scraper.checkState()
			time.sleep(15)

	except KeyError as e:
		logger.error(f"KeyError: {e}.  Please define missing key.")
	except KeyboardInterrupt:
		logger.info("Launcher cancelled")
	except Exception as e:
		logger.error(f"Error: {type(e)} {e}")
	
