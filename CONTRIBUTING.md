# Contribution guide

## Development install

```sh
git clone https://github.com/mondeja/mdpo
cd mdpo
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
