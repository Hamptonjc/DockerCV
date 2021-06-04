import dockercv as dcv
import cv2


def main():

    dcv_node = dcv.HostNode(shm_size=4000000)
    vid = cv2.VideoCapture('./solidWhiteRight.mp4')

    
    while True:
        # Read in frame
        _ , frame = vid.read()

        if frame is None:
            break

        frame = dcv_node.transmit(frame)

        #display
        cv2.imshow('Processed', frame)
        cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    vid.release()
    cv2.destroyAllWindows()
    del dcv_node


if __name__ == '__main__':
    main()