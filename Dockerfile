### Build and install packages
FROM python:3.10

USER root

# Switch root to app user, fix pip param
# @author: Nebil Müren - cas3322
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install Python dependencies
WORKDIR /app
COPY requirements.txt requirements.txt
COPY plugin_example  plugin_example
COPY flaskshop  flaskshop
COPY app.py  app.py

# param fix --no-cache (docker) --> --no-cache-dir (pip)
RUN pip install --no-cache-dir -r requirements.txt \
  # Handover app to appuser
  && chown -R appuser:appuser /app
USER appuser

CMD ["flask", "run", "--host=0.0.0.0"]
