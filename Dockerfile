# ---- Builder Stage ----
# Use a full Python image that includes build tools to compile dependencies.
FROM python:3.11 as builder

# Set the working directory in the container
WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files
# and create/activate a virtual environment.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Create the virtual environment
RUN python -m venv $VIRTUAL_ENV

# Copy only the necessary files for dependency installation first
# This leverages Docker's layer caching. If these files don't change,
# this layer won't be re-run.
COPY pyproject.toml ./

# Install the project and its dependencies into the virtual environment
RUN pip install --upgrade pip && pip install .

# ---- Final Stage ----
# Use a slim Python image for a smaller final image size.
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the virtual environment from the builder stage.
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code from the builder stage.
COPY --from=builder /app/orch /app/orch

# Set the entrypoint to the CLI command.
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["orch"]

# Set a default command to run when the container starts (e.g., show the help message)
CMD ["--help"]