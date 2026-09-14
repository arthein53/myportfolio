FROM python:3.13-alpine AS builder

WORKDIR /app

RUN apk add --no-cache gcc musl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.13-alpine AS runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# Build static files without injecting production secrets into the image.
# PWS supplies production environment variables only when the container runs.
RUN PRODUCTION=False python manage.py collectstatic --noinput

EXPOSE 80

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:80 --workers 2 portfolio.wsgi:application"]
