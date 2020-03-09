#### Example execution:

##### Regular files
```
cd src/
python main.py -i ../data/toy_data/wiki/ -o ../output/toy_data/to_concat.txt
```

##### Files already sentence splitted and concatenated
```
cd src/
python main.py -i ../data/toy_data/shuf/ -o ../output/toy_data/to_concat.txt -c True
```

#### Directory structure:
Needs to read from /data/ folder and have an already created /output/ directory
