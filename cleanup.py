import posix_ipc as ipc



if __name__ == '__main__':

    try:
        local_sem = ipc.Semaphore("/localsem")
        local_sem.unlink()
    except:
        pass
    
    try:
        docker_sem = ipc.Semaphore('/dockersem')
        docker_sem.unlink()
    except:
        pass

    try:
        shm = ipc.SharedMemory("/shm")
        shm.unlink()
    except:
        pass