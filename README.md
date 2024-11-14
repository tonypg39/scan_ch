## This projects creates the REST-API server to provide the images from the RPi

* It publishes the following endpoints:
    *  `/initialize` : To create the camera object and perform the initial configuration of the device.
    *  `/capture`: To capture the image and send the result (raw depth and IR images and camera intrinsec parameters).