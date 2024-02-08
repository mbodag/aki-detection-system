FROM ubuntu:jammy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install python3 python3-pip
COPY simulator.py /simulator/
COPY simulator_test.py /simulator/
WORKDIR /simulator
RUN ./simulator_test.py
COPY messages.mllp /data/
COPY history.csv /simulator/
COPY message_parser.py /simulator/
COPY hospital_message.py /simulator/
COPY message_listener.py /simulator/
COPY storage_manager.py /simulator/
COPY aki_predictor.py /simulator/
COPY alert_manager.py /simulator/
COPY config.py /simulator/
COPY utils.py /simulator/
COPY model/finalized_model.pkl /simulator/model/
COPY model/model.jl /simulator/model/
COPY tests /simulator/tests
COPY requirements.txt /simulator/
EXPOSE 8440
EXPOSE 8441
RUN pip3 install -r requirements.txt
CMD /simulator/simulator.py --messages=/data/messages.mllp
