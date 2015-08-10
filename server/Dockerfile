from python:2.7

ENV PYTHONUNBUFFERED 1
RUN mkdir /projects
WORKDIR /projects
ADD requirements.txt /projects/

RUN pip install Django
RUN pip install djangorestframework
RUN pip install psycopg2
RUN pip install Mako
RUN pip install -r requirements.txt
ADD . /projects/
