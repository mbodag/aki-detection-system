FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3 python3-pip
COPY history.csv /main/
COPY message_parser.py /main/
COPY hospital_message.py /main/
COPY message_listener.py /main/
COPY storage_manager.py /main/
COPY aki_predictor.py /main/
COPY alert_manager.py /main/
COPY config.py /main/
COPY model/model.jl /main/model/
COPY requirements.txt /main/
RUN pip3 install -r /main/requirements.txt

CMD /main/message_listener.py

