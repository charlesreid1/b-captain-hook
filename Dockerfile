FROM python:3-alpine
MAINTAINER "Charles Reid" <charles@charlesreid1.com>

VOLUME ["/app/hooks"]
VOLUME ["/tmp/triggers"]

RUN apk add --update git

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000
CMD ["python", "./captain_hook.py"]
