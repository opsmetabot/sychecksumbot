FROM python:3.6.15-slim
# RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
# RUN  sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list 
# RUN  apt-get clean

# RUN apt-get update && apt-get install -y cron
# # RUN apt-get install -y cron
# RUN apt-get install -y vim
RUN mkdir /work
ADD ./requirements.txt /work
# RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple 
ADD ./synced-bot /work
WORKDIR /work

# RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

# CMD ["cron", "-f"]