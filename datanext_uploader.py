import os
from time import sleep
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


class DataNextUploader:
    def __init__(self, chrome_profile_path: str = './chrome_profile', wait_timeout: int = 15):
        self.driver = None
        self.wait = None
        self.wait_timeout = wait_timeout
        self.chrome_profile_path = chrome_profile_path

    def is_element_available(self, locator: str, timeout: int = 10, poll_frequency: float = 0.2) -> bool:
        if locator.strip().startswith(('//', './/')):
            by = By.XPATH
        else:
            by = By.CSS_SELECTOR

        try:
            WebDriverWait(self.driver, timeout, poll_frequency=poll_frequency).until(
                EC.presence_of_element_located((by, locator)))
            return True
        except TimeoutException:
            return False

    def start_driver(self) -> None:
        options = Options()
        # service = Service("/usr/bin/chromedriver") 
        # options.add_argument("--headless=new")  # VERY IMPORTANT
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-gpu")

        options.add_argument(f"--user-data-dir={self.chrome_profile_path}")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.wait_timeout)
        sleep(randint(a=1, b=3))

    def navigate_to_site(self, url: str = 'http://beaconhouse.datanext.co/') -> None:
        self.driver.get(url=url)
        sleep(randint(a=1, b=3))
        self.driver.maximize_window()
        sleep(randint(a=1, b=3))

    def wait_for_login(self):
        if self.is_element_available(locator='//input[@placeholder="Position"]', timeout=15):
            input('Please login and then press enter in terminal>>>>>>>')
        else:
            print('Already logged in')

        sleep(randint(a=1, b=3))

    def click_if_body_hidden(self):
        if self.is_element_available(locator='body[style="overflow: hidden;"]', timeout=5):
            element = self.driver.find_element("css selector", "button")  # replace with your element
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()

    def click_class_text(self, class_text: str = 'Only Me'):
        self.click_if_body_hidden()

        # Waiting if the create folder is already open or not
        if self.is_element_available(locator='.overflow-auto.text-sm', timeout=5):
            locator = '//button/span[text()="Cancel"]'
            if self.is_element_available(locator=locator):
                self.driver.find_element(by=By.XPATH, value=locator).click()
                sleep(randint(a=1, b=3))

        print(f"Looking for text: '{class_text}'")
        class_text_locator = f'//div[contains(@class,"wrapper")]//p[translate(@title,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="{class_text.lower()}"]'
        if self.is_element_available(locator=class_text_locator):
            required_element = self.driver.find_element(by=By.XPATH, value=class_text_locator)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", required_element)
            sleep(randint(a=1, b=3))
            # if folders are exceed the limit
            try:
                self.driver.execute_script("arguments[0].click();", required_element)
            except:
                view_all_selector = '.overflow-x-auto + div [type="button"]'
                if self.is_element_available(locator=view_all_selector):
                    self.driver.find_element(by=By.CSS_SELECTOR, value=view_all_selector).click()
                    sleep(randint(a=1, b=3))
                    class_text_locator_on_view_all = f'//div[contains(@class,"grid")]//p[@title and translate(@title,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="{class_text.lower()}"]'
                    if self.is_element_available(locator=class_text_locator_on_view_all):
                        self.driver.find_element(by=By.XPATH, value=class_text_locator_on_view_all).click()
                        sleep(randint(a=1, b=3))

            sleep(randint(a=1, b=3))
            print(f"Clicked on '{class_text}' text")
        else:
            self.create_new_folder(class_text=class_text)


    def create_new_folder(self, class_text: str):
        class_text_locator = f'//div[contains(@class,"wrapper")]//p[translate(@title,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="{class_text.lower()}"]'
        self.driver.get(url='https://beaconhouse.datanext.co/folders')
        sleep(randint(a=1, b=3))

        if self.is_element_available(locator='[title="Create new folders"]'):
            self.driver.find_element(by=By.CSS_SELECTOR, value='[title="Create new folders"]').click()
            sleep(randint(a=1, b=3))

            locator = '.items-start .items-center svg'
            if self.is_element_available(locator=locator):
                for index, _ in enumerate(self.driver.find_elements(by=By.CSS_SELECTOR, value=locator)):
                    self.driver.find_elements(by=By.CSS_SELECTOR, value=locator)[index].click()
                    sleep(1)

                locator = '[placeholder="Enter space name"]'
                if self.is_element_available(locator=locator):
                    self.driver.find_element(by=By.CSS_SELECTOR, value=locator).clear()
                    sleep(1)
                    self.driver.find_element(by=By.CSS_SELECTOR, value=locator).send_keys(class_text)
                    sleep(1)

                    locator = '//button/span[text()="Create Folder"]'
                    if self.is_element_available(locator=locator):
                        self.driver.find_element(by=By.XPATH, value=locator).click()
                        sleep(randint(a=2, b=5))

                        # If Create Folder page didn't vanished
                        locator = '//button/span[text()="Cancel"]'
                        if self.is_element_available(locator=locator, timeout=5):
                            self.driver.find_element(by=By.XPATH, value=locator).click()
                            sleep(randint(a=2, b=5))

                        self.navigate_to_site()
                        if self.is_element_available(locator=class_text_locator):
                            required_element = self.driver.find_element(by=By.XPATH, value=class_text_locator)
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", required_element)
                            sleep(randint(a=1, b=3))
                            self.driver.execute_script("arguments[0].click();", required_element)
                            sleep(randint(a=1, b=3))
                            print(f'Clicked on {class_text} text')

                        sleep(randint(a=1, b=3))
                else:
                    print('Folder name field not found')
            else:
                print('User list not found')
        else:
            print('Create new folders button not found')

    def clear_upload_button(self):
        """Click the delete pending Upload button."""
        print('Looking for pending Upload button...')
        delete_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Delete all')]")))
        delete_btn.click()  # Separate the click from the wait
        print('Clicked Delete all button')
        sleep(2)

    def click_upload_button(self):
        """Click the Upload button."""
        # Check and clear pending uploads if they exist
        pending_btns = self.driver.find_elements(By.XPATH, "//button[@title='show pending uploads']//p")
        if len(pending_btns) > 0:
            print('Found pending uploads, clearing them...')
            self.clear_upload_button()

        print('Looking for Upload button...')
        upload_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(),'Upload')])[2]")))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", upload_btn)
        sleep(1)
        self.driver.execute_script("arguments[0].click();", upload_btn)
        print('Clicked Upload button')
        sleep(5)

    def upload_files(self, file1_path, file2_path):
        print('Preparing to upload files...')
        file_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='files']")))

        # Get absolute paths
        file1 = os.path.abspath(file1_path)
        file2 = os.path.abspath(file2_path)

        # Verify files exist
        print(f'File 1 path: {file1}')
        print(f'File 1 exists: {os.path.exists(file1)}')
        print(f'File 2 path: {file2}')
        print(f'File 2 exists: {os.path.exists(file2)}')

        if not os.path.exists(file1):
            raise FileNotFoundError(f'File not found: {file1}')
        if not os.path.exists(file2):
            raise FileNotFoundError(f'File not found: {file2}')

        file_input.send_keys(f'{file1}\n{file2}')
        print('Files uploaded successfully')
        sleep(5)

    def click_metadata_button(self):
        """Click the Metadata buton if visible"""
        print("Looking for metadata button")
        metadeta_button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//button[@title="add files to metadata"]')))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", metadeta_button)
        sleep(1)
        self.driver.execute_script("arguments[0].click();", metadeta_button)
        print('Clicked Metadata button')
        sleep(5)
        # //button[@title="add files to metadata"]

    def click_srt_upload_button(self):
        """Click the SRT upload button."""
        print("🔍 Looking for SRT upload button...")
        srt_upload_btn = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='px-3']"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", srt_upload_btn)
        sleep(1)
        self.driver.execute_script("arguments[0].click();", srt_upload_btn)
        print("✅ Clicked SRT upload button")
        sleep(5)

    def fill_form(self, post_title, title, description):
        """
        Fill the form fields.
        
        Args:
            post_title: Text for Post Title field
            title: Text for Title field
            description: Text for Description field
        """
        # Fill Post Title
        print("📝 Waiting for post title...")
        post_title_input = WebDriverWait(self.driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Post Title']")))
        print("📝 Filling Post Title...")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", post_title_input)
        sleep(1)
        post_title_input.clear()
        sleep(0.5)
        post_title_input.send_keys(post_title)
        print(f"✅ Post Title set to: '{post_title}'")
        sleep(2)

        # Fill Title
        print("📝 Filling Title...")
        title_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Title']")))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", title_input)
        sleep(1)
        title_input.clear()
        sleep(0.5)
        title_input.send_keys(title)
        print(f"✅ Title set to: '{title}'")
        sleep(2)

        # Fill Description
        print("📝 Filling Description...")
        description_textarea = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Description']")))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", description_textarea)
        sleep(1)
        description_textarea.clear()
        sleep(0.5)
        description_textarea.send_keys(description)
        print(f"✅ Description set to: '{description}'")
        sleep(3)

        # Check if mp4 file is present
        print("🔍 Checking for mp4 file...")
        has_mp4 = False
        try:
            mp4_element = self.driver.find_element(By.XPATH, "//span[contains(text(),'mp4')]")
            has_mp4 = True
            print("✅ mp4 file detected")
        except:
            print("⚠️  No mp4 file found")

        # Select checkbox based on mp4 presence
        print("☑️  Selecting checkbox...")
        if has_mp4:
            # Select FacialRecognition if mp4 is present
            try:
                facial_recognition_checkbox = self.driver.find_element(By.XPATH, "//input[@name='FacialRecognition']")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", facial_recognition_checkbox)
                sleep(1)
                if not facial_recognition_checkbox.is_selected():
                    self.driver.execute_script("arguments[0].click();", facial_recognition_checkbox)
                    print("✅ FacialRecognition checkbox selected (mp4 detected)")
                else:
                    print("✅ FacialRecognition checkbox already selected")
            except:
                print("❌ Error: FacialRecognition checkbox not found despite mp4 being present")
        else:
            # Select SpeechToText if no mp4
            try:
                speech_to_text_checkbox = self.driver.find_element(By.XPATH, "//input[@name='SpeechToText']")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", speech_to_text_checkbox)
                sleep(1)
                if not speech_to_text_checkbox.is_selected():
                    self.driver.execute_script("arguments[0].click();", speech_to_text_checkbox)
                    print("✅ SpeechToText checkbox selected (no mp4 detected)")
                else:
                    print("✅ SpeechToText checkbox already selected")
            except:
                print("❌ Error: SpeechToText checkbox not found")

        sleep(3)

    def click_submit_button(self):
        """Click the Submit button."""
        print("📤 Clicking Submit button...")
        submit_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='px-3']")))
        self.driver.execute_script("arguments[0].click();", submit_btn)
        print("✅ Submit button clicked")
        sleep(5)

        sleep(randint(a=1, b=3))
        self.click_if_body_hidden()
        sleep(randint(a=1, b=3))

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()

    def run_full_workflow(self, class_text: str, file1_path, file2_path, post_title: str, title: str, description: str):
        """
        Run the complete upload workflow.
        
        Args:
            class_text: Text to click in the navigation
            file1_path: Path to first file
            file2_path: Path to second file
            post_title: Post title text
            title: Title text
            description: Description text
        """
        try:
            self.start_driver()
            self.navigate_to_site()
            self.wait_for_login()
            self.click_class_text(class_text=class_text)
            self.click_upload_button()
            self.upload_files(file1_path, file2_path)
            try:
                self.click_srt_upload_button()
            except:
                self.click_metadata_button()  # //button[@title="add files to metadata"]
            # Submit twice as in original code
            sleep(2)
            self.fill_form(post_title, title, description)
            self.click_submit_button()

            self.fill_form(post_title, title, description)
            self.click_submit_button()

            sleep(10)
            print("🎉 All tasks completed successfully!")
            sleep(3)

        finally:
            self.close()


# Example usage
if __name__ == '__main__':
    uploader = DataNextUploader()

    # Get script directory for file paths
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # file1 = os.path.join(script_dir, 'input', 'sample.mp3')
    file2 = os.path.join(script_dir, 'sample.mp4')
    file1 = os.path.join(script_dir, 'sample.mp3')

    uploader.run_full_workflow(class_text='Only 1', file1_path=file1, file2_path=file2, post_title='Testing',
                               title='testing', description='raspotin lover of russian')
