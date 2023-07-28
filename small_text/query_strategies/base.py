from __future__ import annotations

from enum import Enum
from functools import partial, wraps
from typing import Union

from scipy.sparse import csr_matrix


class ClassificationType(Enum):
    """Represents the classification type which can be either single-label or multi-label."""
    SINGLE_LABEL = 'single-label'
    MULTI_LABEL = 'multi-label'

    @staticmethod
    def from_str(classification_type_str: str) -> ClassificationType:
        """Creates a ClassificationType instance from the given string `classification_type_str`.

        Parameters
        ----------
        classification_type_str : {'single-label', 'multi-label'}
        """
        if classification_type_str == 'single-label':
            return ClassificationType.SINGLE_LABEL
        elif classification_type_str == 'multi-label':
            return ClassificationType.MULTI_LABEL
        else:
            raise ValueError('Cannot convert string to classification type enum: '
                             f'{classification_type_str}')


def constraints(cls=None, classification_type: Union[None, str, ClassificationType] = None):
    """Restricts a query strategy to certain settings such as single- or multi-label classification.

    This should be used sparingly and mostly in cases where a misconfiguration would not raise
    an error but is clearly unwanted.
    """
    if not callable(cls):
        return partial(constraints, classification_type=classification_type)

    @wraps(cls, updated=())
    class QueryStrategyConstraints(cls):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def query(self, clf, datasets, indices_unlabeled, indices_labeled, y, *args, n=10, **kwargs):

            if classification_type is not None:
                if isinstance(classification_type, str):
                    classification_type_ = ClassificationType.from_str(classification_type)
                else:
                    classification_type_ = classification_type

                if classification_type_ == ClassificationType.SINGLE_LABEL and isinstance(y, csr_matrix):
                    raise RuntimeError(f'Invalid configuration: This query strategy requires '
                                       f'classification_type={str(classification_type_.value)} '
                                       f'but multi-label data was encountered')
                elif classification_type_ == ClassificationType.MULTI_LABEL \
                        and not isinstance(y, csr_matrix):
                    raise RuntimeError(f'Invalid configuration: This query strategy requires '
                                       f'classification_type={str(classification_type_.value)} '
                                       f'but single-label data was encountered')

            return super().query(clf, datasets, indices_unlabeled, indices_labeled, y,
                                 *args, n=n, **kwargs)

    return QueryStrategyConstraints
