import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datanext_uploader import DataNextUploader


class DataNextPDFUploader(DataNextUploader):
    """
    Extends DataNextUploader to handle PDF uploads with simplified form submission.
    """
    
    def upload_pdf(self, pdf_path):
        """
        Upload a single PDF file to the platform.
        
        Args:
            pdf_path: Path to the PDF file
        """
        print("📂 Preparing to upload PDF...")
        file_input = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='files']"))
        )
        
        # Get absolute path
        pdf_file = os.path.abspath(pdf_path)
        
        # Verify file exists
        print(f"📄 PDF path: {pdf_file}")
        print(f"✓ PDF exists: {os.path.exists(pdf_file)}")
        
        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"PDF not found: {pdf_file}")
        
        file_input.send_keys(pdf_file)
        print("📂 PDF uploaded successfully")
        time.sleep(5)

        print("🔍 Looking for SRT upload button...")
        srt_upload_btn = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='px-3']"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", srt_upload_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", srt_upload_btn)
        print("✅ Clicked SRT upload button")

        time.sleep(5)
    
    def fill_pdf_form(self, post_title, title, description):
        """
        Fill the form fields for PDF upload (simpler than media upload).
        
        Args:
            post_title: Text for Post Title field
            title: Text for Title field
            description: Text for Description field
        """
        # Fill Post Title
        print("📝 Filling Post Title...")
        post_title_input = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Post Title']"))
        )
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
    
    def run_pdf_workflow(self, class_text, pdf_path, post_title, title, description):
        """
        Run the complete PDF upload workflow.
        
        Args:
            class_text: Text to click in the navigation
            pdf_path: Path to PDF file
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
            self.upload_pdf(pdf_path)
            
            # Fill form once and submit
            time.sleep(2)
            self.fill_pdf_form(post_title, title, description)
            self.click_submit_button()
            
            time.sleep(10)
            print("🎉 PDF upload completed successfully!")
            time.sleep(3)
            
        finally:
            self.close()


# Example usage
if __name__ == "__main__":
    uploader = DataNextPDFUploader()
    
    # Get script directory for file path
    script_dir = os.path.dirname(os.path.realpath(__file__))
    pdf_file = os.path.join(script_dir, "sample.pdf")
    
    uploader.run_pdf_workflow(
        class_text='Only',
        pdf_path=pdf_file,
        post_title='Test PDF Document',
        title='Sample PDF',
        description='This is a test PDF upload'
    )