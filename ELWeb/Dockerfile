FROM alpine:3.17.1
ENV EL_RS_HOST=''
ENV EL_RS_PORT=''
ENV EL_AM_HOST=''
ENV EL_AM_PORT=''
ENV EL_AM_REALM_NAME=''
ENV CLIENT_ID=''
ENV CLIENT_REDIRECT_URL=''
COPY ./Web /Web
WORKDIR /Web/
RUN apk add --update --no-cache python3 && \
python3 -m ensurepip && \
pip3 install flask flask-cors requests
CMD python3 el_rs_web.py ${EL_RS_HOST} ${EL_RS_PORT} ${EL_AM_HOST} ${EL_AM_PORT} ${EL_AM_REALM_NAME} ${CLIENT_ID} ${CLIENT_REDIRECT_URL}