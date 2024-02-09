FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3 python3-pip
COPY simulator.py /main/
COPY simulator_test.py /main/
COPY messages.mllp /main/
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
WORKDIR /main
EXPOSE 8440
EXPOSE 8441
CMD /main/message_listener.py & /simulator/simulator.py

