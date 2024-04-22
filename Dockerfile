FROM python:3.10 AS build

RUN apt-get update && apt-get install -y \
    cmake \
    swig \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/YDLIDAR/YDLidar-SDK/archive/refs/tags/V1.1.1.tar.gz && \
    tar -xvf V1.1.1.tar.gz && \
    cd YDLidar-SDK-1.1.1 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    make install && \
    cd .. && \
    pip3 install wheel && \
    python3 setup.py bdist_wheel 




FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*


COPY . .
ADD . /app

# Copy from first container to second container
COPY --from=build /YDLidar-SDK-1.1.1/dist/*.whl .
COPY --from=build /YDLidar-SDK-1.1.1/dist/*.whl ./app


COPY requirements.txt requirements.txt


RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "bin/main.py"]

CMD ["-r", "rise"]

