
import os
import fitz


def create_outline(data):
    # 初始化目录
    outline = []
    # 初始化一级标题
    chapter_1 = {}
    chapter_1['title'] = data[0][1]
    chapter_1['pages'] = data[0][2]
    chapter_1['subitems'] = []
    outline.append(chapter_1)
    # 初始化二级标题和三级标题
    chapter_2 = {}
    chapter_3 = {}
    chapter_4 = {}
    for item in data[1:]:
        if item[0] == 1:
            # 创建新的一级标题
            chapter_1 = {}
            chapter_1['title'] = item[1]
            chapter_1['pages'] = item[2]
            chapter_1['subitems'] = []
            outline.append(chapter_1)
        elif item[0] == 2:
            # 创建新的二级标题
            chapter_2 = {}
            chapter_2['title'] = item[1]
            chapter_2['pages'] = item[2]
            chapter_2['subitems'] = []
            chapter_1['subitems'].append(chapter_2)
        elif item[0] == 3:
            # 创建新的三级标题
            chapter_3 = {}
            chapter_3['title'] = item[1]
            chapter_3['pages'] = item[2]
            chapter_3['subitems'] = []
            chapter_2['subitems'].append(chapter_3)
        elif item[0] == 4:
            # 创建新的四级标题
            chapter_4 = {}
            chapter_4['title'] = item[1]
            chapter_4['pages'] = item[2]
            chapter_3['subitems'].append(chapter_4)
    return outline


def create_mkdir(data, current_path):
    for item in data:
        title = item['title']
        path = os.path.join(current_path, title)
        if not os.path.exists(path):
            os.mkdir(path)
        subitems = item['subitems']
        if isinstance(subitems, list) and len(subitems) > 0:
            create_mkdir(subitems, path)





def extract_images_from_range(doc, start_page, end_page, path, dpi):
    name = 1
    for pg in range(start_page - 1, end_page - 1):
        page = doc.load_page(pg)
        pix = page.get_pixmap(dpi=dpi)
        image_path = os.path.join(path, f"{name}.png")
        pix.save(image_path)
        name += 1

def create_directory_structure(PDFPath, WorkSpace):
    doc = fitz.open(PDFPath)
    data = doc.get_toc()
    data = create_outline(data)
    if not os.path.exists(WorkSpace):
        os.mkdir(WorkSpace)
    create_mkdir(data, WorkSpace)
    doc.close()



def extract_pdf_images_recursive(outline, doc, parent_path, parent_start_page, parent_end_page, dpi):
    for index, item in enumerate(outline):
        item_path = os.path.join(parent_path, item['title'])
        os.makedirs(item_path, exist_ok=True)

        start_page = item['pages']
        if index < len(outline) - 1:
            end_page = outline[index + 1]['pages']
        else:
            end_page = parent_end_page

        if len(item['subitems']) > 0:
            extract_pdf_images_recursive(item['subitems'], doc, item_path, start_page, end_page, dpi)
        else:
            extract_images_from_range(doc, start_page, end_page, item_path, dpi)


def extract_pdf_images(PDFPath, WorkSpace, dpi):
    """
    将PDF转换为图片，一页一图
    :param PDFPath:
    :param WorkSpace:
    :param dpi:
    :return:
    """
    doc = fitz.open(PDFPath)
    outline = create_outline(doc.get_toc())
    extract_pdf_images_recursive(outline, doc, WorkSpace, 1, doc.page_count + 1, dpi)
    doc.close()






# 给用户展示目录
def process_section(section):
    """递归的处理一段
    为了格式化输出目录，将其标题和子标题展示出来
    Args:
        section (dic): outline里面的一个字典

    Returns:
        _type_: [{标题：子标题}]
    """
    if section['subitems']:
        return {
            section['title']: [process_section(subitem) for subitem in section['subitems']]
        }
    else:
        return section['title']


def show_outline(PDFFile):
    """展示目录

    Args:
        PDFFile (_type_): pdf路径

    Returns:
        _type_: 格式化后目录的内容
    """
    doc = fitz.open(PDFFile)
    data = doc.get_toc()
    outline = create_outline(data)
    ans = []
    for item in outline:
        ans.append(process_section(item))

    output = ""

    def format_outline(ans, indent=""):
        """格式化输出


        Args:
            ans (list): 内部是各级标题的关系
            indent (str, optional): 缩进. Defaults to "".

        Returns:
            str: _description_
        """
        output = ""
        if isinstance(ans, list):
            for item in ans:
                output += format_outline(item, indent)
        elif isinstance(ans, dict):
            for title, subitems in ans.items():
                output += indent + title + ":\n"
                output += format_outline(subitems, indent + "  ")
        else:
            output += indent + ans + "\n"
        return output

    output = format_outline(ans)
    return output





# def extract_pdf_images_(outline:list, doc, root_path:str,dpi=500):
#     """根据页码提取pdf

#     Args:
#         outline (list): 目录结构
#         doc (pdf对象): _description_
#         root_path (str): 顶级目录
#     """
#     end_index = 1

#     for level1 in outline:
#         l1_path = os.path.join(root_path, level1['title'])

#         if end_index > len(outline) - 1:            # 取最后一页最为endpage
#             end_page = doc.page_count + 1           # 因为下面循环的时候会减1，因此为了取到最后一页在此处加1
#         else:
#             end_page = outline[end_index]['pages']   # 取下一章的第一页作为结束页

#         if isinstance(level1['subitems'], list) and len(level1['subitems']) != 0:
#             count = 1      # 取下一小节的第一页作为结束页

#             for level2 in level1['subitems']:
#                 l2_path = os.path.join(l1_path, level2['title'])

#                 start = level2['pages']

#                 if count > len(level1['subitems']) - 1:         # 取下一章的第一页作为最后的结束
#                     end = end_page
#                 else:
#                     end = level1['subitems'][count]['pages']

#                 name = 1

#                 for pg in range(start - 1, end - 1):
#                     page = doc.load_page(pg)
#                     pix = page.get_pixmap(dpi = 500)
#                     image_path = os.path.join(l2_path, f"{name}.png")
#                     pix.save(image_path)
#                     name += 1

#                 count += 1

#         end_index += 1
# def extract_pdf_images(PDFPath,WorkSpace,dpi=500):
#     doc = fitz.open(PDFPath)
#     outline = create_outline(doc.get_toc())
#     extract_pdf_images_(outline,doc,WorkSpace,dpi)
#     doc.close()