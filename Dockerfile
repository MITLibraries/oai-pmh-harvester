FROM python:3

RUN pip install pipenv

WORKDIR /app
COPY . .
RUN pipenv install --system

ENTRYPOINT ["python3", "harvester/cli.py"]
CMD ["--help"]
