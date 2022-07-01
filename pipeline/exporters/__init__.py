from .mlm import MlmExporter
from .query import QueyExporter
from .sts import StsExporter
from .sts_scale import TripletAndBinaryExporter, StsScaleExporter

query_exporter = QueyExporter()
mlm_exporter = MlmExporter()


def sts_exporter(sts_type):
    if sts_type == 'binary':
        return TripletAndBinaryExporter(is_triplet=False)
    elif sts_type == 'triplet':
        return TripletAndBinaryExporter(is_triplet=True)
    elif sts_type == 'scale':
        return StsScaleExporter()
