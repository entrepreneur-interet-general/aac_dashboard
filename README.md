# AAC_Dash
 [![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0) [![Build Status](https://travis-ci.org/raphaelleroffo/aac_dash.svg?branch=master)](https://travis-ci.org/raphaelleroffo/aac_dash) [![Updates](https://pyup.io/repos/github/raphaelleroffo/aac_dash/shield.svg)](https://pyup.io/repos/github/raphaelleroffo/aac_dash/) [![Python 3](https://pyup.io/repos/github/raphaelleroffo/aac_dash/python-3-shield.svg)](https://pyup.io/repos/github/raphaelleroffo/aac_dash/) [![Coverage](https://codecov.io/github/raphaelleroffo/aac_dash/coverage.svg?branch=master)](https://codecov.io/github/raphaelleroffo/aac_dash?branch=master) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


This dashboard is designed to improve team collaboration in reviewing job applications. It has been specifically designed to review applications to the EIG Programme from Etalab


## Usage
If you are on Linux and you have [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) installed you can run the script `utility/setup_virtualenv_and_repo.sh` to:

- create a python virtual environment and activate it
- install all project dependencies from `requirements.txt`
- create a git repository
- create your `Initial commit`

Here is how you run the script:

```shell
cd aac_dash
# mind the dot!
. utility/setup_virtualenv_and_repo.sh
```

Then you will need to create an `.env` file where to store your environment variables (SECRET key, plotly credentials, API keys, etc). Do NOT TRACK this `.env` file. See `.env.example`.

Run all tests with a simple:

```
pytest -v
```


## Run your Dash app
Check that the virtual environment is activated, then run:

```shell
cd aac_dash
python app.py
```

## Code formatting
To format all python files, run:

```shell
black .
```

## Pin your dependencies

```shell
pip freeze > requirements.txt
```

## Deploy on Heroku
Follow the [Dash deployment guide](https://dash.plot.ly/deployment) or have a look at the [dash-heroku-template](https://github.com/plotly/dash-heroku-template)
