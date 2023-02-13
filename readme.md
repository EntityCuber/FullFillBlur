# FullFillBlur

![preview](https://user-images.githubusercontent.com/61630792/218519033-9272a3e0-629f-4f4e-8fbc-155d6769622d.jpg)

FullFillBlur is a system tray application that eliminates black borders when setting a wallpaper by using a blurred version of the wallpaper to fill the background. This way, your wallpaper will fit your screen without any unsightly borders. You can adjust the blur amount and dim amount of the background image to your liking.

## Features
-   Set slideshow of wallpapers
-   Blur and dim adjustments for the background image

## Running the Application

1.  Clone the repository:
```
$ git clone https://github.com/EntityCuber/FullFillBlur.git
```

2.  Navigate to the repository directory:
```
$ cd FullFillBlur
```

3.  Install Python dependencies:
```
$ pip install -r requirements.txt
```

4.  Running FullFillBlur:
```
$ python main.py`
```

### Building with PyInstaller (Recommended)

Building the application with PyInstaller is recommended as it enables the "Run at Startup" option. To build the application, follow these steps after cloning the repo:

1.  Install PyInstaller:
```
$ pip install pyinstaller
```

2.  Run the `freeze_with_pyinstaller.bat` file to build the executable:
```
$ freeze_with_pyinstaller.bat
```

The executable will be located in the `dist` directory.