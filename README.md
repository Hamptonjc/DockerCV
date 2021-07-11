# DockerCV

DockerCV is a solution to visualizing Docker-based computer-vision / machine learning applications locally. Rather than fooling with other options such as Xserver, DockerCV provides a simple API to visualize images/videos processed in a local Docker container.

DockerCV uses IPC mechanisms to pass a local image to a Docker container for processing, then receives the processed image back to then display locally.

## Installation

DockerCV is currently only supported on Linux :-(

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install DockerCV.

```bash
pip install dockercv
```

## Usage

For a complete demo, see the demo folder.

The process that runs on the host:

```python
# Imports
import dockercv as dcv
import numpy as np

# create host node
host_node = dcv.HostNode(shm_size=4000000)

# some random image as a numpy array
some_image = np.ones((256,256))

# transmit the image to the docker node for processing
# then receive the processed image back
processed_image = host_node.transmit(some_image)

# display processed_image with OpenCV, PIL, etc.

```

The process that runs in a Docker container:

```python
# Imports
import dockercv as dcv

# Create docker node
docker_node = dcv.DockerNode()

# receive some_image from host node
some_image = docker_node.receive()

# apply some processing to the image
processed_image = some_processing_function(some_image)

# send the processed image back to the host node
docker_node.send(processed_image)

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
