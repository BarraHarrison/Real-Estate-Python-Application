# Real Estate Application in Python
import os 
import json 
import time 
from functools import cache 

import requests 
import numpy as np 
import pandas as pd 

import folium
from folium.plugins import MarkerCluster
from folium import MacroElement

from flask import Flask, render_template, request

app = Flask(__name__)