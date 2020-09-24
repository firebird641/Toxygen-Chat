# Toxygen-Chat: Python-based Tox Client (custom version)

This is a custom version of the Toxygen Messenger App. It contains a modified source of Toxygen (based on the original project https://github.com/toxygen-project/toxygen) and a built version of it.
There is also a Plugin directory for this specific client.

## Running the Source version

Please follow the instructions here: https://github.com/toxygen-project/toxygen/blob/develop/docs/install.md
You need to install toxcore in order to run Toxygen-Chat from source.

## Running the Built version

Simply mark the binary toxygen file as an executable and run it.

## Building from Source

Go to the 'source' folder and make sure everything is running. Then type in:

~~~
pyinstaller --windowed --icon images/icon.ico main.py
~~~

Next, copy the following directories to ./dist/main:
- images
- sounds
- translations
- styles
- smileys
- stickers
- plugins

Then rename the ./dist/main/main binary to 'toxygen'.
Copy the 'main' directory to wherever you need it.

## Generating a Debian-Package (.deb)

Enter to the 'built' folder, and run:

~~~
dpkg-deb --build toxygen
~~~

The output should be a toxygen.deb file.

