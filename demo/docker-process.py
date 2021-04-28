import mmap
import dockercv as dcv
import cv2


def processing(frame):
    # font
    font = cv2.FONT_HERSHEY_SIMPLEX
    # org
    org = (200, 200)
    # fontScale
    fontScale = 4
    # Blue color in BGR
    color = (0, 255, 0)
    # Line thickness of 2 px
    thickness = 2
    # Using cv2.putText() method
    frame = cv2.putText(frame, 'Wumbo', org, font, 
                    fontScale, color, thickness, cv2.LINE_AA)
    return frame 

def main():
    dcv_node = dcv.DockerNode(image_bytes=1555200, image_shape=(540, 960, 3))

    while True:
        frame = dcv_node.receive()

        frame = processing(frame)

        dcv_node.send(frame)

    del dcv_node

if __name__ == '__main__':
    main()