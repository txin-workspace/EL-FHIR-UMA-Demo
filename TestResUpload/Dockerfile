FROM alpine:3.17.1
ENV EL_RS_HOST=''
ENV EL_RS_PORT=''
ENV EL_RS_UNAME=''
ENV EL_RS_PW=''
ENV FHIR_RS_HOST=''
ENV FHIR_RS_PORT=''
ENV FHIR_RS_UNAME=''
ENV FHIR_RS_PW=''
COPY ./Agent /Agent
WORKDIR /Agent/
RUN apk add --update --no-cache python3 && \
python3 -m ensurepip && \
pip3 install requests
CMD sh run.sh ${EL_RS_HOST} ${EL_RS_PORT} ${EL_RS_UNAME} ${EL_RS_PW} ${FHIR_RS_HOST} ${FHIR_RS_PORT} ${FHIR_RS_UNAME} ${FHIR_RS_PW}