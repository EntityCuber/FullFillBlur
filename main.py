from pystray import Icon as icon, Menu as menu, MenuItem as item
import threading
import wallpaper_manager
import sys
import ctypes
import os.path
import logging

from PIL import Image

from tendo import singleton


# sets logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


try:

    me = singleton.SingleInstance()  # will sys.exit(-1) if other instance is running

    # sets dark mode for pystray
    ctypes.windll["uxtheme.dll"][135](1)

    class TrayIcon:
        def __init__(self, wallpaper_manager):
            # disables run_at_startup menu
            self.run_at_startup_menu_enabled = False

            self.wallpaper_manager = wallpaper_manager
            self.icon = icon(
                name="Full Fill Blur",
                icon=Image.open(self.resource_path("tray_icon.png")),
                title="Full Fill Blur",
            )

            self.menu = menu(
                item(
                    "Run Slideshow",
                    self.wallpaper_manager.select_run_slideshow,
                    checked=lambda item: self.wallpaper_manager.run_slideshow,
                ),
                item(
                    "Interval",
                    menu(
                        item(
                            "1 minute",
                            self.wallpaper_manager.select_interval,
                            checked=lambda item: self.wallpaper_manager.timeout == 60,
                        ),
                        item(
                            "10 minutes",
                            self.wallpaper_manager.select_interval,
                            checked=lambda item: self.wallpaper_manager.timeout
                            == 60 * 10,
                        ),
                        item(
                            "30 minutes",
                            self.wallpaper_manager.select_interval,
                            checked=lambda item: self.wallpaper_manager.timeout
                            == 60 * 30,
                        ),
                        item(
                            "1 hour",
                            self.wallpaper_manager.select_interval,
                            checked=lambda item: self.wallpaper_manager.timeout
                            == 60 * 60,
                        ),
                        item(
                            "6 hours",
                            self.wallpaper_manager.select_interval,
                            checked=lambda item: self.wallpaper_manager.timeout
                            == 60 * 60 * 6,
                        ),
                        item(
                            "1 day",
                            self.wallpaper_manager.select_interval,
                            checked=lambda item: self.wallpaper_manager.timeout
                            == 60 * 60 * 24,
                        ),
                    ),
                ),
                item(
                    "Slideshow Order",
                    menu(
                        item(
                            "Random",
                            self.wallpaper_manager.select_sort_method,
                            checked=lambda item: self.wallpaper_manager.sort_method
                            == "random",
                        ),
                        item(
                            "Date Modified",
                            menu(
                                item(
                                    "Ascending",
                                    self.wallpaper_manager.select_sort_method,
                                    checked=lambda item: self.wallpaper_manager.sort_method
                                    == "date modified asc",
                                ),
                                item(
                                    "Descending",
                                    self.wallpaper_manager.select_sort_method,
                                    checked=lambda item: self.wallpaper_manager.sort_method
                                    == "date modified desc",
                                ),
                            ),
                        ),
                    ),
                ),
                menu.SEPARATOR,
                item(
                    "Blur Amount",
                    menu(
                        item(
                            "3",
                            self.wallpaper_manager.select_blur_amount,
                            checked=lambda item: str(self.wallpaper_manager.blur_amount)
                            == item.text,
                        ),
                        item(
                            "8",
                            self.wallpaper_manager.select_blur_amount,
                            checked=lambda item: str(self.wallpaper_manager.blur_amount)
                            == item.text,
                        ),
                        item(
                            "15",
                            self.wallpaper_manager.select_blur_amount,
                            checked=lambda item: str(self.wallpaper_manager.blur_amount)
                            == item.text,
                        ),
                    ),
                ),
                item(
                    "Dim",
                    menu(
                        item(
                            "0.0",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                        item(
                            "0.1",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                        item(
                            "0.2",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                        item(
                            "0.3",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                        item(
                            "0.4",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                        item(
                            "0.5",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                        item(
                            "0.6",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                        item(
                            "0.7",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                        item(
                            "0.8",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                        item(
                            "0.9",
                            self.wallpaper_manager.select_dim_amount,
                            checked=lambda item: str(self.wallpaper_manager.dim_amount)
                            == item.text,
                        ),
                    ),
                ),
                menu.SEPARATOR,
                item(
                    "Run at startup",
                    self.wallpaper_manager.select_run_at_startup,
                    checked=lambda item: self.wallpaper_manager.run_at_startup,
                    enabled=lambda item: self.run_at_startup_menu_enabled,
                ),
                menu.SEPARATOR,
                item(
                    "Next",
                    self.wallpaper_manager.select_next,
                    default=True,
                ),
                item("Select folder", self.wallpaper_manager.select_folder),
                item("Select file", self.wallpaper_manager.select_file),
                menu.SEPARATOR,
                item("Quit", self.on_quit),
            )

            self.icon.menu = self.menu

        def run(self):
            self.wallpaper_thread = threading.Thread(target=self.wallpaper_manager.run)
            self.wallpaper_thread.start()
            self.icon.run_detached()

        def on_quit(self):
            self.wallpaper_manager.stop()
            self.wallpaper_thread.join()  # waiting for the wallpaper_manager thread to finish before quitting to avoid ghost threads
            self.icon.stop()

        # for pyinstaller to work with files
        def resource_path(self, relative_path):
            """Get absolute path to resource, works for dev and for PyInstaller"""
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
                self.run_at_startup_menu_enabled = True
            except Exception:
                base_path = os.path.abspath(".")
                self.run_at_startup_menu_enabled = False

            return os.path.join(base_path, relative_path)

    if __name__ == "__main__":
        wallpaper_manager = wallpaper_manager.WallpaperManager()
        tray_icon = TrayIcon(wallpaper_manager)
        tray_icon.run()

except Exception as e:
    handler = logging.FileHandler("error.log")
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        "%(asctime)s\n%(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.error(e, exc_info=True)
