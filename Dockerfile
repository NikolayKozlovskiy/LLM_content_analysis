# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /usr/src/app

# Install the PostgreSQL development packages and other dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get clean

# Copy the current directory contents into the container at /usr/src/app
COPY . .

ARG install_dir=/tmp/install
# Standard requirements
COPY resources/requirements/requirements.txt ${install_dir}/requirements.txt
RUN pip3 install -r ${install_dir}/requirements.txt

# Verify openpyxl installation
RUN pip show openpyxl

# Download NLTK data
RUN python -m nltk.downloader punkt

RUN echo "alias jl='jupyter lab --ip=0.0.0.0 --port=8888 --no-browser  \
  --allow-root --NotebookApp.base_url=${JUPYTER_BASE_URL} --NotebookApp.token='" >> ~/.bashrc

RUN rm -r ${install_dir}
RUN rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/usr/src/app

CMD ["tail", "-f", "/dev/null"]