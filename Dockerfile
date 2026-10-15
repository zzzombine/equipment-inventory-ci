FROM python:3.12.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8005 \
    MESSAGE="Inventory online"

WORKDIR /srv/inventory

RUN groupadd --gid 10005 svc \
    && useradd --uid 10005 --gid svc --no-create-home \
       --shell /usr/sbin/nologin svc \
    && mkdir -p /data \
    && chown svc:svc /data

COPY server.py inventory.json.example ./

USER svc

EXPOSE 8005

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8005') + '/health', timeout=2).close()"]

CMD ["python", "server.py"]