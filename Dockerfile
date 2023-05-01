FROM python:3.8.0 AS base


WORKDIR /usr/src/app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r /usr/src/app/requirements.txt
RUN rm -rf /root/.cache/pip

FROM base AS production
COPY . /usr/src/app/
RUN chmod a+x /usr/src/app/docker/entrypoint.sh
HEALTHCHECK --start-period=5s --interval=30s --timeout=5s CMD curl -f http://localhost:8080/ || exit 1
CMD ["/usr/src/app/docker/entrypoint.sh"]


FROM base AS command
COPY . /usr/src/app/
