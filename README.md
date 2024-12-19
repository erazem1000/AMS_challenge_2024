# AMS IZZIV - final report
Author: ERAZEM STONIČ

Model: uni/multiGradICON

Link: [AMS_challenge_2024 Github public repository](https://github.com/erazem1000/AMS_challenge_2024)

## Method Explanation
**uniGradICON** is a deep learning-based medical image registration model designed to **generalize across various datasets and anatomical regions**. It builds upon the GradICON framework, utilizing **gradient inverse consistency regularization to ensure transformation invertibility**. Trained on a composite dataset comprising multiple public medical image corpora, **uniGradICON achieves state-of-the-art performance without the need for task-specific retraining**. This universality enables it to handle diverse registration tasks, including **zero-shot applications to new anatomical regions and modalities**. 

## Results
Attached are some of the *case* as well as *aggregated* results based on [OncoReg]https://learn2reg.grand-challenge.org/oncoreg/ datased. 

```bash
case_results [1] ['0012_0001<--0012_0000']:
	LogJacDetStd        : 0.00000
	num_foldings        : 0.00000
	TRE_kp              : 6.58416
	TRE_lm              : 7.92968
	DSC                 : 0.41284
	HD95                : 34.12803

case_results [2] ['0013_0001<--0013_0000']:
	LogJacDetStd        : 0.71347
	num_foldings        : 0.00000
	TRE_kp              : 32.35297
	TRE_lm              : 26.74784
	DSC                 : 0.12033
	HD95                : 70.85243

...

aggregated_results:
	LogJacDetStd        : 0.29426 +- 0.34554 | 30%: 0.41402
	TRE_kp              : 18.48474 +- 10.26682 | 30%: 23.12678
	TRE_lm              : 19.55000 +- 6.57607 | 30%: 24.50685
	DSC                 : 0.21308 +- 0.09645 | 30%: 0.15938
	HD95                : 51.57832 +- 15.16391 | 30%: 38.63345
```


## Docker Information
To set up the environment, ensure that Docker Compose is installed. It’s typically included with Docker Desktop. For installation guidance, refer to [an Overview of installing Docker Compose](https://docs.docker.com/compose/install/).

In case of cloning the GitHub repository, the `compose.yaml` and `Makefile` are already present in the root directory, as they are essential for running Docker Compose. Otherwise, make sure to put these two files in the root directory of the project.

## Data Preparation
Obtain the OncoReg dataset and place it in the `./input` directory. 
```bash
cd input
wget https://cloud.imi.uni-luebeck.de/s/xQPEy4sDDnHsmNg/download/ThoraxCBCT_OncoRegRelease_06_12_23.zip
unzip ThoraxCBCT_OncoRegRelease_06_12_23.zip
rm -r __MACOSX/
rm ThoraxCBCT_OncoRegRelease_06_12_23.zip
```


## Registration and validation commands
To execute the registration process, navigate to the root directory and run:

```bash
make run-registration
```
For validation, execute:

```bash
make run-validation
```
For additional assistance on `Makefile` commands, feel free to use:

```bash
make help
```

Ensure that the output deformation field from the registration is saved in the `output/disp_{moving}_{fixed}.hdf5` dir, where **fixed** and **moving** correspond to the fixed and moving image names, respectively. 

The `registration` Docker container will guide you through the registration and deformation field transformation processes, preparing the data for validation.

In order to properly adjust deformation field in .hdf5 format **manually** (not required if following all of the procedure of the `registration`), run the following command in the root directory:

```bash
python scripts/data_transform_2.py
```
and then  

```bash
python scripts/data_reshape_2.py
```

You can as well run seprately each image - the registration and the validation.
To run the registration image, use the following command:
```bash
docker run \
    --rm \
    erazem1000/ams_izziv_24_stonic:latest \
    .
```
To run the validation image, use the following command:

```bash
docker run \
    --rm \
    -u $UID:$UID \
    -v ./output/reshaped_validation:/input \
    -v ./output:/output/ \
    gitlab.lst.fe.uni-lj.si:5050/domenp/deformable-registration \
    python evaluation.py -v
```

## Train Commands
There is a possibility to further train the model. In the `./uniGradICON_model_main` subrepository, there is a `/training` dir with `dataset.py` and `train.py` files (and multi versions for the multiGradICON model). Note that these scripts may require adjustments for compatibility with the OncoReg dataset.

## Extensions
An extension for **3D Slicer** is available. For detailed information, refer to the `./extensions/slicer_extension/README.md` file in the repository.

Another option to visualise registered images is via runing the following command from the root directory:
```bash
python scripts/post_process.py --fixed={fixed image path} --warped={warped image path} --transform_file={.hdf5 transform file path}
```
