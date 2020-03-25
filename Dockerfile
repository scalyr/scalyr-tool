FROM python:3-alpine3.10

COPY scalyr /bin/scalyr
RUN chmod u+x /bin/scalyr
ENTRYPOINT ["/bin/scalyr"]
