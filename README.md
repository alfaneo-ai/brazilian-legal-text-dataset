# Brazilian Legal Text Dataset
Brazilian Legal Text Dataset for pre-trainning transformer based models

## Requeriments
Before run, you have to install in your path a Firefox WebDriver for Selenium.
Download last release at <https://github.com/mozilla/geckodriver/releases>
Put executable file in PATH.

## Get Started
Run command below to install all required dependencies.

```shell
pip install -r requirements.txt
```

## Generate MLM Dataset
To generate a dataset for MLM BERT pre-trainning.
Run the command below to execute all pipeline that will generate a single file `output/mlm/corpus.txt`.

```shell
python mlm.py all
```

To run individual tasks, you can pass a task as parameter:

```shell
python mlm.py scrap
python run.py parse
python run.py export
```

## Generate STS Dataset
To generate a dataset for STS BERT fine-tunning.
Run the command below to execute all pipeline that will generate two files `output/sts/train.csv` and `output/sts/dev.csv`.

```shell
python sts.py all
```