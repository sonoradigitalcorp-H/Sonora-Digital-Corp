FROM alpine:3.20 AS builder

RUN apk add --no-cache curl tar
RUN curl -sL https://github.com/openclaw/wacli/releases/download/v0.12.0/wacli_0.12.0_linux_amd64.tar.gz \
  -o /tmp/wacli.tar.gz && \
  tar xzf /tmp/wacli.tar.gz -C /usr/local/bin/ && \
  chmod +x /usr/local/bin/wacli

FROM alpine:3.20

RUN apk add --no-cache ca-certificates tzdata

COPY --from=builder /usr/local/bin/wacli /usr/local/bin/wacli

ENV WACLI_STORE_DIR=/home/wacli/.wacli
ENV WACLI_HTTP_PORT=9090

RUN adduser -D -h /home/wacli wacli
USER wacli
WORKDIR /home/wacli

VOLUME ["/home/wacli/.wacli", "/home/wacli/media"]

EXPOSE 9090

ENTRYPOINT ["wacli"]
CMD ["--help"]
