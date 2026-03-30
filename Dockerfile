# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy only the necessary files for dependency installation first
# This leverages Docker's layer caching. If these files don't change,
# this layer won't be re-run.
COPY pyproject.toml ./

# Install the project and its dependencies
# Using `pip install .` will install the package defined in pyproject.toml
RUN pip install .

# Copy the rest of the application source code
COPY ./orch ./orch

# The user should provide a .env file or environment variables at runtime
# for API keys.

# Set the entrypoint to the CLI command.
ENTRYPOINT ["orch"]

# Set a default command to run when the container starts (e.g., show the help message)
CMD ["--help"]