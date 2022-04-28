
# tools enviroment
```bash
conda activate -n tools python=3.6
conda install -c menpo opencv
pip3 install matplotlib
conda install opencv 
conda install scikit-image

```

# ORC enviroment
this is tools package

conda install -c conda-forge tesseract
pip3 install pyocr


# hausdorff

```bash
conda create -n hausdorff python=3.6
conda activate hausdorff
pip install monai
pip3 install matplotlib
pip install scikit-image
pip install plyfile


```
## overcommit handling 

```bash
$ cat /proc/sys/vm/overcommit_memory
0
```

```bash
$ sudo su
$ echo 1 > /proc/sys/vm/overcommit_memory

```
