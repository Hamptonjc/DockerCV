import mmap
import posix_ipc as ipc
import numpy as np

class HostNode:


    def __init__(self, shm_size, image_bytes, image_shape):
        self.image_bytes = image_bytes
        self.image_shape = image_shape

        # Setup IPC
        shm = ipc.SharedMemory("/dcv_shm", flags=ipc.O_CREAT, mode=0o777, size=shm_size)
        self.__mapfile = mmap.mmap(shm.fd, shm.size)
        shm.close_fd()
        self.__local_sem = ipc.Semaphore("/dcv_localsem", ipc.O_CREAT, initial_value=0)
        self.__docker_sem = ipc.Semaphore("/dcv_dockersem", ipc.O_CREAT, initial_value=1)


    def __del__(self):
        self.__mapfile.close()
        ipc.unlink_shared_memory("/dcv_shm")
        self.__local_sem.unlink()
        self.__docker_sem.unlink()

    def send(self, image: np.array)->None:
        # Get image info
        self.__image_shape = image.shape
        self.__image_dtype = image.dtype
        # Convert to bytes
        image = image.tobytes()
        # Write to shared memory
        self.__docker_sem.acquire()
        self.__write_to_memory(self.__mapfile, image)

    def receive(self):
        # wait for processing
        self.__local_sem.release()
        # Read from shared memory
        self.__docker_sem.acquire()
        image = self.__read_from_memory(self.__mapfile, n_bytes=self.image_bytes)
        self.__local_sem.release()
        # Convert back to numpy arr
        image = np.frombuffer(image, dtype=self.__image_dtype).reshape(self.__image_shape)
        return image

    def __write_to_memory(self, mapfile, data):
        mapfile.seek(0)
        return mapfile.write(data)

    def __read_from_memory(self, mapfile, n_bytes):
        mapfile.seek(0)
        data = mapfile.read(n_bytes)
        return data
    


 

