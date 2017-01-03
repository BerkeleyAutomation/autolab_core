#!/bin/sh
if [ -z "$1" ]
then
  echo "Please provide the folder you want to deploy to GitHub Pages as an argument"
  exit 1
fi
git push origin --delete gh-pages
git subtree push --prefix $1 origin gh-pages
