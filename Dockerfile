FROM python:3.9.16-alpine3.17

COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "fast_api_app:app", "--host", "0.0.0.0", "--port", "80"]


# docker build -t recipe_eater .
# docker run -d --name recipe_eater -p 127.0.0.1:20001:80 --restart unless-stopped recipe_eater