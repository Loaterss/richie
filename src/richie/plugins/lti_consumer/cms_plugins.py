"""
LTI consumer CMS plugin
"""
from django.conf import settings
from django.forms import URLField
from django.utils.translation import gettext_lazy as _

import exrex
from cms.models import Placeholder
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from richie.apps.core.defaults import PLUGINS_GROUP

from .defaults import LTI_CONSUMER_CONFIGURATION
from .models import LTIConsumer


@plugin_pool.register_plugin
class LTIConsumerPlugin(CMSPluginBase):
    """
    A plugin to consume LTI content.
    """

    allow_children = False
    cache = True
    disable_child_plugins = True
    fieldsets = ((None, {"fields": ["url", "course"]}),)
    model = LTIConsumer
    module = PLUGINS_GROUP
    name = _("LTI consumer")
    render_template = "richie/lti_consumer/lti_consumer.html"

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Choose LTI type depending on placeholder
        """
        form = super().get_form(request, obj=obj, change=change, **kwargs)

        placeholder_id = request.GET.get("placeholder_id")
        if not placeholder_id and not obj:
            return form

        if placeholder_id:
            placeholder = Placeholder.objects.only("slot").get(id=placeholder_id)
        else:
            placeholder = obj.placeholder

        for configuration in LTI_CONSUMER_CONFIGURATION:
            if (
                "placeholders" not in configuration
                or placeholder.slot in configuration["placeholders"]
            ):
                break
        else:
            configuration = {}

        url_field: URLField = form.base_fields["url"]
        if configuration.get("url_regex"):
            url_field.initial = exrex.getone(
                getattr(settings, "LTI_CONSUMER", {}).get("base_url")
                + configuration["url_regex"]
            )

        return form

    def render(self, context, instance, placeholder):
        """
        Build plugin context passed to its template to perform rendering
        and pass edit mode
        """
        if "request" in context:
            request = context["request"]
            instance.edit_mode = request.toolbar and request.toolbar.edit_mode_active

        context = super().render(context, instance, placeholder)
        return context
