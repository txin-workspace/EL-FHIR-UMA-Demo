FROM alpine:3.17.1
ENV EL_RS_HOST=''
ENV EL_RS_PORT=''
ENV EL_AM_HOST=''
ENV EL_AM_PORT=''
ENV EL_AM_REALM_NAME=''
ENV CLIENT_ID=''
ENV CLIENT_REDIRECT_URL=''
ENV APP_AM_HOST=''
ENV APP_AM_PORT=''
ENV APP_AM_REALM_NAME=''
ENV APP_CLIENT_ID=''
ENV APP_CLIENT_REDIRECT_URL=''
COPY ./DemoHealthCareApp /DemoHealthCareApp
WORKDIR /DemoHealthCareApp/
RUN apk add --update --no-cache python3 && \
python3 -m ensurepip && \
pip3 install flask flask-cors requests
CMD python3 DemoHealthCare.py ${EL_RS_HOST} ${EL_RS_PORT} ${EL_AM_HOST} ${EL_AM_PORT} ${EL_AM_REALM_NAME} ${CLIENT_ID} ${CLIENT_REDIRECT_URL} ${APP_AM_HOST} ${APP_AM_PORT} ${APP_AM_REALM_NAME} ${APP_CLIENT_ID} ${APP_CLIENT_REDIRECT_URL}