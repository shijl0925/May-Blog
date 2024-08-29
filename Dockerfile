# base image
ARG IMAGE=shijl0925/rockylinux-8-python:3.11.9

FROM ${IMAGE}

RUN dnf install --nogpgcheck -y unzip mysql-devel git vim && \
    dnf clean all && \
    dnf autoremove -y

# setup environment variable
ENV DockerHOME=/Blog

# set work directory
RUN mkdir -p $DockerHOME

# where your code lives
WORKDIR $DockerHOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# copy whole project to your docker home directory.
COPY . $DockerHOME

# run this command to install all dependencies
RUN --mount=type=cache,target=/root/.cache/pip/http \
    python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# clean pip cache
RUN python3 -m pip cache purge

RUN python3 -m pip install supervisor
RUN mkdir -p /etc/supervisor/ /etc/supervisord.d/

COPY supervisord.d/supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisord.d/blog.ini /etc/supervisord.d/blog.ini

# port where the Django app runs
EXPOSE 8080

RUN chmod +x /Blog/entrypoint.sh
ENTRYPOINT [ "/Blog/entrypoint.sh" ]