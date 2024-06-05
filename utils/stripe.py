import stripe
from arspace import settings
from authentication.models import User
from utils.constants import ATTACHED_NEW_CARD_SUCCESS, CREATE_STRIPE_CUSTOMER_FAILED, DATA, DETACHED_OLD_CARD_SUCCESS, ERROR, FALSE, MESSAGE, PAYMENT_FAILED, STRIPE_CREATE_CARD_SOURCE_FAILED, STRIPE_CREATE_CARD_TOKEN_SUCCESS, STRIPE_CUSTOMER_NOT_FOUND, SUCCESS, TRUE, USD
from utils.utils import deduct_events_seats, get_settings

# Stripe API key
# stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_secret_key = get_settings('stripe_secret_key')
stripe.api_key = stripe_secret_key

import logging
logger = logging.getLogger(__name__)



# Get stripe customer by email
def get_stripe_customer_by_email(email):
    try:
        stripe.api_key = get_settings('stripe_secret_key')
        customers = stripe.Customer.list(email=email, limit=1)
        if customers.data:
            return {SUCCESS:TRUE, DATA:customers.data[0]}
        return {SUCCESS:FALSE, ERROR:STRIPE_CUSTOMER_NOT_FOUND}
    except [Exception, stripe.error.StripeError] as ex:
        return {SUCCESS:FALSE, ERROR:str(ex)}


# Create a card token
def create_card_token(payload):
    try:
        logger.info(f"method:create_card_token(), process:start, payload:{payload}")
        
        # user_id = payload['user_id']
        # number = payload['number']
        # exp_month = payload['exp_month']
        # exp_year = payload['exp_year']
        # cvc = payload['cvc']
        card_token = payload['card_token']
        stripe_customer_id = payload['stripe_customer_id']
        
        # card = stripe.Token.create(
        #     card={
        #         "number": number,
        #         "exp_month": exp_month,
        #         "exp_year": exp_year,
        #         "cvc": cvc,
        #     },
        # )
        # logger.info(f"method:create_card_token(), card:{card}")
        # if card.id:
        # create_card_source = update_customer_card_token(stripe_customer_id,card.id)
        create_card_source = update_customer_card_token(stripe_customer_id,card_token)
        if create_card_source[SUCCESS]:
            return {SUCCESS:TRUE, MESSAGE:STRIPE_CREATE_CARD_TOKEN_SUCCESS}
        return {SUCCESS:FALSE, ERROR:STRIPE_CREATE_CARD_TOKEN_SUCCESS}
    except [Exception, stripe.error.StripeError] as ex:
        return {SUCCESS:FALSE, ERROR:str(ex)}


# Update customer card token
def update_customer_card_token(stripe_customer_id,new_card_token):
    try:
        logger.info("method:update_customer_card_token(), process:start")
        stripe.api_key = get_settings('stripe_secret_key')
        update_customer = stripe.Customer.modify(stripe_customer_id,source=new_card_token)
        # create_source = stripe.Customer.create_source(stripe_customer_id,source=new_card_token)
        logger.info(f"method:update_customer_card_token(), create_source:{update_customer}")
        if update_customer.id:
            return {SUCCESS:TRUE, DATA:update_customer.id}
        return {SUCCESS:FALSE,ERROR:STRIPE_CREATE_CARD_SOURCE_FAILED}    
    except [Exception, stripe.error.StripeError] as ex:
        return {SUCCESS:FALSE, ERROR:str(ex)}

