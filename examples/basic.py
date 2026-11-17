from parse_md import EXTENDED, render

result = render('# Example\n\n| A | B |\n| --- | --- |\n| one | two |\n', dialect=EXTENDED)
assert '<table>' in result.html
print(result.html)
