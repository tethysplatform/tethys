# WARNING this is completely untested!!!!
# Just some snippits to get started

# TODO make these commandline options
SET TETHYS_HOME="C:\tethys"
SET TETHYS_PORT=8000
SET TETHYS_DB_PORT=5435
SET CONDA_HOME="%TETHYS_HOME%\miniconda"
SET BRANCH=dev

sudo mkdir -p %TETHYS_HOME%

bitsadmin.exe /transfer "JobName" https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe "%TETHYS_HOME%\miniconda.exe"
start /wait "" %TETHYS_HOME%\miniconda.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%CONDA_HOME%

# clone Tethys repo
conda install --yes git
git clone https://github.com/tethysplatform/tethys "%TETHYS_HOME%/src"
cd "%TETHYS_HOME%/src"
git checkout %BRANCH%

# create conda env and install Tethys
conda env create -f tethys_conda_env.yml
. activate tethys
python setup.py develop
tethys gen settings -d "%TETHYS_HOME%/src/tethys_apps"

# Setup local database
conda install --yes -c conda-forge postgresql
initdb  -U postgres -D "%TETHYS_HOME%/psql/data"
pg_ctl -U postgres -D "%TETHYS_HOME%/psql/data" -l "%TETHYS_HOME%/psql/logfile" start -o "-p %TETHYS_DB_PORT%"
echo 'wating for databases to startup...'; sleep 10
psql -U postgres -p %TETHYS_DB_PORT% --command "CREATE USER tethys_default WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD 'pass';"
createdb -U postgres -p %TETHYS_DB_PORT% -O tethys_default tethys_default -E utf-8 -T template0

# Initialze Tethys database
tethys manage syncdb
tethys manage createsuperuser


ACTIVATE_DIR="%CONDA_HOME%\envs\tethys\etc\conda\activate.d"
DEACTIVATE_DIR="%CONDA_HOME%\envs\tethys\etc\conda\deactivate.d"
mkdir -p %ACTIVATE_DIR% %DEACTIVATE_DIR%
ACTIVATE_SCRIPT="%ACTIVATE_DIR%\tethys-activate.bat"
DEACTIVATE_SCRIPT="%DEACTIVATE_DIR%\tethys-deactivate.bat"

echo "set TETHYS_HOME='%TETHYS_HOME%'" >> %ACTIVATE_SCRIPT%
echo "set TETHYS_PORT='$%TETHYS_PORT%'"
echo "set TETHYS_DB_PORT='%TETHYS_DB_PORT%'" >> %ACTIVATE_SCRIPT%
echo "doskey tethys_start_db='pg_ctl -U postgres -D \%TETHYS_HOME%/psql/data -l \%TETHYS_HOME%/psql/logfile start -o \"-p \%TETHYS_DB_PORT%\"'" >> %ACTIVATE_SCRIPT%
echo "doskey tstartdb=tethys_start_db" >> %ACTIVATE_SCRIPT%
echo "doskey tms='tethys manage start -p 127.0.0.1:%TETHYS_PORT%'" >> %ACTIVATE_SCRIPT%

. %ACTIVATE_SCRIPT%

echo "set TETHYS_HOME=" >> %DEACTIVATE_SCRIPT%
echo "set TETHYS_DB_PORT=" >> %DEACTIVATE_SCRIPT%
echo "set TETHYS_PORT=" >> %DEACTIVATE_SCRIPT%
echo "doskey tethys_start_db=" >> %DEACTIVATE_SCRIPT%
echo "doskey tstartdb=" >> %DEACTIVATE_SCRIPT%
echo "doskey tms=" >> %DEACTIVATE_SCRIPT%