# led_server

![Philingvo Logo](https://user-images.githubusercontent.com/108828980/177620920-a224e706-581a-4cfe-a0db-082f95e7a01a.png)

The **LED server** is a main software part of the **Philingvo** project: making a LED ticker based on Rapberry Pi 3 and WS2812B matrices.

The main task is transforming text messages to pulse-width modulation signals sending to the LED panel for rendering.
These text messages can be sent to this sever as POST-requests via http protocol. 
For some working processes the server can use volumes of saved messages, fetches and sends them automatically. 
Also it makes requests to the Dictionary Server, handles responses and prepares text messages to show.
The server handles control commands by a user or scripts, for instance, choosing working processes.
Control commands can be sent from this server via its native web interface either the Graphic Interface Application.

All project's software parts:
1. [LED Server](https://github.com/philingvo/led_server)
2. [Graphic Interface Application](https://github.com/philingvo/remote_unit_interface)
3. [Dictionary](https://github.com/philingvo/dictionary)

project.philingvo@gmail.com

https://youtube.com/channel/UCkObkfT1lGT-y0SOVYLwsvg

https://www.flickr.com/photos/196150690@N08/
