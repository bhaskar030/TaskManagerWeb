FROM python:3.10-slim-bullseye

# Set environment variables
ENV ACCEPT_EULA=Y
ENV DEBIAN_FRONTEND=noninteractive

# Install base tools and certificates for apt over HTTPS
RUN apt-get update && apt-get install -y \
     curl gnupg2 apt-transport-https ca-certificates \
     unixodbc-dev gcc g++ libffi-dev libssl-dev libpq-dev \
     software-properties-common build-essential \
     unixodbc-dev python3-dev \
 && rm -rf /var/lib/apt/lists/*

# Add crosoft package signing key (GPG secured method)
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg

# Add Microsoft SQL Server repository
RUN echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" \
    > /etc/apt/sources.list.d/mssql-release.list

# Update and install the ODBC Driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up working dir
WORKDIR /app

RUN pip install huggingface_hub[hf_xet]

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

EXPOSE 8001
ENV FLASK_APP=app.py FLASK_RUN_HOST=0.0.0.0

#CMD ["flask", "run"]
# Start the app
CMD ["./startup.sh"]