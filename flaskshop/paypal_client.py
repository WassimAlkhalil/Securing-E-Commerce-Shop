from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from .settings import Config
def get_paypal_client():

    if Config.PAYPAL_ENV == "live":
        environment = LiveEnvironment(
            client_id=Config.PAYPAL_CLIENT_ID,
            client_secret=Config.PAYPAL_CLIENT_SECRET
        )
    else:
        environment = SandboxEnvironment(
                client_id=Config.PAYPAL_CLIENT_ID,
                client_secret=Config.PAYPAL_CLIENT_SECRET
            )
    return PayPalHttpClient(environment)
