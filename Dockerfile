FROM python:2.7-alpine
MAINTAINER "Charles Reid" <charles@charlesreid1.com>

RUN apk add --update git

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000
CMD ["python", "captain_hook.py"]
