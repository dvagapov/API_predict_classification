FROM python:3.7

WORKDIR /api
COPY . /api

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["manage.py","run"]