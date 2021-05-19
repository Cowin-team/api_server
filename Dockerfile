FROM python:3.9.5

# Get rid of the warning: "debconf: unable to initialize frontend: Dialog"
# https://github.com/moby/moby/issues/27988
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update -qq; \
    apt-get install -y build-essential \
                       libpq-dev \
                       tzdata \
                       apt-utils \
                       neovim \
                       sudo \
                       lsb-release \
                       locales; \
    rm -rf /var/lib/apt/lists/*;


RUN addgroup --system app_user --gid 1000; \
    adduser --gecos '' --uid 1000 --gid 1000 --disabled-password app_user;

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN sudo mkdir /app; sudo chown -R app_user:app_user /app

USER app_user

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app

