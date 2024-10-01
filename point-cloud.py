import aditofpython as tof
import numpy as np
import cv2 as cv
import open3d as o3d
from enum import Enum

class ModesEnum(Enum):
    MODE_NEAR = 0
    MODE_MEDIUM = 1
    MODE_FAR = 2

def transform_image(np_image):
    return o3d.geometry.Image(np_image)


if __name__ == "__main__":
    system = tof.System()

    cameras = []
    status = system.getCameraList(cameras)
    if not status:
        print("system.getCameraList() failed with status: ", status)

    modes = []
    status = cameras[0].getAvailableModes(modes)
    if not status:
        print("system.getAvailableModes() failed with status: ", status)

    types = []
    status = cameras[0].getAvailableFrameTypes(types)
    if not status:
        print("system.getAvailableFrameTypes() failed with status: ", status)

    status = cameras[0].initialize()
    if not status:
        print("cameras[0].initialize() failed with status: ", status)

    status = cameras[0].setFrameType(types[0])
    if not status:
        print("cameras[0].setFrameType() failed with status:", status)

    status = cameras[0].setMode(modes[ModesEnum.MODE_NEAR.value])
    if not status:
        print("cameras[0].setMode() failed with status: ", status)

    camDetails = tof.CameraDetails()
    status = cameras[0].getDetails(camDetails)
    if not status:
        print("system.getDetails() failed with status: ", status)

    # Enable noise reduction for better results
    smallSignalThreshold = 100
    cameras[0].setControl("noise_reduction_threshold", str(smallSignalThreshold))

    # Get the first frame for details
    frame = tof.Frame()
    status = cameras[0].requestFrame(frame)
    frameDetails = tof.FrameDetails()
    status = frame.getDetails(frameDetails)
    width = frameDetails.width
    height = int(frameDetails.height)

    # Get intrinsic parameters from camera
    intrinsicParameters = camDetails.intrinsics
    fx = intrinsicParameters.cameraMatrix[0]
    fy = intrinsicParameters.cameraMatrix[4]
    cx = intrinsicParameters.cameraMatrix[2]
    cy = intrinsicParameters.cameraMatrix[5]
    cameraIntrinsics = o3d.camera.PinholeCameraIntrinsic(width, height, fx, fy, cx, cy)

    # Get camera details for frame correction
    camera_range = camDetails.depthParameters.maxDepth
    bitCount = camDetails.bitCount
    max_value_of_IR_pixel = 2 ** bitCount - 1
    distance_scale_ir = 255.0 / max_value_of_IR_pixel
    distance_scale = 255.0 / camera_range

    point_cloud = o3d.geometry.PointCloud()

    while True:
        # Capture frame-by-frame
        status = cameras[0].requestFrame(frame)
        if not status:
            print("cameras[0].requestFrame() failed with status: ", status)

        depth_map = np.array(frame.getData(tof.FrameDataType.Depth), dtype="uint16", copy=False)
        ir_map = np.array(frame.getData(tof.FrameDataType.IR), dtype="uint16", copy=False)
        
        # Create the IR image
        ir_map = ir_map[0: int(ir_map.shape[0]), :]
        ir_map = distance_scale_ir * ir_map
        ir_map = np.uint8(ir_map)
        ir_map = cv.cvtColor(ir_map, cv.COLOR_GRAY2RGB)

        # Create the Depth image
        new_shape = (int(depth_map.shape[0]), depth_map.shape[1])
        depth16bits_map = depth_map = np.resize(depth_map, new_shape)
        depth_map = distance_scale * depth_map
        depth_map = np.uint8(depth_map)
        depth_map = cv.applyColorMap(depth_map, cv.COLORMAP_RAINBOW)

        # Create color image
        img_color = cv.addWeighted(ir_map, 0.4, depth_map, 0.6, 0)

        color_image = o3d.geometry.Image(img_color)
        depth16bits_image = o3d.geometry.Image(depth16bits_map)

        # Export the images 
        cv.imwrite("color.jpg",color_image)
        cv.imwrite("depth.jpg",depth_map)

        rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color_image, depth16bits_image, 1000.0, 3.0, False)
        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cameraIntrinsics)

        # Flip it, otherwise the point cloud will be upside down
        pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])

        # Show the point cloud
        point_cloud.points = pcd.points
        point_cloud.colors = pcd.colors

        # print(np.asarray(point_cloud.points))
        o3d.io.write_point_cloud("test.pcd",point_cloud)
        if cv.waitKey(1) >= 0 or True:
            break
        