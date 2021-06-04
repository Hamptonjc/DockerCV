############################################
#       Author: Jonathan Hampton
#       github.com/hamptonjc
############################################

# Imports
import mmap
import posix_ipc as ipc
import numpy as np

class HostNode:

    """
    The HostNode sends the image array to the DockerNode then receives the processed image back from the DockerNode.
    This is done via IPC.

    shm_size (int) : This determines in bytes how much space the IPC mechanism has to transfer an image.

    """

    def __init__(self, shm_size: int) -> None:
        # Setup IPC
        shm = ipc.SharedMemory("/dcv_shm", flags=ipc.O_CREAT, mode=0o777, size=shm_size)
        self.__mapfile = mmap.mmap(shm.fd, shm.size)
        shm.close_fd()
        self.__local_sem = ipc.Semaphore("/dcv_localsem", ipc.O_CREAT, initial_value=0)
        self.__docker_sem = ipc.Semaphore("/dcv_dockersem", ipc.O_CREAT, initial_value=1)


    def __del__(self) -> None:
        self.__mapfile.close()
        ipc.unlink_shared_memory("/dcv_shm")
        self.__local_sem.unlink()
        self.__docker_sem.unlink()

    def transmit(self, image: np.array) -> np.array:
        """
        Sends an image array to the DockerNode, then waits for the DockerNode to return it.

        image (np.array) : An image array to send to the DockerNode.

        """
        # Get image info
        self.__image_shape = image.shape
        self.__image_dtype = image.dtype
        # Convert to bytes
        image = image.tobytes()
        # Write size to shm
        self.__docker_sem.acquire()
        byte_size = str(len(image)) + '\0'
        bytes_wrote = self.__write_to_memory(self.__mapfile, byte_size.encode())
        # wait for processing
        self.__local_sem.release()
        # Write shape to shm
        self.__docker_sem.acquire()
        str_shape = ''
        for i in self.__image_shape:
            str_shape += str(i)
            str_shape += ','
        str_shape += '\0'
        self.__write_to_memory(self.__mapfile, str_shape.encode())
        # wait for processing
        self.__local_sem.release()
        # Write frame to shm
        self.__docker_sem.acquire()
        try:
            bytes_wrote = self.__write_to_memory(self.__mapfile, image)
        except:
            raise ValueError("Image could not be wrote to shared memory. Try increasing shm_size.")
        # wait for processing
        self.__local_sem.release()
       # Read from shared memory
        self.__docker_sem.acquire()
        frame = self.__read_from_memory(self.__mapfile, n_bytes=bytes_wrote)
        self.__local_sem.release()
        # Convert back to numpy arr
        frame = np.frombuffer(frame, dtype=self.__image_dtype).reshape(self.__image_shape)
        return frame


    #########################################################################
    #       Private Methods
    #########################################################################

    def __write_to_memory(self, mapfile: mmap.mmap, data: bytes) -> int:
        mapfile.seek(0)
        return mapfile.write(data)

    def __read_from_memory(self, mapfile: mmap.mmap, n_bytes: int) -> bytes:
        mapfile.seek(0)
        data = mapfile.read(n_bytes)
        return data

    
    


 

