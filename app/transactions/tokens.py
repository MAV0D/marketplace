from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings

class TransactionTokenGenerator(PasswordResetTokenGenerator):
  # Set your long timeout window here (e.g., 7 days = 604800 seconds)
  timeout_seconds = 2592000

  def _make_hash_value(self, transaction, timestamp):
    return (
      str(transaction.pk) + 
      str(timestamp) + 
      str(transaction.status)
    )

  def check_token(self, transaction, token):
    """
    Temporarily swap settings.PASSWORD_RESET_TIMEOUT during execution
    so Django's core engine validates against our custom long window.
    """
    if not (transaction and token):
      return False
      
    global_timeout_backup = getattr(settings, 'PASSWORD_RESET_TIMEOUT', 86400)
    
    try:
      settings.PASSWORD_RESET_TIMEOUT = self.timeout_seconds
      return super().check_token(transaction, token)
    finally:
      settings.PASSWORD_RESET_TIMEOUT = global_timeout_backup

transaction_token_generator = TransactionTokenGenerator()