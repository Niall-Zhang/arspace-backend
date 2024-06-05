from utils.stripe import capture_stripe_charge, create_payment_intent,create_stripe_customer
from utils.constants import DATA, ERROR, FALSE, SUCCESS, TRUE

import logging
logger = logging.getLogger(__name__)

def pay_via_stripe(payload):
    try:
        logger.info(f"process:start, method:pay_via_stripe(), payload:{payload}")
        charge = create_payment_intent(payload)
        if charge[SUCCESS]:
            return {SUCCESS:TRUE, DATA:charge[DATA]}
        return {SUCCESS:FALSE, ERROR:charge[ERROR]}
    except Exception as ex:
        return {SUCCESS:FALSE, ERROR:str(ex)}