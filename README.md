# Brazilian Legal Text Dataset
Brazilian Legal Text Dataset for pre-trainning transformer based models

## Requeriments
Before run, you have to install in your path a Firefox WebDriver for Selenium.

## Get Started

#### Dependencies
Run command below to install all required dependencies.

```shell
pip install -r requirements.txt
```

#### Running all pipeline
Run the command below to run all pipeline (scraper, parser and merge all files). 
You have to specify a goal (mlm or sts).

```shell
python run.py mlm
```

or 

```shell
python run.py sts
```

#### Running individual task
To run individual tasks, you have tod specify task and :

```shell
python run.py sts --scrap
python run.py sts --parse
python run.py sts --export
python run.py mlm --scrap
python run.py mlm --parse
python run.py mlm --export
```

All outputs will be created in path `output` folder.
