FROM python:3.10-alpine
LABEL maintainer="Mariano Ruiz <mrsarm@gmail.com>"

ENV PROCESS_TYPE="web" \
    PORT=8888

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN apk add --no-cache --purge shadow \
    && useradd -ms /bin/bash worker \
    && chown -R worker:worker /usr/src/app \
    && chown worker:worker requirements.txt \
    && pip install --no-cache-dir -U pip \
    && pip3 install --no-cache-dir \
        honcho \
    && pip3 install --no-cache-dir -r requirements.txt

COPY --chown=worker ./ ./

ARG BUILD
LABEL build=${BUILD}
RUN echo "Build: $BUILD" > image_build \
    && echo "UTC: $(date --utc +%FT%R)" >> image_build

RUN chown worker -R *

USER worker

CMD ["sh", "-c", "exec honcho start --no-prefix $PROCESS_TYPE"]
