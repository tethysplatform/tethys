FROM mambaorg/micromamba:jammy
ARG PYTHON_VERSION="3.*"
ARG NEW_MAMBA_USER=tethysdev
ARG NEW_MAMBA_USER_ID=1000
ARG NEW_MAMBA_USER_GID=1000

ENV CONDA_HOME="/opt/conda"
ENV ENV_NAME="tethys"
ENV TETHYS_DB_HOST=""
ENV TETHYS_DB_PORT=""
ENV TETHYS_DB_USERNAME="tethys_default"
ENV TETHYS_DB_PASSWORD="pass"
ENV TETHYS_DB_SUPER_USERNAME="tethys_super"
ENV TETHYS_DB_SUPER_PASSOWRD="pass"
ENV PGPASSWORD="mysecretpassword"
ENV TETHYS_HOME="/tethysdev"
ENV TETHYS_SRC="/tethys"
ENV TERM="xterm"

USER root
RUN if grep -q '^ID=alpine$' /etc/os-release; then \
      # alpine does not have usermod/groupmod
      apk add --no-cache --virtual temp-packages shadow; \
    fi && \
    usermod "--login=${NEW_MAMBA_USER}" "--home=/home/${NEW_MAMBA_USER}" \
        --move-home "-u ${NEW_MAMBA_USER_ID}" "${MAMBA_USER}" && \
    groupmod "--new-name=${NEW_MAMBA_USER}" \
        "-g ${NEW_MAMBA_USER_GID}" "${MAMBA_USER}" && \
    if grep -q '^ID=alpine$' /etc/os-release; then \
      # remove the packages that were only needed for usermod/groupmod
      apk del temp-packages; \
    fi && \
    # Update the expected value of MAMBA_USER for the
    # _entrypoint.sh consistency check.
    echo "${NEW_MAMBA_USER}" > "/etc/arg_mamba_user" && \
    :
ENV MAMBA_USER=$NEW_MAMBA_USER

RUN mkdir -p ${TETHYS_SRC} \
 && mkdir -p ${TETHYS_HOME} \
 && chown -R ${MAMBA_USER}:${MAMBA_USER} ${TETHYS_SRC} ${TETHYS_HOME} \
 && chmod -R 775 ${TETHYS_SRC} ${TETHYS_HOME}

# Setup conda symlink for the micromamba command
RUN mkdir -p ${CONDA_HOME}/bin \
 && ln -s /bin/micromamba ${CONDA_HOME}/bin/conda

# Setup Conda Environment
USER ${MAMBA_USER}
COPY --chown=${MAMBA_USER}:${MAMBA_USER} environment.yml /tmp/environment.yml
RUN sed -i "s/- python$/- python=${PYTHON_VERSION}/g" /tmp/environment.yml \
 && micromamba create -n "${ENV_NAME}" --yes --file /tmp/environment.yml \
 && micromamba clean --all --yes

# Copy Tethys Src
ADD --chown=${MAMBA_USER}:${MAMBA_USER} . ${TETHYS_SRC}
ADD --chown=${MAMBA_USER}:${MAMBA_USER} docker/tethys-dev/run.sh ${TETHYS_SRC}/run.sh

ARG MAMBA_DOCKERFILE_ACTIVATE=1  # (otherwise python will not be found)
RUN pip install -e ${TETHYS_SRC}

WORKDIR ${TETHYS_HOME}

CMD bash ${TETHYS_SRC}/run.sh