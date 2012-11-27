from django.utils.translation import ugettext_lazy as _

from model_utils import Choices


QUERY_STR_PATTERNS = {
    "Answer": "answer=%(id)s",
    "Question": "question=%(id)s"
}

ANCHOR_PATTERNS = {
    "Answer": "a-%(id)s",
    "Question": "q-%(id)s"
}

STATUSES = Choices(
    (0, "draft", _("Draft")),
    # (1, "sandbox", _("Sandbox")),
    (2, "public", _("Public"))
)

EMPTY_SCORE = {"num_votes": 0, "score": 0}
