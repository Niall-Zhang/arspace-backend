TRUE = True
FALSE = False
SUCCESS = "success"
MESSAGE = "message"
ERROR = "error"
DATA = "data"
TOKEN = "token"
USER = "user"
CLUB = "club"
USER_ID = "user_id"
NEXT = "next"
PREVIOUS = "previous"
COUNT = "count"
EMAIL = "email"
PICTURE = "picture"
IS_REGISTERED = "is_registered"
IS_LOGIN = "is_login"
INACTIVE = "inactive"
IS_LIKED = "is_liked"
IS_REQUEST_SENT = "is_request_sent"
USD = "usd"
TITLE="title"
TYPE = "type"
BODY="body"
DEVICE_TOKEN="device_token"
IS_DEVICE_TOKEN="is_device_token"
PENDING = "pending"
ACCEPTED = "accepted"
REJECTED = "rejected"
FORM = "form"
POST = "POST"
ROOM = "room"
NOTIFICATION="notification"
ROOM_ID = "room_id"
LIKE = "like"
LIKED_BY = "liked_by"
INVALID_REQUEST_METHOD = "Invalid request method."
PRIVATE="private"
STATUS="status"
EXPIRED = "expired"
VERIFIED = "verified"
NOT_VERIFIED = "not_verified"
MALE="male"
FEMALE="female"
ALL = "all"
NULL = 'null'
FREE='free'

# Auth
LOGIN_ACCOUNT = "Please log in to your account"
LOGIN_SUCCESS = "You are logged in successfully."
PASSWORD_CHANGED_SUCCESS = "Password changed successfully."
PASSWORD_RESET_SUCCESS = "Password has been reset successfully."
PROFILE_DATA_SUCCESS = "Fetched profile data."
PROFILE_CHANGED_SUCCESS = "Profile updated successfully."
USER_CREATED_SUCCESS = "User registered successfully."
USER_UPDATED_SUCCESS = "User updated successfully."
OTP_SENT_SUCCESS = "OTP sent successfully."
OTP_VERIFIED_SUCCESS = "OTP verified."
USER_LIST_SUCCESS = "Fetched user list."
USER_STATUS_CHANGED_SUCCESS = "User status updated."
USER_REGISTERED_SUCCESS = "User registered successfully."
USER_DELETE_SUCCESS = "User deleted successfully."
USER_IMAGE_DELETE_SUCCESS = "User Image deleted successfully."
USER_IMAGE_NOT_FOUND = "User Image not found."
EMAIL_ALREADY_EXISTS_AND_NAVIGATE_TO_LOGIN = (
    "Email already verified. Please login into your account."
)
TOKEN_SEND_EMAIL_SUCCESS = "An Token on your email has been sent."
LOGOUT_SUCCESSFULLY = "User logged out successfully."
EMAIL_IS_AVAILABLE = "Email is available to use."
USERNAME_IS_AVAILABLE = "Username is available to use."
OTP_SEND_SUCCESS = "Otp has been sent on your email."

# List
LIST_FETCHED_SUCCESS = "List fetched successfully."
LIST_NOT_FOUND = "List not found."

USER_BLOCKED_SUCCESS = "User blocked successfully."
USER_FOLLOWED_SUCCESS = "User followed successfully."
USER_VERIFICATION_SUCCESS = "User verified successfully."

ATTACHMENT_UPLOAD_SUCCESS = "Attachment file uploaded successfully."
ATTACHMENT_UPLOAD_FAILED = "Failed to upload attachment file."

# Error Messages
INVALID_LOGIN_CREDENTIALS = "Invalid login details."
INVALID_USER_TYPE = "Invalid user type."
INCORRECT_OLD_PASSWORD = "Incorrect old password."
OTP_SENT_FAILED = "OTP not sent."
OTP_VERIFIED_FAILED = "Invalid OTP."
TOKEN_EXPIRED = "Token has expired."
INVALID_TOKEN = "Invalid token."
VALID_TOKEN = "Token is valid."
FAILED_FIREBASE_AUTHENTICATION = "Unable to authenticate token."
USER_UNBLOCKED_SUCCESS = "User unblocked successfully."
UNAUTHORIZED_ACCESS = "Unauthorized access."

USER_NOT_FOUND = "User not found."
EMAIL_NOT_AVAILABLE = "Email is already taken."
EMAIL_ALREADY_EXISTS = "Account is already exist. Need to verify your account."
USERNAME_NOT_AVAILABLE = "Username is already taken."
USER_IMAGE_DELETE_SUCCESS = "User image delete successfully."
USER_IMAGE_NOT_FOUND = "User image not found."

OTP_GENERATION_FAILED = "Otp generation failed."
OTP_SEND_FAILED = "There was an error sending OTP. Please try again."
INCORRECT_USERNAME_EMAIL_PASSWORD = "Incorrect username/email or password."
USER_IS_INACTIVE = "User is inactive."
USER_IS_UNVERIFIED = "User is not verified."
TOKEN_SEND_EMAIL_FAILED = "An error occurred while sending email. Please try again."
ACCESS_DENIED = "You do not have permission to access this resource."
INVALID_ATTACHMENT = "Attachment file not found."
INVALID_SELLER_BUYER_ID = "Invalid seller & buyer id."
IS_VERIFIED = "is_verified"

