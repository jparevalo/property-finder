FROM python:3

ARG APP_NAME=daily_properties
ENV APP_NAME=${APP_NAME}

ARG USER_ID="10001"
ARG GROUP_ID="app"
ARG HOME="/app"

ENV HOME=${HOME}
RUN groupadd --gid ${USER_ID} ${GROUP_ID} && \
    useradd --create-home --uid ${USER_ID} --gid ${GROUP_ID} --home-dir /app ${GROUP_ID}

# List packages here
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        file        \
        gcc         \
        libwww-perl && \
    apt-get autoremove -y && \
    apt-get clean

# Upgrade pip
RUN pip install --upgrade pip

WORKDIR ${HOME}

ADD requirements requirements/
RUN pip install -r requirements/requirements.txt

ADD . ${HOME}/${APP_NAME}
ENV PATH $PATH:${HOME}/${APP_NAME}/bin

# Drop root and change ownership of the application folder to the user
RUN chown -R ${USER_ID}:${GROUP_ID} ${HOME}
USER ${USER_ID}

# start app
CMD ["python", "/app/daily_properties/main.py"]