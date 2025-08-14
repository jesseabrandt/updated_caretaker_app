FROM python:3.12

WORKDIR /st_app


RUN apt-get update && apt-get clean && apt-get install -y build-essential     curl     software-properties-common     git     && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip

RUN pip install -r ASA_Hackathon_Solution/requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "ASA_Hackathon_Solution/Home_Page.py", "--server.port=8501", "--server.address=0.0.0.0"]


