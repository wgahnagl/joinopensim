FROM fedora:latest

RUN useradd -u 5000 app

RUN dnf update -y && \
    dnf install -y python-pip 
# We copy just the requirements.txt first to leverage Docker cache

USER app:app
ENV PATH="/home/app/.local/bin:${PATH}"


COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt --user

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

