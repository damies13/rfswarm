import codecs
import csv
import math
import os
import re
import shutil
import time
import zipfile
import json
import urllib

from cmath import log10
from datetime import datetime
from decimal import Decimal
from io import StringIO

import chardet
import pandas as pd
import pyperclip
import xmltodict
from PIL import Image
from robot.api.deco import keyword, library