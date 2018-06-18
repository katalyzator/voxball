# Build from python image.
FROM python:2-onbuild

# Set project name
ENV DJANGO_SETTINGS_MODULE=votem.new_prod_settings

# Set volume for database and static files.
# RUN mkdir /db && mkdir /back_static && mkdir /photo && mkdir /votem_django_logs

WORKDIR /app
COPY ./requirements.txt /requirements.txt

# Install python dependencies
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# Copy source code
# COPY . /code/votem

CMD bash run.sh
