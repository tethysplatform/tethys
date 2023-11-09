FROM mambaorg/micromamba:jammy
ARG PYTHON_VERSION="3.*"

ENV CONDA_HOME="/opt/conda"
ENV ENV_NAME="tethys"
ENV TETHYS_DB_HOST=""
ENV TETHYS_DB_PORT=""
ENV TETHYS_DB_ENGINE=""
ENV TETHYS_DB_NAME=""
ENV TETHYS_DB_USERNAME=""
ENV TETHYS_DB_PASSWORD=""
ENV POSTGRES_PASSWORD=""
ENV TETHYS_HOME="/tethysdev"
ENV TETHYS_SRC="/tethys"

USER root
RUN mkdir -p ${TETHYS_SRC} \
 && mkdir -p ${TETHYS_HOME} \
 && chown -R ${MAMBA_USER}:${MAMBA_USER} ${TETHYS_SRC} ${TETHYS_HOME}

# Setup conda symlink for the micromamba command
RUN mkdir -p ${CONDA_HOME}/bin
RUN ln -s /bin/micromamba ${CONDA_HOME}/bin/conda

# Setup Conda Environment
COPY --chown=${MAMBA_USER}:${MAMBA_USER} environment.yml /tmp/environment.yml
RUN sed -i "s/- python$/- python=${PYTHON_VERSION}/g" /tmp/environment.yml \
 && micromamba create -n "${ENV_NAME}" --yes --file /tmp/environment.yml \
 && micromamba clean --all --yes

# Copy Tethys Src
ADD --chown=${MAMBA_USER}:${MAMBA_USER} . ${TETHYS_SRC}
ADD --chown=${MAMBA_USER}:${MAMBA_USER} docker/app-dev-environment/run.sh ${TETHYS_SRC}/run.sh

ARG MAMBA_DOCKERFILE_ACTIVATE=1  # (otherwise python will not be found)
RUN pip install -e ${TETHYS_SRC}

WORKDIR ${TETHYS_HOME}

CMD bash ${TETHYS_SRC}/run.sh