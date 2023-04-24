# Download Dataset
Download the dataset from the following link:
```angular2html
https://www.dropbox.com/s/vdrt3e1vcav9jpm/ethereum_dataset.tar.gz?dl=0
```
Then, extract it under `EthereumDataset/`.

# Download Model
Download the model from the following link:
```angular2html
https://www.dropbox.com/s/wu6vsnrqzfdj0vq/ethereum_model.tar.gz?dl=0
```
Then, extract it under `src/data`

# Run
Run the following command to install the requirements and create a local server that runs the API:
```
make poetry
```
Note that we suggest you to create a virtual env for the project first. For example,

```
$ conda create -n eth python=3.8
```
then and install poetry
```
$ activate eth
$ pip install poetry
```