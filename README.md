<h2>Required Environment Variables</h2>

<h3>API values</h3>

* <b>kroger_api_location_id</b>: Use the [Locations](https://developer.kroger.com/reference/#tag/Locations) endpoint to locate the desired store.
* <b>kroger_app_client_id</b>: [Register an app](https://developer.kroger.com/)
* <b>kroger_app_client_secret</b>: [Register an app](https://developer.kroger.com/)

<h3>Communication details</h3>
Uses Google's SMTP work flow for sending alert emails

* <b>ip_alert_email</b>: Gmail account to send emails from e.g. example@gmail.com
* <b>ip_alert_email_pw</b>: A special password for non-humans.  Google Account -> Security -> App passwords
* <b>sale_checker_recipients</b>: semi-colon delineated field of email addresses
