FROM python:3.9-alpine

COPY ./requirements.txt /flask_server/requirements.txt
WORKDIR /flask_server
RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps
RUN adduser -D appuser
COPY --chown=appuser:appuser . /flask_server

LABEL maintainer="nitzanmr@gmail.com" \
      description="Flask application server"


RUN mkdir -p /flask_server/flask_session && \
    chown -R appuser:appuser /flask_server/flask_session && \
    chmod 755 /flask_server/flask_session

EXPOSE 9090

# Set up healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:9090/health || exit 1

# Switch to non-root user
USER appuser

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:9090", "flask_server:app"]