# Validation Messages
INVALID_OTP = "Invalid OTP."
INVALID_PHONE_NUMBER = "Invalid phone number."
USER_ALREADY_EXISTS = "User with this phone number already exists."
INVALID_EMAIL_PASSWORD = "Invalid Email & Password."
EMAIL_DOES_NOT_EXIST = "Email does not exists."
INVALID_EMAIL_OR_OTP = "Invalid email or otp."
INVALID_EMAIL = "Invalid Email."
INVALID_USERNAME = "Invalid Username."
INVALID_PASSWORD = "Invalid Password."
INVALID_OLD_PASSWORD = "Invalid Old Password."
INVALID_STATUS = "Invalid Status."
INVALID_MESSAGE = "Invalid message."
INVALID_FORM_DATA = "Invalid form data."
INVALID_TICKET_ID = "Invalid ticket id."
INVALID_QTY = "Invalid qty."


# Interest
INTEREST_CREATED_SUCCESS = "Interest created successfully."
INTEREST_UPDATED_SUCCESS = "Interest updated successfully."
INTEREST_DELETED_SUCCESS = "Interest deleted successfully."

# Club
CLUB_CREATED_SUCCESS = "Club created successfully."
CLUB_UPDATED_SUCCESS = "Club updated successfully."
CLUB_DELETED_SUCCESS = "Club deleted successfully."


# CAST
CAST_CREATED_SUCCESS = "Cast created successfully."
CAST_UPDATED_SUCCESS = "Cast updated successfully."
CAST_DELETED_SUCCESS = "Cast deleted successfully."

# Ticket
TICKET_CREATED_SUCCESS = "Ticket created successfully."
TICKET_UPDATED_SUCCESS = "Ticket updated successfully."
TICKET_DELETED_SUCCESS = "Ticket deleted successfully."

# Event
EVENT_CREATED_SUCCESS = "Event created successfully."
EVENT_UPDATED_SUCCESS = "Event updated successfully."
EVENT_DELETED_SUCCESS = "Event deleted successfully."
EVENT_INFO_SUCCESS = "Fetched event info successfully."
EVENT_NOT_FOUND = "Event not found."
EVENT_LIKED_SUCCESS = "Event liked successfully."
EVENT_UNLIKED_SUCCESS = "Event unliked successfully."
EVENT_IMAGE_DELETED_SUCCESS = "Event image deleted successfully."
EVENT_DELETED_SUCCESS = "Event deleted successfully"
EVENT_EXPIRED = "event_expired"
EVENT_HAS_EXPIRED = "Event has expired"
TICKET_ALREADY_USED = "Ticket already used"
TICKET_ALREADY_VERIFIED = "already_verified"
TICKET_VERIFIED = "verified"
TICKET_INVALID = "invalid_ticket"
TICKET_NOT_FOUND = "Ticket not found."

# Card
CARD_CREATED_SUCCESS = "Card created successfully."
CARD_INFO_SUCCESS = "Fetched card info successfully."
CARD_NOT_FOUND = "Card not found."
CARD_DELETED_SUCCESS = "Card deleted successfully."


# Order
ORDER_CREATED_SUCCESS = "Order created successfully."
ORDER_NOT_FOUND = "Order not found."
ORDER_INFO_SUCCESS = "Fetched order info successfully."
NO_ORDER_FOUND = "No order found."
NO_ORDER_ITEMS_FOUND = "No order items found."
DEDUCTED_EVENT_TICKET_UNITS = "Deducted event ticket units/seats."
NO_MORE_SEATS_AVAILABLE = "No more seats available."

# Payment
PAYMENT_FAILED = "Payment failed. Please try again later."

# Stripe
CREATE_STRIPE_CUSTOMER_FAILED = "Failed customer creation on stripe."
STRIPE_CUSTOMER_NOT_FOUND = "Stripe customer not found."
ATTACHED_NEW_CARD_SUCCESS = "Attached new card successfully."
DETACHED_OLD_CARD_SUCCESS = "Detached old card successfully."
STRIPE_CREATE_CARD_TOKEN_SUCCESS = "Created stripe card token successfully."
STRIPE_CREATE_CARD_SOURCE_FAILED = "Failed creating stripe card source."

# Firebase Notification
FIREBASE_NOTIFICATION_SUCCESS = "Notification sent successfully."
FIREBASE_NOTIFICATION_FAILED = "Failed to send notification."
EVENT = "event"
UPCOMING_EVENT_NEAR = "An upcoming event."

# Favourite User
USER_FAVOURITE_SUCCESS = "User added into favourites successfully."
USER_UNFAVOURITE_SUCCESS = "User removed from favourites successfully."
LIKED_YOUR_PROFILE = "Liked your profile."

# Request
CHAT_REQUEST_TITLE="Chat Request"
CHAT_REQUEST_BODY="You have recieved a chat request."
REQUEST_SENT_SUCCESS = "Request sent successfully."
REQUEST_REVERT_SUCCESS = "Request reverted successfully."
REQUEST_ACCEPTED_SUCCESS = "Request accepted successfully."
REQUEST_REJECTED_SUCCESS = "Request has been rejected."
INVALID_ATTACHMENT="Invalid attachment."

# Message
CHAT_MESSAGE_RECEIVED = "Message Received"

# Settings
SETTINGS_ADDED_SUCCESS = "Settings added successfully."

# Chat
NEW_MESSAGE_RECEIVED = "New message received."


# Notification
NOTIFICATION_READ_SUCCESS = "Notification read successfully."
NOTIFICATION_SENT_SUCCESS = "Notification sent successfully."


# messages to topics
SEND_MESSAGE_TO_TOPIC = 'NOTIFICATION_BROADCAST'

# error message for event id and status
EVENT_ID_REQUIRED = 'Event id field is required. Hint ( event_id: UUID)'
STATUS_REQIURED = 'Status is required.Hint (status: true)'

#ticket

FREE_TICKET_CREATED_SUCCESS = 'Ticket created successfully.'