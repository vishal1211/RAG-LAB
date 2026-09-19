docker build -t rag-lab-backend .

docker stop rag-lab-api

docker rm rag-lab-api

docker run \
  --name rag-lab-api \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  rag-lab-backend