# fetch_esco

Simple command-line tool to fetch occupation, skill and knowledge data from ESCO (the European Skills, Competences, Qualifications and Occupations) 

## Requirements

- Dart SDK (tested with 3.9.2)

See package configuration in [pubspec.yaml](pubspec.yaml).

## Run

1. Install dependencies
```
dart pub get
```
2. Run
```
dart run
```

Data is written is `data/` folder
- `data/data.json`: full job description
- `data/knowledge.json`: Unique list of knowledges appear in the dataset
- `data/skill.json`: Unique list of skills appear in the dataset