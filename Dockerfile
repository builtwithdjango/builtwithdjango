# Build stage
FROM node:16 AS build

WORKDIR /app
COPY . .

RUN npm install
RUN npm run build

# Production stage
FROM python:3.11

WORKDIR /app

COPY . .
COPY --from=build /app/frontend/build/ ./frontend/build/

RUN pip install --no-cache-dir -r requirements.txt
# RUN opentelemetry-bootstrap -a install

EXPOSE 80

CMD ["deployment/entrypoint.sh"]
