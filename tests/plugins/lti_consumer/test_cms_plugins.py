"""Testing DjangoCMS plugin declaration for Richie's lti consumer plugin."""
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from cms.api import add_plugin
from cms.models import Placeholder
from cms.plugin_rendering import ContentRenderer

from richie.plugins.lti_consumer.cms_plugins import LTIConsumerPlugin
from richie.plugins.lti_consumer.factories import LTIConsumerFactory


@override_settings(
    LTI_CONSUMER_SECRETS={
        "marsha": {
            "oauth_consumer_key": "InsecureOauthConsumerKey",
            "shared_secret": "InsecureSharedSecret",
        }
    },
    LTI_CONSUMER={
        "display_name": "Marsha Video",
        "base_url": "https://marsha.education.*",
        "is_launch_url_regex": True,
        "automatic_resizing": True,
        "inline_ratio": 0.5625,
    },
)
class LTIConsumerPluginTestCase(TestCase):
    """Test suite for the lti consumer plugin."""

    def test_cms_plugins_lti_consumer_context_and_html(self):
        """
        Instanciating this plugin with an instance should populate the context
        and render in the template.
        """
        placeholder = Placeholder.objects.create(slot="test")

        lti_consumer = LTIConsumerFactory()

        model_instance = add_plugin(
            placeholder,
            LTIConsumerPlugin,
            "en",
            url=lti_consumer.url,
            course=lti_consumer.course,
        )
        plugin_instance = model_instance.get_plugin_class_instance()
        context = plugin_instance.render({}, model_instance, None)

        # Check if instance is in context
        self.assertEqual(model_instance, context["instance"])

        # Get generated html for lti consumer url
        renderer = ContentRenderer(request=RequestFactory())
        html = renderer.render_plugin(model_instance, {})

        # Check rendered url is correct after save and sanitize
        self.assertIn(lti_consumer.url, html)
        self.assertIn("student", html)

    def test_cms_plugins_lti_auth_parameters_no_edit_mode(self):
        """
        Verify that LTI authentication parameters are correctly build
        """
        lti_consumer = LTIConsumerFactory()
        expected_auth_parameters = {
            "lti_message_type": settings.LTI_CONSUMER.get("display_name"),
            "lti_version": "LTI-1p0",
            "resource_link_id": str(lti_consumer.id),
            "context_id": lti_consumer.course.code,
            "user_id": "richie",
            "lis_person_contact_email_primary": "",
            "roles": "student",
        }
        self.assertDictEqual(expected_auth_parameters, lti_consumer.auth_parameters)

    def test_cms_plugins_lti_auth_parameters_edit_mode(self):
        """
        Verify that LTI authentication parameters are correctly build
        """
        lti_consumer = LTIConsumerFactory()
        lti_consumer.edit_mode = True
        expected_auth_parameters = {
            "lti_message_type": settings.LTI_CONSUMER.get("display_name"),
            "lti_version": "LTI-1p0",
            "resource_link_id": str(lti_consumer.id),
            "context_id": lti_consumer.course.code,
            "user_id": "richie",
            "lis_person_contact_email_primary": "",
            "roles": "instructor",
        }
        self.assertDictEqual(expected_auth_parameters, lti_consumer.auth_parameters)

    def test_cms_plugins_lti_authorize(self):
        """
        Verify that oauth authentication returns headers
        """
        lti_consumer = LTIConsumerFactory()
        expected_auth_headers_keys = (
            "oauth_nonce",
            "oauth_timestamp",
            "oauth_version",
            "oauth_consumer_key",
            "oauth_signature",
        )
        auth_headers = lti_consumer.authorize()
        for expected_key in expected_auth_headers_keys:
            self.assertIn(expected_key, auth_headers.get("Authorization"))

    def test_cms_plugins_lti_build_content_parameters_edit_mode(self):
        """
        Verify that LTI content consumption parameters are correctly build
        """
        lti_consumer = LTIConsumerFactory()
        lti_consumer.edit_mode = True
        auth_headers = {
            "Authorization": (
                'OAuth oauth_nonce="80966668944732164491378916897", oauth_timestamp="1378916897", '
                'oauth_version="1.0", oauth_signature_method="HMAC-SHA1", '
                'oauth_consumer_key="InsecureOauthConsumerKey", '
                'oauth_signature="frVp4JuvT1mVXlxktiAUjQ7%2F1cw%3D"'
            )
        }
        expected_content_parameters = {
            "lti_message_type": settings.LTI_CONSUMER.get("display_name"),
            "lti_version": "LTI-1p0",
            "resource_link_id": str(lti_consumer.id),
            "context_id": lti_consumer.course.code,
            "user_id": "richie",
            "lis_person_contact_email_primary": "",
            "roles": "instructor",
            "oauth_consumer_key": "InsecureOauthConsumerKey",
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": "1378916897",
            "oauth_nonce": "80966668944732164491378916897",
            "oauth_version": "1.0",
            "oauth_signature": "frVp4JuvT1mVXlxktiAUjQ7/1cw=",
        }
        self.assertDictEqual(
            expected_content_parameters,
            lti_consumer.build_content_parameters(auth_headers),
        )

    @mock.patch(
        "richie.plugins.lti_consumer.models.LTIConsumer.authorize",
        return_value={
            "Authorization": (
                'OAuth oauth_nonce="80966668944732164491378916897", oauth_timestamp="1378916897", '
                'oauth_version="1.0", oauth_signature_method="HMAC-SHA1", '
                'oauth_consumer_key="InsecureOauthConsumerKey", '
                'oauth_signature="frVp4JuvT1mVXlxktiAUjQ7%2F1cw%3D"'
            )
        },
    )
    def test_cms_plugins_lti_content_parameters(self, _):
        """
        Verify that LTI content consumption parameters are correctly build trough
        content_parameters wrapper
        """
        lti_consumer = LTIConsumerFactory()
        lti_consumer.edit_mode = True
        expected_content_parameters = {
            "lti_message_type": settings.LTI_CONSUMER.get("display_name"),
            "lti_version": "LTI-1p0",
            "resource_link_id": str(lti_consumer.id),
            "context_id": lti_consumer.course.code,
            "user_id": "richie",
            "lis_person_contact_email_primary": "",
            "roles": "instructor",
            "oauth_consumer_key": settings.LTI_CONSUMER_SECRETS.get("marsha").get(
                "oauth_consumer_key"
            ),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": "1378916897",
            "oauth_nonce": "80966668944732164491378916897",
            "oauth_version": "1.0",
            "oauth_signature": "frVp4JuvT1mVXlxktiAUjQ7/1cw=",
        }
        self.assertDictEqual(
            expected_content_parameters, lti_consumer.content_parameters
        )
