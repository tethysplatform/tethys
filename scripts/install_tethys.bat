@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

IF %ERRORLEVEL% NEQ 0 (SET ERRORLEVEL=0)

:: Set defaults
SET ALLOWED_HOST=127.0.0.1
SET TETHYS_HOME=C:%HOMEPATH%\tethys
SET TETHYS_SRC=%TETHYS_HOME%\src
SET TETHYS_PORT=8000
SET TETHYS_DB_USERNAME=tethys_default
SET TETHYS_DB_PASSWORD=pass
SET TETHYS_DB_PORT=5436
SET CONDA_HOME=
SET CONDA_EXE=Miniconda3-latest-Windows-x86_64.exe
SET CONDA_ENV_NAME=tethys
SET PYTHON_VERSION=3
SET BRANCH=release

SET TETHYS_SUPER_USER=admin
SET "TETHYS_SUPER_USER_EMAIL="
SET TETHYS_SUPER_USER_PASS=pass
SET ECHO_COMMANDS=

:loop
IF NOT "%1"=="" (
    SET OPTION_RECOGNIZED=FALSE
    IF "%1"=="-t" (
        SET TETHYS_HOME=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--tethys-home" (
        SET TETHYS_HOME=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-s" (
        SET TETHYS_SRC=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--tethys-src" (
        SET TETHYS_SRC=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-a" (
        SET ALLOWED_HOST=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--allowed-host" (
        SET ALLOWED_HOST=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-p" (
        SET TETHYS_PORT=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--port" (
        SET TETHYS_PORT=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-b" (
        SET BRANCH=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--branch" (
        SET BRANCH=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-c" (
        SET CONDA_HOME=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--conda-home" (
        SET CONDA_HOME=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-C" (
        SET CONDA_EXE=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--conda-exe" (
        SET CONDA_EXE=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-n" (
        SET CONDA_ENV_NAME=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--conda-env-name" (
        SET CONDA_ENV_NAME=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--python-version" (
        SET PYTHON_VERSION=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--db-username" (
        SET TETHYS_DB_USERNAME=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--db-password" (
        SET TETHYS_DB_PASS=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--db-port" (
        SET TETHYS_DB_PORT=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-S" (
        SET TETHYS_SUPER_USER=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--superuser" (
        SET TETHYS_SUPER_USER=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-E" (
        SET TETHYS_SUPER_USER_EMAIL=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--superuser-email" (
        SET TETHYS_SUPER_USER_EMAIL=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-P" (
        SET TETHYS_SUPER_USER_PASS=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--superuser-pass" (
        SET TETHYS_SUPER_USER_PASS=%2
        SHIFT
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-x" (
        SET ECHO_COMMANDS=@ECHO ON
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="-h" (
        GOTO :usage
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "%1"=="--help" (
        GOTO :usage
        SET OPTION_RECOGNIZED=TRUE
    )
    IF "!OPTION_RECOGNIZED!"=="FALSE" (
        ECHO Ignoring unrecognized option: %1
    )
    SHIFT
    GOTO :loop
)

IF %ERRORLEVEL% NEQ 0 (
    ECHO Error occured while parsing command line arguments.
    EXIT /B %ERRORLEVEL%
)

SET CEANUP=

:: Resolve relative paths
IF NOT EXIST "!TETHYS_HOME!" (
    MKDIR "!TETHYS_HOME!"
    SET CLEANUP=TRUE
)

IF EXIST "!CD!\!TETHYS_HOME!" (
    :: TETHYS_HOME is a relative path so make it absolute
    PUSHD .\
    CD "!TETHYS_HOME!"
    SET TETHYS_HOME=!CD!
    POPD
)

IF "!CLEANUP!"=="TRUE" (
    RMDIR "!TETHYS_HOME!"
    SET CLEANUP=
)

:: set CONDA_HOME relative to TETHYS_HOME if not already set
IF NOT DEFINED CONDA_HOME (
    SET CONDA_HOME=!TETHYS_HOME!\miniconda
) ELSE (
    IF NOT EXIST "!CONDA_HOME!" (
        MKDIR "!CONDA_HOME!"
        SET CLEANUP=TRUE
    )
    echo "!CD!\!CONDA_HOME!"
    IF EXIST "!CD!\!CONDA_HOME!" (
        :: CONDA_HOME is a relative path so make it absolute
        PUSHD .\
        CD "!CONDA_HOME!"
        SET CONDA_HOME=!CD!
        POPD
    )

    IF "!CLEANUP!"=="TRUE" (
        RMDIR "!CONDA_HOME!"
    )
)

:: check if CONDA_HOME has spaces
IF NOT "!CONDA_HOME!"=="!CONDA_HOME: =!" (
    ECHO ERROR: Miniconda cannot be installed at "!CONDA_HOME!" becuase it contains spaces. Please specify a different conda home path using the '--conda-home' option.
    EXIT /B 1
)

!ECHO_COMMANDS!

ECHO Starting Tethys Installation...

:: Make tethys directory
MKDIR "!TETHYS_HOME!"

:: Install miniconda
:: first see if Miniconda is already installed
IF EXIST "!CONDA_HOME!\Scripts\activate" (
    ECHO Using existing Miniconda installation...
) ELSE (
    ECHO Installing Miniconda...
    START /wait "" !CONDA_EXE! /InstallationType=JustMe /RegisterPython=0 /S /D=!CONDA_HOME!
)
CALL "!CONDA_HOME!\Scripts\activate"

IF %ERRORLEVEL% NEQ 0 (
    ECHO Error occured while attempting to install Miniconda.
    EXIT /B %ERRORLEVEL%
)

:: clone Tethys repo
ECHO Cloning the Tethys Platform repo...
conda install --yes git
git clone https://github.com/tethysplatform/tethys "!TETHYS_SRC!"
CD "!TETHYS_SRC!"
git checkout !BRANCH!

IF %ERRORLEVEL% NEQ 0 (
    ECHO Error occured while cloning the tethys repo.
    EXIT /B %ERRORLEVEL%
)

:: create conda env and install Tethys
ECHO Setting up the !CONDA_ENV_NAME! environment...
conda env create -n !CONDA_ENV_NAME! -f environment_py!PYTHON_VERSION!.yml
CALL activate !CONDA_ENV_NAME!
python setup.py develop

IF NOT "!ALLOWED_HOST!"=="127.0.0.1" (
    SET ALLOWED_HOST_OPT=--allowed-host !ALLOWED_HOST!
)

tethys gen settings !ALLOWED_HOST_OPT! --db-username !TETHYS_DB_USERNAME! --db-password !TETHYS_DB_PASSWORD! --db-port !TETHYS_DB_PORT!

IF %ERRORLEVEL% NEQ 0 (
    ECHO Error occured while setting up the !CONDA_ENV_NAME! environment.
    EXIT /B %ERRORLEVEL%
)

:: Setup local database
ECHO Setting up the Tethys database...
initdb  -U postgres -D "!TETHYS_HOME!\psql\data"
pg_ctl -U postgres -D "!TETHYS_HOME!\psql\data" -l "!TETHYS_HOME!\psql\logfile" start -o "-p !TETHYS_DB_PORT!"
ECHO Waiting for databases to startup...
TIMEOUT 10 /NOBREAK
psql -U postgres -p !TETHYS_DB_PORT! --command "CREATE USER !TETHYS_DB_USERNAME! WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD '!TETHYS_DB_PASSWORD!';"
createdb -U postgres -p !TETHYS_DB_PORT! -O !TETHYS_DB_USERNAME! -E utf-8 -T template0 !TETHYS_DB_USERNAME!

IF %ERRORLEVEL% NEQ 0 (
    ECHO Error occured while setting up the tethys database.
    EXIT /B %ERRORLEVEL%
)

:: Initialze Tethys database
tethys manage syncdb
ECHO from django.contrib.auth.models import User; User.objects.create_superuser('!TETHYS_SUPER_USER!', '!TETHYS_SUPER_USER_EMAIL!', '!TETHYS_SUPER_USER_PASS!') | python manage.py shell
ECHO Stopping database server...
pg_ctl -U postgres -D "!TETHYS_HOME!\psql\data" stop

IF %ERRORLEVEL% NEQ 0 (
    ECHO Error occured while initializing the database.
    EXIT /B %ERRORLEVEL%
)

:: Create environment activate/deactivate scripts
SET ACTIVATE_DIR=!CONDA_HOME!\envs\!CONDA_ENV_NAME!\etc\conda\activate.d
SET DEACTIVATE_DIR=!CONDA_HOME!\envs\!CONDA_ENV_NAME!\etc\conda\deactivate.d
MKDIR "!ACTIVATE_DIR!" "!DEACTIVATE_DIR!"
SET ACTIVATE_SCRIPT=%ACTIVATE_DIR%\tethys-activate.bat
SET DEACTIVATE_SCRIPT=!DEACTIVATE_DIR!\tethys-deactivate.bat

ECHO @ECHO OFF>> "!ACTIVATE_SCRIPT!"
ECHO SET TETHYS_HOME=!TETHYS_HOME!>> "!ACTIVATE_SCRIPT!"
ECHO SET TETHYS_PORT=!TETHYS_PORT!>> "!ACTIVATE_SCRIPT!"
ECHO SET TETHYS_DB_PORT=!TETHYS_DB_PORT!>> "!ACTIVATE_SCRIPT!"
ECHO DOSKEY tethys_start_db=pg_ctl -U postgres -D "%%TETHYS_HOME%%\psql\data" -l "%%TETHYS_HOME%%\psql\logfile" start -o "-p %%TETHYS_DB_PORT%%" >> "!ACTIVATE_SCRIPT!"
ECHO DOSKEY tstartdb=pg_ctl -U postgres -D "%%TETHYS_HOME%%\psql\data" -l "%%TETHYS_HOME%%\psql\logfile" start -o "-p %%TETHYS_DB_PORT%%" >>"!ACTIVATE_SCRIPT!"
ECHO DOSKEY tethys_stop_db=pg_ctl -U postgres -D "%%TETHYS_HOME%%\psql\data" stop >>"!ACTIVATE_SCRIPT!"
ECHO DOSKEY tstopdb=pg_ctl -U postgres -D "%%TETHYS_HOME%%\psql\data" stop >> "!ACTIVATE_SCRIPT!"
ECHO DOSKEY tms=tethys manage start -p !ALLOWED_HOST!:%%TETHYS_PORT%% >> "!ACTIVATE_SCRIPT!"
ECHO DOSKEY tstart=pg_ctl -U postgres -D "%%TETHYS_HOME%%\psql\data" -l "%%TETHYS_HOME%%\psql\logfile" start -o "-p %%TETHYS_DB_PORT%%" $T tethys manage start -p !ALLOWED_HOST!:%%TETHYS_PORT%% >> "!ACTIVATE_SCRIPT!"

ECHO @ECHO OFF>> "!DEACTIVATE_SCRIPT!"
ECHO SET TETHYS_HOME=>> "!DEACTIVATE_SCRIPT!"
ECHO SET TETHYS_DB_PORT=>> "!DEACTIVATE_SCRIPT!"
ECHO SET TETHYS_PORT=>> "!DEACTIVATE_SCRIPT!"
ECHO DOSKEY tethys_start_db= >> "!DEACTIVATE_SCRIPT!"
ECHO DOSKEY tstartdb= >> "!DEACTIVATE_SCRIPT!"
ECHO DOSKEY tethys_stop_db= >> "!DEACTIVATE_SCRIPT!"
ECHO DOSKEY tstopdb= >> "!DEACTIVATE_SCRIPT!"
ECHO DOSKEY tms= >> "!DEACTIVATE_SCRIPT!"
ECHO DOSKEY tstart= >> "!DEACTIVATE_SCRIPT!"

IF %ERRORLEVEL% NEQ 0 (
    ECHO Error occured while creating activate scripts.
    EXIT /B %ERRORLEVEL%
)

SET TETHYS_CMD=!TETHYS_HOME!\tethys_cmd.bat
ECHO @ECHO OFF>> "!TETHYS_CMD!"
ECHO CD !TETHYS_HOME! >> "!TETHYS_CMD!"
ECHO CMD /K !CONDA_HOME!\Scripts\activate !CONDA_ENV_NAME! >> "!TETHYS_CMD!"

ECHO Tethys installation complete^^!
ECHO.
ECHO To open a new command prompt with the !CONDA_ENV_NAME! environment activated double click the file "!TETHYS_CMD!"

EXIT /B %ERRORLEVEL%

:usage
@ECHO OFF
ECHO USAGE: install_tethys.bat [options]
ECHO.
ECHO OPTIONS:
ECHO     -t, --tethys-home [PATH]            Path for tethys home directory. Default is 'C:\%HOMEPATH%\tethys'.
ECHO     -s, --tethys-src [PATH]             Path for tethys source directory. Default is %%TETHYS_HOME%%\src.
ECHO     -a, --allowed-host [HOST]           Hostname or IP address on which to serve tethys. Default is 127.0.0.1.
ECHO     -p, --port [PORT]                   Port on which to serve tethys. Default is 8000.
ECHO     -b, --branch [BRANCH_NAME]          Branch to checkout from version control. Default is 'release'.
ECHO     -c, --conda-home [PATH]             Path to conda home directory where Miniconda will be installed. Default is %%TETHYS_HOME%%\miniconda.
ECHO     -C, --conda-exe [PATH]              Path to Miniconda installer executable. Default is '.\Miniconda3-latest-Windows-x86_64.exe'.
ECHO     -n, --conda-env-name [NAME]         Name for tethys conda environment. Default is 'tethys'.
ECHO     --python-version [PYTHON_VERSION]   Main python version to install tethys environment into (2-deprecated or 3). Default is 3.
ECHO     --db-username [USERNAME]            Username that the tethys database server will use. Default is 'tethys_default'.
ECHO     --db-password [PASSWORD]            Password that the tethys database server will use. Default is 'pass'.
ECHO     --db-port [PORT]                    Port that the tethys database server will use. Default is 5436.
ECHO     -S, --superuser [USERNAME]          Tethys super user name. Default is 'admin'.
ECHO     -E, --superuser-email [EMAIL]       Tethys super user email. Default is ''.
ECHO     -P, --superuser-pass [PASSWORD]     Tethys super user password. Default is 'pass'.
ECHO     -x                                  Flag to echo all commands.
ECHO     -h, --help                          Print this help information.

EXIT /B 0