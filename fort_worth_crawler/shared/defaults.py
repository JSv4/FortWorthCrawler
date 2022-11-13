import io
import json
import logging

from django.forms import JSONField
from django.db.models import JSONField as DbJSONField
from django.forms.fields import InvalidJSONInput

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Needed to override the default JSONField due to some undesired validation behavior where an empty dict throws a
# validation error for JSONField.
# See: https://stackoverflow.com/questions/55147169/django-admin-jsonfield-default-empty-dict-wont-save-in-admin
class MyJSONField(JSONField):

    empty_values = [None, "", [], ()]


# Combined a couple things into a single custom JSON Field...
#
# FIRST:
#
# Needed to override the default JSONField due to some undesired validation behavior where an empty dict throws a
# validation error for JSONField.
# See: https://stackoverflow.com/questions/55147169/django-admin-jsonfield-default-empty-dict-wont-save-in-admin
#
# SECOND:
#
# UTF-8 DOES NOT RENDER PROPERLY IN DJANGO ADMIN - incorporated this solution
# http://blog.qax.io/unescaped-utf-8-in-djangos-admin-with-jsonfield/
class UTF8JSONFormField(JSONField):

    empty_values = [None, "", [], ()]

    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, ensure_ascii=False)


# The default JSONField validations in admin don't allow blank JSON obj unless you override JSONField
# and forms.JsonField
class NullableJSONField(DbJSONField):
    """
    JSONField for postgres databases.
    Displays UTF-8 characters directly in the admin, i.e. äöü instead of
    unicode escape sequences.
    Also lets you have null inputs, which otherwise throw a validation error...
    """

    empty_values = [None, "", [], ()]

    def formfield(self, **kwargs):
        return super().formfield(**{"form_class": UTF8JSONFormField, **kwargs})
