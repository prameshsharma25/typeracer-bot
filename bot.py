from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located
from PIL import Image
import numpy
import pytesseract
import pyautogui
import enchant
import time


class typeracer_bot:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        self.dictionary = enchant.Dict("en_US")
        self.driver = Chrome(
            executable_path="C:\\Program Files (x86)\\chromedriver.exe")
        self.driver.get("https://play.typeracer.com/")
        self.driver.maximize_window()

    def find_practice_mode(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(presence_of_all_elements_located(
                (By.XPATH, "//*[@id=\"gwt-uid-2\"]/a")))
        except TimeoutException:
            self.__del__()

    def click_practice_button(self):
        practice_yourself_button = self.driver.find_element_by_xpath(
            "//*[@id=\"gwt-uid-2\"]/a")
        practice_yourself_button.click()

    def grab_pixels_from_window_screen(self):
        # top half of maximized screen
        self.driver.save_screenshot("screen.png")
        top_half_of_window = Image.open("screen.png")
        displacement_height = int(top_half_of_window.height * 0.8)
        self.driver.execute_script(
            f"window.scrollTo(0, {displacement_height})")

        # bottom half of maximized screen
        self.driver.save_screenshot("screen.png")
        bottom_half_of_screen = Image.open("screen.png")
        screen = numpy.array(bottom_half_of_screen, dtype=numpy.uint8)
        pixels = [list(pixel_row) for pixel_row in screen]
        return [bottom_half_of_screen.width, pixels]

    def locate_blue_background(self, image_data):
        screen_width = image_data[0]
        pixel_row = image_data[1]
        left, top = 0, 0

        for pixels in pixel_row:
            for pixel in pixels:
                if left == screen_width:
                    top += 1
                    left = 0

                if pixel[0] == 245 and pixel[1] == 251 and pixel[2] == 255:
                    return [left, top]

                left += 1

        return [0, 0]  # default value

    def take_screenshot_of_text(self, coordinates):
        text_image = Image.open("screen.png")
        text_image = text_image.crop(
            (coordinates[0], coordinates[1], coordinates[0] + 910, coordinates[1] + 150))
        text_image.save("text.png")

    def process_text_from_image(self):
        return pytesseract.image_to_string(Image.open("text.png"))

    def generate_characters_from_text(self, text):
        for word in text.split(" "):
            yield(word)

    def spell_checker(self, word):
        phrase = ""
        for char in range(len(word)):
            phrase += word[char]
            if self.dictionary.check(phrase) and self.dictionary.check(word[char+1:]):
                return f" {phrase} {word[char+1]} "

        return ""  # in case two words can't be found

    def automate_keyboard_typing(self):
        paragraph = self.process_text_from_image()
        while True:
            for word in self.generate_characters_from_text(paragraph):
                if self.dictionary.check(word):
                    pyautogui.write(word)
                    pyautogui.write(" ", interval=0.01)
                else:
                    pyautogui.write(self.spell_checker(word))
            break

    def __del__(self):
        self.driver.quit()


def main():
    bot = typeracer_bot()
    bot.find_practice_mode()
    bot.click_practice_button()
    time.sleep(6)
    arr = bot.grab_pixels_from_window_screen()
    location = bot.locate_blue_background(arr)
    bot.take_screenshot_of_text(location)
    bot.automate_keyboard_typing()


if __name__ == "__main__":
    main()
