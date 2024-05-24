from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class NxtbnS3Storage(S3Boto3Storage):
    """
        Customize it in your own risk
    """
    file_overwrite = False



class ForgivingManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
        When the file is missing during collectstatic command, let's forgive and ignore that
    """
    def hashed_name(self, name, content=None, filename=None):
        try:
            result = super().hashed_name(name, content, filename)
        except ValueError:
            # if the fille are missing, let's forgive and ignore hasing the file name.
            result = name
        return result