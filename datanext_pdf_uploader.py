import os
from time import sleep
from random import randint

# from pydevd_file_utils import report
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from datanext_uploader import DataNextUploader


class DataNextPDFUploader(DataNextUploader):
    """
    Extends DataNextUploader to handle PDF uploads with simplified form submission.
    """

    def upload_pdf(self, pdf_path):
        print("📂 Preparing to upload PDF...")
        file_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='files']")))

        # Get absolute path
        pdf_file = os.path.abspath(pdf_path)

        # Verify file exists
        print(f'PDF path: {pdf_file}')
        print(f'PDF exists: {os.path.exists(pdf_file)}')

        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f'PDF not found: {pdf_file}')

        file_input.send_keys(pdf_file)
        print('PDF uploaded successfully')
        sleep(5)

        print('Looking for SRT upload button...')
        srt_upload_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='px-3']")))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", srt_upload_btn)
        sleep(1)
        self.driver.execute_script("arguments[0].click();", srt_upload_btn)
        print('Clicked SRT upload button')
        sleep(5)

    def fill_pdf_form(self, post_title: str, title: str, description: str):
        """
        Fill the form fields for PDF upload (simpler than media upload).
        
        Args:
            post_title: Text for Post Title field
            title: Text for Title field
            description: Text for Description field
        """
        # Fill Post Title
        print('Filling Post Title...')
        post_title_input = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='Post Title']")))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", post_title_input)
        sleep(1)
        post_title_input.clear()
        sleep(0.5)
        post_title_input.send_keys(post_title)
        print(f'Post Title set to: {post_title}')
        sleep(2)

        # Fill Title
        print('Filling Title...')
        title_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Title']")))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", title_input)
        sleep(1)
        title_input.clear()
        sleep(0.5)
        title_input.send_keys(title)
        print(f'Title set to: {title}')
        sleep(2)

        # Fill Description
        print('Filling Description...')
        description_textarea = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Description']")))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", description_textarea)
        sleep(1)
        description_textarea.clear()
        sleep(0.5)
        description_textarea.send_keys(description)
        print(f'Description set to: {description}')
        sleep(3)

    def run_pdf_workflow(self, class_text: str, pdf_path, post_title: str, title: str, description: str):
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

            self.click_class_text(class_text=class_text)
            self.click_upload_button()
            self.upload_pdf(pdf_path=pdf_path)

            # Fill form once and submit
            sleep(2)
            self.fill_pdf_form(post_title, title, description)
            self.click_submit_button()

            # Creating a new folder with the name of addition of " report"
            # class_text_report = f'{class_text} report'
            # class_text_locator = f'//div[contains(@class,"wrapper")]//p[translate(@title,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="{class_text_report.lower()}"]'
            # if not self.is_element_available(locator=class_text_locator, timeout=15):
            #     self.create_new_folder(class_text=class_text_report)
            #
            # # opening the main class name again
            # sleep(randint(a=1, b=3))
            # self.click_class_text(class_text=class_text)
            #
            # # Sharing the file
            # if self.is_element_available(locator='.justify-center.gap-2 [type="button"]'):
            #     self.driver.find_element(by=By.CSS_SELECTOR, value='.justify-center.gap-2 [type="button"]').click()
            #     sleep(randint(a=1, b=3))
            #     if self.is_element_available(locator='#context-menu-parent'):
            #         self.driver.find_element(by=By.XPATH, value="//button[contains(text(), 'Share')]").click()
            #         sleep(randint(a=1, b=3))
            #
            #     # In-App Share
            #     if self.is_element_available(locator='#portal [type="radio"]'):
            #         self.driver.find_element(by=By.CSS_SELECTOR, value='#portal [type="radio"]').click()
            #         sleep(randint(a=1, b=3))
            #
            #         # Required folder
            #         locator = f'//p[translate(@title,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="{class_text_report.lower()}"]/ancestor::div[contains(@class,"hover:bg-slate-100")]'
            #         if self.is_element_available(locator=locator):
            #             main_element = self.driver.find_element(by=By.XPATH, value=locator)
            #             main_element.find_element(by=By.CSS_SELECTOR, value='svg.absolute').click()
            #             sleep(randint(a=1, b=3))
            #
            #             # share button
            #             locator = '[type="button"].text-slate-500.rounded-full'
            #             if self.is_element_available(locator=locator):
            #                 self.driver.find_element(by=By.CSS_SELECTOR, value=locator).click()
            #                 sleep(randint(a=1, b=3))
            #                 print('PDF is shared')

            print('PDF upload completed successfully!')
            sleep(3)

        finally:
            self.close()


# Example usage
if __name__ == '__main__':
    uploader = DataNextPDFUploader()

    # Get script directory for file path
    script_dir = os.path.dirname(os.path.realpath(__file__))
    pdf_file = os.path.join(script_dir, 'sample.pdf')

    uploader.run_pdf_workflow(
        class_text='DSA',
        pdf_path=pdf_file,
        post_title='Test PDF Document',
        title='Sample PDF',
        description='This is a test PDF upload'
    )
