<b>Required environment variables</b>
<br><br>
API values<br>
* kroger_api_location_id: Use the [Locations](https://developer.kroger.com/reference/#tag/Locations) endpoint to locate the desired store.
* kroger_app_client_id: [Register an app](https://developer.kroger.com/)
* kroger_app_client_secret: [Register an app](https://developer.kroger.com/)

Communication details<br>
  Uses Google's SMTP work flow to send an email to each<br>
* ip_alert_email: Gmail account to send emails from e.g. example@gmail.com
* ip_alert_email_pw: A special password for non-humans.  Google Account -> Security -> App passwords
* sale_checker_recipients: semi-colon delineated field of email addresses
