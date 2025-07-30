from playwright.sync_api import Page, sync_playwright
import os
import time
from dotenv import load_dotenv

from data_science.src.utils import create_logger

load_dotenv()


class VideoRecorder:

    def __init__(self):
        self.logger = create_logger("video_recorder", "video_recorder.log")

    def login_to_provisionisr(self, page: Page) -> None:
        self.logger.info("Navigating to provision ISR login page")
        page.goto("https://www.provisionisr-cloud.com/index.html")

        # Wait for login form to be ready
        page.get_by_role("textbox", name="QR code number").wait_for(timeout=10000)

        self.logger.info("Entering login details")
        page.get_by_role("textbox", name="QR code number").fill(os.getenv("PROVISION_QR_CODE"))
        page.get_by_role("textbox", name="Enter Your Username").fill(os.getenv("PROVISION_USERNAME"))
        page.get_by_role("textbox", name="Enter Your Password").fill(os.getenv("PROVISION_PASSWORD"))
        page.get_by_role("button", name="Login").click()

        page.locator("#divLiveOCX").wait_for()

    def record_camera_stream(self, page: Page, camera_name: str, duration_in_sec: int = 30) -> None:
        self.logger.info(f"Navigating to the camera stream of {camera_name}")
        for i in range(2):
            page.get_by_text(camera_name).dblclick()
            time.sleep(2)

        self.logger.info("Started recording")
        time.sleep(1)
        page.get_by_title("Client Record On").click()

        self.logger.info(f"Recording for {duration_in_sec} seconds...")
        time.sleep(duration_in_sec)

        page.get_by_title("Client Record Off").click()
        self.logger.info("Recording finished")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    video_recorder = VideoRecorder()
    video_recorder.login_to_provisionisr(page)
    video_recorder.record_camera_stream(page, camera_name="Back storage 2")

    browser.close()
