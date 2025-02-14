#!/bin/bash
echo "hello, world!"
git checkout dev

cd myscript
python tvbox.json.aes.enc.py
cd ..
cat my.enc.json > my.json
git commit -am "Update my.json."

git checkout src
git checkout dev my.json
git commit -am "Update my.json."

git checkout master
git checkout dev my.json
git commit -am "Update my.json."
git push gitee master

git checkout dev
git push gitee --all
git push github --all
