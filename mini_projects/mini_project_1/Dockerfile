FROM python:3.14.2-slim
WORKDIR /app
COPY .env .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY hotel_bookings.csv .
COPY clean_data.py .
CMD [ "python", "clean_data.py" ]




