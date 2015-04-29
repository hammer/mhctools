from collections import defaultdict

import pandas as pd
from varcode import Collection
from .binding_prediction import BindingPrediction

class EpitopeCollection(Collection):
    """
    Collection of BindingPrediction objects
    """
    def __init__(self, binding_predictions):
        Collection.__init__(
            self,
            elements=binding_predictions,
            distinct=True,
            sort_key=lambda x: x.percentile_rank)

    def strong_binders(self, threshold=None):
        """
        No default threshold since we're not sure if we're always going to
        be predicting IC50 affinity (as opposed to stability or some other
        criterion)
        """
        if len(self) == 0:
            return self

        def filter_fn(x):
            if threshold is None:
                return x.measure.is_binder(x.value)
            else:
                return x.measure.is_binder(x.value, threshold)
        return self.filter(filter_fn)

    def strong_binders_by_rank(self, max_rank=2.0):
        return self.filter(lambda x: x.percentile_rank <= max_rank)

    def groupby(self, key_fn):
        groups = defaultdict(list)
        for binding_prediction in self.binding_predictions:
            key = key_fn(binding_prediction)
            groups[key].append(binding_prediction)
        # want to create an EpitopeCollection for each group
        # but need to write the construction in terms of
        # self.__class__ so that this works with derived classes
        return {
            key: self.__class__(binding_predictions)
            for (key, binding_predictions)
            in groups.items()
        }

    def groupby_allele(self):
        return self.groupby(key_fn=lambda x: x.allele)

    def groupby_peptide(self):
        return self.groupby(key_fn=lambda x: x.peptide)

    def groupby_allele_and_peptide(self):
        return self.groupby(key_fn=lambda x: (x.allele, x.peptide))

    def dataframe(self):
        return pd.DataFrame(
            self.elements,
            columns=BindingPrediction._fields)
