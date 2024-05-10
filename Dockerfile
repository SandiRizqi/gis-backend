FROM python:3.8-slim-buster


EXPOSE 9000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV USEDOCKER=1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1


RUN apt-get clean 
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        libgdal-dev \
        python3-dev \
        libssl-dev
# Install the Python bindings for GDAL
RUN pip install numpy \
    && pip install gdal==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}')

# Install pip requirements
COPY requirements.txt .
RUN apt-get -y install gcc
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app
RUN chmod -R 777 /app


# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER root

RUN python manage.py makemigrations
RUN python manage.py migrate


# During debugging, this entry point will"./manage.py runserver 0.0.0.0:9000 be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["python", "./manage.py", "runserver", "0.0.0.0:9000" ]
