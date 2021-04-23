import cv2
import numpy as np
import posix_ipc as ipc
import mmap
import sys
import os
import time
import utils

def main(shm_size: int=40000000):
    # init
    vid = cv2.VideoCapture('solidWhiteRight.mp4')
    shm = ipc.SharedMemory("/shm", flags=ipc.O_CREAT, mode=0o777, size=shm_size)
    mapfile = mmap.mmap(shm.fd, shm.size)
    shm.close_fd()
    local_sem = ipc.Semaphore("/localsem", ipc.O_CREAT, initial_value=0)
    docker_sem = ipc.Semaphore("/dockersem", ipc.O_CREAT, initial_value=1)

    while True:
        # Read in frame
        _ , frame = vid.read()
        shape = frame.shape
        dtype = frame.dtype
        # Convert to bytes
        frame = frame.tobytes()


        # Write to shared memory
        docker_sem.acquire()
        bytes_wrote = utils.write_to_memory(mapfile, frame)
        # wait for processing
        local_sem.release()

        # Read from shared memory
        docker_sem.acquire()
        frame = utils.read_from_memory(mapfile, n_bytes=bytes_wrote)
        local_sem.release()
        # Convert back to numpy arr
        frame = np.frombuffer(frame, dtype=dtype).reshape(shape)

        #display
        cv2.imshow('Live', frame)
        cv2.waitKey(30)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    vid.release()
    cv2.destroyAllWindows()
    mapfile.close()
    ipc.unlink_shared_memory("/shm")
   # local_sem.unlink()
   # docker_sem.unlink()


if __name__ == '__main__':
    main()