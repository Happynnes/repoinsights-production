# Repositty
- get repos/user/repo - 1
- get users/user - 1


# commits
-  repos/user/repo/commits - C (paginado)
    -  users/user/%committer% (por commit)
    -  users//user/%author% (por commit)


# commit_comments
- repos/user/repo/comments - CC (paginado)
    - users/user/%user% (por comentario)


# PR
- repos/user/repo/pulls - P (paginado)
    - repos/user/repo/commit/%base% (por pr)
        -  users/user/%committer% (por commit)
        -  users//user/%author% (por commit)

    - repos/user/repo/commit/%head%  (por pr)
        -  users/user/%committer% (por commit)
        -  users//user/%author% (por commit)

    - users/user/%user%  (por pr)
    - users/user/%head.user% (por pr)
    - users/user/%base.user% (por pr)
    - users/user/%head.repo.owner% (por pr)
    - users/user/%base.repo.owner% (por pr) 

    - repos/user/repo/pulls/%number%/commits - PC (paginado) [min 1, max 255]
        - users/user/%author% (por commit)
        - users/user/%committer% (por commit)


# PR comments
- repos/user/repo/pulls/comments - PCM (paginado)
    - users/user/%user% (por comentario)


# issue
- repos/user/repo/issues - I (paginado)
    - users/user/%user% (por issue)
    - users/user/%asssignee% (por issue)

    - repos/user/repo/issues/number/events - IE (por issue)
        - users/user/%actor% (por evento)


# issue comments
- repos/user/repo/issues/comments - IC (paginado)
    - users/user/%user% (por comentario)


# labels
- repos/user/repo/labels - L (paginado)


# milestones
- repos/user/repo/milestones - M (paginado)