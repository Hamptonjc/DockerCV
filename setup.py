from setuptools import setup, find_packages


VERSION = '0.0.1'
DESCRIPTION = 'A solution for visualizing Docker-based computer vision applications'
LONG_DESCRIPTION = 'DockerCV uses IPC mechanisms to allow for Numpy processing (OpenCV / PyTorch / TensorFlow / etc.) within a Docker container while still viewing the resulting images/videos locally on the host device. This eliminates the need for X11 Forwarding.'


setup(name='dockercv',
      version=VERSION,
      author='Jonathan Hampton',
      author_email='hamptonjc221@gmail.com',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      packages=find_packages(),
      install_requires=['posix_ipc', 'numpy'],
      keywords=['docker cv', 'docker visual'],
      classifiers= ['Development Status :: 3 - Alpha',
                    'Programming Language :: Python :: 3',
                    'Operating System :: Unix']
        )