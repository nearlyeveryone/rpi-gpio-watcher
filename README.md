# rpi-gpio-watcher
The project is divided into three parts: the Angular5 project(front end), the .NET Core 2.0 (back end), and the python script. The website’s static files and API is served through the reverse proxy, NGINX. The website implements authentication through JSON web tokens and is additionally enforces SSL through the HTTPS protocol. A webcam stream is also served behind authentication and uses the embedded hardware decoder to encode the video feed using FFMPEG that is built with OpenMAX IL H.264 support.

