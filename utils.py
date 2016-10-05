"""utils.py.

File for collecting general utility functions
"""

from google.appengine.ext import ndb
import endpoints


def get_by_urlsafe(urlsafe, model):
    """Return an ndb.Model entity that the urlsafe key points to.

    Check that the type of entity returned is of the correct kind. Raise an
    error if the key String is malformed or the entity is of the incorrect
    kind

    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:
    """
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception as e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def find_all_indexes(word, letter):
    """Return the indexes of all occurrences of a letter in a string."""
    return [index for index, character in enumerate(word) if character == letter]
