import os

from BeautifulSoup import BeautifulSoup
from softhyphen.hyphenator import Hyphenator
from softhyphen.html import (hyphenate_element, get_hyphenator_for_language
                             as _get_hyphenator_for_language)

DEFAULT_BLACKLIST_TAGS = (
    'code', 'tt', 'pre', 'head', 'title', 'script', 'style', 'meta', 'object',
    'embed', 'samp', 'var', 'math', 'select', 'option', 'input', 'textarea',
    'span',
)


def hyphenate(html, language='en-us', hyphenator=None,
              blacklist_tags=DEFAULT_BLACKLIST_TAGS):
    """
    Hyphenate a fragement of HTML

    >>> hyphenate_html('<p>It is <em>beautiful</em> outside today!</p>')
    u'<p>It is <em>beau&shy;ti&shy;ful</em> out&shy;side today!</p>'

    >>> hyphenate_html('O paralelepipedo atrevessou a ru', 'pt-br')
    u'O pa&shy;ra&shy;le&shy;le&shy;pi&shy;pe&shy;do atre&shy;ves&shy;sou a ru'

    Content inside <code>, <tt>, and <pre> blocks is not hyphenated
    >>> hyphenate_html('Document: <code>document + page_status</code>')
    u'Doc&shy;u&shy;ment: <code>document + page_status</code>'

    Short words are not hyphenated

    >>> hyphenate_html("<p>The brave men, living and dead.</p>")
    u'<p>The brave men, liv&shy;ing and dead.</p>'
    """
    # Load hyphenator if one is not provided
    if not hyphenator:
        hyphenator = get_hyphenator_for_language(language)

    # Create HTML tree
    soup = BeautifulSoup(html)

    # Recursively hyphenate each element
    hyphenate_element(soup, hyphenator, blacklist_tags)

    return unicode(soup)


def get_hyphenator_for_language(language):
    if language == "fr-FR":
        path = os.path.join(os.path.dirname(__file__), "dicts/hyph_fr_FR.dic")
        return Hyphenator(path)
    else:
        return _get_hyphenator_for_language(language)
