FROM python:3.10.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY Pipfile Pipfile.lock /app/

RUN pip install django && pip install pipenv
COPY . /app/

RUN pipenv install --deploy
RUN pipenv install --system 

CMD ["pipenv", "run", "gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
