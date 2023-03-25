FROM alpine:3.17.1
ENV HEALTH_RS_HOST=''
ENV HEALTH_RS_PORT=''
ENV HEALTH_AM_HOST=''
ENV HEALTH_AM_PORT=''
ENV HEALTH_AM_REALM_NAME=''
ENV CLIENT_ID=''
ENV CLIENT_REDIRECT_URL=''
COPY ./Web /Web
WORKDIR /Web/
RUN apk add --update --no-cache python3 && \
python3 -m ensurepip && \
pip3 install flask flask-cors requests
CMD python3 fhir_rs_web.py ${HEALTH_RS_HOST} ${HEALTH_RS_PORT} ${HEALTH_AM_HOST} ${HEALTH_AM_PORT} ${HEALTH_AM_REALM_NAME} ${CLIENT_ID} ${CLIENT_REDIRECT_URL}