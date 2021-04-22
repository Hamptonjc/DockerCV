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


def main(shm_size: int=10600000):

    shm = ipc.SharedMemory("/shm")
    mapfile = mmap.mmap(shm.fd, shm.size)
    shm.close_fd()
    local_sem = ipc.Semaphore("/localsem")
    docker_sem = ipc.Semaphore("/dockersem")

    while True:

        local_sem.acquire(timeout=5)

        """ Processing """
        frame = utils.read_from_memory(mapfile)
        frame = np.frombuffer(frame, dtype=np.uint8).reshape((720,1280,3))
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

    
