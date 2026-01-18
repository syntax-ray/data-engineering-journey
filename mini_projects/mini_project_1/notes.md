# Docker file

A docker file is like a recipe. We use it to build an image. The docker file used is as follows:

FROM python:3.14.2-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY hotel_bookings.csv .
COPY clean_data.py .
CMD [ "python", "clean_data.py" ]

FROM pulls python from the docker repository. Slim is chosen because it is light weight but still has enough to support the dependancies needed eg: Pandas.
WORKDIR -> cd's into the container directory creating it first if it does not exist.
COPY -> This is used to copy files from local machine to container.

A 2 step COPY is used because of caching. We do not want a full rebuild if only contents of clean_data.py change.
We use --no-cache-dir to navigate around pip's behaviour of saving library install files. This cuts down on space.
CMD -> This is used to define the deafult start up command that can be overwritten.

## Build

To build the image run:

docker build -t image_name:image_tag


## Run

To run it is important to mount local machine's directory so that you can obtain the output from the machine.

That would look like:

docker run --rm -it -v $(pwd):/app hotel-bookings-cleaner:1.0 

Note: the --rm flag removes the container once the run is complete.
-it runs the container in interactive mode so that it can accept command line user inputs
-v: used to mount in our case $(pwd) the current directory to the output directory of the container (/app) 