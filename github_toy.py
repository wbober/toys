#!/usr/bin/env python3

import csv
import time
import github
from argparse import ArgumentParser
from github import Github
from github import Commit

class PullRequestComment2(github.PullRequestComment.PullRequestComment):
    @property
    def line(self):
        self._completeIfNotSet(self._line)
        return self._line.value

    def _initAttributes(self):
        super()._initAttributes()
        self._line = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        super()._useAttributes(attributes)
        if "line" in attributes:
            self._line = self._makeIntAttribute(attributes["line"])

def create_comment(pr, body, commit_id, path, line):
    assert isinstance(body, str), body
    assert isinstance(commit_id, github.Commit.Commit), commit_id
    assert isinstance(path, str), path
    assert isinstance(line, int), line
    post_parameters = {
        "body": body,
        "commit_id": commit_id._identity,
        "path": path,
        "line": line,
    }
    headers, data = pr._requester.requestJsonAndCheck(
        "POST", pr.url + "/comments", input=post_parameters
    )
    return github.PullRequestComment.PullRequestComment(
        pr._requester, headers, data, completed=True
    )

def get_review_comments(pr, since=github.GithubObject.NotSet):
    assert since is github.GithubObject.NotSet or isinstance(
        since, datetime.datetime
    ), since
    url_parameters = dict()
    if since is not github.GithubObject.NotSet:
        url_parameters["since"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    return github.PaginatedList.PaginatedList(
        PullRequestComment2,
        pr._requester,
        pr.url + "/comments",
        url_parameters,
    )

def upload_comments(args, comments):
    g = Github(args.token)
    repo = g.get_repo(args.repo)
    pr = repo.get_pull(args.pull_req)

    commits = pr.get_commits()
    for comment in comments:
        comment_text=comment['comment'].encode().decode('unicode_escape')
        create_comment(pr, f"[{comment['type']}]\n[{args.c}]\n\n{comment_text}",
                       commits.reversed[0],
                       comment['file'],
                       int(comment['line']))

if __name__ == "__main__":
    argparse = ArgumentParser()
    argparse.add_argument("token", help="GitHub authorization token")
    argparse.add_argument("repo", help="Github repository")
    argparse.add_argument("pull_req", help="Pull Request number", type=int)
    argparse.add_argument("csv", help="CSV file with comments")
    argparse.add_argument("-c", help="Company name")

    args = argparse.parse_args()
    print(args)

    comments = []

    with open(args.csv, newline='') as csvfile:
        comments = csv.DictReader(csvfile)
        upload_comments(args, comments)