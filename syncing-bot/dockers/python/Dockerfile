FROM python:3.9
# RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
# RUN  sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list 
# RUN  apt-get clean

# RUN apt-get update 
# RUN apt-get install -y vim

# RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple 

ADD ./requirements.txt /requirements.txt
RUN  pip3 install -f /requirements.txt

#RUN pip install pyyaml
#RUN pip install kafka
#RUN pip3 install etcd3

