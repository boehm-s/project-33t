FROM python:3.8

COPY requirements.txt docker/wait-for-it.sh ./

RUN apt-get update && \
    apt-get install -y libopenblas-dev gfortran && \
    pip install -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

RUN pip install certifi
RUN pip install --upgrade pyopenssl

WORKDIR /project

RUN touch  __init__.py

COPY setup.py src/ scripts/  ./

WORKDIR /


EXPOSE 80
ENV PORT=80 \
    WORKER_COUNT=4 \
    ELASTICSEARCH_URL=https://elasticsearch:9200 \
    ELASTICSEARCH_INDEX=images \
    ELASTICSEARCH_DOC_TYPE=images \
    ALL_ORIENTATIONS=true

# CMD gunicorn \
#     -t 60 \
#     --log-level debug \
#     --access-logfile - \
#     --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" - %(D)s' \
#     -b 0.0.0.0:${PORT} \
#     -w ${WORKER_COUNT} \
#     server:app

# CMD FLASK_APP=server.py flask run -p ${PORT}
