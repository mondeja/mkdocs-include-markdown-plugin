# Contribution guide

## Development install

```sh
git clone https://github.com/mondeja/mkdocs-include-markdown-plugin
cd mkdocs-include-markdown-plugin
pip install hatch
```

## Test

```sh
hatch run tests:unit
# `hatch run tests:integration`
# `hatch run tests:all`
# `hatch run tests:cov`
```

## Linting and translations processing

```sh
hatch run style:lint
```

## Release

```sh
version="$(hatch run bump <major/minor/patch>)"
git add .
git commit -m "Bump version"
git push origin master
git tag -a "v$version"
git push origin "v$version"
```

## Compatibility

Latest version supporting Python3.7 and Mkdocs<1.4.0 is v4.0.4.
