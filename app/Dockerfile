FROM python

RUN pip install fastapi
RUN pip install gunicorn
RUN pip install sqlalchemy
RUN pip install asyncpg
RUN pip install pydantic_settings
COPY app/ app/
COPY web/ web/
# COPY routes/ app/routes/
# ADD __init__.py app/__init__.py
# ADD app.py app/app.py
ADD settings_app.cfg settings_app.cfg