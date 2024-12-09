FROM python:3

RUN  pip install -i https://mirrors.ustc.edu.cn/pypi/web/simple  protobuf grpcio

COPY example/etl-flow /app
COPY realtime_rec/protobuf /app/realtime_rec/protobuf

ENTRYPOINT ["python"]

