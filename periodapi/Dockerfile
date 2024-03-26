FROM python:3.11
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN git clone -b features_refactoring https://github.com/alercebroker/pipeline.git
RUN pip install Cython scipy fastapi "uvicorn[standard]"
RUN cd pipeline/P4J && python -m pip install -e .
COPY main.py compute_periodogram.py .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
