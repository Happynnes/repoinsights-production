from django.db.models import Count, OuterRef, Subquery
from django.db import connections
from typing import Dict, List, Any
from ...models import Project, Commit

from ..helper.metric_score import ProjectMetricScore

class FilterDataManager:

    @staticmethod
    def sort_by(projects: List[Any], sort_name: int):
        rating_metrics = ProjectMetricScore.get_metrics()
        exist = next((metric for metric in rating_metrics if metric['name'] == sort_name), None)
        if exist:
            projects = sorted(projects, key=lambda project: next((rating['value'] for rating in project['rating'] if rating['id'] == sort_name), 0), reverse=True)
        return projects



    @staticmethod
    def get_languages(projects):
        langs = projects.values_list("language", flat=True).distinct()
        lang_count = []
        for lang in langs:
            lang_count.append({"name": lang, "total": projects.filter(language=lang).count(), "language": lang})
        return lang_count
    

    @staticmethod
    def get_intervals(commit: str) -> list[int]:
        splited = commit.split(" - ")
        if len(splited) == 2:
            inf_limit = splited[0]
            sup_limit = splited[1]
            if splited[1].isdigit():
                sup_limit = int(splited[1])
            else:
                sup_limit = 10000000000
            return [int(inf_limit), sup_limit]
        else:
            raise Exception("Invalid commit interval")
                        

    @staticmethod
    def get_projects_by_commits(projects, min, max):
        commit_count = Commit.objects.using("repoinsights").filter(
            project_id=OuterRef("id")
        ).values("project_id").annotate(total=Count("id")).values("total")
        projects = projects.annotate(commit_count=Subquery(commit_count)).filter(
            commit_count__gte=min, commit_count__lte=max
        )
        return projects

    @staticmethod
    def get_commits_data(user_project_ids, langs):
        project_condition = f"AND p.id IN ({','.join([str(project_id) for project_id in user_project_ids])})" if user_project_ids else ""
        lang_condition = "AND p.language IN ({})".format(','.join(["'{}'".format(lang) for lang in langs])) if langs else ""

        query = f"""
            SELECT 
                CASE
                    WHEN total >= 100000 THEN '100000 - more'
                    WHEN total < 1000 THEN '0 - 1000'
                    ELSE CONCAT((FLOOR(total / 5000) * 5000), ' - ', ((FLOOR(total / 5000) + 1) * 5000))
                END AS total_interval,
                COUNT(*) AS project_count
            FROM
                (
                    SELECT 
                        CONCAT(u.login, '/', p.name) AS project_owner,
                        COUNT(c.project_id) AS total
                    FROM 
                        commits c 
                    JOIN 
                        projects p ON p.id = c.project_id
                    JOIN 
                        users u ON u.id = p.owner_id
                    WHERE 
                        p.forked_from IS NULL
                        {project_condition}
                        {lang_condition}
                    GROUP BY  
                        project_owner
                ) AS subquery
            GROUP BY
                total_interval
            ORDER BY 
                MIN(total) DESC;
        """
        cursor = connections['repoinsights'].cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        data = []
        for result in results:
            name, count = result
            if name == "0 - 5000":
                name = "1000 - 5000"
            data.append({"name": name, "count": count})
        return data


    @staticmethod
    def project_filtered_by_commits(projects, min_total: int, max_total: int):
        commit_count = (
            Commit.objects.using("repoinsights")
            .filter(project_id=OuterRef("id"))
            .values("project_id")
            .annotate(total=Count("id"))
            .values("total")
        )
        return projects.annotate(commit_count=Subquery(commit_count)).filter(
            commit_count__gte=min_total, commit_count__lte=max_total
        )
    

    @staticmethod
    def user_selected(result: list, user_project_ids):
        for project in result:
            if project["id"] in user_project_ids:
                project["selected"] = True
            else:
                project["selected"] = False
        return result