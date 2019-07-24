# WRIVCam
"Wooden Ragtag In-Vehicle Camera" - A dash camera for you car, consisting of a Raspberry Pi 3 B+, LEDs, and Push-buttons - all fitting inside a wooden box from A.C. Moore.

Dash Cameras are extremely useful: they can be used to capture evidence of accidents on the road, proving that it was not you, but the hooligan in front of you, that caused the collision. They can also be used to record clips of you driving down some awesome roads (like I-77 heading from Virginia into West Virginia). However, there's one problem: they're pretty expensive.

Behold, a cheap solution to the problem! I'm building this dash cam to address this issue: I would like to have a dash cam for the reasons I described above, but I don't want to pay too much for it. (I'm also using this as a way to learn about Raspberry Pis and improve my Python knowledge.)

## Features
The dash cam has (or will have) the following features:
* Passive Recording: Records video clips every 10 minutes, and stores up to an hour of footage. Afterwards, the oldest clip is overwritten with the next clip.
* Active Recording: Records a 10-minute clip instantly, by the press of a button. These clips are stored away from the passive-recording clips, to avoid deletion.
* Image Capturing: Via the click of a button, the dash cam will take a picture.
* LED Indicators: Multiple LEDs indicate the status of the camera's inner workings: one "running light" (when the camera is powered on), one "rolling light" (when the camera is recording, actively or passively), and one "auxiliary light" (an extra light for any features I may add in the future)
* Session Logging: The camera logs every "tick" of its main loop, marking any updates, errors, or hardware changes.
* CPU Temperature Detection: Since dash cams sit in cars all day long, I'm expecting the Raspberry Pi to get hot. If the CPU's temperature rises above some threshold, the Pi is shut down.
* Flash-Drive file dumping (iffy): When the camera is running, and a flash drive with a specific name is plugged in, all the camera's logs and media are dumped onto the flash drive. (Why iffy? I'm having a hard time giving Raspbian write permissions to a newly-inserted flash drive)
