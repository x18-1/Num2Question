import gradio as gr
import os
import fitz
from ultralytics import YOLO
from PIL import Image
from reportlab.lib import pagesizes
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
