import time
import os
import tkinter as tk
from tkinter import filedialog
import win32api
import cv2
import numpy as np
import ctypes
import random
import toml
import win32com.client
import sys


class WallpaperManager:
    def __init__(self):

        # Read config from toml file
        with open("config.toml", "r") as f:
            data = toml.load(f)

        self.timeout = data["timeout"]
        self.run_slideshow = data["run_slideshow"]
        self.blur_amount = data["blur_amount"]
        self.dim_amount = data["dim_amount"]
        self.folder_path = data["folder_path"]
        self.wallpaper_path = data["wallpaper_path"]
        self.sort_method = data["sort_method"]

        self.wallpapers = []

        if self.folder_path:
            self.update_wallpapers_list(self.folder_path)
        # else:
        #     # tries to load current wallpapers location
        #     self.folder_path = os.path.join(
        #         os.path.expanduser("~"),
        #         "AppData",
        #         "Roaming",
        #         "Microsoft",
        #         "Windows",
        #         "Themes",
        #         "CachedFiles",
        #     )
        #     self.update_wallpapers_list(self.folder_path)

        self.quit = False
        self.i = 0

        # achieves wallpaper index history
        if self.wallpaper_path in self.wallpapers:
            print("wallpaper found in current wallpapers list")
            self.index = self.wallpapers.index(self.wallpaper_path)
            print(f"index is {self.index}")
        else:
            self.index = 0

        self.startup_folder = os.path.join(
            os.path.expanduser("~"),
            "AppData",
            "Roaming",
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup",
        )
        self.shortcut_name = "Full Fill Blur.lnk"

        self.run_at_startup = os.path.exists(
            os.path.join(self.startup_folder, self.shortcut_name)
        )

        self.screen_width, self.screen_height = win32api.GetSystemMetrics(
            0
        ), win32api.GetSystemMetrics(1)

    def resize_to_display(self, img):
        height, width = img.shape[:2]
        aspect_ratio = float(width) / float(height)

        if aspect_ratio >= 1:
            # wide image
            new_width = int(self.screen_width)
            new_height = int(self.screen_width / aspect_ratio)
            if new_height > self.screen_height:
                new_height = int(self.screen_height)
                new_width = int(self.screen_height * aspect_ratio)
        else:
            # portrait image
            new_height = int(self.screen_height)
            new_width = int(self.screen_height * aspect_ratio)
            if new_width > self.screen_width:
                new_width = int(self.screen_width)
                new_height = int(self.screen_width / aspect_ratio)

        resized_img = cv2.resize(
            img, (new_width, new_height), interpolation=cv2.INTER_CUBIC
        )
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_RGB2RGBA)
        return resized_img

    def add_transparent_borders(self, img, screen_width, screen_height):
        transparent = np.zeros((screen_height, screen_width, 4), dtype=np.uint8)
        transparent[:, :, 3] = 0  # set the alpha channel to fully opaque
        height, width = img.shape[:2]
        x_offset = int((screen_width - width) / 2)
        y_offset = int((screen_height - height) / 2)
        transparent[y_offset : y_offset + height, x_offset : x_offset + width] = img
        return transparent

    def add_blurred_background(self, img, screen_width, screen_height, blur_amount):
        width, height = img.shape[1], img.shape[0]

        # Calculate aspect ratio of image
        aspect_ratio = height / width

        # Calculate aspect ratio of screen
        screen_aspect_ratio = screen_height / screen_width

        # Determine the larger dimension to stretch
        if aspect_ratio > screen_aspect_ratio:
            stretched_width = screen_width
            stretched_height = stretched_width * aspect_ratio
        else:
            stretched_height = screen_height
            stretched_width = stretched_height / aspect_ratio

        # Stretch the image to the screen size
        stretched_img = cv2.resize(img, (int(stretched_width), int(stretched_height)))

        # Crop the stretched image to the screen size
        mid_x, mid_y = int(stretched_width / 2), int(stretched_height / 2)
        sw2, sh2 = int(screen_width / 2), int(screen_height / 2)
        crop_img = stretched_img[mid_y - sh2 : mid_y + sh2, mid_x - sw2 : mid_x + sw2]

        # darken cropped image

        crop_img_dark = crop_img * (1.0 - self.dim_amount)

        # Blur the cropped image
        blurred_img = cv2.blur(crop_img_dark, (blur_amount, blur_amount))

        return blurred_img

    def set_wallpaper(self, index):
        if self.wallpapers:
            img = cv2.imread(self.wallpapers[index])
            resized_img = self.resize_to_display(img)
            transparent_img = self.add_transparent_borders(
                resized_img, self.screen_width, self.screen_height
            )

            blurred_img = self.add_blurred_background(
                img, self.screen_width, self.screen_height, self.blur_amount
            )

            result = np.zeros(
                (transparent_img.shape[0], transparent_img.shape[1], 3),
                dtype=np.uint8,
            )
            alpha = transparent_img[:, :, 3] / 255.0
            result = (1.0 - alpha[:, :, np.newaxis]) * blurred_img + alpha[
                :, :, np.newaxis
            ] * transparent_img[:, :, :3]

            result = np.uint8(result)

            cv2.imwrite("output.png", result)

            path = os.path.abspath("output.png")

            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
        else:
            print("wallpaper list empty")

    def update_wallpapers_list(self, folder_path):
        self.wallpapers = []
        self.index = 0
        if folder_path:
            for filename in os.listdir(folder_path):
                if (
                    filename.endswith(".jpg")
                    or filename.endswith(".png")
                    or filename.endswith(".jpeg")
                ):
                    self.wallpapers.append(os.path.join(folder_path, filename))

        # sort wallpaper list accordingly
        if self.sort_method == "random":
            random.shuffle(self.wallpapers)
        elif self.sort_method == "date modified asc":
            self.wallpapers.sort(key=lambda path: os.stat(path).st_mtime)
        elif self.sort_method == "date modified desc":
            self.wallpapers.sort(key=lambda path: os.stat(path).st_mtime, reverse=True)

    def select_interval(self, icon, item):
        # it resets timer but doesnt change wallpaper by triggering  if self.i % self.timeout == 0:
        self.i = 1
        if item.text == "1 minute":
            self.timeout = 60
        elif item.text == "10 minutes":
            self.timeout = 60 * 10
        elif item.text == "30 minutes":
            self.timeout = 60 * 30
        elif item.text == "1 hour":
            self.timeout = 60 * 60
        elif item.text == "6 hours":
            self.timeout = 60 * 60 * 6
        elif item.text == "1 day":
            self.timeout = 60 * 60 * 24

        self.update_config_file()

    def select_blur_amount(self, icon, item):
        self.blur_amount = int(item.text)
        self.update_config_file()
        self.set_wallpaper(self.index - 1)

    def select_dim_amount(self, icon, item):
        self.dim_amount = float(item.text)
        self.update_config_file()
        self.set_wallpaper(self.index - 1)

    def select_sort_method(self, icon, item):
        if item.text == "Ascending":
            self.sort_method = "date modified asc"
        elif item.text == "Descending":
            self.sort_method = "date modified desc"
        elif item.text == "Random":
            self.sort_method = "random"

        self.update_config_file()

        self.update_wallpapers_list(self.folder_path)

    def select_next(self):
        self.i = 0

    def select_folder(self, icon, item):
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()

        if folder_path:
            self.folder_path = folder_path
        else:
            return

        self.update_wallpapers_list(self.folder_path)
        root.destroy()
        self.i = 0

        # if there is only one image in wallpaper list make slideshow false
        if len(self.wallpapers) <= 1:
            self.run_slideshow = False
            self.set_single_wallpaper()
        else:
            self.run_slideshow = True

        self.update_config_file()

    def set_single_wallpaper(self):
        if self.wallpapers:
            # sets wallpaper
            self.set_wallpaper(self.index)
            print(f"Wallpaper Set | index:{self.index}")

            # incrementing the index even tho its a single wallpaper cause
            # the amount and dim amount sets wallpaper again using index - 1
            if self.index != len(self.wallpapers) - 1:
                self.index += 1
            else:
                self.index = 0

    def select_file(self, icon, item):

        root = tk.Tk()
        root.withdraw()
        file = filedialog.askopenfile(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

        if not file:
            return

        # to avoid setting the image again the slideshow is stopped
        self.run_slideshow = False
        self.update_config_file()

        print(file.name)
        self.wallpapers = []
        self.wallpapers.append(file.name)
        self.index = 0
        root.destroy()
        self.i = 0

        self.set_single_wallpaper()

    def select_run_slideshow(self, icon, item):
        if self.run_slideshow:
            self.run_slideshow = False
        else:
            self.run_slideshow = True
        self.update_config_file()

    def select_run_at_startup(self):
        shortcut_path = os.path.join(self.startup_folder, self.shortcut_name)

        if self.run_at_startup:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            self.run_at_startup = False
        else:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            else:
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(shortcut_path)
                shortcut.TargetPath = sys.executable
                # shortcut.Arguments = os.path.join(os.getcwd(), "main.pyw")
                shortcut.WorkingDirectory = os.getcwd()
                shortcut.windowStyle = 7
                shortcut.save()
            self.run_at_startup = True

    def update_config_file(self):
        data = {
            "timeout": self.timeout,
            "run_slideshow": self.run_slideshow,
            "blur_amount": self.blur_amount,
            "dim_amount": self.dim_amount,
            "folder_path": self.folder_path,
            "wallpaper_path": self.wallpaper_path,
            "sort_method": self.sort_method,
        }

        with open("config.toml", "w") as f:
            toml.dump(data, f)

    def stop(self):
        self.quit = True

    # thread function
    def run(self):
        # loop that runs when wallpaper manager is running
        while True:
            while self.run_slideshow:
                # quit this loop
                if self.quit:
                    return

                # every self.timeout seconds change wallpaper
                if self.i % self.timeout == 0:
                    self.i = 0

                    if self.wallpapers:
                        # sets wallpaper
                        self.set_wallpaper(self.index)
                        # saves wallpaper path to config
                        self.wallpaper_path = self.wallpapers[self.index]
                        self.update_config_file()
                        print(f"Wallpaper Set | index:{self.index}")
                        if self.index != len(self.wallpapers) - 1:
                            self.index += 1
                        else:
                            self.index = 0
                self.i += 1

                print(f"{self.i}                 ", end="\r")
                time.sleep(1)
            # quit program
            if self.quit:
                return
            time.sleep(1)
