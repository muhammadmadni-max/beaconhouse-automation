import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DataNextUploader:
    """
    Automates file upload and form submission on DataNext platform.
    """
    
    def __init__(self, chrome_profile_path="./chrome_profile", wait_timeout=15):
        """
        Initialize the uploader with Chrome driver.
        
        Args:
            chrome_profile_path: Path to Chrome user data directory
            wait_timeout: Timeout for element waits in seconds
        """
        self.chrome_profile_path = chrome_profile_path
        self.wait_timeout = wait_timeout
        self.driver = None
        self.wait = None
        
    def start_driver(self):
        """Start Chrome driver with specified profile."""
        options = Options()
        options.add_argument(f"--user-data-dir={self.chrome_profile_path}")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.wait_timeout)
        
    def navigate_to_site(self, url="http://beaconhouse.datanext.co/"):
        """Navigate to the target URL."""
        self.driver.get(url)
        
    def wait_for_login(self):
        """Wait for user to login manually if needed."""
        try:
            welcome = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Position"]'))
            )
            if welcome:
                input(f"Please login and then press enter in terminal>>>>>>>")
        except:
            pass
        time.sleep(2)
        
    def click_class_text(self, class_text):
        """Click on dynamic text element."""
        print(f"🔍 Looking for text: '{class_text}'")
        dynamic_xpath = f"//div[@class='relative flex items-center gap-6 pt-2 pl-6 w-fit snap-x']//p[contains(text(),'{class_text}')]"
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, dynamic_xpath)))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", element)
        print(f"✅ Clicked on '{class_text}' text")
        time.sleep(3)

    def clear_upload_button(self):
        """Click the delete pending Upload button."""
        print("🔍 Looking for pending Upload button...")
        delete_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Delete all')]"))
        )
        delete_btn.click()  # Separate the click from the wait
        print("✅ Clicked Delete all button")
        time.sleep(2)
            
    def click_upload_button(self):
        """Click the Upload button."""
        # Check and clear pending uploads if they exist
        pending_btns = self.driver.find_elements(By.XPATH, "//button[@title='show pending uploads']//p")
        if len(pending_btns) > 0:
            print("⚠️ Found pending uploads, clearing them...")
            self.clear_upload_button()

        print("🔍 Looking for Upload button...")
        upload_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(),'Upload')])[2]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", upload_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", upload_btn)
        print("✅ Clicked Upload button") 
        time.sleep(5)
        
    def upload_files(self, file1_path, file2_path):
        """
        Upload files to the platform.
        
        Args:
            file1_path: Path to first file (e.g., sample.mp3)
            file2_path: Path to second file (e.g., sample.mp4)
        """
        print("📂 Preparing to upload files...")
        file_input = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='files']"))
        )
        
        # Get absolute paths
        file1 = os.path.abspath(file1_path)
        file2 = os.path.abspath(file2_path)
        
        # Verify files exist
        print(f"📄 File 1 path: {file1}")
        print(f"✓ File 1 exists: {os.path.exists(file1)}")
        print(f"📄 File 2 path: {file2}")
        print(f"✓ File 2 exists: {os.path.exists(file2)}")
        
        if not os.path.exists(file1):
            raise FileNotFoundError(f"File not found: {file1}")
        if not os.path.exists(file2):
            raise FileNotFoundError(f"File not found: {file2}")
        
        file_input.send_keys(f"{file1}\n{file2}")
        print("📂 Files uploaded successfully")
        time.sleep(5)

    def click_metadata_button(self):
        """Click the Metadata buton if visible"""
        print("Looking for metadata button")
        metadeta_button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//button[@title="add files to metadata"]'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", metadeta_button)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", metadeta_button)
        print("✅ Clicked Metadata button")
        time.sleep(5)
         #//button[@title="add files to metadata"]
        
    def click_srt_upload_button(self):
        """Click the SRT upload button."""
        print("🔍 Looking for SRT upload button...")
        srt_upload_btn = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='px-3']"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", srt_upload_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", srt_upload_btn)
        print("✅ Clicked SRT upload button")
        time.sleep(5)
        
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
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Post Title']"))
        )
        print("📝 Filling Post Title...")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", post_title_input)
        time.sleep(1)
        post_title_input.clear()
        time.sleep(0.5)
        post_title_input.send_keys(post_title)
        print(f"✅ Post Title set to: '{post_title}'")
        time.sleep(2)
        
        # Fill Title
        print("📝 Filling Title...")
        title_input = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Title']"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", title_input)
        time.sleep(1)
        title_input.clear()
        time.sleep(0.5)
        title_input.send_keys(title)
        print(f"✅ Title set to: '{title}'")
        time.sleep(2)
        
        # Fill Description
        print("📝 Filling Description...")
        description_textarea = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Description']"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", description_textarea)
        time.sleep(1)
        description_textarea.clear()
        time.sleep(0.5)
        description_textarea.send_keys(description)
        print(f"✅ Description set to: '{description}'")
        time.sleep(3)
        
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
                time.sleep(1)
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
                time.sleep(1)
                if not speech_to_text_checkbox.is_selected():
                    self.driver.execute_script("arguments[0].click();", speech_to_text_checkbox)
                    print("✅ SpeechToText checkbox selected (no mp4 detected)")
                else:
                    print("✅ SpeechToText checkbox already selected")
            except:
                print("❌ Error: SpeechToText checkbox not found")
        
        time.sleep(3)
        
    def click_submit_button(self):
        """Click the Submit button."""
        print("📤 Clicking Submit button...")
        submit_btn = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='px-3']"))
        )
        self.driver.execute_script("arguments[0].click();", submit_btn)
        print("✅ Submit button clicked")
        time.sleep(5)
        
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            
    def run_full_workflow(self, class_text, file1_path, file2_path, post_title, title, description):
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
            self.click_class_text(class_text)
            self.click_upload_button()
            self.upload_files(file1_path, file2_path)
            try:
                self.click_srt_upload_button()
            except:  
                self.click_metadata_button() #//button[@title="add files to metadata"]
            # Submit twice as in original code
            time.sleep(2)
            self.fill_form(post_title, title, description)
            self.click_submit_button()
            
            self.fill_form(post_title, title, description)
            self.click_submit_button()
            
            time.sleep(10)
            print("🎉 All tasks completed successfully!")
            time.sleep(3)
            
        finally:
            self.close()


# Example usage
if __name__ == "__main__":
    uploader = DataNextUploader()
    
    # Get script directory for file paths
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file1 = os.path.join(script_dir, "sample.mp3")
    file2 = os.path.join(script_dir, "sample.mp4")
    
    uploader.run_full_workflow(
        class_text='Only',
        file1_path=file1,
        file2_path=file2,
        post_title='Testing',
        title='testing',
        description='raspotin lover of russian'
    )
