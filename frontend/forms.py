from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django import forms
from django.conf import settings

from .utils import get_grouped_sets


class LabelGeneratorForm(forms.Form):
    sets = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
    )

    # labels_template = forms.ChoiceField(
    #     choices=(
    #         ("30", "30 per page (Avery Template Presta® 94200)"),
    #         ("24", "24 per page (Avery Template Presta® 94221)"),
    #     ),
    #     help_text="Tested with Avery blank labels 8460.",
    #     widget=forms.RadioSelect,
    # )

    def __init__(self, *args, **kwargs):
        sets = get_grouped_sets()

        default_sets = []
        for set_type, set_list in sets:
            if set_type in (
                "core",
                "expansion",
                "masters",
                "commander",
                "draft innovation",
                "starter",
            ):
                default_sets.extend([code for code, exp in set_list])

        # Setup the default initial data
        if "initial" not in kwargs:
            kwargs["initial"] = {}
        kwargs["initial"].update(
            {
                # "labels_template": "30",
                "sets": default_sets,
            }
        )

        super().__init__(*args, **kwargs)

        self.fields["sets"].choices = sets

        self.helper = FormHelper()

        # Currently, this is a stripped down Django setup
        # There's no sessions or CSRF so remove that for now
        self.helper.disable_csrf = (
            "django.middleware.csrf.CsrfViewMiddleware" not in settings.MIDDLEWARE
        )

        self.helper.layout = layout.Layout(
            layout.Fieldset(
                "",
                layout.Field("sets", template="frontend/includes/sets-field.html"),
                layout.HTML(
                    "<ul class='list-inline small'>"
                    "<li class='list-inline-item'><a class='quick-update' href='#' data-selector='[data-set-code]' data-target='.sets-columns input'>Select all</a></li>"
                    "<li class='list-inline-item'><a class='quick-update' href='#' data-selector='[data-set-none]' data-target='.sets-columns input'>Select none</a></li>"
                    "</ul>"
                ),
                # "labels_template",
                css_class="my-3",
            ),
            layout.HTML("<hr class='mb-4'>"),
            layout.Submit(
                "submit",
                "Generate PDF",
                css_class="btn btn-primary btn-lg btn-block",
            ),
        )
