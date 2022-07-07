from .mlm import MlmExporter
from .query import QueyExporter
from .sts import TripletAndBinaryStsExporter, ScaleStsExporter, BenchmarkStsExporter, BatchTripletStsExporter

query_exporter = QueyExporter()
mlm_exporter = MlmExporter()


def sts_exporter(sts_type):
    if sts_type == 'binary':
        return TripletAndBinaryStsExporter(is_triplet=False)
    elif sts_type == 'triplet':
        return TripletAndBinaryStsExporter(is_triplet=True)
    elif sts_type == 'scale':
        return ScaleStsExporter()
    elif sts_type == 'benchmark':
        return BenchmarkStsExporter()
    elif sts_type == 'batch_triplet':
        return BatchTripletStsExporter()
