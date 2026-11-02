# One image for both the Inventory Service and the client (different commands in the YAML).
FROM python:3.12-slim
WORKDIR /app
COPY inventory.py client.py ./
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "inventory.py"]
