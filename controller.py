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
	controller = None	
	
	while True:
		try:
			if controller is None:
				logger.info("Starting Foxtel Watcher")
				controller = FoxtelWatcher()	

			if not controller.video_exists():#not started or died, will add other tests if needed
				
				if not controller.logged_in():
					controller.login()				

				controller.play_channel()
				controller.go_fullscreen()
				logger.info("Starting monitor...")
				time.sleep(30)#allow this long to settle before monitoring
		except Exception:
			logger.exception("Error, retrying")
			controller = None
			time.sleep(30)#wait this long after exception before retry

		time.sleep(5)#check working every sec, could like reduce for faster error detection and recovery
