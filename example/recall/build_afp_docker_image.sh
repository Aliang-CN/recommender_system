#!bin/bash
prefix=""
tag=$prefix$(date "+%Y%m%d%H%M%S")
docker build --platform=linux/amd64 . -t ccr.deepwisdomai.com/recsys/autorecall/k11_autorecall_api:$tag   -f ./Dockerfile

docker push ccr.deepwisdomai.com/recsys/autorecall/k11_autorecall_api:$tag 
