"""
LTI consumer plugin models
"""
from urllib.parse import unquote

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from cms.models.pluginmodel import CMSPlugin
from oauthlib import oauth1

from richie.apps.courses.models import Course


class LTIConsumer(CMSPlugin):
    """
    LTI consumer plugin model.
    """

    url = models.URLField(_("LTI url"))
    course = models.ForeignKey(to=Course, on_delete=models.PROTECT)
    edit_mode = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.url:
            self.url = getattr(settings, "LTI_CONSUMER", {}).get("base_url")

    @property
    def auth_parameters(self):
        """
        Builds required parameters for LTI authentication
        """
        role = "instructor" if self.edit_mode else "student"
        return {
            "lti_message_type": settings.LTI_CONSUMER.get("display_name"),
            "lti_version": "LTI-1p0",
            "resource_link_id": str(self.id),
            "context_id": self.course.code,
            "user_id": "richie",
            "lis_person_contact_email_primary": "",
            "roles": role,
        }

    def authorize(self):
        """
        Returns headers from LTI authentication
        """
        client = oauth1.Client(
            client_key=settings.LTI_CONSUMER_SECRETS.get("marsha").get(
                "oauth_consumer_key"
            ),
            client_secret=settings.LTI_CONSUMER_SECRETS.get("marsha").get(
                "shared_secret"
            ),
        )

        _uri, headers, _body = client.sign(
            self.url,
            http_method="POST",
            body=self.auth_parameters,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return headers

    def build_content_parameters(self, auth_headers):
        """
        Builds required parameters for LTI content consumption
        """
        oauth_dict = dict(
            param.strip().replace('"', "").split("=")
            for param in auth_headers["Authorization"].split(",")
        )
        signature = oauth_dict["oauth_signature"]
        oauth_dict["oauth_signature"] = unquote(signature)
        oauth_dict["oauth_nonce"] = oauth_dict.pop("OAuth oauth_nonce")

        oauth_dict.update(self.auth_parameters)
        return oauth_dict

    @property
    def content_parameters(self):
        """
        Convenient wrapper to authorise and return required parameters
        for LTI content consumption
        """
        return self.build_content_parameters(self.authorize())

    def __str__(self):
        return self.url
