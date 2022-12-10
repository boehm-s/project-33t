FROM python:3.8

COPY requirements.txt docker/wait-for-it.sh ./

RUN apt-get update && \
    apt-get install -y libopenblas-dev gfortran && \
    pip install -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

RUN pip install certifi
RUN pip install uvicorn
RUN pip install --upgrade pyopenssl

COPY .  /

WORKDIR /

EXPOSE 80
ENV PORT=80 \
    WORKER_COUNT=4 \
    ELASTICSEARCH_URL=http://elasticsearch:9200 \
    ELASTICSEARCH_INDEX=images \
    ELASTICSEARCH_DOC_TYPE=images \
    ALL_ORIENTATIONS=true
