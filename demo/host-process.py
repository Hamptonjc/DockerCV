import dockercv as dcv
import cv2
import mmap


def main():

    dcv_node = dcv.HostNode(shm_size=40000000, image_bytes=1555200, image_shape=(540, 960, 3))
    vid = cv2.VideoCapture('../solidWhiteRight.mp4')

    
    while True:
        # Read in frame
        _ , frame = vid.read()

        if frame is None:
            break

        dcv_node.send(frame)
        frame = dcv_node.receive()

        #display
        cv2.imshow('Live', frame)
        cv2.waitKey(30)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    del dcv_node


if __name__ == '__main__':
    main()