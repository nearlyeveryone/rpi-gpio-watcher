# rpi-gpio-watcher
The project is divided into three parts: the Angular5 project(front end), the .NET Core 2.0 (back end), and the python script. The website’s static files and API is served through the reverse proxy, NGINX. The website implements authentication through JSON web tokens and is additionally enforces SSL through the HTTPS protocol. A webcam stream is also served behind authentication and uses the embedded hardware decoder to encode the video feed using FFMPEG that is built with OpenMAX IL H.264 support.

Currently the python script is setup to control devices for an automated chicken coop.

## Description
The front end Angular5 application is responsible for controlling each configured GPIO control. The front end allows the creation of new GPIO controls as well was the editing of pre existing controls. A GPIO control consists of the following properties:
The front end Angular5 application is responsible for controlling each configured GPIO control. The front end allows the creation of new GPIO controls as well was the editing of pre existing controls. A GPIO control consists of the following properties:

```
class GpioControl 
    controlModelId: number;
    description: string;
    status: string;
    tooltip: string;
    parameters: string
    value: boolean;
```

On the front end, only the Description, Tooltip, Parameters, and Value can be configured. The controlModelId is controlled by the backend while the Status is controlled by the python script. The front end allows the user to configure the state of the GPIO control by turning it ON or OFF in addition to controlling the parameters that are passed to the python script.

The .NET Core 2.0 application on the back end is responsible for authentication and serving the GPIO control data as well as providing an REST API for modifying and retrieving the objects. This application also serves the authenticated HLS video stream data from the webcam. This video data is encoded using FFMPEG using the RPi’s hardware encoder, streamed to the NGINX RTMP server, and converted into an HLS stream. The GPIO controls are stored in a SQLite database to provide an easily configurable and deployable storage solution.

The python script also directly accesses the SQLite database to retrieve and update the GPIO Control objects. In retrospect, it may have been better to access the database through the REST API created in the .NET Core application (due to how the python script was written it would be relatively easy to achieve). The python script reads the GPIO control objects and finally consumes the objects and reads their parameters in order to modify the GPIO outputs on the RPi. This involves the Status of the object to be modified and, in some cases, the object is switched back off once the GPIO process completes.

One control is the automatic chicken feeder control. When this control is turned on, it activates a 12v DC motor for a period of time (duration is determined by parameters), plays a sound to help classically condition the chickens, and turns back off. The status of the GPIO control is updated as this process occurs which the user can view through the web application.

Another control is the automatic chicken door control, this control would ideally be hooked up a linear actuator that opens and closes a door. This time that is door closes is based on the sunrise and sunset with the addition of being able to be tweaked by parameters set on the web application. When the GPIO control is set off, the door is then controlled by another parameter to determine its opened/closed state, acting as an override.

In addition to the two other controls, the webcam’s rotation can be controlled on two axes using two servos mounted on a bracket. The process of setting up a new control is as easy as creating the new control on the web application and configuring how it interacts with the GPIO in the python script. For example, if one would want to control a light in a chicken coop, all they would need to do is create a control, consume it in the python script, and hook up a relay to the GPIO pins on the RPi. All the actions of these GPIO operations be viewed from the webcam, creating quite an entertaining experience.
On the front end, only the Description, Tooltip, Parameters, and Value can be configured. The controlModelId is controlled by the backend while the Status is controlled by the python script. The front end allows the user to configure the state of the GPIO control by turning it ON or OFF in addition to controlling the parameters that are passed to the python script.
The .NET Core 2.0 application on the back end is responsible for authentication and serving the GPIO control data as well as providing an REST API for modifying and retrieving the objects. This application also serves the authenticated HLS video stream data from the webcam. This video data is encoded using FFMPEG using the RPi’s hardware encoder, streamed to the NGINX RTMP server, and converted into an HLS stream. The GPIO controls are stored in a SQLite database to provide an easily configurable and deployable storage solution.

The python script also directly accesses the SQLite database to retrieve and update the GPIO Control objects. In retrospect, it may have been better to access the database through the REST API created in the .NET Core application (due to how the python script was written it would be relatively easy to achieve). The python script reads the GPIO control objects and finally consumes the objects and reads their parameters in order to modify the GPIO outputs on the RPi. This involves the Status of the object to be modified and, in some cases, the object is switched back off once the GPIO process completes.
One control is the automatic chicken feeder control. When this control is turned on, it activates a 12v DC motor for a period of time (duration is determined by parameters), plays a sound to help classically condition the chickens, and turns back off. The status of the GPIO control is updated as this process occurs which the user can view through the web application.

Another control is the automatic chicken door control, this control would ideally be hooked up a linear actuator that opens and closes a door. This time that is door closes is based on the sunrise and sunset with the addition of being able to be tweaked by parameters set on the web application. When the GPIO control is set off, the door is then controlled by another parameter to determine its opened/closed state, acting as an override.

In addition to the two other controls, the webcam’s rotation can be controlled on two axes using two servos mounted on a bracket. The process of setting up a new control is as easy as creating the new control on the web application and configuring how it interacts with the GPIO in the python script. For example, if one would want to control a light in a chicken coop, all they would need to do is create a control, consume it in the python script, and hook up a relay to the GPIO pins on the RPi. All the actions of these GPIO operations be viewed from the webcam, creating quite an entertaining experience.


## Scripts and config files
### FFMPEG Script (setup as a service)
```bash
#!/bin/sh

ffmpeg  -i /dev/video0                          \
        -framerate 15                           \
        -video_size 640x480                     \
        -vcodec h264_omx                        \
        -b:v 2M -maxrate 3M                     \
        -bufsize 10K                            \
        -f flv rtmp://localhost/show/stream     \
```
### ngnix.conf
```

#user  nobody;
worker_processes  1;

error_log  logs/error.log;
error_log  logs/error.log  notice;
error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}

# RTMP configuration
rtmp {
    server {
        listen 1935; # Listen on standard RTMP port
        chunk_size 4000;

        application show {
            live on;
            # Turn on HLS
            hls on;
            hls_path /stream/hls/;
            hls_fragment 3;
            hls_playlist_length 12;
            # disable consuming the stream from nginx as rtmp
            deny play all;
        }
    }
}

http {
    sendfile off;
    tcp_nopush on;
    #aio on;
    directio 512;

    server {
        listen 80;
        listen [::]:80;
        server_name domain.com;
        return 301 https://$server_name$request_uri;
    }


    server {
        listen 443 ssl;
        listen [::]:443 ssl;
	    server_name domain.com;

        ssl_certificate /etc/letsencrypt/live/domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/domain.com/privkey.pem;
        
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;
        ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
        ssl_ecdh_curve secp384r1;
        ssl_session_cache shared:SSL:10m;
        ssl_session_tickets off;
        ssl_stapling on;
        ssl_stapling_verify on;
        
        ssl_dhparam /etc/ssl/certs/dhparam.pem;

        location /api {
            proxy_pass http://localhost:5000;
            rewrite ^/api/(.*) /$1 break;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection keep-alive;
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;

            proxy_redirect off;
            proxy_set_header X-Real-IP 		$remote_addr;
            proxy_set_header X-Forwarded-For	$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
                        
        }
        location / {
            try_files $uri $uri/ /index.html;
            root /home/pi/site;
        }
    }
}
```
