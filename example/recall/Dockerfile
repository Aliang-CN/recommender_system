FROM python:3.7

RUN pip install -i https://mirrors.ustc.edu.cn/pypi/web/simple  dask  fastapi uvicorn protobuf grpcio
RUN pip install sanic
COPY ./ /app
RUN mkdir -p /app/log/
EXPOSE 80
WORKDIR /app

CMD ["python", "entrypoint.py"]
