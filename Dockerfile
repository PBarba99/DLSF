# Dockerfile for DeepRL development

FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

# Install Java and Maven
RUN apt-get update && apt-get install -y openjdk-17-jdk maven git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /workspace/DLSF

# You will mount this repo during docker run, so no COPY or git clone here

# Default shell
CMD [ "bash" ]

