FROM nvidia/cuda:10.1-cudnn7-devel

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV DEBIAN_FRONTEND noninteractive
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update && apt-get install -y \
	python3-opencv ca-certificates python3-dev git wget sudo libjemalloc-dev && \
  rm -rf /var/lib/apt/lists/*


RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

ENV PATH="/home/appuser/.local/bin:${PATH}"

# install dependencies
# See https://pytorch.org/ for other options if you use a different version of CUDA
RUN pip install --user torch torchvision tensorboard cython
RUN pip install --user 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'

RUN pip install --user 'git+https://github.com/facebookresearch/fvcore'
# install detectron2
RUN git clone --branch v0.1.3 https://github.com/facebookresearch/detectron2 detectron2_repo
ENV FORCE_CUDA="1"
# This will build detectron2 for all common cuda architectures and take a lot more time,
# because inside `docker build`, there is no way to tell which architecture will be used.
ENV TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
RUN pip install --user -e detectron2_repo

RUN pip install Flask==1.1.2 anytree==2.8.0 Shapely==1.7.0 google-cloud-vision==1.0.0 opencv-python==4.2.0.34

WORKDIR /home/app

ENV LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libjemalloc.so.1"
ENV LRU_CACHE_CAPACITY=1  
ENV remote=http://183.91.11.38/nic
ENV CONFIG=/home/app/config/config.yml

COPY . /home/app

ADD $remote/doc/config.yml model/doc/
ADD $remote/doc/model.pth model/doc/

ADD $remote/crop/config.yml model/crop/ 
ADD $remote/crop/model.pth model/crop/ 

ADD $remote/layout/config.yml model/layout/ 
ADD $remote/layout/model.pth model/layout/ 

ADD $remote/ocr/config.yml model/ocr/ 
ADD $remote/ocr/model.pth model/ocr/ 

ADD $remote/dtree/config.yml model/dtree/ 

ADD $remote/translate/map.json model/translate/ 

RUN pip install -r requirements.txt
 
# Set a fixed model cache directory.
ENV FVCORE_CACHE="/tmp"
EXPOSE 8000

ENTRYPOINT ["gunicorn", "--config", "config/gunicorn_config.py", "api:app"]
