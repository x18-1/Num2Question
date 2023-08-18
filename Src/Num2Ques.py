import os
import sys

import gradio as gr
import fitz
from ultralytics import YOLO
from reportlab.lib import pagesizes
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from setting import *


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)                                               # 添加根目录



img_lists = []

def add(level0: str, level1: str, level2: str, num_question: str):
    """获取用户输入的问题
    将用户每一次add的内容放在一个全局变量img_lists中。
    Args:
        level0 (str): DATASPACE
        level1 (str): 一级标题
        level2 (str): 二级标题
        num_question (str): 用户输入的题号，用空格隔开

    Returns:
        _type_: 全局变量img_lists的内容进行展示
    """
    imgdir = rf"{level0}\{level1}\{level2}"
    img_list = num_question.strip().split(" ")  # 用空格隔开
    img_list = [os.path.join(imgdir, f) for f in [i + ".png" for i in img_list]]
    img_lists.extend(img_list)

    return "\n".join(["/".join(i.split("\\")[-3:]) for i in img_lists])


def generate(output_name):
    doc = fitz.open()
    for i in img_lists:
        img = fitz.open(i)
        rect = img[0].rect  # pic dimension
        pdfbytes = img.convert_to_pdf()  # make a PDF stream
        img.close()  # no longer needed
        imgPDF = fitz.open("pdf", pdfbytes)  # open stream as PDF

        page = doc.new_page(width=rect.width,  # new page with ...
                            height=rect.height)  # pic dimension
        page.show_pdf_page(rect, imgPDF, 0)  # image fills the page

    output_path = os.path.join(os.path.join(root_dir,OUTPATH),output_name)
    doc.save(output_path)
    img_lists.clear()
    return output_path


def show_question_series(path0, path1, path2):
    """显示用户可选择的题号

    Args:
        path0 (_type_): _description_
        path1 (_type_): _description_
        path2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    return "  ".join(sorted([i[:-4] for i in os.listdir(os.path.join(os.path.join(path0, path1), path2))],
                            key=lambda x: int(x.split(".")[0])))


def show_listdir(path):
    return gr.Dropdown.update(choices=os.listdir(path))


def show_listdir2(path0, path1):
    return gr.Dropdown.update(choices=os.listdir(os.path.join(path0, path1)))


def clear_img_lists():
    img_lists.clear()


def load_model():
    """加载yolo模型

    Returns:
        _type_: _description_
    """
    model = YOLO(os.path.join(os.path.join(root_dir,MODEL),"yolov8n.pt"))  # load an official model
    model = YOLO(os.path.join(os.path.join(root_dir,MODEL),"best.pt"))  # pretrained YOLOv8n model
    return model


def Inference(pic_list, model):
    """模型推理

    Args:
        pic_list (list[str]): 图片路径列表
        model (_type_): _description_

    Returns:
        _type_: _description_
    """
    results = model(pic_list)
    return [i.boxes.xyxy.numpy()[0].tolist() for i in results]  # 返回左上角坐标，右下角坐标


def crop_image(input_image_path, crop_area):
    """裁剪图片

    Args:
        input_image_path (_type_): _description_
        crop_area (_type_): _description_

    Returns:
        _type_: _description_
    """
    image = Image.open(input_image_path)
    cropped_image = image.crop(crop_area)
    return cropped_image


def crop_images(pic_list, model):
    """裁剪多个图片

    Args:
        pic_list (_type_): _description_
        model (_type_): _description_

    Returns:
        _type_: _description_
    """
    crop_area_list = Inference(pic_list, model)
    images = []
    for pic, crop_area in zip(pic_list, crop_area_list):
        images.append(crop_image(pic, crop_area))
    return images


def create_pdf_with_images(spacing, output_name, size="A4"):
    pic_list = img_lists
    model = load_model()

    output_path = os.path.join(os.path.join(root_dir, OUTPATH), output_name)

    page_width, page_height = getattr(pagesizes, size)

    c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
    x = 0
    y = page_height - 50  # 调整起始 y 坐标

    images = crop_images(pic_list, model)
    for image in images:
        image_reader = ImageReader(image)
        image_width, image_height = image_reader.getSize()

        # 调整图片大小以适应页面宽度
        if image_width > page_width:
            image_height *= page_width / image_width
            image_width = page_width

        # 检查是否需要换页
        if y - image_height < 50:
            c.showPage()
            y = page_height - 50

        c.drawImage(image_reader, x, y - image_height, width=image_width, height=image_height)

        y -= image_height + spacing
    c.save()
    img_lists.clear()
    return output_path