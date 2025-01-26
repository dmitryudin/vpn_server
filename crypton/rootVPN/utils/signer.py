from django.utils import timezone
from django.core.signing import Signer
from django.conf import settings

def generate_verification_token(email):
    signer = Signer()
    return signer.sign(email)