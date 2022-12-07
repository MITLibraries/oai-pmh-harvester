FROM python:3.11-slim AS py3
RUN pip install pipenv

FROM py3 AS wheel
WORKDIR /app
COPY . .
RUN python3 setup.py bdist_wheel

FROM py3
COPY Pipfile* /
RUN pipenv install --system --ignore-pipfile --deploy
COPY --from=wheel /app/dist/harvest*-py3-none-any.whl .
RUN pip3 install harvest*-py3-none-any.whl

ENTRYPOINT ["oai"]
CMD ["--help"]
