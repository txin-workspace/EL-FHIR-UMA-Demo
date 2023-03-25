FROM alpine:3.17.1
ENV AM_HOST=''
ENV AM_PORT=''
ENV REALM_NAME=''
ENV CLIENT_ID=''
ENV CLIENT_SCRET=''
ENV HAPI_HOST=''
ENV HAPI_PORT=''
ENV EL_AGENT_NAME=''
ENV EL_AGENT_ID=''
COPY ./ResourceServer /ResourceServer
WORKDIR /ResourceServer/
RUN apk add --update --no-cache python3 && \
python3 -m ensurepip && \
pip3 install flask flask-cors requests
CMD python3 fhir_rs.py ${AM_HOST} ${AM_PORT} ${REALM_NAME} ${CLIENT_ID} ${CLIENT_SCRET} ${HAPI_HOST} ${HAPI_PORT} ${EL_AGENT_NAME} ${EL_AGENT_ID}