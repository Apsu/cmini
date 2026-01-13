#!/usr/bin/env bash

export GITHUB_TOKEN="$(<github-pat.txt)"

cd ~/workspace/cmini
git add -A authors.json corpora.json likes.json links.json layouts cache
git commit -m "Sync data"
git pull
git push
sudo systemctl restart cmini
