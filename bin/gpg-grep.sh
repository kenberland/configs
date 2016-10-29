#!/bin/bash

gpg --use-agent -d $1 | grep $2
