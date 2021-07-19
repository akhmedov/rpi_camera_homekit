## RPi WiFi connection via Teletype over wpa_supplicant demon
sudo vim /etc/wpa_supplicant/wpa_supplicant.conf
wpa_cli -i wlan0 reconfigure

## Ubuntu P2P Ethernet connection with RPi
1. Plug RG45 and change connection type of IPv4 to «Shared with other device»
2. sudo arp-scan -I enp4s0 —localnet

## Available resolutions of RPi Camera V2 for aspect ratio 4:3:  
1. 320 x 240 (240p)
2. 480 x 360 (360p, SD)
3. 640 x 480 (480p)
4. 960 x 720 (720p, HD)
5. 1440 x 1080 (1080p, FHD)

## VLC streamer over UDP
https://raspberry-projects.com/pi/pi-hardware/raspberry-pi-camera/streaming-video-using-vlc-player
nohup raspivid -o - -t 0 -n -w 800 -h 600 -fps 30 | cvlc --rtsp-timeout 99999 -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8081/}' :demux=h264
connect with rtsp://xxx.xxx.xxx.:8081/

## Net socket stream over TCP
Send command for RPi:
nohup raspivid -n -t 0 -w 1440 -h 1080 -fps 30 -ih -fl -l -o - | nc -klvp 8081
Use «-ro 180» option for «raspivid» if wide is upside down
Recive commands on Ubuntu:
nc 192.168.31.122 8081 | mplayer -fps 200 -demuxer h264es -
Or video capture with OpenCV
cap = cv2.VideoCapture("tcp://192.168.31.122:8081")

## Install Homebridge for RPi
Install Homebridge and HomebridgeUI

Start HB service with WebUI
sudo hb-service install --user homebridge
install module for ffmpeg cameras
prepare configuration from config.json


activate motion triget via request http://192.168.31.106:8080/motion/motion?RPi%20Camera