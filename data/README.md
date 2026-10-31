# Dataset

This folder is intentionally empty in the public repository.

Download the official capstone dataset from the course materials:

**Capstone_Project_Dataset_FTTT_2026.zip**  
https://drive.google.com/file/d/1jeGjWgZJ4vdfmbB71kghovcCUYNeSHOY/view

Extract it so that the following structure exists relative to the project root:

```
data/
├── kb/          # 21 Markdown documents
├── customers.csv
├── orders.csv
├── order_items.csv
├── products.csv
├── pincodes.csv
├── holidays.csv
├── support_logs.csv
└── practice/
    ├── questions.csv
    └── conversations.csv
```

The mock tools in `src/tools/` expect the CSVs to be present (or adjust the path in tools.py).

Do not commit the full dataset if it is large; the organizers already have it.  
All data is synthetic. Dataset reference date is 20 October 2026.
