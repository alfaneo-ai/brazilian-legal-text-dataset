# Brazilian Legal Text Dataset
Brazilian Legal Text Dataset for pre-trainning transformer based models

## Requeriments
Before run, you have to install in your path a Firefox WebDriver for Selenium.

## Get Started
To start scraper, parser and merge all files just run the commands:

```shell
pip install -r requirements.txt
python run.py
```
The output will be created in path `output/corpus.txt`.

You can also run individual tasks:

```shell
python run.py scrap
python run.py parse
python run.py merge
```