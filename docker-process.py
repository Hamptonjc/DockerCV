import cv2
import numpy as np
import posix_ipc as ipc
import mmap
import utils


def processing(frame):
    # font
    font = cv2.FONT_HERSHEY_SIMPLEX
    # org
    org = (100, 100)
    # fontScale
    fontScale = 1
    # Blue color in BGR
    color = (0, 255, 0)
    # Line thickness of 2 px
    thickness = 2
    # Using cv2.putText() method
    frame = cv2.putText(frame, 'Wumbo', org, font, 
                    fontScale, color, thickness, cv2.LINE_AA)
    return frame

def detectlines(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    minLineLength = 100
    maxLineGap = 10
    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
    for x1,y1,x2,y2 in lines[0]:
        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
    return img


def main(shm_size: int=10600000):

    shm = ipc.SharedMemory("/shm")
    mapfile = mmap.mmap(shm.fd, shm.size)
    shm.close_fd()
    local_sem = ipc.Semaphore("/localsem")
    docker_sem = ipc.Semaphore("/dockersem")

    while True:

        local_sem.acquire(timeout=1)
        # get frame byte size
        n_bytes = ''
        mapfile.seek(0)
        b = mapfile.read_byte()
        while b != 0:
            n_bytes += chr(b)
            b = mapfile.read_byte()
        docker_sem.release()
        n_bytes = int(n_bytes)

        # get shape
        local_sem.acquire()
        mapfile.seek(0)
        b = mapfile.read_byte()
        n = ''
        shape = []
        while b != 0:
            b = chr(b)
            if b != ',':
                n += b
            else:
                shape.append(int(n))
                n = ''
            b = mapfile.read_byte()

        docker_sem.release()

        # Get frame
        local_sem.acquire()
        frame = utils.read_from_memory(mapfile, n_bytes)
        frame = np.frombuffer(frame, dtype=np.uint8).reshape(tuple(shape))
        frame = detectlines(frame)
        frame = processing(frame)
        frame = frame.tobytes()
        utils.write_to_memory(mapfile, frame)
        docker_sem.release()

        # for local process reading
        local_sem.acquire()
        docker_sem.release()

    local_sem.unlink()
    docker_sem.unlink()

if __name__ == '__main__':
    main()

    
