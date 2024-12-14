from django.db import models


class User(models.Model):
    class Meta:
        db_table = "users"
        managed = False

    id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=255, null=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(null=False)
    ext_ref_id = models.CharField(max_length=32, null=False)
    type = models.CharField(max_length=255, default="USR", null=False)


class Project(models.Model):
    class Meta:
        db_table = "projects"
        managed = False

    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(null=False)
    ext_ref_id = models.CharField(max_length=32, null=False)
    forked_from = models.IntegerField(null=True)
    deleted = models.BooleanField(default=False, null=False)
    private = models.BooleanField(null=False, default=False, blank=False)

class Extractions(models.Model):
    class Meta:
        db_table = "extractions"
        managed = False

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="extractions")
    date = models.DateTimeField()
    ext_ref_id = models.CharField(max_length=32)


class Commit(models.Model):
    class Meta:
        db_table = "commits"
        managed = False

    sha = models.CharField(max_length=40)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_commits')
    committer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='committed_commits')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='commits')
    created_at = models.DateTimeField()
    message = models.CharField(max_length=256)
    ext_ref_id = models.CharField(max_length=32)

    def __str__(self):
        return self.sha
    

class Metrics(models.Model):
    class Meta:
        db_table = 'metrics'
        managed = False

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    measurement_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)



class ProjectMetrics(models.Model):
    class Meta:
        db_table = 'project_metrics'

    id = models.IntegerField(primary_key=True)
    extraction = models.ForeignKey(Extractions, on_delete=models.CASCADE)  # Modificación aquí
    metric = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)  # Stored as strings, convert as needed
    created_at = models.DateTimeField(auto_now_add=True)
