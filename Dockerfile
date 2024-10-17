FROM surnet/alpine-wkhtmltopdf:3.16.0-0.12.6-full as wkhtmltopdf
FROM python:3.8.5-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies for wkhtmltopdf and lxml
RUN apk add --no-cache \
  libstdc++ \
  libx11 \
  libxrender \
  libxext \
  libssl1.1 \
  ca-certificates \
  fontconfig \
  freetype \
  ttf-dejavu \
  ttf-droid \
  ttf-freefont \
  ttf-liberation \
  libxml2-dev \
  libxslt-dev \
  && apk add --no-cache --virtual .build-deps \
  msttcorefonts-installer \
  \
  # Install microsoft fonts
  && update-ms-fonts \
  && fc-cache -f \
  \
  # Clean up when done
  && rm -rf /tmp/* \
  && apk del .build-deps

RUN apk add --no-cache --virtual .build-deps \
  ca-certificates gcc postgresql-dev linux-headers musl-dev \
  libffi-dev jpeg-dev zlib-dev libreoffice

WORKDIR $HOME/project

COPY ./requirements.txt ./requirements.txt
COPY ./loaddata.sh ./loaddata.sh

# Install a stable version of setuptools
RUN pip install --upgrade pip==24.0
RUN pip install setuptools==58.0.4 wheel==0.37.0 incremental==21.3.0 zope.interface==5.4.0 setuptools-rust==0.11.6
RUN pip install -r ./requirements.txt

COPY ./project $HOME/project

# Copy wkhtmltopdf files from docker-wkhtmltopdf image
COPY --from=wkhtmltopdf /bin/wkhtmltopdf /bin/wkhtmltopdf
COPY --from=wkhtmltopdf /bin/wkhtmltoimage /bin/wkhtmltoimage
COPY --from=wkhtmltopdf /bin/libwkhtmltox* /bin/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
