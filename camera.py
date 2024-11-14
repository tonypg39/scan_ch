import aditofpython as tof
import numpy as np
import cv2 as cv
import open3d as o3d
from enum import Enum

class ModesEnum(Enum):
    MODE_NEAR = 0
    MODE_MEDIUM = 1
    MODE_FAR = 2

class CameraToF():

    def __init__(self) -> None:
        self.system = tof.System()
        self._initialize_cameras()
    
    def _initialize_cameras(self):
        self.cameras = []
        status = self.system.getCameraList(self.cameras)
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

        # Enable noise reduction for better results
        smallSignalThreshold = 100
        self.cameras[0].setControl("noise_reduction_threshold", str(smallSignalThreshold))

    
    def capture(self):
        camDetails = tof.CameraDetails()
        # Get the first frame for details
        frame = tof.Frame()
        status = self.cameras[0].requestFrame(self.frame)
        frameDetails = tof.FrameDetails()
        status = self.frame.getDetails(frameDetails)
        
        params = self.get_params(camDetails,frameDetails)
        maps = self.get_maps(frame)
        return {
            "params": params,
            "maps": maps
        }
    
    def get_params(self,camDetails, frameDetails):
        # Get intrinsic parameters from camera
        intrinsicParameters = camDetails.intrinsics
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

    
    def get_maps(self, frame):
        depth_map = np.array(frame.getData(tof.FrameDataType.Depth), dtype="uint16", copy=False)
        ir_map = np.array(frame.getData(tof.FrameDataType.IR), dtype="uint16", copy=False)
        return {
            "depth": depth_map,
            "ir_map": ir_map
        }