# Attach new card to customer
def attach_card_to_customer(customer_id,new_card_token):
    try:
        logger.info(f"customer_id:{customer_id}, new_card_token:{new_card_token}")
        logger.info("method:attach_card_to_customer(), process:start")
        stripe.api_key = get_settings('stripe_secret_key')
        customer = stripe.Customer.retrieve(customer_id)
        logger.info(f"method:attach_card_to_customer(), customer:{customer}")
        if customer.id:            
            attach_card = stripe.Customer.modify(customer_id,source=new_card_token)
            logger.info(f"method:attach_card_to_customer(), attach_card:{attach_card}")
            create_source = stripe.Customer.create_source(customer_id,source=new_card_token)
            logger.info(f"method:attach_card_to_customer(), create_source:{create_source}")
            
            return {SUCCESS:TRUE,MESSAGE:ATTACHED_NEW_CARD_SUCCESS,DATA:attach_card}        
        return {SUCCESS:FALSE, ERROR:STRIPE_CUSTOMER_NOT_FOUND}
    except [Exception, stripe.error.StripeError] as ex:
        return {SUCCESS:FALSE, ERROR:str(ex)}
    
# Detach old card to customer
def detach_card_to_customer(customer_id,old_card_token):
    try:
        stripe.api_key = get_settings('stripe_secret_key')
        customer = stripe.Customer.retrieve(customer_id)        
        if customer:
            customer.sources.retrieve(old_card_token).detach()
            return {SUCCESS:TRUE,MESSAGE:DETACHED_OLD_CARD_SUCCESS}        
        return {SUCCESS:FALSE, ERROR:STRIPE_CUSTOMER_NOT_FOUND}
    except [Exception, stripe.error.StripeError] as ex:
        return {SUCCESS:FALSE, ERROR:str(ex)}

# Create a customer and save card for future payments
def create_stripe_customer(email):
    try:
        stripe.api_key = get_settings('stripe_secret_key')
        logger.info(f"method:create_stripe_customer(), email:{email}")
        customer = stripe.Customer.create(email=email)
        logger.info(f"method:create_stripe_customer(), customer:{customer}")
        if customer.id:
            user = User.objects.get(email=email)
            user.stripe_customer_id = customer.id
            user.save()
            return {SUCCESS:TRUE, DATA:customer}
        return {SUCCESS:FALSE, ERROR:CREATE_STRIPE_CUSTOMER_FAILED}
    except [Exception, stripe.error.StripeError] as ex:
        logger.info(f"method:create_stripe_customer(), error:{str(ex)}")
        return {SUCCESS:FALSE, ERROR:str(ex)}
    

# Charge a customer using their saved card
def create_payment_intent(payload):
    try:
        logger.info(f"method:create_payment_intent(), process:start, payload:{payload}")
        stripe_customer_id = payload['stripe_customer_id']
        amount = int(payload['amount']) * 100
        stripe.api_key = get_settings('stripe_secret_key')
        charge = stripe.PaymentIntent.create(
            amount=amount,
            currency=USD,
            automatic_payment_methods={"enabled": True,"allow_redirects":"never"},
            customer=stripe_customer_id,
            confirm=True,
        )
        if charge.id:
            is_deducted = deduct_events_seats(payload)
            if is_deducted[SUCCESS]:
                return {SUCCESS:TRUE, DATA:charge}
            return is_deducted
        return {SUCCESS:FALSE, ERROR:PAYMENT_FAILED}
    except [Exception, stripe.error.StripeError] as ex:
        logger.info(f"method:create_payment_intent(), error:{str(ex)}")
        return {SUCCESS:FALSE, ERROR:str(ex)}
    

# Capture Stripe Charge
def capture_stripe_charge(charge_id):
    try:
        logger.info("method:capture_stripe_charge(), process:start")
        stripe.api_key = get_settings('stripe_secret_key')
        capture_charge = stripe.PaymentIntent.capture(charge_id)
        logger.info(f"method:capture_stripe_charge(), capture_charge:{capture_charge}")
        if capture_charge.id:
            return {SUCCESS:TRUE, DATA:None}
        return {SUCCESS:FALSE, ERROR:PAYMENT_FAILED}
    except [Exception, stripe.error.StripeError] as ex:
        return {SUCCESS:FALSE, ERROR:str(ex)}