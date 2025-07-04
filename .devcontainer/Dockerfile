# .devcontainer/Dockerfile

FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install PostgreSQL and tools
RUN apt-get update && \
    apt-get install -y postgresql postgresql-contrib && \
    apt-get clean
