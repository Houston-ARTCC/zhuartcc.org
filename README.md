
# VATUSA Django Template

A full-stack website template for management of VATUSA ARTCCs.

Written in Python 3.8 using the Django web framework.

**By Michael Romashov, Houston ARTCC Webmaster**

## Prerequisites

- Python 3.8 (with pip)
- Nginx or Apache

## Installation

1. Update pip to the latest version.
	- `python -m pip install --upgrade pip`

2. Clone the repository to a local directory and cd into it.
	-	`git clone https://github.com/MikeRomaa/zhuartcc.git`

3. Inside the directory, create a virtual environment (venv) and activate it.
	-	`python -m venv venv`
	-	`source venv/bin/activate` (Linux)
	-	`venv\Scripts\activate` (Windows)

4. You should now see `(venv)` next to your cursor, indicating that you are now running python from the venv.
	-	`(venv) user@host:~/zhuartcc.org$`

5. Install the required dependencies for the project.
	-	`pip install -r requirements.txt`

6. Create `logs` directory for log file storage.
	-	`mkdir logs`

7. Make a copy of `.env.example` and name it `.env`.
	-	`cp .env.example .env`

8. Edit `.env` to fill in environment variables.
	- **DEV_ENV** = `True` if used in development, `False` if used in production.
	- **SECRET_KEY** = Django secret key used to provide cryptographic signing. Can be generated at  https://djecrety.ir/. (Not required in development)
	- **WEBSITE_DOMAIN** = Domain of your website (eg. `zhuartcc.org`). Used to generate hostnames.
	- **EMAIL_*** = Self explanatory email configuration. Refer to SMTP host's instructions to get values.
	- **ULS_K_VALUE** = The `k` value in your facility's ULS JWK.
	- **API_KEY** = Your facility's *VATUSA APIv2* key.
	- **AIRPORT_IATA** = JSON encoded list of IATA codes of controlled airfields within your ARTCC. Used to detect online controllers. (eg. `"['IAH', 'MSY', 'HOU']"`)
	- **MAVP_ARTCCS** = JSON encoded list of ICAO codes of ARTCCS with whom you have Mutual Automatic Visiting Privileges. Used to allow MAVP controllers to log in. (eg. `"['ZJX', 'PCF', 'ZFW']"`)
		- Use `"[]"` if your facility does not utilize MAVPs.

9. Perform Django migration, which creates the database and its tables.
	-	`python manage.py makemigrations administration api event feedback pilots resource training user visit`
	-	`python manage.py migrate`

10. Pull your facility's home roster from VATUSA's API.
	-	`python manage.py pull_roster`
