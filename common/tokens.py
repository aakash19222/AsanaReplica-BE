# """
# Token models for Personal Access Tokens.
# """
# from django.db import models
# from django.utils import timezone
# from datetime import timedelta
# import secrets
# import hashlib


# class PersonalAccessToken(models.Model):
#     """
#     Personal Access Token model for API authentication.
#     """
#     token_hash = models.CharField(
#         max_length=64,
#         unique=True,
#         db_index=True,
#         help_text="SHA256 hash of the token for lookup"
#     )
#     name = models.CharField(
#         max_length=255,
#         help_text="A name for this token (e.g., 'My API Token')"
#     )
#     user = models.ForeignKey(
#         'users.User',
#         on_delete=models.CASCADE,
#         related_name='personal_access_tokens',
#         help_text="The user who owns this token"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         help_text="When this token expires (null = never expires)"
#     )
#     last_used_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         help_text="When this token was last used"
#     )
#     is_active = models.BooleanField(
#         default=True,
#         help_text="Whether this token is active"
#     )

#     class Meta:
#         db_table = 'personal_access_tokens'
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.name} ({self.user})"

#     @classmethod
#     def generate_token(cls):
#         """Generate a new secure random token."""
#         return secrets.token_urlsafe(32)

#     @classmethod
#     def hash_token(cls, token):
#         """Hash a token for storage."""
#         return hashlib.sha256(token.encode()).hexdigest()

#     @classmethod
#     def create_token(cls, user, name, expires_in_days=None):
#         """
#         Create a new personal access token.
#         Returns: (token_obj, plain_token_string)
#         """
#         plain_token = cls.generate_token()
#         token_hash = cls.hash_token(plain_token)
        
#         expires_at = None
#         if expires_in_days:
#             expires_at = timezone.now() + timedelta(days=expires_in_days)
        
#         token_obj = cls.objects.create(
#             token_hash=token_hash,
#             name=name,
#             user=user,
#             expires_at=expires_at
#         )
        
#         return token_obj, plain_token

#     @classmethod
#     def validate_token(cls, token_string):
#         """
#         Validate a token string and return the token object if valid.
#         """
#         try:
#             token_hash = cls.hash_token(token_string)
#             token = cls.objects.get(token_hash=token_hash)
            
#             if not token.is_valid():
#                 return None
                
#             token.mark_used()
#             return token
#         except cls.DoesNotExist:
#             return None

#     def is_valid(self):
#         """Check if token is valid."""
#         if not self.is_active:
#             return False
#         if self.expires_at and timezone.now() > self.expires_at:
#             return False
#         return True

#     def mark_used(self):
#         """Update last_used_at timestamp."""
#         self.last_used_at = timezone.now()
#         self.save(update_fields=['last_used_at'])
