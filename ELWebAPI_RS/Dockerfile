FROM alpine:3.17.1
ENV AM_HOST=''
ENV AM_PORT=''
ENV REALM_NAME=''
ENV CLIENT_ID=''
ENV CLIENT_SCRET=''
ENV WEB_CLIENT_ID=''
ENV HEALTH_RS_HOST=''
ENV HEALTH_RS_PORT=''
ENV AGENT_NAME_HEALTH=''
ENV AGENT_PW_HEALTH=''
ENV AGENT_NAME_EL=''
ENV AGENT_PW_EL=''
COPY ./ResourceServer /ResourceServer
WORKDIR /ResourceServer/
RUN apk add --update --no-cache python3 && \
python3 -m ensurepip && \
pip3 install flask flask-cors requests
CMD python3 el_rs.py ${AM_HOST} ${AM_PORT} ${REALM_NAME} ${CLIENT_ID} ${CLIENT_SCRET} ${WEB_CLIENT_ID} ${HEALTH_RS_HOST} ${HEALTH_RS_PORT} ${AGENT_NAME_HEALTH} ${AGENT_PW_HEALTH} ${AGENT_NAME_EL} ${AGENT_PW_EL}