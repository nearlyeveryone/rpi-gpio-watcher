# rpi-gpio-watcher
The project is divided into three parts: the Angular5 project(front end), the .NET Core 2.0 (back end), and the python script. The website’s static files and API is served through the reverse proxy, NGINX. The website implements authentication through JSON web tokens and is additionally enforces SSL through the HTTPS protocol. A webcam stream is also served behind authentication and uses the embedded hardware decoder to encode the video feed using FFMPEG that is built with OpenMAX IL H.264 support.

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
