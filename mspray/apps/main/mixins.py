from django.conf import settings


class SiteNameMixin(object):
    def get_context_data(self, **kwargs):
        context = super(SiteNameMixin, self).get_context_data(**kwargs)
        context["site_name"] = settings.SITE_NAME
        context["active_site"] = (
            "MDA" if "mda" in self.request.get_full_path() else "IRS"
        )

        return context
