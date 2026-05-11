# fatawa-data-collection

Collect and format Fatawa data

`git checkout main`
`cd ../`

1. `git checkout -b data-1` OR `git checkout data-1` for this direct go to step 4
2. `git push`
3. Copy `git push --set-upstream origin data-1`
4. cd `cd 1-alikhlasonline.com`
5. `python fetch_data.py`
6. `git push`

## Installation

```shell
pip install requests bs4 undetected_chromedriver
```

## Note

if there is any SSL related error then install python from homebrew and after that create venv using homebrew python

```
/opt/homebrew/bin/python3 -m venv venv
```

for **undetected_chromedriver**

```
/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv venv
```
