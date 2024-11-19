import aditofpython as tof
import numpy as np
import cv2 as cv
import open3d as o3d
import time
from enum import Enum

class ModesEnum(Enum):
    MODE_NEAR = 0
    MODE_MEDIUM = 1
    MODE_FAR = 2

class CameraToF():

    def __init__(self) -> None:
        
        self._initialize_cameras()
    
    def _initialize_cameras(self):
        system = tof.System()
        self.cameras = []
        status = system.getCameraList(self.cameras)
        if not status:
            print("system.getCameraList() failed with status: ", status)

        modes = []
        status = self.cameras[0].getAvailableModes(modes)
        if not status:
            print("system.getAvailableModes() failed with status: ", status)

        types = []
        status = self.cameras[0].getAvailableFrameTypes(types)
        if not status:
            print("system.getAvailableFrameTypes() failed with status: ", status)

        status = self.cameras[0].initialize()
        if not status:
            print("self.cameras[0].initialize() failed with status: ", status)

        status = self.cameras[0].setFrameType(types[0])
        if not status:
            print("self.cameras[0].setFrameType() failed with status:", status)

        status = self.cameras[0].setMode(modes[ModesEnum.MODE_NEAR.value])
        if not status:
            print("self.cameras[0].setMode() failed with status: ", status)

        camDetails = tof.CameraDetails()
        
        status = self.cameras[0].getDetails(camDetails)
        if not status:
            print("system.getDetails() failed with status: ", status)
            
        print("\n\nThe Parameters here are::= ", camDetails.intrinsics.cameraMatrix)
        # Enable noise reduction for better results
        smallSignalThreshold = 100
        self.cameras[0].setControl("noise_reduction_threshold", str(smallSignalThreshold))

    
    def capture(self):
        camDetails = tof.CameraDetails()
        # Get the first frame for details
        status = self.cameras[0].getDetails(camDetails)
        if not status:
            print("system.getDetails() failed with status: ", status)
            return {"error": status}

        frame = tof.Frame()
        # status = self.cameras[0].requestFrame(frame)
        frameDetails = tof.FrameDetails()
        status = frame.getDetails(frameDetails)
        
        self.params = self.update_params(camDetails,frameDetails)
        self.maps = self.update_maps(frame)
        return {
            "success": True
        }
    
    def get_params(self):
        return self.params
    
    def get_maps(self):
        return self.maps
    
    def update_params(self,camDetails, frameDetails):
        # Get intrinsic parameters from camera
        intrinsicParameters = camDetails.intrinsics
        # print("The Parameters here are::= ", camDetails.intrinsics.cameraMatrix)     
        fx = intrinsicParameters.cameraMatrix[0]
        fy = intrinsicParameters.cameraMatrix[4]
        cx = intrinsicParameters.cameraMatrix[2]
        cy = intrinsicParameters.cameraMatrix[5]

        # cameraIntrinsics = o3d.camera.PinholeCameraIntrinsic(width, height, fx, fy, cx, cy)
        width = frameDetails.width
        height = int(frameDetails.height)

        # Get camera details for frame correction
        camera_range = camDetails.depthParameters.maxDepth
        bitCount = camDetails.bitCount
        max_value_of_IR_pixel = 2 ** bitCount - 1
        distance_scale_ir = 255.0 / max_value_of_IR_pixel
        distance_scale = 255.0 / camera_range
        return {"distance_scale": distance_scale,
                "distance_scale_ir": distance_scale_ir,
                "width": width,
                "height": height,
                "fx":fx,
                "fy":fy,
                "cx": cx,
                "cy": cy}

    
    def update_maps(self, frame):
        status = self.cameras[0].requestFrame(frame)
        if not status:
            print("cameras[0].requestFrame() failed with status: ", status)

        depth_map = np.array(frame.getData(tof.FrameDataType.Depth), dtype="uint16", copy=False)
        ir_map = np.array(frame.getData(tof.FrameDataType.IR), dtype="uint16", copy=False)

        return {
            "depth": depth_map.tolist(),
            "ir_map": ir_map.tolist()
        }
    
    
if __name__ == "__main__":
    cam = CameraToF()
    while True:
        print("Attempt to send...")
        x = cam.capture()
        y = cam.get_maps()
        print(type(y["depth"]),len(y["depth"]))
        time.sleep(5)
        