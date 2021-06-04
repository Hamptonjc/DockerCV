############################################
#       Author: Jonathan Hampton
#       github.com/hamptonjc
############################################

# Imports
import mmap
import posix_ipc as ipc
import numpy as np

class DockerNode:
    """
    The DockerNode recieves an image array from the HostNode. Image processing can then be done Docker-side. The DockerNode can then
    send the processed image back to the HostNode.

    """

    def __init__(self)->None:
        # Set up IPC
        shm = ipc.SharedMemory("/dcv_shm")
        self.__mapfile = mmap.mmap(shm.fd, shm.size)
        shm.close_fd()
        self.__local_sem = ipc.Semaphore("/dcv_localsem")
        self.__docker_sem = ipc.Semaphore("/dcv_dockersem")


    def receive(self, timeout: int=None) -> np.array:
        """
        Receive an image array from a HostNode.
        
        timeout (Union[int, None]) : Set the amount of time to wait for the HostNode to send an image array before timing out.

        """

        self.__local_sem.acquire(timeout=timeout)
        # get frame byte size
        n_bytes = ''
        self.__mapfile.seek(0)
        b = self.__mapfile.read_byte()
        while b != 0:
            n_bytes += chr(b)
            b = self.__mapfile.read_byte()
        self.__docker_sem.release()
        n_bytes = int(n_bytes)
        # get shape
        self.__local_sem.acquire()
        self.__mapfile.seek(0)
        b = self.__mapfile.read_byte()
        n = ''
        shape = []
        while b != 0:
            b = chr(b)
            if b != ',':
                n += b
            else:
                shape.append(int(n))
                n = ''
            b = self.__mapfile.read_byte()
        self.__docker_sem.release()
        self.__local_sem.acquire()
        frame = self.__read_from_memory(self.__mapfile, n_bytes)
        frame = np.frombuffer(frame, dtype=np.uint8).reshape(tuple(shape))
        return frame

    def send(self, frame: np.array)->None:
        """
        Send an image array back to the HostNode.

        frame (np.array) : The image array to send back to the HostNode.

        """

        frame = frame.tobytes()
        self.__write_to_memory(self.__mapfile, frame)
        self.__docker_sem.release()
        # for local process reading
        self.__local_sem.acquire()
        self.__docker_sem.release()
    

    ###################################################
    #       Private Methods
    ###################################################

    def __write_to_memory(self, mapfile, data):
        mapfile.seek(0)
        return mapfile.write(data)

    def __read_from_memory(self, mapfile, n_bytes):
        mapfile.seek(0)
        data = mapfile.read(n_bytes)
        return data