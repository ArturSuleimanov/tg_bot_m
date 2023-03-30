FROM python

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# root to save data from container
VOLUME [ "/app/models" ]
# app is a context of our root source, which was defined higher

CMD [ "python3", "main.py" ]