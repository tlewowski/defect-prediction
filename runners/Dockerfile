FROM ubuntu:22.04

RUN apt-get update && apt-get -y install python3 python3-pip python3-virtualenv openjdk-17-jre

RUN mkdir -p /opt/projects

RUN mkdir -p /opt/tools

WORKDIR /opt/tools

RUN virtualenv init

COPY requirements.txt .

RUN bash -c "source ./init/bin/activate && pip install -r requirements.txt"

RUN apt-get install -y git
RUN git config --global --add safe.directory '*'

COPY metric_gathering metric_gathering

VOLUME "/opt/ext_tool"
VOLUME "/opt/workspace"
VOLUME "/opt/reports"
VOLUME "/opt/projects"
VOLUME "/opt/config/commits.txt"

CMD ["bash", "-c", "source ./init/bin/activate && python3 metric_gathering/multirun.py --tool $METRICS_TOOL_NAME --analyze --postprocess --tool_path /opt/ext_tool --wd_path /opt/workspace --report_path /opt/reports --project_path /opt/projects/${PROJECT_NAME} --only_commits /opt/config/commits.txt --allow_no_metrics --max_failures 10000 --skip_missing_commits"]
