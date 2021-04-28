import mmap
import posix_ipc as ipc
import numpy as np


class DockerNode:


    def __init__(self, image_bytes: int, image_shape: tuple)->None:
        self.image_bytes = image_bytes
        self.image_shape = image_shape

        # Set up IPC
        shm = ipc.SharedMemory("/dcv_shm")
        self.__mapfile = mmap.mmap(shm.fd, shm.size)
        shm.close_fd()
        self.__local_sem = ipc.Semaphore("/dcv_localsem")
        self.__docker_sem = ipc.Semaphore("/dcv_dockersem")

    def receive(self, timeout: int=None)->np.array:
        if timeout:
            self.__local_sem.acquire(timeout)
        else:
            self.__local_sem.acquire()

        frame = self.__read_from_memory(self.__mapfile, self.image_bytes)
        frame = np.frombuffer(frame, dtype=np.uint8).reshape(self.image_shape)
        return frame

    def send(self, frame: np.array)->None:
        frame = frame.tobytes()
        self.__write_to_memory(self.__mapfile, frame)
        self.__docker_sem.release()
        self.__local_sem.acquire()
        self.__docker_sem.release()

    def __write_to_memory(self, mapfile, data):
        mapfile.seek(0)
        return mapfile.write(data)

    def __read_from_memory(self, mapfile, n_bytes):
        mapfile.seek(0)
        data = mapfile.read(n_bytes)
        return data