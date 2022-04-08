# STEP 1: Install base image. Optimized for Python.
FROM python:3.7

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN apt-get install gcc

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

# Step 9: Run Flask
RUN pip install -U cpython

RUN conda install -c conda-forge libsndfile



# Step 2: Add requirements.txt file
COPY /requirements.txt /requirements.txt

# Step 3:  Install required python dependencies from requirements file
RUN pip install webrtcvad-wheels
RUN pip install google-cloud-documentai
RUN pip install -r requirements.txt


# Step 4: Copy source code in the current directory to the container
ADD /app /App/app
ADD /Real_Time_Voice_Cloning /App/Real_Time_Voice_Cloning
ADD /saved_models /App/saved_models
COPY /index.py /App/index.py


# Step 5: Set working directory to previously added app directory
WORKDIR /App


# Step 6: Expose the port Flask is running on
EXPOSE 8000

# Step 9: Run Flask
CMD ["uvicorn", "index:app"]