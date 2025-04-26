import pyaudio
import wave
import asyncio
import tkinter as tk
from shazamio import Shazam
import requests
from PIL import Image, ImageTk, ImageFilter, ImageStat
import io
import os
import json
from screeninfo import get_monitors
import threading

# set enviroment variable for ALSA
os.enviroment['PA_ALSA_PLUGHW'] = '1'
