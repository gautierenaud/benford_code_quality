# Benford

After hearing a documentary about how [Benford's law](https://en.wikipedia.org/wiki/Benford%27s_law) was used to discover anomalies in tax declaration, I wanted to know if I can use it for code quality.

First hypothesis:
```
LOC should follow Benford's law. If not, there is something fishy.
```

With the first version of the script, we can already see that the different metrics seem to follow Benford's law.

The metrics are from [pygount](https://pygount.readthedocs.io/en/latest/api.html):
* code: line of code
* empty: line with only whitespaces/newline
* doc: documentation
* string: lines containing only strings for the language)

### Pygount

![Scan of pygount](docs/pygount_v1.png)

### Numpy

![Scan of numpy](docs/numpy_v1.png)

It looks very good, especially with numpy. The bigger the project, the more it matches.

# Reminders

Python venv:
```bash
python3 -m venv venv
source venv/bin/activate
```