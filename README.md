# project-33t

## Introduction

The goal of this project is to use [image-match](https://github.com/ProvenanceLabs/image-match) and the [Discogs API](https://www.discogs.com/developers) to recognize vinyl album covers and fetch related data. 

Use cases : 

> I'm in a vinyl store, I take a picture of a cover to know if I have it in my collection. If I don't have it, then what's the mean price on Discogs, is the price I'm seeing fair ?

> I want to quickly add a dozen (or hundreds of) records to my collection

Using image-match to recognize albums cover [has proven successful at Deezer](https://deezer.io/matching-albums-through-cover-art-fingerprinting-bdca82cd17dc), that's why I'll be using this method.

## Building the API with docker-compose

```
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build
```

## Notes

Seems to work only for near-identical images

## TODO

- Preprocess image : crop it into a square and always download the image when we're dealing with an URL
