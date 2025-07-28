# DaeguS-W

* mission_computer_main.log의 내용을 통해서 사고의 원인을 분석하고 정리해서 보고서(log_analysis.md)를 Markdown 형태로 를 작성해 놓는다.


## docker img build

```shell

docker build -t daeguS-W .

```

## Docker RUN

```shell
docker run -it \
  --name daeguS-W_temp \
  -v /Users/ywlee/daeguS-W:/app/project_data \
  -e DISPLAY=host.docker.internal:0 \
  daeguS-W:1.0

```
