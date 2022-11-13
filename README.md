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

Elastic is thread safe but one instance cannot be used across threads. 
So, in order to parallelize multi-orientation image saerch, we'll have to create a new instance of SignatureES per thread.

Seems to work only for near-identical images

## TODO

- Use FastAPI instead of Flask
